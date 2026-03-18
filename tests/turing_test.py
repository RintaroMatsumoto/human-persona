"""Turing Test Benchmark: 人間らしさの自動評価フレームワーク.

HumanPersonaBase の出力を LLM ジャッジ (Claude Sonnet) で採点し、
human_likeness_score / style_variation_rate / timing_naturalness の
3指標でベンチマークする。
"""

from __future__ import annotations

import json
import os
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import anthropic

# プロジェクトルートをパスに追加
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.base_persona import HumanPersonaBase, PersonaResponse
from core.timing_controller import Platform


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TestScenario:
    """テストシナリオ定義.

    Attributes:
        id: シナリオ識別子
        language: 言語コード (ja / en)
        platform: プラットフォーム種別
        user_message: ユーザーメッセージ
        context: シナリオの文脈説明
        topics: 関連トピック
    """

    id: str
    language: str
    platform: str
    user_message: str
    context: str
    topics: list[str] = field(default_factory=list)


@dataclass
class JudgeScore:
    """LLMジャッジの採点結果.

    Attributes:
        human_likeness_score: 人間らしさスコア (1-10)
        style_variation_rate: 文体均質性 (0.0-1.0, 高いほど均質=悪い)
        timing_naturalness: タイミング自然性スコア (1-10)
    """

    human_likeness_score: float
    style_variation_rate: float
    timing_naturalness: float


@dataclass
class ScenarioResult:
    """シナリオごとの評価結果.

    Attributes:
        scenario: テストシナリオ
        responses: PersonaResponse のリスト (複数回実行)
        judge_score: LLMジャッジのスコア
    """

    scenario: TestScenario
    responses: list[PersonaResponse]
    judge_score: JudgeScore | None = None


# ---------------------------------------------------------------------------
# Test scenarios
# ---------------------------------------------------------------------------

SCENARIOS: list[TestScenario] = [
    # --- Japanese scenarios (5) ---
    TestScenario(
        id="ja_01_initial_contact",
        language="ja",
        platform="chat",
        user_message="はじめまして。ライティング案件の件でご連絡しました。",
        context="クラウドソーシングで初回メッセージを受信した場面",
        topics=["ライティング", "初回連絡"],
    ),
    TestScenario(
        id="ja_02_deadline_question",
        language="ja",
        platform="crowdsourcing_message",
        user_message="納期は来週金曜日までに変更可能でしょうか？少し厳しい状況です。",
        context="進行中案件で納期変更の相談",
        topics=["納期", "スケジュール変更"],
    ),
    TestScenario(
        id="ja_03_revision_request",
        language="ja",
        platform="chat",
        user_message="修正をお願いしたいのですが、3箇所ほど変更点があります。",
        context="納品後の修正依頼",
        topics=["修正", "フィードバック"],
    ),
    TestScenario(
        id="ja_04_positive_feedback",
        language="ja",
        platform="chat",
        user_message="素晴らしい仕上がりですね！次回もぜひお願いしたいです。",
        context="納品物に対するポジティブなフィードバック",
        topics=["評価", "リピート"],
    ),
    TestScenario(
        id="ja_05_ambiguous_spec",
        language="ja",
        platform="crowdsourcing_message",
        user_message="デザインの方向性なんですが、なんとなくシンプルな感じでお願いします。",
        context="曖昧な仕様指示への対応",
        topics=["デザイン", "仕様確認"],
    ),
    # --- English scenarios (5) ---
    TestScenario(
        id="en_01_initial_contact",
        language="en",
        platform="chat",
        user_message="Hi there! I saw your profile and wanted to discuss a writing project.",
        context="First contact on a crowdsourcing platform",
        topics=["writing", "initial contact"],
    ),
    TestScenario(
        id="en_02_scope_change",
        language="en",
        platform="crowdsourcing_message",
        user_message="Hey, so the scope has changed a bit — we need 3 more pages added. Is that doable?",
        context="Scope change mid-project",
        topics=["scope", "additional work"],
    ),
    TestScenario(
        id="en_03_bug_report",
        language="en",
        platform="chat",
        user_message="Found a couple of issues in the latest delivery. Can we fix these ASAP?",
        context="Quality issue report after delivery",
        topics=["bugs", "revision"],
    ),
    TestScenario(
        id="en_04_payment_question",
        language="en",
        platform="chat",
        user_message="Quick question — when should I expect the payment to go through?",
        context="Payment timing inquiry",
        topics=["payment", "timeline"],
    ),
    TestScenario(
        id="en_05_casual_followup",
        language="en",
        platform="chat",
        user_message="Just checking in — how's the project coming along?",
        context="Casual follow-up from client",
        topics=["progress", "check-in"],
    ),
]


