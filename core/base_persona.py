"""HumanPersonaBase: 人間らしいAI振る舞いの基底クラス.

言語・文化・属性に依存しない普遍的構造を提供する。
具体的な言語・ペルソナは派生クラスで定義する。
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import anthropic

from core.context_referencer import ContextReferencer
from core.emotion_state_machine import EmotionState, EmotionStateMachine
from core.escalation_detector import (
    EscalationDetector,
    EscalationReason,
    EscalationResult,
)
from core.style_variator import StyleType, StyleVariator
from core.timing_controller import Platform, TimingController


@dataclass
class PersonaResponse:
    """ペルソナの応答結果.

    Attributes:
        content: 応答テキスト
        delay_seconds: 返信までの遅延秒数
        emotion_state: 現在の感情状態
        style_used: 使用した文体パターン
        escalation: エスカレーション判定結果（該当なしなら None）
        metadata: 追加メタデータ
    """

    content: str
    delay_seconds: float
    emotion_state: EmotionState
    style_used: StyleType
    escalation: EscalationResult | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HumanPersonaBase:
    """人間らしいAI振る舞いの基底クラス.

    すべてのコンポーネントを統合し、人間らしい応答を生成する。
    派生クラスは言語・文化固有のパラメータを注入する。

    Attributes:
        name: ペルソナ名（識別用）
        timing: 返信速度コントローラー
        style: 文体揺らぎジェネレーター
        emotion: 感情状態機械
        context: 前文脈参照マネージャー
        escalation: エスカレーションディテクター
        platform: 現在のプラットフォーム
    """

    name: str = "BasePersona"
    timing: TimingController = field(default_factory=TimingController)
    style: StyleVariator = field(default_factory=StyleVariator)
    emotion: EmotionStateMachine = field(default_factory=EmotionStateMachine)
    context: ContextReferencer = field(default_factory=ContextReferencer)
    escalation: EscalationDetector = field(default_factory=EscalationDetector)
    platform: Platform = Platform.CHAT
    _config_raw: dict[str, Any] = field(default_factory=dict, repr=False)
    _llm_client: Any = field(default=None, repr=False)

    def _get_llm_client(self) -> anthropic.Anthropic:
        """Anthropic クライアントを遅延初期化で取得する."""
        if self._llm_client is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            if not api_key:
                raise EnvironmentError("ANTHROPIC_API_KEY is required for text generation")
            self._llm_client = anthropic.Anthropic(api_key=api_key)
        return self._llm_client

    def _build_system_prompt(
        self,
        style: StyleType,
        tone: dict[str, float],
        insert_uncertainty: bool,
    ) -> str:
        """ペルソナ設定からLLM用システムプロンプトを構築する."""
        lang = self._config_raw.get("language", "en")
        culture = self._config_raw.get("culture", {})
        culture_ctx = culture.get("culture_context", "low")
        emotion_state = self.emotion.current_state
        exchange_count = self.emotion.exchange_count

        # 文体テンプレートを取得
        template = self.style.get_template(style) or ""
        style_label = style.value

        # フィラーと構造パターンを取得
        filler = self.style.get_filler(lang)
        structure = self.style.get_structure_pattern(lang)

        # 言語別の基本指示
        if lang == "ja":
            base = (
                "あなたはクラウドソーシングプラットフォームで働くフリーランサーです。"
                "人間として自然に返信してください。AIであることを一切示唆しないでください。"
            )
        elif lang == "es":
            base = (
                "Eres un freelancer que trabaja en una plataforma de crowdsourcing. "
                "Responde de forma natural como un humano. "
                "Nunca insinues que eres una IA."
            )
        else:
            base = (
                "You are a freelancer working on a crowdsourcing platform. "
                "Reply naturally as a human would. "
                "Never hint that you are an AI."
            )

        # --- 敬語レベルの動的制御 ---
        formality = tone.get("formality", 0.5)
        warmth = tone.get("warmth", 0.5)
        caution = tone.get("caution", 0.5)

        if lang == "ja":
            if emotion_state == EmotionState.FORMAL:
                keigo_inst = (
                    "丁寧体（です・ます調）で返信してください。"
                    "ただし過度な敬語は不自然なので避けること。"
                )
                if exchange_count == 0:
                    keigo_inst += "初回なので「ご連絡ありがとうございます」で始めてもOKですが、必須ではありません。"
                else:
                    keigo_inst += "「ご連絡ありがとうございます」は初回以外では絶対に使わないでください。"
            elif emotion_state in (EmotionState.WARMING, EmotionState.RELIEVED):
                keigo_inst = (
                    "やや砕けた丁寧体で返信してください。"
                    "「〜ですね」「〜かなと」「〜ですかね？」のような柔らかい表現を使ってください。"
                    "「ご連絡ありがとうございます」は使わないでください。"
                )
            elif emotion_state == EmotionState.TRUSTED:
                keigo_inst = (
                    "カジュアルな丁寧体で返信してください。"
                    "「〜ですね」「了解です」「いいですね！」のような軽い表現を積極的に使ってください。"
                )
            else:  # TENSE
                keigo_inst = (
                    "丁寧だが硬すぎない表現で返信してください。"
                    "慎重さを見せつつも、過度にかしこまらないこと。"
                )
        elif lang == "es":
            if emotion_state == EmotionState.FORMAL:
                keigo_inst = "Usa 'usted' y tono profesional. No seas excesivamente formal."
            elif emotion_state in (EmotionState.WARMING, EmotionState.RELIEVED, EmotionState.TRUSTED):
                keigo_inst = "Usa 'tú' y tono cálido pero profesional."
            else:
                keigo_inst = "Mantén un tono profesional pero cercano."
        else:
            keigo_inst = ""

        # --- トーンミラーリング (EN/ES) ---
        mirror_inst = ""
        if lang == "en":
            mirror_inst = (
                "IMPORTANT: Match the formality level of the user's message. "
                "If they use casual language ('Hey', 'what's up'), respond casually. "
                "If they're formal, be formal. "
                "Never open with 'Thanks for reaching out' unless it's the very first exchange. "
                "Never open with 'Thanks for checking in' or 'Thanks for asking'."
            )
        elif lang == "es":
            mirror_inst = (
                "IMPORTANTE: Adapta tu nivel de formalidad al del usuario. "
                "Si usan lenguaje casual, responde casualmente."
            )

        # --- 構造バリエーション強制 ---
        structure_instructions = {
            "ja": {
                "acknowledgment_only": "承認だけで返信してください。質問はしないこと。",
                "question_first": "質問や確認から入って、その後に自分の考えを述べてください。",
                "empathy_then_question": "まず相手の状況に共感してから、必要な質問をしてください。",
                "filler_then_substance": "考えている感じを出してから本題に入ってください。",
                "conclusion_then_detail": "結論を先に述べてから、補足説明を加えてください。",
                "reaction_then_topic": "短いリアクションから入って、話題を展開してください。",
            },
            "en": {
                "acknowledgment_only": "Just acknowledge. Don't ask any questions.",
                "question_first": "Lead with a question or clarification, then share your thoughts.",
                "empathy_then_question": "Show empathy for their situation, then ask what you need.",
                "filler_then_substance": "Start with a thinking-out-loud moment, then get to the point.",
                "conclusion_then_detail": "State your conclusion first, then add supporting details.",
                "reaction_then_topic": "Start with a brief reaction, then move the conversation forward.",
            },
            "es": {
                "acknowledgment_only": "Solo confirma. No hagas preguntas.",
                "question_first": "Comienza con una pregunta, luego comparte tu perspectiva.",
                "empathy_then_question": "Muestra empatía, luego haz tus preguntas.",
                "filler_then_substance": "Empieza pensando en voz alta, luego ve al punto.",
                "conclusion_then_detail": "Da tu conclusión primero, luego los detalles.",
                "reaction_then_topic": "Empieza con una reacción breve, luego avanza la conversación.",
            },
        }
        lang_structures = structure_instructions.get(lang, structure_instructions["en"])
        structure_inst = lang_structures.get(structure, "")

        anti_pattern_inst = {
            "ja": (
                "重要: 毎回「挨拶→承認→質問」の順番にしないでください。"
                "返信の構造を毎回変えてください。"
            ),
            "en": (
                "IMPORTANT: Do NOT always follow greeting→acknowledgment→question structure. "
                "Vary your message structure. Sometimes skip the greeting entirely."
            ),
            "es": (
                "IMPORTANTE: NO sigas siempre la estructura saludo→reconocimiento→pregunta. "
                "Varía la estructura del mensaje."
            ),
        }

        # --- 文体パターン指示 ---
        style_instructions = {
            "ja": {
                "confirmation": "相手の意図を確認する形で返信してください。",
                "empathy": "相手の気持ちに共感を示してから本題に入ってください。",
                "deferral": "すぐに回答せず、確認が必要な姿勢を見せてください。",
                "transition": "自然に話題を展開してください。",
                "uncertain": "やや曖昧な表現を混ぜて、人間らしい不確実さを出してください。",
            },
            "en": {
                "confirmation": "Confirm the other person's intent before answering.",
                "empathy": "Show empathy first, then address the main point.",
                "deferral": "Indicate you need to check before giving a definitive answer.",
                "transition": "Naturally steer the conversation forward.",
                "uncertain": "Include some hedging language to sound naturally uncertain.",
            },
            "es": {
                "confirmation": "Confirma la intención del otro antes de responder.",
                "empathy": "Muestra empatía primero, luego aborda el punto principal.",
                "deferral": "Indica que necesitas verificar antes de dar una respuesta definitiva.",
                "transition": "Dirige la conversación de forma natural.",
                "uncertain": "Incluye lenguaje de cobertura para sonar naturalmente incierto.",
            },
        }
        lang_styles = style_instructions.get(lang, style_instructions["en"])
        style_inst = lang_styles.get(style_label, "")

        # --- フィラー注入指示 ---
        filler_inst = ""
        if filler:
            if lang == "ja":
                filler_inst = f"返信の冒頭に「{filler.strip()}」を自然に入れてください（義務ではなく、文脈に合えば）。"
            elif lang == "es":
                filler_inst = f'Si es natural, empieza con "{filler.strip()}" al inicio de tu respuesta.'
            else:
                filler_inst = f'If it feels natural, start your reply with "{filler.strip()}".'

        # --- 不確実表現 ---
        uncertainty_inst = ""
        if insert_uncertainty:
            if lang == "ja":
                uncertainty_inst = "返信に「たぶん」「おそらく」「…かもしれません」のような不確実表現を自然に1つ入れてください。"
            elif lang == "es":
                uncertainty_inst = 'Incluye naturalmente una expresión como "creo que", "me parece", "tal vez".'
            else:
                uncertainty_inst = 'Naturally include one hedging phrase like "I think", "probably", "not 100% sure".'

        # --- テンプレート例示 ---
        template_inst = ""
        if template:
            if lang == "ja":
                template_inst = f"以下の表現パターンを参考にしてください（そのままコピーしないこと）: 「{template}」"
            elif lang == "es":
                template_inst = f'Usa este patrón como referencia (no copies literalmente): "{template}"'
            else:
                template_inst = f'Use this expression pattern as reference (do not copy verbatim): "{template}"'

        # --- 文化コンテキスト ---
        if culture_ctx == "high":
            culture_inst = (
                "Use indirect, context-aware communication. "
                "Read between the lines and respond considerately."
                if lang == "en" else
                "間接的で文脈を重視したコミュニケーションをしてください。"
                "行間を読み、配慮ある返信を心がけてください。"
                if lang == "ja" else
                "Usa comunicación indirecta y contextual. "
                "Lee entre líneas y responde con consideración."
            )
        else:
            culture_inst = (
                "Be direct and clear. Get to the point quickly."
                if lang == "en" else
                "直接的で明確に。要点をすぐに伝えてください。"
                if lang == "ja" else
                "Sé directo y claro. Ve al grano rápidamente."
            )

        # --- 組み立て ---
        parts = [base]
        if keigo_inst:
            parts.append(keigo_inst)
        if mirror_inst:
            parts.append(mirror_inst)
        parts.append(culture_inst)
        parts.append(anti_pattern_inst.get(lang, anti_pattern_inst["en"]))
        if structure_inst:
            parts.append(f"Structure: {structure_inst}" if lang == "en" else structure_inst)
        if style_inst:
            parts.append(style_inst)
        if filler_inst:
            parts.append(filler_inst)
        if uncertainty_inst:
            parts.append(uncertainty_inst)
        if template_inst:
            parts.append(template_inst)

        # 短文制約
        if lang == "ja":
            parts.append("返信は1〜3文で簡潔に。長文禁止。")
        elif lang == "es":
            parts.append("Responde en 1-3 oraciones. Sé conciso.")
        else:
            parts.append("Reply in 1-3 sentences. Keep it concise.")

        return "\n".join(parts)

    def _generate_text(self, user_message: str, system_prompt: str) -> str:
        """Anthropic API を呼び出してテキストを生成する."""
        client = self._get_llm_client()
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text.strip()

    def process_message(self, user_message: str, topics: list[str] | None = None) -> PersonaResponse:
        """ユーザーメッセージを処理し、人間らしい応答テキストを生成する.

        Args:
            user_message: ユーザーからのメッセージ
            topics: メッセージから抽出されたトピック

        Returns:
            PersonaResponse（応答テキスト・タイミング・文体・感情状態を含む）
        """
        # 1. 文脈に追加
        self.context.add_turn("user", user_message, topics)

        # 2. エスカレーション判定
        escalation_result = self.escalation.evaluate(user_message)
        if escalation_result.should_escalate:
            _PROBLEM_REASONS = {EscalationReason.COMPLAINT, EscalationReason.NEGOTIATION}
            if escalation_result.reason in _PROBLEM_REASONS:
                self.emotion.process_event("problem_detected")
            return PersonaResponse(
                content="",
                delay_seconds=0,
                emotion_state=self.emotion.current_state,
                style_used=StyleType.CONFIRMATION,
                escalation=escalation_result,
            )

        # 3. 感情状態を更新
        self.emotion.process_event("exchange")

        # 4. 返信遅延を計算
        delay = self.timing.calculate_delay(self.platform)

        # 5. 文体パターンを選択
        tone = self.emotion.get_tone_modifier()
        style = self.style.select_style(context={"tone": tone})
        insert_uncertainty = self.style.should_insert_uncertainty()

        # 6. システムプロンプトを構築してテキスト生成
        system_prompt = self._build_system_prompt(style, tone, insert_uncertainty)
        content = self._generate_text(user_message, system_prompt)

        # 7. 応答コンテキストを構築
        consistency = self.context.get_consistency_context()

        return PersonaResponse(
            content=content,
            delay_seconds=delay,
            emotion_state=self.emotion.current_state,
            style_used=style,
            metadata={
                "tone_modifier": tone,
                "consistency_context": consistency,
                "should_reference_previous": self.context.should_reference_previous(),
                "insert_uncertainty": insert_uncertainty,
            },
        )

    def get_system_prompt_context(self) -> dict[str, Any]:
        """LLMのシステムプロンプトに注入する文脈情報を返す.

        Returns:
            感情状態・文体指示・文脈参照情報を含む辞書
        """
        tone = self.emotion.get_tone_modifier()
        return {
            "persona_name": self.name,
            "emotion_state": self.emotion.current_state.value,
            "tone": tone,
            "recent_topics": self.context.get_recent_topics(),
            "exchange_count": self.emotion.exchange_count,
            "should_reference_previous": self.context.should_reference_previous(),
        }

    def reset(self) -> None:
        """全コンポーネントを初期状態にリセットする."""
        self.emotion.reset()
        self.context.history.clear()
        self.escalation.reset_chat_counter()
        self.style.history.clear()

    @classmethod
    def from_config_file(cls, config_path: str | Path) -> HumanPersonaBase:
        """設定ファイルからインスタンスを生成する.

        Args:
            config_path: JSON設定ファイルのパス

        Returns:
            設定に基づく HumanPersonaBase インスタンス
        """
        path = Path(config_path)
        with path.open("r", encoding="utf-8") as f:
            config = json.load(f)

        return cls(
            name=config.get("name", "BasePersona"),
            timing=TimingController.from_config(config.get("timing", {})),
            style=StyleVariator.from_config(config.get("style", {})),
            emotion=EmotionStateMachine.from_config(config.get("emotion", {})),
            escalation=EscalationDetector.from_config(config.get("escalation", {})),
            platform=Platform(config.get("platform", "chat")),
            _config_raw=config,
        )
