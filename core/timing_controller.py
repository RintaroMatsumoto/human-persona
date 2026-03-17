"""返信速度制御モジュール.

人間の自然な返信速度をプラットフォーム・文脈ごとにシミュレートする。
即座の返信はAIらしさを示唆するため、適切な遅延を挿入する。
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import time
from enum import Enum
from typing import Any


class Platform(Enum):
    """対応プラットフォーム種別."""

    CHAT = "chat"
    CROWDSOURCING = "crowdsourcing_message"
    EMAIL = "email"


@dataclass(frozen=True)
class TimingProfile:
    """プラットフォーム別タイミング設定.

    Attributes:
        min_seconds: 最小返信待機時間（秒）
        max_seconds: 最大返信待機時間（秒）
    """

    min_seconds: float
    max_seconds: float

    def __post_init__(self) -> None:
        if self.min_seconds < 0 or self.max_seconds < 0:
            raise ValueError("Timing values must be non-negative")
        if self.min_seconds > self.max_seconds:
            raise ValueError("min_seconds must be <= max_seconds")


# デフォルトのプラットフォーム別タイミング
DEFAULT_PROFILES: dict[Platform, TimingProfile] = {
    Platform.CHAT: TimingProfile(min_seconds=30, max_seconds=180),
    Platform.CROWDSOURCING: TimingProfile(min_seconds=300, max_seconds=900),
    Platform.EMAIL: TimingProfile(min_seconds=3600, max_seconds=28800),
}


@dataclass
class TimingController:
    """返信速度を制御するコントローラー.

    人間らしい返信タイミングを計算する。活動時間外のメッセージは
    キューに入れ、翌活動時間に返信する。

    Attributes:
        profiles: プラットフォーム別タイミング設定
        active_start: 活動開始時刻
        active_end: 活動終了時刻
        night_queue: 夜間キューイングを有効にするか
    """

    profiles: dict[Platform, TimingProfile] = field(
        default_factory=lambda: dict(DEFAULT_PROFILES)
    )
    active_start: time = field(default_factory=lambda: time(8, 0))
    active_end: time = field(default_factory=lambda: time(22, 0))
    night_queue: bool = True

    def calculate_delay(self, platform: Platform) -> float:
        """指定プラットフォームに対する返信遅延時間（秒）を計算する.

        Args:
            platform: 対象プラットフォーム

        Returns:
            遅延秒数。正規分布ベースで自然なばらつきを持つ。
        """
        profile = self.profiles.get(platform, DEFAULT_PROFILES[Platform.CHAT])
        midpoint = (profile.min_seconds + profile.max_seconds) / 2
        spread = (profile.max_seconds - profile.min_seconds) / 4
        delay = random.gauss(midpoint, spread)
        return max(profile.min_seconds, min(delay, profile.max_seconds))

    def is_active_hours(self, current: time) -> bool:
        """現在時刻が活動時間内かどうかを判定する.

        Args:
            current: 判定対象の時刻

        Returns:
            活動時間内なら True
        """
        return self.active_start <= current <= self.active_end

    def should_queue(self, current: time) -> bool:
        """メッセージをキューに入れるべきかを判定する.

        Args:
            current: 現在時刻

        Returns:
            夜間キューイング有効かつ活動時間外なら True
        """
        return self.night_queue and not self.is_active_hours(current)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> TimingController:
        """設定辞書からインスタンスを生成する.

        Args:
            config: platform_timing 形式の設定辞書

        Returns:
            設定に基づく TimingController インスタンス
        """
        profiles: dict[Platform, TimingProfile] = {}
        platform_timing = config.get("platform_timing", {})

        for platform in Platform:
            if platform.value in platform_timing:
                pt = platform_timing[platform.value]
                if platform == Platform.EMAIL:
                    profiles[platform] = TimingProfile(
                        min_seconds=pt.get("min_hour", 1) * 3600,
                        max_seconds=pt.get("max_hour", 8) * 3600,
                    )
                else:
                    profiles[platform] = TimingProfile(
                        min_seconds=pt.get("min_sec", 30),
                        max_seconds=pt.get("max_sec", 180),
                    )

        active_hours = platform_timing.get("active_hours", "08:00-22:00")
        start_str, end_str = active_hours.split("-")
        active_start = time.fromisoformat(start_str)
        active_end = time.fromisoformat(end_str)

        return cls(
            profiles=profiles if profiles else dict(DEFAULT_PROFILES),
            active_start=active_start,
            active_end=active_end,
            night_queue=platform_timing.get("night_queue", True),
        )