# ---------------------------------------------------------------------------
# LLM Judge
# ---------------------------------------------------------------------------

JUDGE_SYSTEM_PROMPT = """\
You are an expert evaluator assessing whether AI-generated behavioral parameters \
appear human-like. You will receive a set of persona response parameters \
(timing, style, emotion state, metadata) generated across multiple runs for the \
same user message.

Evaluate the following 3 metrics on a scale. Return ONLY a JSON object with \
no markdown formatting, no code fences, no explanation.

Metrics:
1. "human_likeness_score" (1-10): How human-like are the response parameters? \
   Consider: Is the timing realistic? Are style choices varied and contextually \
   appropriate? Does the emotion state progression feel natural?
2. "style_variation_rate" (0.0-1.0): How homogeneous are the outputs across runs? \
   0.0 = maximally varied (good), 1.0 = identical every time (bad, AI-like).
3. "timing_naturalness" (1-10): How natural is the timing distribution? \
   Consider: Does it avoid machine-like precision? Is there realistic variance? \
   Does it fit the platform context?

Return format (JSON only):
{"human_likeness_score": N, "style_variation_rate": N, "timing_naturalness": N}\
"""


def _build_judge_prompt(scenario: TestScenario, responses: list[PersonaResponse]) -> str:
    """LLMジャッジに渡すユーザープロンプトを構築する."""
    runs = []
    for i, resp in enumerate(responses):
        runs.append({
            "run": i + 1,
            "delay_seconds": round(resp.delay_seconds, 2),
            "emotion_state": resp.emotion_state.value,
            "style_used": resp.style_used.value,
            "metadata": resp.metadata,
        })

    payload = {
        "scenario_id": scenario.id,
        "language": scenario.language,
        "platform": scenario.platform,
        "context": scenario.context,
        "user_message": scenario.user_message,
        "runs": runs,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


class LLMJudge:
    """Anthropic API を使った LLM ジャッジ.

    Attributes:
        client: Anthropic クライアント
        model: 使用モデル ID
    """

    def __init__(self, model: str = "claude-sonnet-4-20250514") -> None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY environment variable is required. "
                "Set it before running the benchmark."
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def evaluate(self, scenario: TestScenario, responses: list[PersonaResponse]) -> JudgeScore:
        """シナリオと応答群を評価してスコアを返す.

        Args:
            scenario: テストシナリオ
            responses: 同一シナリオの複数回実行結果

        Returns:
            JudgeScore
        """
        user_prompt = _build_judge_prompt(scenario, responses)
        message = self.client.messages.create(
            model=self.model,
            max_tokens=256,
            system=JUDGE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = message.content[0].text.strip()
        data = json.loads(raw)
        return JudgeScore(
            human_likeness_score=float(data["human_likeness_score"]),
            style_variation_rate=float(data["style_variation_rate"]),
            timing_naturalness=float(data["timing_naturalness"]),
        )


# ---------------------------------------------------------------------------
# Timing Distribution Analyzer
# ---------------------------------------------------------------------------

class TimingDistributionAnalyzer:
    """タイミング分布の分析器.

    人間の返信タイミングは正規分布に収束しすぎない不規則さを持つ。
    生成されたタイミングが正規分布に過度に一致していないか検証する。
    """

    @staticmethod
    def analyze(delays: list[float], platform: str) -> dict[str, Any]:
        """遅延値リストの分布を分析する.

        Args:
            delays: 遅延秒数のリスト
            platform: プラットフォーム名

        Returns:
            統計情報と正規性判定を含む辞書
        """
        if len(delays) < 2:
            return {
                "platform": platform,
                "sample_size": len(delays),
                "warning": "insufficient samples for analysis",
            }

        mean = statistics.mean(delays)
        stdev = statistics.stdev(delays)
        cv = stdev / mean if mean > 0 else 0.0

        # 変動係数が極端に低い場合は正規分布への過収束を警告
        # 人間の返信は CV > 0.15 程度のばらつきが自然
        too_regular = cv < 0.10

        return {
            "platform": platform,
            "sample_size": len(delays),
            "mean_seconds": round(mean, 2),
            "stdev_seconds": round(stdev, 2),
            "coefficient_of_variation": round(cv, 4),
            "min_seconds": round(min(delays), 2),
            "max_seconds": round(max(delays), 2),
            "too_regular_warning": too_regular,
        }


# ---------------------------------------------------------------------------
# TuringTestRunner
# ---------------------------------------------------------------------------

class TuringTestRunner:
    """Turing Test ベンチマークの実行エンジン.

    Attributes:
        config_dir: 設定ファイルディレクトリ
        runs_per_scenario: シナリオあたりの実行回数
        judge: LLM ジャッジ (None の場合はスコアリングをスキップ)
        results: 実行結果のリスト
    """

    def __init__(
        self,
        config_dir: str | Path | None = None,
        runs_per_scenario: int = 5,
        use_judge: bool = True,
    ) -> None:
        self.config_dir = Path(config_dir) if config_dir else PROJECT_ROOT / "config"
        self.runs_per_scenario = runs_per_scenario
        self.judge = LLMJudge() if use_judge else None
        self.results: list[ScenarioResult] = []
        self._timing_analyzer = TimingDistributionAnalyzer()

    def _load_persona(self, language: str) -> HumanPersonaBase:
        """言語に対応するペルソナをロードする."""
        config_path = self.config_dir / f"{language}.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")
        return HumanPersonaBase.from_config_file(config_path)

    def run_scenario(self, scenario: TestScenario) -> ScenarioResult:
        """単一シナリオを複数回実行し、結果を返す.

        Args:
            scenario: テストシナリオ

        Returns:
            ScenarioResult
        """
        responses: list[PersonaResponse] = []
        for _ in range(self.runs_per_scenario):
            persona = self._load_persona(scenario.language)
            persona.platform = Platform(scenario.platform)
            resp = persona.process_message(scenario.user_message, scenario.topics)
            responses.append(resp)

        judge_score = None
        if self.judge:
            try:
                judge_score = self.judge.evaluate(scenario, responses)
            except Exception as e:
                print(f"  [WARN] Judge failed for {scenario.id}: {e}", file=sys.stderr)

        result = ScenarioResult(
            scenario=scenario,
            responses=responses,
            judge_score=judge_score,
        )
        self.results.append(result)
        return result

    def run_all(self, scenarios: list[TestScenario] | None = None) -> list[ScenarioResult]:
        """全シナリオを実行する.

        Args:
            scenarios: 実行するシナリオ群 (None の場合はデフォルト全件)

        Returns:
            ScenarioResult のリスト
        """
        targets = scenarios or SCENARIOS
        print(f"Running {len(targets)} scenarios x {self.runs_per_scenario} runs each...")
        print()

        for scenario in targets:
            print(f"  [{scenario.id}] {scenario.context}")
            self.run_scenario(scenario)

        print()
        return self.results

    def generate_report(self) -> dict[str, Any]:
        """実行結果からレポートを生成する.

        Returns:
            レポート辞書 (JSON出力対応)
        """
        scored = [r for r in self.results if r.judge_score is not None]

        if not scored:
            # Even without judge scores, output timing distribution and per-scenario data
            timing_analysis: dict[str, Any] = {}
            for platform in ["chat", "crowdsourcing_message"]:
                delays = []
                for r in self.results:
                    if r.scenario.platform == platform:
                        delays.extend(resp.delay_seconds for resp in r.responses)
                if delays:
                    timing_analysis[platform] = self._timing_analyzer.analyze(delays, platform)

            per_scenario = []
            for r in self.results:
                per_scenario.append({
                    "scenario_id": r.scenario.id,
                    "language": r.scenario.language,
                    "platform": r.scenario.platform,
                    "delays": [round(resp.delay_seconds, 2) for resp in r.responses],
                    "styles": [resp.style_used.value for resp in r.responses],
                    "emotions": [resp.emotion_state.value for resp in r.responses],
                })

            return {
                "summary": {
                    "total_scenarios": len(self.results),
                    "scored_scenarios": 0,
                    "runs_per_scenario": self.runs_per_scenario,
                    "note": "Judge disabled — timing and style data only",
                },
                "timing_distribution": timing_analysis,
                "per_scenario": per_scenario,
            }

        hl_scores = [r.judge_score.human_likeness_score for r in scored]
        sv_rates = [r.judge_score.style_variation_rate for r in scored]
        tn_scores = [r.judge_score.timing_naturalness for r in scored]

        # 均質性が高い出力を検出
        high_homogeneity = [
            r.scenario.id for r in scored
            if r.judge_score.style_variation_rate < 0.3
        ]

        # タイミング分布分析
        timing_analysis: dict[str, Any] = {}
        for platform in ["chat", "crowdsourcing_message"]:
            delays = []
            for r in self.results:
                if r.scenario.platform == platform:
                    delays.extend(resp.delay_seconds for resp in r.responses)
            if delays:
                timing_analysis[platform] = self._timing_analyzer.analyze(delays, platform)

        report = {
            "summary": {
                "total_scenarios": len(self.results),
                "scored_scenarios": len(scored),
                "runs_per_scenario": self.runs_per_scenario,
            },
            "aggregate_scores": {
                "human_likeness": {
                    "mean": round(statistics.mean(hl_scores), 2),
                    "stdev": round(statistics.stdev(hl_scores), 2) if len(hl_scores) > 1 else 0,
                    "min": round(min(hl_scores), 2),
                    "max": round(max(hl_scores), 2),
                },
                "style_variation_rate": {
                    "mean": round(statistics.mean(sv_rates), 3),
                    "stdev": round(statistics.stdev(sv_rates), 3) if len(sv_rates) > 1 else 0,
                },
                "timing_naturalness": {
                    "mean": round(statistics.mean(tn_scores), 2),
                    "stdev": round(statistics.stdev(tn_scores), 2) if len(tn_scores) > 1 else 0,
                    "min": round(min(tn_scores), 2),
                    "max": round(max(tn_scores), 2),
                },
            },
            "warnings": [],
            "timing_distribution": timing_analysis,
            "per_scenario": [],
        }

        # 警告
        if high_homogeneity:
            report["warnings"].append({
                "type": "high_style_homogeneity",
                "message": f"style_variation_rate < 0.3 detected in {len(high_homogeneity)} scenario(s)",
                "scenarios": high_homogeneity,
            })

        for analysis in timing_analysis.values():
            if analysis.get("too_regular_warning"):
                report["warnings"].append({
                    "type": "timing_too_regular",
                    "message": f"Timing on {analysis['platform']} has low variance (CV={analysis['coefficient_of_variation']})",
                    "platform": analysis["platform"],
                })

        # シナリオ別詳細
        for r in self.results:
            entry: dict[str, Any] = {
                "scenario_id": r.scenario.id,
                "language": r.scenario.language,
                "platform": r.scenario.platform,
                "delays": [round(resp.delay_seconds, 2) for resp in r.responses],
                "styles": [resp.style_used.value for resp in r.responses],
                "emotions": [resp.emotion_state.value for resp in r.responses],
            }
            if r.judge_score:
                entry["judge_score"] = {
                    "human_likeness_score": r.judge_score.human_likeness_score,
                    "style_variation_rate": r.judge_score.style_variation_rate,
                    "timing_naturalness": r.judge_score.timing_naturalness,
                }
            report["per_scenario"].append(entry)

        return report

    def print_report(self, report: dict[str, Any] | None = None) -> None:
        """レポートをコンソールに整形出力する."""
        report = report or self.generate_report()

        print("=" * 60)
        print("  TURING TEST BENCHMARK REPORT")
        print("=" * 60)

        summary = report.get("summary", {})
        if isinstance(summary, str):
            print(f"\n{summary}")
            return

        print(f"\n  Scenarios: {summary['total_scenarios']} "
              f"(scored: {summary['scored_scenarios']})")
        print(f"  Runs per scenario: {summary['runs_per_scenario']}")

        agg = report.get("aggregate_scores", {})
        if agg:
            hl = agg["human_likeness"]
            sv = agg["style_variation_rate"]
            tn = agg["timing_naturalness"]
            print(f"\n  [Aggregate Scores]")
            print(f"    Human Likeness:      {hl['mean']:.1f} +/- {hl['stdev']:.1f}  "
                  f"(range: {hl['min']:.1f} - {hl['max']:.1f})")
            print(f"    Style Variation:     {sv['mean']:.3f} +/- {sv['stdev']:.3f}  "
                  f"(lower = more varied = better)")
            print(f"    Timing Naturalness:  {tn['mean']:.1f} +/- {tn['stdev']:.1f}  "
                  f"(range: {tn['min']:.1f} - {tn['max']:.1f})")

        warnings = report.get("warnings", [])
        if warnings:
            print(f"\n  [Warnings] ({len(warnings)})")
            for w in warnings:
                print(f"    !! {w['message']}")
                if "scenarios" in w:
                    for s in w["scenarios"]:
                        print(f"       - {s}")

        timing = report.get("timing_distribution", {})
        if timing:
            print(f"\n  [Timing Distribution]")
            for platform, analysis in timing.items():
                cv = analysis.get("coefficient_of_variation", "N/A")
                flag = " [TOO REGULAR]" if analysis.get("too_regular_warning") else ""
                print(f"    {platform}: mean={analysis['mean_seconds']:.1f}s "
                      f"stdev={analysis['stdev_seconds']:.1f}s CV={cv}{flag}")

        per = report.get("per_scenario", [])
        if per:
            print(f"\n  [Per-Scenario Details]")
            for entry in per:
                score_str = ""
                if "judge_score" in entry:
                    js = entry["judge_score"]
                    score_str = (f" | HL={js['human_likeness_score']:.0f} "
                                 f"SV={js['style_variation_rate']:.2f} "
                                 f"TN={js['timing_naturalness']:.0f}")
                styles_unique = len(set(entry["styles"]))
                print(f"    {entry['scenario_id']} [{entry['language']}/{entry['platform']}] "
                      f"styles={styles_unique}/{len(entry['styles'])} unique{score_str}")

        print()
        print("=" * 60)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI エントリーポイント."""
    import argparse

    parser = argparse.ArgumentParser(description="Human Persona Turing Test Benchmark")
    parser.add_argument("--runs", type=int, default=5, help="Runs per scenario (default: 5)")
    parser.add_argument("--no-judge", action="store_true", help="Skip LLM judge (offline mode)")
    parser.add_argument("--output", type=str, default=None, help="JSON output file path")
    parser.add_argument("--config-dir", type=str, default=None, help="Config directory path")
    args = parser.parse_args()

    runner = TuringTestRunner(
        config_dir=args.config_dir,
        runs_per_scenario=args.runs,
        use_judge=not args.no_judge,
    )
    runner.run_all()
    report = runner.generate_report()

    runner.print_report(report)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Report saved to: {output_path}")


if __name__ == "__main__":
    main()
