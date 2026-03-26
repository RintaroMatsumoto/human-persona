"""プラットフォーム別タイミングテストスイート.

TimingController の遅延計算・活動時間判定・キューイングロジックを
プラットフォームごとに検証する。

統計的検証:
    - 遅延値が指定範囲内に収まること
    - 正規分布ベースの遅延が中央寄りの分布を示すこと
    - プラットフォーム間の遅延差が設計通りであること
"""

from __future__ import annotations

import json
import statistics
import unittest
from datetime import time
from pathlib import Path

from core.timing_controller import (
    DEFAULT_PROFILES,
    Platform,
    TimingController,
    TimingProfile,
)


# ──────────────────────────────────────────────
# 1. TimingProfile の検証
# ──────────────────────────────────────────────

class TestTimingProfile(unittest.TestCase):
    """TimingProfile データクラスの制約を検証する."""

    def test_valid_profile(self) -> None:
        """正常な値で生成できること."""
        p = TimingProfile(min_seconds=30, max_seconds=180)
        self.assertEqual(p.min_seconds, 30)
        self.assertEqual(p.max_seconds, 180)

    def test_negative_values_raise(self) -> None:
        """負の値で ValueError が発生すること."""
        with self.assertRaises(ValueError):
            TimingProfile(min_seconds=-1, max_seconds=100)
        with self.assertRaises(ValueError):
            TimingProfile(min_seconds=10, max_seconds=-5)

    def test_min_greater_than_max_raises(self) -> None:
        """min > max で ValueError が発生すること."""
        with self.assertRaises(ValueError):
            TimingProfile(min_seconds=200, max_seconds=100)

    def test_equal_min_max(self) -> None:
        """min == max が許容されること（固定遅延）."""
        p = TimingProfile(min_seconds=60, max_seconds=60)
        self.assertEqual(p.min_seconds, p.max_seconds)

    def test_frozen(self) -> None:
        """frozen dataclass であり変更不可であること."""
        p = TimingProfile(min_seconds=30, max_seconds=180)
        with self.assertRaises(AttributeError):
            p.min_seconds = 50  # type: ignore[misc]


# ──────────────────────────────────────────────
# 2. デフォルトプロファイルの検証
# ──────────────────────────────────────────────

class TestDefaultProfiles(unittest.TestCase):
    """DEFAULT_PROFILES の設計意図を検証する."""

    def test_all_platforms_have_defaults(self) -> None:
        """全 Platform に対してデフォルト設定が存在すること."""
        for platform in Platform:
            self.assertIn(platform, DEFAULT_PROFILES)

    def test_chat_is_fastest(self) -> None:
        """CHAT が最も短い遅延設定であること."""
        chat = DEFAULT_PROFILES[Platform.CHAT]
        for platform in Platform:
            if platform != Platform.CHAT:
                other = DEFAULT_PROFILES[platform]
                self.assertLess(chat.min_seconds, other.min_seconds)
                self.assertLess(chat.max_seconds, other.max_seconds)

    def test_email_is_slowest(self) -> None:
        """EMAIL が最も長い遅延設定であること."""
        email = DEFAULT_PROFILES[Platform.EMAIL]
        for platform in Platform:
            if platform != Platform.EMAIL:
                other = DEFAULT_PROFILES[platform]
                self.assertGreater(email.min_seconds, other.min_seconds)

    def test_crowdsourcing_is_middle(self) -> None:
        """CROWDSOURCING が CHAT と EMAIL の中間であること."""
        chat = DEFAULT_PROFILES[Platform.CHAT]
        crowd = DEFAULT_PROFILES[Platform.CROWDSOURCING]
        email = DEFAULT_PROFILES[Platform.EMAIL]
        self.assertGreater(crowd.min_seconds, chat.min_seconds)
        self.assertLess(crowd.min_seconds, email.min_seconds)


# ──────────────────────────────────────────────
# 3. TimingController.calculate_delay() の検証
# ──────────────────────────────────────────────

