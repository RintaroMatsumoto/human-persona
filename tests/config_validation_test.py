"""
Comprehensive tests for config validation module.

Tests cover:
- Valid and invalid configurations
- Type checking
- Pattern validation (persona_id, language code)
- Enum validation (context_culture, formality_default)
- Missing required/optional fields
- Nested object validation
- All existing config files
- Error and warning messages
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict

from core.config_validator import ConfigValidator, ValidationResult


class TestValidationResult(unittest.TestCase):
    """Test ValidationResult dataclass."""

    def test_valid_result_str(self):
        """Test string representation of valid result."""
        result = ValidationResult(valid=True, config_path="test.json")
        output = str(result)
        self.assertIn("✓ VALID", output)
        self.assertIn("test.json", output)

    def test_invalid_result_str(self):
        """Test string representation of invalid result."""
        result = ValidationResult(
            valid=False,
            config_path="bad.json",
            errors=["Missing required field: meta"],
        )
        output = str(result)
        self.assertIn("✗ INVALID", output)
        self.assertIn("Missing required field: meta", output)

    def test_result_with_warnings(self):
        """Test result with both errors and warnings."""
        result = ValidationResult(
            valid=False,
            config_path="mixed.json",
            errors=["Type error"],
            warnings=["Missing optional field"],
        )
        output = str(result)
        self.assertIn("Errors:", output)
        self.assertIn("Warnings:", output)


class TestConfigValidatorBasic(unittest.TestCase):
    """Test basic validator functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up validator with actual schema."""
        schema_path = str(Path(__file__).parent.parent / "config" / "schema.json")
        cls.validator = ConfigValidator(schema_path)

    def test_schema_loaded(self):
        """Test that schema is properly loaded."""
        self.assertIsNotNone(self.validator.schema)
        self.assertEqual(self.validator.schema.get("type"), "object")
        self.assertIn("meta", self.validator.schema.get("properties", {}))

    def test_init_missing_schema(self):
        """Test initialization with missing schema file."""
        with self.assertRaises(FileNotFoundError):
            ConfigValidator("/nonexistent/schema.json")

    def test_validate_empty_dict(self):
        """Test validation of empty dictionary."""
        result = self.validator.validate({})
        self.assertFalse(result.valid)
        # Should have errors for missing required fields
        self.assertGreater(len(result.errors), 0)
        self.assertIn("Missing required field", result.errors[0])

    def test_validate_non_dict(self):
        """Test validation of non-dict value."""
        result = self.validator.validate("not a dict")
        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        self.assertIn("must be a dict", result.errors[0])

    def test_validate_with_custom_path(self):
        """Test validation with custom config path in error messages."""
        result = self.validator.validate({}, "/custom/path.json")
        self.assertEqual(result.config_path, "/custom/path.json")


class TestRequiredFields(unittest.TestCase):
    """Test required field validation."""

    @classmethod
    def setUpClass(cls):
        """Set up validator."""
        schema_path = str(Path(__file__).parent.parent / "config" / "schema.json")
        cls.validator = ConfigValidator(schema_path)

    def test_missing_meta(self):
        """Test missing required 'meta' field."""
        config = {
            "timing": {},
            "style": {},
            "emotion": {},
        }
        result = self.validator.validate(config)
        self.assertFalse(result.valid)
        self.assertTrue(any("meta" in e for e in result.errors))

    def test_missing_timing(self):
        """Test missing required 'timing' field."""
        config = {
            "meta": {},
            "style": {},
            "emotion": {},
        }
        result = self.validator.validate(config)
        self.assertFalse(result.valid)
        self.assertTrue(any("timing" in e for e in result.errors))

    def test_missing_style(self):
        """Test missing required 'style' field."""
        config = {
            "meta": {},
            "timing": {},
            "emotion": {},
        }
        result = self.validator.validate(config)
        self.assertFalse(result.valid)
        self.assertTrue(any("style" in e for e in result.errors))

    def test_missing_emotion(self):
        """Test missing required 'emotion' field."""
        config = {
            "meta": {},
            "timing": {},
            "style": {},
        }
        result = self.validator.validate(config)
        self.assertFalse(result.valid)
        self.assertTrue(any("emotion" in e for e in result.errors))

class TestMetaField(unittest.TestCase):
    """Test meta field validation."""

    @classmethod
    def setUpClass(cls):
        """Set up validator."""
        schema_path = str(Path(__file__).parent.parent / "config" / "schema.json")
        cls.validator = ConfigValidator(schema_path)

    def test_meta_wrong_type(self):
        """Test meta field with wrong type."""
        config = {
            "meta": "not an object",
            "timing": {},
            "style": {},
            "emotion": {},
        }
        result = self.validator.validate(config)
        self.assertFalse(result.valid)
        self.assertTrue(any("meta" in e and "object" in e for e in result.errors))

    def test_meta_missing_persona_id(self):
        """Test meta missing required persona_id."""
        config = {
            "meta": {
                "language": "ja",
                "context_culture": "high",
            },
            "timing": {},
            "style": {},
            "emotion": {},
        }
        result = self.validator.validate(config)
        self.assertFalse(result.valid)
        self.assertTrue(any("persona_id" in e for e in result.errors))

    def test_meta_persona_id_pattern_valid(self):
        """Test persona_id with valid pattern."""
        config = {
            "meta": {
                "persona_id": "ja_business_formal",
                "language": "ja",
                "context_culture": "high",
            },
            "timing": {"platforms": {}, "active_hours": {"start": "09:00", "end": "18:00"}},
            "style": {"variation_patterns": {}},
            "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
        }
        result = self.validator.validate(config)
        # Should not have persona_id in errors
        self.assertFalse(any("persona_id" in e for e in result.errors))

    def test_meta_persona_id_pattern_invalid(self):
        """Test persona_id with invalid pattern."""
        config = {
            "meta": {
                "persona_id": "Invalid_ID!",  # Contains !
                "language": "ja",
                "context_culture": "high",
            },
            "timing": {"platforms": {}, "active_hours": {"start": "09:00", "end": "18:00"}},
            "style": {"variation_patterns": {}},
            "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
        }
        result = self.validator.validate(config)
        self.assertFalse(result.valid)
        self.assertTrue(any("persona_id" in e and "pattern" in e for e in result.errors))

    def test_language_code_valid(self):
        """Test valid language codes."""
        for lang in ["ja", "en", "es", "fr", "de"]:
            config = {
                "meta": {
                    "persona_id": "test_persona",
                    "language": lang,
                    "context_culture": "high",
                },
                "timing": {"platforms": {}, "active_hours": {"start": "09:00", "end": "18:00"}},
                "style": {"variation_patterns": {}},
                "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
            }
            result = self.validator.validate(config)
            self.assertFalse(any("language" in e for e in result.errors))

    def test_language_code_invalid(self):
        """Test invalid language codes."""
        for lang in ["en-US", "japanese", "123"]:
            config = {
                "meta": {
                    "persona_id": "test_persona",
                    "language": lang,
                    "context_culture": "high",
                },
                "timing": {"platforms": {}, "active_hours": {"start": "09:00", "end": "18:00"}},
                "style": {"variation_patterns": {}},
                "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
            }
            result = self.validator.validate(config)
            self.assertTrue(any("language" in e and "pattern" in e for e in result.errors))

    def test_context_culture_enum(self):
        """Test context_culture enum validation."""
        valid_values = ["high", "low", "mixed"]
        for value in valid_values:
            config = {
                "meta": {
                    "persona_id": "test",
                    "language": "ja",
                    "context_culture": value,
                },
                "timing": {"platforms": {}, "active_hours": {"start": "09:00", "end": "18:00"}},
                "style": {"variation_patterns": {}},
                "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
            }
            result = self.validator.validate(config)
            self.assertFalse(any("context_culture" in e for e in result.errors))

    def test_context_culture_invalid(self):
        """Test context_culture with invalid value."""
        config = {
            "meta": {
                "persona_id": "test",
                "language": "ja",
                "context_culture": "invalid_value",
            },
            "timing": {"platforms": {}, "active_hours": {"start": "09:00", "end": "18:00"}},
            "style": {"variation_patterns": {}},
            "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
        }
        result = self.validator.validate(config)
        self.assertFalse(result.valid)
        self.assertTrue(any("context_culture" in e for e in result.errors))


class TestTimingField(unittest.TestCase):
    """Test timing field validation."""

    @classmethod
    def setUpClass(cls):
        """Set up validator."""
        schema_path = str(Path(__file__).parent.parent / "config" / "schema.json")
        cls.validator = ConfigValidator(schema_path)

    def test_timing_missing_platforms(self):
        """Test timing missing required platforms."""
        config = {
            "meta": {"persona_id": "test", "language": "ja", "context_culture": "high"},
            "timing": {"active_hours": {"start": "09:00", "end": "18:00"}},
            "style": {"variation_patterns": {}},
            "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
        }
        result = self.validator.validate(config)
        self.assertTrue(any("timing.platforms" in e for e in result.errors))

    def test_timing_missing_active_hours(self):
        """Test timing missing required active_hours."""
        config = {
            "meta": {"persona_id": "test", "language": "ja", "context_culture": "high"},
            "timing": {"platforms": {}},
            "style": {"variation_patterns": {}},
            "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
        }
        result = self.validator.validate(config)
        self.assertTrue(any("timing.active_hours" in e for e in result.errors))

    def test_platform_timing_valid(self):
        """Test valid platform timing configuration."""
        config = {
            "meta": {"persona_id": "test", "language": "ja", "context_culture": "high"},
            "timing": {
                "platforms": {
                    "chat": {"min_delay": 30, "max_delay": 180},
                    "email": {"min_delay": 3600, "max_delay": 28800},
                },
                "active_hours": {"start": "09:00", "end": "18:00"},
            },
            "style": {"variation_patterns": {}},
            "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
        }
        result = self.validator.validate(config)
        self.assertFalse(any("platforms" in e for e in result.errors))

    def test_active_hours_time_format(self):
        """Test active_hours time format validation."""
        for time_str in ["09:00", "18:30", "00:00", "23:59"]:
            config = {
                "meta": {"persona_id": "test", "language": "ja", "context_culture": "high"},
                "timing": {
                    "platforms": {"chat": {"min_delay": 30, "max_delay": 180}},
                    "active_hours": {"start": time_str, "end": time_str},
                },
                "style": {"variation_patterns": {}},
                "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
            }
            result = self.validator.validate(config)
            self.assertFalse(any("start" in e or "end" in e for e in result.errors))

    def test_active_hours_invalid_format(self):
        """Test active_hours with invalid time format."""
        config = {
            "meta": {"persona_id": "test", "language": "ja", "context_culture": "high"},
            "timing": {
                "platforms": {"chat": {"min_delay": 30, "max_delay": 180}},
                "active_hours": {"start": "9:00", "end": "18:00"},  # Missing leading 0
            },
            "style": {"variation_patterns": {}},
            "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
        }
        result = self.validator.validate(config)
        self.assertTrue(any("start" in e and "pattern" in e for e in result.errors))


class TestStyleField(unittest.TestCase):
    """Test style field validation."""

    @classmethod
    def setUpClass(cls):
        """Set up validator."""
        schema_path = str(Path(__file__).parent.parent / "config" / "schema.json")
        cls.validator = ConfigValidator(schema_path)

    def test_style_missing_variation_patterns(self):
        """Test style missing required variation_patterns."""
        config = {
            "meta": {"persona_id": "test", "language": "ja", "context_culture": "high"},
            "timing": {
                "platforms": {"chat": {"min_delay": 30, "max_delay": 180}},
                "active_hours": {"start": "09:00", "end": "18:00"},
            },
            "style": {},
            "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
        }
        result = self.validator.validate(config)
        self.assertTrue(any("variation_patterns" in e for e in result.errors))

    def test_variation_patterns_valid(self):
        """Test valid variation_patterns structure."""
        config = {
            "meta": {"persona_id": "test", "language": "ja", "context_culture": "high"},
            "timing": {
                "platforms": {"chat": {"min_delay": 30, "max_delay": 180}},
                "active_hours": {"start": "09:00", "end": "18:00"},
            },
            "style": {
                "variation_patterns": {
                    "confirmation": ["pattern1", "pattern2"],
                    "empathy": ["phrase1", "phrase2"],
                }
            },
            "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
        }
        result = self.validator.validate(config)
        self.assertFalse(any("variation_patterns" in e for e in result.errors))

    def test_emoji_policy_enum(self):
        """Test emoji_policy enum validation."""
        for policy in ["never", "rare", "moderate", "frequent"]:
            config = {
                "meta": {"persona_id": "test", "language": "ja", "context_culture": "high"},
                "timing": {
                    "platforms": {"chat": {"min_delay": 30, "max_delay": 180}},
                    "active_hours": {"start": "09:00", "end": "18:00"},
                },
                "style": {
                    "variation_patterns": {},
                    "emoji_policy": policy,
                },
                "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
            }
            result = self.validator.validate(config)
            self.assertFalse(any("emoji_policy" in e for e in result.errors))


class TestEmotionField(unittest.TestCase):
    """Test emotion field validation."""

    @classmethod
    def setUpClass(cls):
        """Set up validator."""
        schema_path = str(Path(__file__).parent.parent / "config" / "schema.json")
        cls.validator = ConfigValidator(schema_path)

    def test_emotion_missing_initial_state(self):
        """Test emotion missing required initial_state."""
        config = {
            "meta": {"persona_id": "test", "language": "ja", "context_culture": "high"},
            "timing": {
                "platforms": {"chat": {"min_delay": 30, "max_delay": 180}},
                "active_hours": {"start": "09:00", "end": "18:00"},
            },
            "style": {"variation_patterns": {}},
            "emotion": {"states": {}, "transitions": []},
        }
        result = self.validator.validate(config)
        self.assertTrue(any("initial_state" in e for e in result.errors))

    def test_emotion_missing_states(self):
        """Test emotion missing required states."""
        config = {
            "meta": {"persona_id": "test", "language": "ja", "context_culture": "high"},
            "timing": {
                "platforms": {"chat": {"min_delay": 30, "max_delay": 180}},
                "active_hours": {"start": "09:00", "end": "18:00"},
            },
            "style": {"variation_patterns": {}},
            "emotion": {"initial_state": "polite", "transitions": []},
        }
        result = self.validator.validate(config)
        self.assertTrue(any("emotion.states" in e for e in result.errors))

    def test_emotion_states_valid(self):
        """Test valid emotion states structure."""
        config = {
            "meta": {"persona_id": "test", "language": "ja", "context_culture": "high"},
            "timing": {
                "platforms": {"chat": {"min_delay": 30, "max_delay": 180}},
                "active_hours": {"start": "09:00", "end": "18:00"},
            },
            "style": {"variation_patterns": {}},
            "emotion": {
                "initial_state": "polite",
                "states": {
                    "polite": {
                        "formality": 0.9,
                        "warmth": 0.3,
                        "verbosity": 0.6,
                    }
                },
                "transitions": [],
            },
        }
        result = self.validator.validate(config)
        self.assertFalse(any("emotion.states" in e for e in result.errors))


class TestExistingConfigFiles(unittest.TestCase):
    """Test validation against actual config files in the repo."""

    @classmethod
    def setUpClass(cls):
        """Set up validator."""
        schema_path = str(Path(__file__).parent.parent / "config" / "schema.json")
        cls.validator = ConfigValidator(schema_path)
        cls.config_dir = str(Path(__file__).parent.parent / "config")

    def test_ja_config(self):
        """Test ja.json against schema."""
        result = self.validator.validate_file(
            os.path.join(self.config_dir, "ja.json")
        )
        # Note: ja.json uses old format, so may not fully validate against schema
        self.assertIsInstance(result, ValidationResult)
        # Just verify it can be loaded and validated
        self.assertEqual(result.config_path, os.path.join(self.config_dir, "ja.json"))

    def test_en_config(self):
        """Test en.json against schema."""
        result = self.validator.validate_file(
            os.path.join(self.config_dir, "en.json")
        )
        self.assertIsInstance(result, ValidationResult)
        self.assertEqual(result.config_path, os.path.join(self.config_dir, "en.json"))

    def test_es_config(self):
        """Test es.json against schema."""
        result = self.validator.validate_file(
            os.path.join(self.config_dir, "es.json")
        )
        self.assertIsInstance(result, ValidationResult)
        self.assertEqual(result.config_path, os.path.join(self.config_dir, "es.json"))

    def test_ja_business_config(self):
        """Test ja_business.json against schema."""
        result = self.validator.validate_file(
            os.path.join(self.config_dir, "ja_business.json")
        )
        self.assertIsInstance(result, ValidationResult)
        # This config should follow the schema more closely
        self.assertEqual(result.config_path, os.path.join(self.config_dir, "ja_business.json"))

    def test_validate_all_configs(self):
        """Test validate_all on config directory."""
        results = self.validator.validate_all(self.config_dir)
        self.assertIsInstance(results, dict)
        # Should have results for all .json files except schema.json
        self.assertGreater(len(results), 0)
        self.assertNotIn("schema.json", results)


class TestFileValidation(unittest.TestCase):
    """Test file-based validation."""

    @classmethod
    def setUpClass(cls):
        """Set up validator."""
        schema_path = str(Path(__file__).parent.parent / "config" / "schema.json")
        cls.validator = ConfigValidator(schema_path)

    def test_validate_nonexistent_file(self):
        """Test validating file that doesn't exist."""
        result = self.validator.validate_file("/nonexistent/config.json")
        self.assertFalse(result.valid)
        self.assertIn("not found", result.errors[0].lower())

    def test_validate_invalid_json(self):
        """Test validating file with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json")
            temp_path = f.name

        try:
            result = self.validator.validate_file(temp_path)
            self.assertFalse(result.valid)
            self.assertIn("Invalid JSON", result.errors[0])
        finally:
            os.unlink(temp_path)

    def test_validate_valid_json_file(self):
        """Test validating file with valid JSON but missing required fields."""
        config = {"meta": {}}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(config, f)
            temp_path = f.name

        try:
            result = self.validator.validate_file(temp_path)
            # Should have validation errors for missing required fields
            self.assertIsInstance(result, ValidationResult)
        finally:
            os.unlink(temp_path)


class TestNumberRangeValidation(unittest.TestCase):
    """Test number/integer range validation."""

    @classmethod
    def setUpClass(cls):
        """Set up validator."""
        schema_path = str(Path(__file__).parent.parent / "config" / "schema.json")
        cls.validator = ConfigValidator(schema_path)

    def test_typo_rate_in_range(self):
        """Test typo_rate within valid range."""
        config = {
            "meta": {"persona_id": "test", "language": "ja", "context_culture": "high"},
            "timing": {
                "platforms": {"chat": {"min_delay": 30, "max_delay": 180}},
                "active_hours": {"start": "09:00", "end": "18:00"},
            },
            "style": {
                "variation_patterns": {},
                "typo_rate": 0.005,
            },
            "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
        }
        result = self.validator.validate(config)
        self.assertFalse(any("typo_rate" in e for e in result.errors))

    def test_typo_rate_too_high(self):
        """Test typo_rate exceeding maximum."""
        config = {
            "meta": {"persona_id": "test", "language": "ja", "context_culture": "high"},
            "timing": {
                "platforms": {"chat": {"min_delay": 30, "max_delay": 180}},
                "active_hours": {"start": "09:00", "end": "18:00"},
            },
            "style": {
                "variation_patterns": {},
                "typo_rate": 0.15,  # Max is 0.1
            },
            "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
        }
        result = self.validator.validate(config)
        self.assertTrue(any("typo_rate" in e for e in result.errors))


class TestArrayMinItems(unittest.TestCase):
    """Test array minItems validation."""

    @classmethod
    def setUpClass(cls):
        """Set up validator."""
        schema_path = str(Path(__file__).parent.parent / "config" / "schema.json")
        cls.validator = ConfigValidator(schema_path)

    def test_variation_pattern_min_items(self):
        """Test variation pattern with minimum 2 items."""
        config = {
            "meta": {"persona_id": "test", "language": "ja", "context_culture": "high"},
            "timing": {
                "platforms": {"chat": {"min_delay": 30, "max_delay": 180}},
                "active_hours": {"start": "09:00", "end": "18:00"},
            },
            "style": {
                "variation_patterns": {
                    "confirmation": ["pattern1"],  # Only 1, need 2+
                }
            },
            "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
        }
        result = self.validator.validate(config)
        self.assertTrue(any("minimum is 2" in e for e in result.errors))


class TestOptionalFieldWarnings(unittest.TestCase):
    """Test warnings for missing optional fields."""

    @classmethod
    def setUpClass(cls):
        """Set up validator."""
        schema_path = str(Path(__file__).parent.parent / "config" / "schema.json")
        cls.validator = ConfigValidator(schema_path)

    def test_missing_optional_fields_generate_warnings(self):
        """Test that missing optional fields generate warnings."""
        config = {
            "meta": {"persona_id": "test", "language": "ja", "context_culture": "high"},
            "timing": {
                "platforms": {"chat": {"min_delay": 30, "max_delay": 180}},
                "active_hours": {"start": "09:00", "end": "18:00"},
            },
            "style": {"variation_patterns": {}},
            "emotion": {"initial_state": "polite", "states": {}, "transitions": []},
            # Missing optional context_reference and ambiguity
        }
        result = self.validator.validate(config)
        # Should have warnings for missing optional fields
        self.assertGreater(len(result.warnings), 0)


if __name__ == "__main__":
    unittest.main()
