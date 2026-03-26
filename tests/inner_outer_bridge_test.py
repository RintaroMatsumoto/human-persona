"""Tests for inner_outer_bridge: InnerOuterBridge class.

Comprehensive test suite covering:
- Modulation application and restoration
- Individual modulation parameters
- Edge cases and error handling
- State consistency

Test count: 17 test methods
"""

import unittest
from dataclasses import dataclass, field

from core.inner_outer_bridge import InnerOuterBridge
from core.timing_controller import TimingController, Platform, TimingProfile
from core.style_variator import StyleVariator, StyleType, StylePattern
from core.emotion_state_machine import EmotionStateMachine, EmotionState
from core.context_referencer import ContextReferencer


class TestInnerOuterBridge(unittest.TestCase):
    """Tests for InnerOuterBridge class."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.timing = TimingController()
        self.style = StyleVariator()
        self.emotion = EmotionStateMachine()
        self.context = ContextReferencer()
        
        self.bridge = InnerOuterBridge(
            self.timing,
            self.style,
            self.emotion,
            self.context,
        )
    
    # ---------------------------------------------------------------
    # Test 1: Basic initialization
    # ---------------------------------------------------------------
    def test_bridge_initialization(self) -> None:
        """Test that bridge initializes without modulation applied."""
        self.assertFalse(self.bridge.is_modulated())
        self.assertEqual(self.bridge.get_current_modulation(), {})
        self.assertIsNone(self.bridge._original_snapshot)
    
    # ---------------------------------------------------------------
    # Test 2: Apply modulation creates snapshot
    # ---------------------------------------------------------------
    def test_apply_modulation_saves_snapshot(self) -> None:
        """Test that apply_modulation saves original state."""
        original_uncertainty = self.style.uncertainty_rate
        original_exchange = self.emotion.exchange_count
        
        modulation = {"style_openness": 1.5}
        self.bridge.apply_modulation(modulation)
        
        self.assertTrue(self.bridge.is_modulated())
        self.assertIsNotNone(self.bridge._original_snapshot)
        self.assertEqual(
            self.bridge._original_snapshot.style_uncertainty_rate,
            original_uncertainty
        )
        self.assertEqual(
            self.bridge._original_snapshot.emotion_exchange_count,
            original_exchange
        )
    
    # ---------------------------------------------------------------
    # Test 3: Restore original values
    # ---------------------------------------------------------------
    def test_restore_original_values(self) -> None:
        """Test that restore_original_values reverts all changes."""
        original_uncertainty = self.style.uncertainty_rate
        original_max_history = self.context.max_history
        
        # Set exchange_count to non-zero first so we can see changes
        self.emotion.exchange_count = 5
        original_exchange = self.emotion.exchange_count
        
        modulation = {
            "style_openness": 1.5,
            "context_depth": 2.0,
            "emotion_amplitude": 1.3,
        }
        self.bridge.apply_modulation(modulation)
        
        # Verify modulation was applied
        self.assertNotEqual(self.style.uncertainty_rate, original_uncertainty)
        self.assertNotEqual(self.context.max_history, original_max_history)
        self.assertNotEqual(self.emotion.exchange_count, original_exchange)
        
        # Restore
        self.bridge.restore_original_values()
        
        self.assertFalse(self.bridge.is_modulated())
        self.assertAlmostEqual(self.style.uncertainty_rate, original_uncertainty)
        self.assertEqual(self.context.max_history, original_max_history)
        self.assertEqual(self.emotion.exchange_count, original_exchange)
    
    # ---------------------------------------------------------------
    # Test 4: style_openness modulation
    # ---------------------------------------------------------------
    def test_style_openness_modulation(self) -> None:
        """Test that style_openness modulates uncertainty_rate correctly."""
        original_rate = self.style.uncertainty_rate
        
        modulation = {"style_openness": 2.0}
        self.bridge.apply_modulation(modulation)
        
        expected = original_rate * 2.0
        self.assertAlmostEqual(self.style.uncertainty_rate, expected, places=5)
    
    # ---------------------------------------------------------------
    # Test 5: emotion_amplitude modulation
    # ---------------------------------------------------------------
    def test_emotion_amplitude_modulation(self) -> None:
        """Test that emotion_amplitude modulates exchange_count."""
        original_count = self.emotion.exchange_count
        
        modulation = {"emotion_amplitude": 1.5}
        self.bridge.apply_modulation(modulation)
        
        # emotion_amplitude accelerates emotional deepening
        expected = int(original_count * 1.5)
        self.assertEqual(self.emotion.exchange_count, expected)
    
    # ---------------------------------------------------------------
    # Test 6: timing_exploration modulation
    # ---------------------------------------------------------------
    def test_timing_exploration_modulation(self) -> None:
        """Test that timing_exploration expands the delay range."""
        original_min = self.timing.profiles[Platform.CHAT].min_seconds
        original_max = self.timing.profiles[Platform.CHAT].max_seconds
        original_range = original_max - original_min
        
        modulation = {"timing_exploration": 2.0}
        self.bridge.apply_modulation(modulation)
        
        new_min = self.timing.profiles[Platform.CHAT].min_seconds
        new_max = self.timing.profiles[Platform.CHAT].max_seconds
        new_range = new_max - new_min
        
        # Range should expand when exploration > 1.0
        # The exact range depends on midpoint clamping to min 0
        self.assertGreater(new_range, original_range)
    
    # ---------------------------------------------------------------
    # Test 7: context_depth modulation
    # ---------------------------------------------------------------
    def test_context_depth_modulation(self) -> None:
        """Test that context_depth adjusts max_history."""
        original_history = self.context.max_history
        
        modulation = {"context_depth": 1.5}
        self.bridge.apply_modulation(modulation)
        
        expected = int(original_history * 1.5)
        self.assertEqual(self.context.max_history, expected)
    
    # ---------------------------------------------------------------
    # Test 8: emotion_volatility modulation
    # ---------------------------------------------------------------
    def test_emotion_volatility_modulation(self) -> None:
        """Test that emotion_volatility modulation is accepted."""
        original_state = self.emotion.current_state
        
        modulation = {"emotion_volatility": 1.2}
        # Should not raise an error
        self.bridge.apply_modulation(modulation)
        
        # State may or may not change (design hook for future)
        # Just verify no exceptions occurred
        self.assertTrue(self.bridge.is_modulated())
    
    # ---------------------------------------------------------------
    # Test 9: Multiple modulations applied simultaneously
    # ---------------------------------------------------------------
    def test_multiple_modulations_applied(self) -> None:
        """Test applying multiple modulations at once."""
        original_uncertainty = self.style.uncertainty_rate
        original_max_history = self.context.max_history
        original_exchange = self.emotion.exchange_count
        
        modulation = {
            "style_openness": 1.3,
            "context_depth": 1.5,
            "emotion_amplitude": 1.2,
            "timing_exploration": 1.4,
            "emotion_volatility": 1.1,
        }
        self.bridge.apply_modulation(modulation)
        
        # All should be modified
        self.assertAlmostEqual(
            self.style.uncertainty_rate,
            original_uncertainty * 1.3,
            places=5
        )
        self.assertEqual(
            self.context.max_history,
            int(original_max_history * 1.5)
        )
        self.assertEqual(
            self.emotion.exchange_count,
            int(original_exchange * 1.2)
        )
    
    # ---------------------------------------------------------------
    # Test 10: Empty modulation dict
    # ---------------------------------------------------------------
    def test_empty_modulation(self) -> None:
        """Test that empty modulation dict doesn't change anything."""
        original_uncertainty = self.style.uncertainty_rate
        original_history = self.context.max_history
        original_exchange = self.emotion.exchange_count
        
        self.bridge.apply_modulation({})
        
        # Everything should remain the same
        self.assertAlmostEqual(self.style.uncertainty_rate, original_uncertainty)
        self.assertEqual(self.context.max_history, original_history)
        self.assertEqual(self.emotion.exchange_count, original_exchange)
    
    # ---------------------------------------------------------------
    # Test 11: Extreme modulation values
    # ---------------------------------------------------------------
    def test_extreme_modulation_values(self) -> None:
        """Test handling of very high and very low modulation values."""
        modulation = {
            "style_openness": 0.1,  # Very low
            "emotion_amplitude": 5.0,  # Very high
            "context_depth": 0.01,  # Extremely low
        }
        self.bridge.apply_modulation(modulation)
        
        # Should not raise errors and values should be positive
        self.assertGreater(self.style.uncertainty_rate, 0)
        self.assertGreaterEqual(self.emotion.exchange_count, 0)
        self.assertGreaterEqual(self.context.max_history, 1)
    
    # ---------------------------------------------------------------
    # Test 12: Restore without modulation raises error
    # ---------------------------------------------------------------
    def test_restore_without_modulation_raises(self) -> None:
        """Test that restore without prior modulation raises RuntimeError."""
        with self.assertRaises(RuntimeError):
            self.bridge.restore_original_values()
    
    # ---------------------------------------------------------------
    # Test 13: Get current modulation
    # ---------------------------------------------------------------
    def test_get_current_modulation(self) -> None:
        """Test that get_current_modulation returns applied values."""
        modulation = {
            "style_openness": 1.3,
            "context_depth": 1.5,
        }
        self.bridge.apply_modulation(modulation)
        
        current = self.bridge.get_current_modulation()
        self.assertEqual(current["style_openness"], 1.3)
        self.assertEqual(current["context_depth"], 1.5)
    
    # ---------------------------------------------------------------
    # Test 14: Reset to original clears state
    # ---------------------------------------------------------------
    def test_reset_to_original(self) -> None:
        """Test that reset_to_original clears all modulation state."""
        modulation = {"style_openness": 1.5}
        self.bridge.apply_modulation(modulation)
        
        self.assertTrue(self.bridge.is_modulated())
        
        self.bridge.reset_to_original()
        
        self.assertFalse(self.bridge.is_modulated())
        self.assertEqual(self.bridge.get_current_modulation(), {})
        self.assertIsNone(self.bridge._original_snapshot)
    
    # ---------------------------------------------------------------
    # Test 15: Sequential modulations override previous
    # ---------------------------------------------------------------
    def test_sequential_modulations(self) -> None:
        """Test that applying modulation twice overrides the first."""
        original_uncertainty = self.style.uncertainty_rate
        
        # First modulation
        self.bridge.apply_modulation({"style_openness": 2.0})
        first_result = self.style.uncertainty_rate
        self.assertAlmostEqual(first_result, original_uncertainty * 2.0, places=5)
        
        # Second modulation should restore to original then apply new
        # This is because we re-save the snapshot if already modulated
        self.bridge.apply_modulation({"style_openness": 1.5})
        second_result = self.style.uncertainty_rate
        # After second apply, should be relative to the original
        self.assertAlmostEqual(second_result, original_uncertainty * 1.5, places=5)
    
    # ---------------------------------------------------------------
    # Test 16: style_mimicry modulation
    # ---------------------------------------------------------------
    def test_style_mimicry_modulation(self) -> None:
        """Test that style_mimicry adjusts pattern weights."""
        # Set up a pattern with known weight
        if StyleType.CONFIRMATION in self.style.patterns:
            original_weight = self.style.patterns[StyleType.CONFIRMATION].weight
            
            modulation = {"style_mimicry": 2.0}
            self.bridge.apply_modulation(modulation)
            
            new_weight = self.style.patterns[StyleType.CONFIRMATION].weight
            self.assertAlmostEqual(new_weight, original_weight * 2.0, places=5)
    
    # ---------------------------------------------------------------
    # Test 17: emotion_curiosity modulation
    # ---------------------------------------------------------------
    def test_emotion_curiosity_modulation(self) -> None:
        """Test that emotion_curiosity increases UNCERTAIN style weight."""
        # Initialize UNCERTAIN pattern if not present
        if StyleType.UNCERTAIN not in self.style.patterns:
            self.style.patterns[StyleType.UNCERTAIN] = StylePattern(
                style_type=StyleType.UNCERTAIN,
                weight=1.0
            )
        
        original_weight = self.style.patterns[StyleType.UNCERTAIN].weight
        
        modulation = {"emotion_curiosity": 0.5}
        self.bridge.apply_modulation(modulation)
        
        # emotion_curiosity 0.5 → weight * (1.0 + 0.5) = weight * 1.5
        new_weight = self.style.patterns[StyleType.UNCERTAIN].weight
        self.assertAlmostEqual(new_weight, original_weight * 1.5, places=5)


if __name__ == "__main__":
    unittest.main()