class TestCalculateDelay(unittest.TestCase):
    """遅延計算ロジックの統計的検証."""

    def setUp(self) -> None:
        self.controller = TimingController()
        self.n_samples = 500

    def test_delay_within_bounds_chat(self) -> None:
        """CHAT の遅延が常に [min, max] 範囲内であること."""
        profile = DEFAULT_PROFILES[Platform.CHAT]
        for _ in range(self.n_samples):
            delay = self.controller.calculate_delay(Platform.CHAT)
            self.assertGreaterEqual(delay, profile.min_seconds)
            self.assertLessEqual(delay, profile.max_seconds)

    def test_delay_within_bounds_crowdsourcing(self) -> None:
        """CROWDSOURCING の遅延が常に [min, max] 範囲内であること."""
        profile = DEFAULT_PROFILES[Platform.CROWDSOURCING]
        for _ in range(self.n_samples):
            delay = self.controller.calculate_delay(Platform.CROWDSOURCING)
            self.assertGreaterEqual(delay, profile.min_seconds)
            self.assertLessEqual(delay, profile.max_seconds)

    def test_delay_within_bounds_email(self) -> None:
        """EMAIL の遅延が常に [min, max] 範囲内であること."""
        profile = DEFAULT_PROFILES[Platform.EMAIL]
        for _ in range(self.n_samples):
            delay = self.controller.calculate_delay(Platform.EMAIL)
            self.assertGreaterEqual(delay, profile.min_seconds)
            self.assertLessEqual(delay, profile.max_seconds)

    def test_delay_distribution_is_central(self) -> None:
        """遅延値が中央値付近に集中すること（正規分布の特性）."""
        profile = DEFAULT_PROFILES[Platform.CHAT]
        delays = [self.controller.calculate_delay(Platform.CHAT)
                  for _ in range(self.n_samples)]
        midpoint = (profile.min_seconds + profile.max_seconds) / 2
        mean_delay = statistics.mean(delays)
        # 平均が中央値の ±15% 以内であること
        tolerance = (profile.max_seconds - profile.min_seconds) * 0.15
        self.assertAlmostEqual(mean_delay, midpoint, delta=tolerance)

    def test_delay_has_variance(self) -> None:
        """遅延に十分なばらつきがあること（機械的でないこと）."""
        delays = [self.controller.calculate_delay(Platform.CHAT)
                  for _ in range(self.n_samples)]
        stdev = statistics.stdev(delays)
        # 標準偏差が 5秒以上あること
        self.assertGreater(stdev, 5.0)

    def test_platform_order_preserved_statistically(self) -> None:
        """統計的に CHAT < CROWDSOURCING < EMAIL の順序が保たれること."""
        chat_mean = statistics.mean(
            [self.controller.calculate_delay(Platform.CHAT)
             for _ in range(self.n_samples)]
        )
        crowd_mean = statistics.mean(
            [self.controller.calculate_delay(Platform.CROWDSOURCING)
             for _ in range(self.n_samples)]
        )
        email_mean = statistics.mean(
            [self.controller.calculate_delay(Platform.EMAIL)
             for _ in range(self.n_samples)]
        )
        self.assertLess(chat_mean, crowd_mean)
        self.assertLess(crowd_mean, email_mean)


# ──────────────────────────────────────────────
# 4. 活動時間・キューイングの検証
# ──────────────────────────────────────────────

class TestActiveHoursAndQueue(unittest.TestCase):
    """活動時間判定とキューイングロジックを検証する."""

    def setUp(self) -> None:
        self.controller = TimingController(
            active_start=time(8, 0),
            active_end=time(22, 0),
            night_queue=True,
        )

    def test_within_active_hours(self) -> None:
        """活動時間内の時刻が is_active_hours=True であること."""
        active_times = [time(8, 0), time(12, 0), time(18, 30), time(22, 0)]
        for t in active_times:
            self.assertTrue(self.controller.is_active_hours(t),
                            f"{t} should be active")

    def test_outside_active_hours(self) -> None:
        """活動時間外の時刻が is_active_hours=False であること."""
        inactive_times = [time(7, 59), time(22, 1), time(3, 0), time(0, 0)]
        for t in inactive_times:
            self.assertFalse(self.controller.is_active_hours(t),
                             f"{t} should be inactive")

    def test_should_queue_at_night(self) -> None:
        """夜間キューイング有効時、活動時間外でキュー判定されること."""
        self.assertTrue(self.controller.should_queue(time(3, 0)))
        self.assertTrue(self.controller.should_queue(time(7, 30)))

    def test_should_not_queue_during_active(self) -> None:
        """活動時間内ではキューイングされないこと."""
        self.assertFalse(self.controller.should_queue(time(12, 0)))
        self.assertFalse(self.controller.should_queue(time(20, 0)))

    def test_queue_disabled(self) -> None:
        """night_queue=False ならキューイングされないこと."""
        controller = TimingController(
            active_start=time(8, 0),
            active_end=time(22, 0),
            night_queue=False,
        )
        self.assertFalse(controller.should_queue(time(3, 0)))

    def test_boundary_start(self) -> None:
        """active_start ちょうどがアクティブであること."""
        self.assertTrue(self.controller.is_active_hours(time(8, 0)))

    def test_boundary_end(self) -> None:
        """active_end ちょうどがアクティブであること."""
        self.assertTrue(self.controller.is_active_hours(time(22, 0)))


# ──────────────────────────────────────────────
# 5. 設定ファイルからの構築テスト
# ──────────────────────────────────────────────

