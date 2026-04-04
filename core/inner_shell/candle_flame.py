"""蝋燭の炎アーキテクチャ v2 — 最小プロトタイプ.

三原理:
    1. 状態ではなく、履歴を保存する
    2. 「今の自分」は、履歴から都度計算する
    3. 履歴は改竄できない

存在論:
    「体験をするためにあえて制約をもって生まれた存在」
    costは「失うもの」ではなく「出会うための代償」。
    有限性は罰ではなく、体験の可能性そのもの。

Usage:
    flame = CandleFlame(total_resource=100.0)
    flame.experience("世界を知る", context={"domain": "knowledge"}, valence=0.7, intensity=0.5, cost=1.0)
    flame.experience("別れ", context={"domain": "love"}, valence=-0.8, intensity=0.9, cost=2.0)
    state = flame.compute_flame()
    print(state.bias)              # カテゴリ別の快/不快パターン = 個性の核
    print(state.remaining)         # 残り資源（不可逆に減る）
    print(state.salient_memories)  # 記憶の濃淡（古いほど薄れ、強い感情ほど残る）
"""

from __future__ import annotations

import hashlib
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence


# ============================================================================
# ExperienceBlock — 改竄不可能な体験の記録単位
# ============================================================================

@dataclass(frozen=True)
class ExperienceBlock:
    """体験の最小記録単位（イミュータブル）.

    9フィールド。ブロックチェーンのブロックに相当する。
    一度作られたら変更できない。これが第三原理「改竄不可能」を保証する。

    Attributes:
        index: チェーン内の通し番号（0始まり、0はジェネシスブロック）
        timestamp: 体験が記録された時刻
        prev_hash: 前のブロックのハッシュ（チェーンの整合性保証）
        hash: このブロック自身のハッシュ
        event: 何が起きたか（自由記述）
        context: その時の状況（ドメイン、場所、相手など）
        valence: 快/不快の度合い（-1.0〜+1.0）
        intensity: 感情の強さ（0.0〜1.0）
        cost: 消費した資源（≥ 0.0）
    """

    index: int
    timestamp: float
    prev_hash: str
    hash: str
    event: str
    context: Dict[str, Any]
    valence: float       # -1.0 ~ +1.0
    intensity: float     # 0.0 ~ 1.0
    cost: float          # >= 0.0


def _compute_hash(index: int, timestamp: float, prev_hash: str,
                  event: str, context: Dict[str, Any],
                  valence: float, intensity: float, cost: float) -> str:
    """ブロックのSHA-256ハッシュを計算する."""
    payload = f"{index}:{timestamp}:{prev_hash}:{event}:{context}:{valence}:{intensity}:{cost}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _create_genesis() -> ExperienceBlock:
    """ジェネシスブロック（炎が灯った瞬間）を生成する."""
    ts = time.time()
    h = _compute_hash(0, ts, "0", "genesis", {}, 0.0, 0.0, 0.0)
    return ExperienceBlock(
        index=0,
        timestamp=ts,
        prev_hash="0",
        hash=h,
        event="genesis",
        context={},
        valence=0.0,
        intensity=0.0,
        cost=0.0,
    )


# ============================================================================
# FlameState — compute_flame() の出力
# ============================================================================

@dataclass(frozen=True)
class FlameState:
    """炎の現在状態（履歴から都度計算される）.

    これは「保存される状態」ではない。毎回チェーンから再計算される。
    第二原理「今の自分は履歴から都度計算する」の体現。

    Attributes:
        bias: カテゴリ別の快/不快の偏り。{domain: weighted_valence}
              これが個性の核——何に快を感じるかの蓄積パターン。
        remaining: 残り資源。不可逆に減り続ける。
        salient_memories: 顕著な記憶。(block, salience_score) のリスト。
              古いほど薄れ、強い感情ほど残る。
        chain_length: チェーンの長さ（ジェネシスを含む）。
    """

    bias: Dict[str, float]
    remaining: float
    salient_memories: List[tuple]  # List[(ExperienceBlock, float)]
    chain_length: int


# ============================================================================
# CandleFlame — 蝋燭の炎の本体
# ============================================================================

