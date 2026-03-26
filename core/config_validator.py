"""
ConfigValidator — JSON schema validation for persona configurations.

Validates configuration files against schema.json, with detailed error
reporting for missing fields, type mismatches, and pattern violations.

Author: Rintaro Matsumoto
License: MIT
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class ValidationResult:
    """Result of schema validation."""
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    config_path: str = ""

    def __str__(self) -> str:
        if self.valid:
            return f"\u2713 VALID: {self.config_path}"
        parts = [f"\u2717 INVALID: {self.config_path}"]
        if self.errors:
            parts.append("Errors:")
            for e in self.errors:
                parts.append(f"  - {e}")
        if self.warnings:
            parts.append("Warnings:")
            for w in self.warnings:
                parts.append(f"  - {w}")
        return "\n".join(parts)


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

    def validate(self, config: Any, config_path: str = "") -> ValidationResult:
        """
        Validate a configuration dict against the schema.

        Args:
            config: Configuration to validate.
            config_path: Optional path for error reporting.

        Returns:
            ValidationResult with errors and warnings.
        """
        errors: list[str] = []
        warnings: list[str] = []

        if not isinstance(config, dict):
            return ValidationResult(
                valid=False,
                errors=["Configuration must be a dict"],
                warnings=[],
                config_path=config_path,
            )

        self._validate_object(config, self.schema, "", errors, warnings)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            config_path=config_path,
        )

    def _validate_object(
        self,
        data: dict[str, Any],
        schema: dict[str, Any],
        prefix: str,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Recursively validate an object against its schema."""
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])

        # Check required fields
        for field_name in required_fields:
            full_path = f"{prefix}.{field_name}" if prefix else field_name
            if field_name not in data:
                errors.append(f"Missing required field: {full_path}")

        # Check for optional top-level fields that are missing (generate warnings)
        if not prefix:
            for field_name in properties:
                if field_name not in required_fields and field_name not in data:
                    warnings.append(f"Missing optional field: {field_name}")

        # Validate each present field
        for field_name, value in data.items():
            full_path = f"{prefix}.{field_name}" if prefix else field_name
            if field_name not in properties:
                if not prefix:
                    warnings.append(f"Unknown field: {field_name}")
                continue

            field_schema = properties[field_name]
            self._validate_value(value, field_schema, full_path, errors, warnings)

    def _validate_value(
        self,
        value: Any,
        schema: dict[str, Any],
        path: str,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Validate a single value against its schema definition."""
        expected_type = schema.get('type')

        # Type check
        if expected_type and not self._check_type(value, expected_type):
            errors.append(
                f"Field '{path}' has wrong type. "
                f"Expected {expected_type}, got {type(value).__name__}"
            )
            return  # Don't validate further if type is wrong

        # For objects, recurse
        if expected_type == 'object' and isinstance(value, dict):
            if 'properties' in schema:
                self._validate_object(value, schema, path, errors, warnings)
            # Handle additionalProperties (e.g. variation_patterns, platforms, states)
            if 'additionalProperties' in schema and isinstance(schema['additionalProperties'], dict):
                ap_schema = schema['additionalProperties']
                for key, sub_value in value.items():
                    sub_path = f"{path}.{key}"
                    self._validate_value(sub_value, ap_schema, sub_path, errors, warnings)

        # Pattern check (strings)
        if 'pattern' in schema and isinstance(value, str):
            if not re.match(schema['pattern'], value):
                errors.append(
                    f"Field '{path}' value '{value}' doesn't match pattern {schema['pattern']}"
                )

        # Enum check
        if 'enum' in schema and value not in schema['enum']:
            errors.append(
                f"Field '{path}' value '{value}' not in allowed values: {schema['enum']}"
            )

        # Minimum / maximum (numbers)
        if 'minimum' in schema and isinstance(value, (int, float)):
            if value < schema['minimum']:
                errors.append(
                    f"Field '{path}' value {value} is below minimum {schema['minimum']}"
                )

        if 'maximum' in schema and isinstance(value, (int, float)):
            if value > schema['maximum']:
                errors.append(
                    f"Field '{path}' value {value} exceeds maximum {schema['maximum']}"
                )

        # Array minItems
        if 'minItems' in schema and isinstance(value, list):
            if len(value) < schema['minItems']:
                errors.append(
                    f"Field '{path}' has {len(value)} items, minimum is {schema['minItems']}"
                )

        # Array item validation
        if expected_type == 'array' and isinstance(value, list) and 'items' in schema:
            item_schema = schema['items']
            for i, item in enumerate(value):
                item_path = f"{path}[{i}]"
                self._validate_value(item, item_schema, item_path, errors, warnings)

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

    def validate_file(self, filepath: str | Path) -> ValidationResult:
        """
        Load a JSON file and validate it against the schema.

        Args:
            filepath: Path to the JSON configuration file.

        Returns:
            ValidationResult with errors, warnings, and config_path set.
        """
        filepath = str(filepath)
        try:
            with open(filepath, encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            return ValidationResult(
                valid=False,
                errors=[f"File not found: {filepath}"],
                config_path=filepath,
            )
        except json.JSONDecodeError as e:
            return ValidationResult(
                valid=False,
                errors=[f"Invalid JSON: {e}"],
                config_path=filepath,
            )

        return self.validate(config, config_path=filepath)

    def validate_all(self, directory: str | Path) -> dict[str, ValidationResult]:
        """
        Validate all .json files in a directory (excluding schema.json).

        Args:
            directory: Path to directory containing config files.

        Returns:
            Dict mapping filename to ValidationResult.
        """
        directory = Path(directory)
        results: dict[str, ValidationResult] = {}
        for json_file in sorted(directory.glob('*.json')):
            if json_file.name == 'schema.json':
                continue
            results[json_file.name] = self.validate_file(str(json_file))
        return results

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

        for field_name, field_schema in properties.items():
            if field_name not in config and 'default' in field_schema:
                config[field_name] = field_schema['default']

        return config
