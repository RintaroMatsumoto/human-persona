"""
ConfigValidator — JSON schema validation for persona configurations.

Validates configuration files against schema.json, with detailed error
reporting for missing fields, type mismatches, and pattern violations.

Author: Rintaro Matsumoto
License: MIT
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class ValidationResult:
    """Result of schema validation."""
    is_valid: bool
    errors: list[str]
    warnings: list[str]


class ConfigValidator:
    """
    Validates persona configuration files against JSON schema.

    Provides detailed error and warning messages for configuration issues.
    """

    def __init__(self, schema_path: str | Path) -> None:
        """
        Initialize ConfigValidator with schema.

        Args:
            schema_path: Path to schema.json file.

        Raises:
            FileNotFoundError: If schema file not found.
            json.JSONDecodeError: If schema is not valid JSON.
        """
        schema_path = Path(schema_path)
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, encoding='utf-8') as f:
            self.schema: dict[str, Any] = json.load(f)

    def validate(self, config: dict[str, Any]) -> ValidationResult:
        """
        Validate a configuration dict against the schema.

        Args:
            config: Configuration to validate.

        Returns:
            ValidationResult with errors and warnings.
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Check required fields
        required_fields = self.schema.get('required', [])
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        # Validate field types
        properties = self.schema.get('properties', {})
        for field, value in config.items():
            if field not in properties:
                warnings.append(f"Unknown field: {field}")
                continue

            field_schema = properties[field]
            expected_type = field_schema.get('type')

            if expected_type and not self._check_type(value, expected_type):
                errors.append(
                    f"Field '{field}' has wrong type. "
                    f"Expected {expected_type}, got {type(value).__name__}"
                )

            # Check constraints
            if 'minimum' in field_schema and isinstance(value, (int, float)):
                if value < field_schema['minimum']:
                    errors.append(
                        f"Field '{field}' value {value} is below minimum {field_schema['minimum']}"
                    )

            if 'maximum' in field_schema and isinstance(value, (int, float)):
                if value > field_schema['maximum']:
                    errors.append(
                        f"Field '{field}' value {value} exceeds maximum {field_schema['maximum']}"
                    )

            # Check pattern (for strings)
            if 'pattern' in field_schema and isinstance(value, str):
                import re
                if not re.match(field_schema['pattern'], value):
                    errors.append(
                        f"Field '{field}' value '{value}' doesn't match pattern {field_schema['pattern']}"
                    )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """
        Check if value matches expected type.

        Args:
            value: Value to check.
            expected_type: Expected type name ('string', 'number', 'object', etc.).

        Returns:
            True if type matches.
        """
        type_mapping: dict[str, type] = {
            'string': str,
            'number': (int, float),
            'integer': int,
            'object': dict,
            'array': list,
            'boolean': bool,
            'null': type(None),
        }

        if expected_type not in type_mapping:
            return True  # Unknown type, allow

        expected = type_mapping[expected_type]
        return isinstance(value, expected)

    def load_and_validate(self, config_path: str | Path) -> tuple[dict[str, Any], ValidationResult]:
        """
        Load config file and validate it.

        Args:
            config_path: Path to config file.

        Returns:
            Tuple of (config_dict, ValidationResult).

        Raises:
            FileNotFoundError: If config file not found.
            json.JSONDecodeError: If config is not valid JSON.
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, encoding='utf-8') as f:
            config = json.load(f)

        result = self.validate(config)
        return config, result

    def __str__(self) -> str:
        """String representation of validator."""
        return f"<ConfigValidator with {len(self.schema.get('properties', {}))} schema properties>"

    def get_schema_properties(self) -> list[str]:
        """
        Get list of all properties in the schema.

        Returns:
            List of property names.
        """
        return list(self.schema.get('properties', {}).keys())

    def get_required_fields(self) -> list[str]:
        """
        Get list of required fields.

        Returns:
            List of required field names.
        """
        return self.schema.get('required', [])

    def validate_with_defaults(self, config: dict[str, Any]) -> dict[str, Any]:
        """
        Validate config and apply default values where missing.

        Args:
            config: Configuration to validate and enhance.

        Returns:
            Config with defaults applied.
        """
        properties = self.schema.get('properties', {})

        for field, field_schema in properties.items():
            if field not in config and 'default' in field_schema:
                config[field] = field_schema['default']

        return config