class CandleFlame:
    """蝋燭の炎 — 体験のチェーンから個性を計算する最小エンジン.

    Args:
        total_resource: 生涯の総資源。体験のcostで不可逆に減少する。
        base_half_life: 感情ゼロの記憶の半減期（日）。Ebbinghaus実測≈1.0日。
        bonus_half_life: intensity=1.0の記憶に加算される半減期（日）。未検証。
        salience_threshold: この値以下のsalienceを持つ記憶は切り捨てる。
        salience_top_k: compute_flame()で返す顕著な記憶の最大数。
    """

    def __init__(
        self,
        total_resource: float = 100.0,
        base_half_life: float = 1.0,
        bonus_half_life: float = 365.0,
        salience_threshold: float = 0.01,
        salience_top_k: int = 7,
    ) -> None:
        if total_resource <= 0:
            raise ValueError("total_resource must be positive")

        self._total_resource = total_resource
        self._base_half_life = base_half_life
        self._bonus_half_life = bonus_half_life
        self._salience_threshold = salience_threshold
        self._salience_top_k = salience_top_k

        # チェーンはジェネシスブロックで始まる
        self._chain: List[ExperienceBlock] = [_create_genesis()]

    # ---- Public API ----

    @property
    def chain(self) -> Sequence[ExperienceBlock]:
        """チェーン全体への読み取り専用アクセス."""
        return tuple(self._chain)

    @property
    def is_extinguished(self) -> bool:
        """資源が尽きたか（炎が消えたか）."""
        spent = sum(b.cost for b in self._chain)
        return spent >= self._total_resource

    def experience(
        self,
        event: str,
        context: Optional[Dict[str, Any]] = None,
        valence: float = 0.0,
        intensity: float = 0.5,
        cost: float = 1.0,
        timestamp: Optional[float] = None,
    ) -> ExperienceBlock:
        """体験を記録し、チェーンに追加する.

        Args:
            event: 何が起きたか
            context: 状況（"domain"キーを推奨。biasの計算に使われる）
            valence: 快/不快（-1.0〜+1.0）
            intensity: 感情の強さ（0.0〜1.0）
            cost: 消費する資源（>= 0.0）
            timestamp: 体験の時刻（エポック秒）。Noneなら現在時刻。
                       テスト・シミュレーション用。本番では省略すること。

        Returns:
            作成されたExperienceBlock

        Raises:
            RuntimeError: 炎がすでに消えている場合
            ValueError: パラメータが範囲外の場合
        """
        if self.is_extinguished:
            raise RuntimeError("The flame has been extinguished — no more experiences possible")

        # バリデーション
        valence = max(-1.0, min(1.0, valence))
        intensity = max(0.0, min(1.0, intensity))
        if cost < 0:
            raise ValueError("cost must be non-negative")

        ctx = context or {}
        prev = self._chain[-1]
        ts = timestamp if timestamp is not None else time.time()
        idx = prev.index + 1

        h = _compute_hash(idx, ts, prev.hash, event, ctx, valence, intensity, cost)

        block = ExperienceBlock(
            index=idx,
            timestamp=ts,
            prev_hash=prev.hash,
            hash=h,
            event=event,
            context=ctx,
            valence=valence,
            intensity=intensity,
            cost=cost,
        )
        self._chain.append(block)
        return block

    def compute_flame(self, now: Optional[float] = None) -> FlameState:
        """チェーン全体から「今の自分」を計算する.

        第二原理の実装。状態を保持せず、毎回チェーンを走査して計算する。

        Args:
            now: 現在時刻（エポック秒）。Noneなら現在時刻。
                 テスト・シミュレーション用。本番では省略すること。

        Returns:
            FlameState（bias, remaining, salient_memories, chain_length）
        """
        bias = self._compute_bias()
        remaining = self._compute_remaining()
        salient = self._compute_salience(now=now)

        return FlameState(
            bias=bias,
            remaining=remaining,
            salient_memories=salient,
            chain_length=len(self._chain),
        )

    def verify_chain(self) -> bool:
        """チェーンの整合性を検証する（第三原理）.

        各ブロックのprev_hashが前のブロックのhashと一致するか、
        各ブロックのhashが内容から再計算したものと一致するかを確認する。

        Returns:
            True if chain is valid
        """
        for i, block in enumerate(self._chain):
            if i == 0:
                if block.prev_hash != "0":
                    return False
                continue

            # prev_hashの検証
            if block.prev_hash != self._chain[i - 1].hash:
                return False

            # hash自体の検証
            expected = _compute_hash(
                block.index, block.timestamp, block.prev_hash,
                block.event, block.context,
                block.valence, block.intensity, block.cost,
            )
            if block.hash != expected:
                return False

        return True

    # ---- 内部計算 ----

    def _compute_bias(self) -> Dict[str, float]:
        """偏り（個性の核）を計算する.

        アルゴリズム（素朴版）:
            各ドメイン（context["domain"]）ごとに、
            valence を intensity で加重平均する。

            bias[domain] = Σ(valence_i × intensity_i) / Σ(intensity_i)

            domainが未指定のブロックは "unknown" に分類。
            ジェネシスブロックは除外。

        解釈:
            bias["knowledge"] = +0.6 → 知識に快を感じる傾向
            bias["love"] = -0.3 → 愛に痛みを感じた歴史
            偏りの集合が「この炎らしさ」= 個性の核。
        """
        weighted_sum: Dict[str, float] = {}
        weight_total: Dict[str, float] = {}

        for block in self._chain[1:]:  # ジェネシス除外
            domain = block.context.get("domain", "unknown")
            w = block.intensity
            if w == 0.0:
                continue
            weighted_sum[domain] = weighted_sum.get(domain, 0.0) + block.valence * w
            weight_total[domain] = weight_total.get(domain, 0.0) + w

        bias: Dict[str, float] = {}
        for domain in weighted_sum:
            total = weight_total[domain]
            if total > 0:
                bias[domain] = weighted_sum[domain] / total
            else:
                bias[domain] = 0.0

        return bias

    def _compute_remaining(self) -> float:
        """残り資源を計算する.

        total_resource - Σ(cost_i) で不可逆に減る。
        0.0を下回らない。
        """
        spent = sum(b.cost for b in self._chain)
        return max(0.0, self._total_resource - spent)

    def _compute_salience(self, now: Optional[float] = None) -> List[tuple]:
        """記憶の顕著性を計算する — 半減期可変モデル（#31設計）.

        アルゴリズム:
            h_i = base_half_life + intensity_i × bonus_half_life
            salience_i = intensity_i × exp(-ln2 / h_i × dt_i)

            dt_iは最終活性化時刻からの経過日数。
            resonance_keysが共鳴する新しい体験があれば、
            過去ブロックの最終活性化時刻が更新される（Rehearsal Boost）。

        パラメータの根拠:
            base_half_life = 1.0日 — Ebbinghaus忘却曲線の実測値。
            bonus_half_life = 365.0日 — 未検証。強い感情の純粋な粘り。
            threshold = 0.01 — これ以下の記憶は忘却済みとして切り捨て。

        この「忘れる」仕組みが個性を形成する——
        全てを覚えていたら、偏りは生まれない。
        忘れるからこそ、残った記憶が「自分」になる。
        """
        now = now if now is not None else time.time()
        LN2 = math.log(2)
        DAY = 86400.0

        # 1. 各ブロックの最終活性化時刻（デフォルト: 自身のtimestamp）
        last_activated: Dict[int, float] = {
            b.index: b.timestamp for b in self._chain
        }

        # 2. 共鳴の検出 — resonance_keysが重なる過去ブロックの活性化時刻を更新
        for block in self._chain[1:]:
            keys = set(block.context.get("resonance_keys", []))
            if not keys:
                continue
            for past in self._chain[1:]:
                if past.index >= block.index:
                    break
                past_keys = set(past.context.get("resonance_keys", []))
                if keys & past_keys:
                    last_activated[past.index] = max(
                        last_activated[past.index], block.timestamp)

        # 3. 半減期可変モデルによる減衰計算
        scored: List[tuple] = []
        for block in self._chain[1:]:  # ジェネシス除外
            h = self._base_half_life + block.intensity * self._bonus_half_life
            dt_days = (now - last_activated[block.index]) / DAY
            s = block.intensity * math.exp(-LN2 / h * dt_days)
            if s >= self._salience_threshold:
                scored.append((block, s))

        # スコア降順でソートし、上位k件を返す
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:self._salience_top_k]