class TestTimingFromConfig(unittest.TestCase):
    """設定ファイルからの TimingController 構築を検証する."""

    def test_from_ja_config(self) -> None:
        """日本語設定から正しくタイミングが構築されること."""
        config_path = Path(__file__).parent.parent / "config" / "ja.json"
        with open(config_path) as f:
            config = json.load(f)
        tc = TimingController.from_config(config["timing"])

        # CHAT: 30-180秒
        chat_profile = tc.profiles[Platform.CHAT]
        self.assertEqual(chat_profile.min_seconds, 30)
        self.assertEqual(chat_profile.max_seconds, 180)

        # CROWDSOURCING: 300-900秒
        crowd_profile = tc.profiles[Platform.CROWDSOURCING]
        self.assertEqual(crowd_profile.min_seconds, 300)
        self.assertEqual(crowd_profile.max_seconds, 900)

        # EMAIL: 1h-24h → 3600-86400秒
        email_profile = tc.profiles[Platform.EMAIL]
        self.assertEqual(email_profile.min_seconds, 3600)
        self.assertEqual(email_profile.max_seconds, 86400)

        # 活動時間: 08:00-23:00
        self.assertEqual(tc.active_start, time(8, 0))
        self.assertEqual(tc.active_end, time(23, 0))
        self.assertTrue(tc.night_queue)

    def test_from_en_config(self) -> None:
        """英語設定から正しくタイミングが構築されること."""
        config_path = Path(__file__).parent.parent / "config" / "en.json"
        with open(config_path) as f:
            config = json.load(f)
        tc = TimingController.from_config(config["timing"])

        # CHAT: 15-90秒（英語はチャットが速い）
        chat_profile = tc.profiles[Platform.CHAT]
        self.assertEqual(chat_profile.min_seconds, 15)
        self.assertEqual(chat_profile.max_seconds, 90)

        # 活動時間: 07:00-23:00
        self.assertEqual(tc.active_start, time(7, 0))
        self.assertEqual(tc.active_end, time(23, 0))

    def test_en_chat_faster_than_ja(self) -> None:
        """英語 CHAT の遅延が日本語 CHAT より短いこと（文化差の設計確認）."""
        ja_path = Path(__file__).parent.parent / "config" / "ja.json"
        en_path = Path(__file__).parent.parent / "config" / "en.json"
        with open(ja_path) as f:
            ja_config = json.load(f)
        with open(en_path) as f:
            en_config = json.load(f)

        ja_tc = TimingController.from_config(ja_config["timing"])
        en_tc = TimingController.from_config(en_config["timing"])

        self.assertLess(
            en_tc.profiles[Platform.CHAT].min_seconds,
            ja_tc.profiles[Platform.CHAT].min_seconds,
        )
        self.assertLess(
            en_tc.profiles[Platform.CHAT].max_seconds,
            ja_tc.profiles[Platform.CHAT].max_seconds,
        )

    def test_delay_respects_config_bounds(self) -> None:
        """設定ファイルから構築した場合も遅延がconfig範囲内であること."""
        config_path = Path(__file__).parent.parent / "config" / "ja.json"
        with open(config_path) as f:
            config = json.load(f)
        tc = TimingController.from_config(config["timing"])

        for platform in Platform:
            profile = tc.profiles[platform]
            for _ in range(200):
                delay = tc.calculate_delay(platform)
                self.assertGreaterEqual(delay, profile.min_seconds)
                self.assertLessEqual(delay, profile.max_seconds)


# ──────────────────────────────────────────────
# 6. カスタムプロファイルの検証
# ──────────────────────────────────────────────

class TestCustomProfiles(unittest.TestCase):
    """カスタムプロファイルでの動作を検証する."""

    def test_custom_tight_range(self) -> None:
        """狭いレンジのカスタム設定でも正しく動作すること."""
        custom = {
            Platform.CHAT: TimingProfile(min_seconds=10, max_seconds=15),
        }
        controller = TimingController(profiles=custom)
        for _ in range(100):
            delay = controller.calculate_delay(Platform.CHAT)
            self.assertGreaterEqual(delay, 10)
            self.assertLessEqual(delay, 15)

    def test_custom_wide_range(self) -> None:
        """広いレンジのカスタム設定でも正しく動作すること."""
        custom = {
            Platform.EMAIL: TimingProfile(min_seconds=60, max_seconds=172800),
        }
        controller = TimingController(profiles=custom)
        delays = [controller.calculate_delay(Platform.EMAIL) for _ in range(100)]
        self.assertTrue(all(60 <= d <= 172800 for d in delays))

    def test_unknown_platform_falls_back_to_chat(self) -> None:
        """未設定プラットフォームで CHAT デフォルトにフォールバックすること.

        profiles に EMAIL だけ設定した場合、CHAT にフォールバック。
        """
        custom = {
            Platform.EMAIL: TimingProfile(min_seconds=3600, max_seconds=7200),
        }
        controller = TimingController(profiles=custom)
        # CROWDSOURCING は未設定 → DEFAULT_PROFILES[CHAT] にフォールバック
        delay = controller.calculate_delay(Platform.CROWDSOURCING)
        chat_default = DEFAULT_PROFILES[Platform.CHAT]
        self.assertGreaterEqual(delay, chat_default.min_seconds)
        self.assertLessEqual(delay, chat_default.max_seconds)


if __name__ == "__main__":
    unittest.main()
