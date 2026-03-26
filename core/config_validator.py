"""
JSON schema validation for HumanPersona configuration files.

This module provides automatic validation of configuration files against
the schema defined in config/schema.json, with detailed error reporting
for missing fields, type mismatches, and pattern violations.

No external dependencies (jsonschema library not used) — validation
is implemented manually to walk the schema and validate configs.
"""

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class ValidationResult:
    """Validation result with errors and warnings."""

    valid: bool
    config_path: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        """Return human-readable validation report."""
        lines = [f"Config: {self.config_path}"]
        lines.append(f"Status: {'✓ VALID' if self.valid else '✗ INVALID'}")

        if self.errors:
            lines.append("\nErrors:")
            for err in self.errors:
                lines.append(f"  - {err}")

        if self.warnings:
            lines.append("\nWarnings:")
            for warn in self.warnings:
                lines.append(f"  - {warn}")

        return "\n".join(lines)


class ConfigValidator:
    """Validates HumanPersona configuration files against schema.json."""

    def __init__(self, schema_path: str):
        """
        Initialize validator with schema file.

        Args:
            schema_path: Path to schema.json file

        Raises:
            FileNotFoundError: If schema file not found
            json.JSONDecodeError: If schema JSON is invalid
        """
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

    def validate(self, config: Dict[str, Any], config_path: str = "<dict>") -> ValidationResult:
        """
        Validate a configuration dictionary against the schema.

        Args:
            config: Configuration dictionary to validate
            config_path: Path for error reporting (default: '<dict>')

        Returns:
            ValidationResult with validation status, errors, and warnings
        """
        result = ValidationResult(valid=True, config_path=config_path)

        if not isinstance(config, dict):
            result.valid = False
            result.errors.append(f"Config must be a dict, got {type(config).__name__}")
            return result

        # Check required top-level properties
        required = self.schema.get("required", [])
        for field_name in required:
            if field_name not in config:
                result.valid = False
                result.errors.append(f"Missing required field: {field_name}")

        # Validate each property present in config
        properties = self.schema.get("properties", {})
        for field_name, field_value in config.items():
            if field_name not in properties:
                # Check additionalProperties setting
                if not self.schema.get("additionalProperties", True):
                    result.valid = False
                    result.errors.append(f"Unexpected field: {field_name}")
                continue

            # Validate field value against its schema
            field_schema = properties[field_name]
            self._validate_field(field_name, field_value, field_schema, result, config_path)

        # Check for completely missing optional fields and generate warnings
        for field_name, field_schema in properties.items():
            if field_name not in config and field_name not in required:
                if "default" not in field_schema:
                    result.warnings.append(f"Missing optional field: {field_name}")

        return result

    def validate_file(self, config_path: str) -> ValidationResult:
        """
        Validate a JSON configuration file.

        Args:
            config_path: Path to JSON config file

        Returns:
            ValidationResult with validation status
        """
        if not os.path.exists(config_path):
            return ValidationResult(
                valid=False,
                config_path=config_path,
                errors=[f"File not found: {config_path}"],
            )

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return ValidationResult(
                valid=False,
                config_path=config_path,
                errors=[f"Invalid JSON: {str(e)}"],
            )

        return self.validate(config, config_path)

    def validate_all(self, config_dir: str) -> Dict[str, ValidationResult]:
        """
        Validate all JSON files in a directory.

        Skips schema.json itself.

        Args:
            config_dir: Directory containing JSON config files

        Returns:
            Dictionary mapping config filenames to ValidationResult objects
        """
        results = {}

        if not os.path.isdir(config_dir):
            return results

        for filename in os.listdir(config_dir):
            if filename == "schema.json" or not filename.endswith(".json"):
                continue

            config_path = os.path.join(config_dir, filename)
            if os.path.isfile(config_path):
                results[filename] = self.validate_file(config_path)

        return results

    def _validate_field(
        self,
        field_name: str,
        field_value: Any,
        field_schema: Dict[str, Any],
        result: ValidationResult,
        config_path: str,
    ) -> None:
        """
        Validate a single field value against its schema definition.

        Args:
            field_name: Name of the field
            field_value: Value to validate
            field_schema: Schema definition for the field
            result: ValidationResult to accumulate errors/warnings
            config_path: Config path for error messages
        """
        field_type = field_schema.get("type")

        # Type checking
        if field_type:
            if not self._check_type(field_value, field_type):
                result.valid = False
                result.errors.append(
                    f"{field_name}: expected {field_type}, got {type(field_value).__name__}"
                )
                return

        # Enum validation
        if "enum" in field_schema:
            if field_value not in field_schema["enum"]:
                result.valid = False
                allowed = ", ".join(str(e) for e in field_schema["enum"])
                result.errors.append(f"{field_name}: must be one of [{allowed}], got {field_value}")
                return

        # Pattern validation (regex)
        if "pattern" in field_schema and isinstance(field_value, str):
            pattern = field_schema["pattern"]
            if not re.match(f"^{pattern}$", field_value):
                result.valid = False
                result.errors.append(f"{field_name}: value '{field_value}' does not match pattern '{pattern}'")
                return

        # String length validation
        if field_type == "string":
            if "minLength" in field_schema and len(field_value) < field_schema["minLength"]:
                result.valid = False
                result.errors.append(f"{field_name}: string too short (min {field_schema['minLength']})")
            if "maxLength" in field_schema and len(field_value) > field_schema["maxLength"]:
                result.valid = False
                result.errors.append(f"{field_name}: string too long (max {field_schema['maxLength']})")

        # Number range validation
        if field_type == "number" or field_type == "integer":
            if "minimum" in field_schema and field_value < field_schema["minimum"]:
                result.valid = False
                result.errors.append(f"{field_name}: value {field_value} is below minimum {field_schema['minimum']}")
            if "maximum" in field_schema and field_value > field_schema["maximum"]:
                result.valid = False
                result.errors.append(f"{field_name}: value {field_value} exceeds maximum {field_schema['maximum']}")

        # Array validation
        if field_type == "array":
            if not isinstance(field_value, list):
                result.valid = False
                result.errors.append(f"{field_name}: expected array, got {type(field_value).__name__}")
                return

            # Check minItems
            if "minItems" in field_schema and len(field_value) < field_schema["minItems"]:
                result.valid = False
                result.errors.append(f"{field_name}: array has {len(field_value)} items, minimum is {field_schema['minItems']}")
                return

            # Validate items
            if "items" in field_schema:
                item_schema = field_schema["items"]
                for i, item in enumerate(field_value):
                    self._validate_field(f"{field_name}[{i}]", item, item_schema, result, config_path)

        # Object validation
        if field_type == "object":
            if not isinstance(field_value, dict):
                result.valid = False
                result.errors.append(f"{field_name}: expected object, got {type(field_value).__name__}")
                return

            # Recurse into object properties
            if "properties" in field_schema:
                self._validate_object(field_name, field_value, field_schema, result, config_path)
            elif "additionalProperties" in field_schema:
                # For additionalProperties, validate all values against the schema
                additional_schema = field_schema["additionalProperties"]
                if isinstance(additional_schema, dict):
                    for key, val in field_value.items():
                        self._validate_field(f"{field_name}.{key}", val, additional_schema, result, config_path)

    def _validate_object(
        self,
        field_name: str,
        obj_value: Dict[str, Any],
        obj_schema: Dict[str, Any],
        result: ValidationResult,
        config_path: str,
    ) -> None:
        """
        Validate an object (nested dictionary).

        Args:
            field_name: Name of the object field
            obj_value: Object dictionary to validate
            obj_schema: Schema definition for the object
            result: ValidationResult to accumulate errors
            config_path: Config path for error messages
        """
        # Check required properties
        required_fields = obj_schema.get("required", [])
        for req_field in required_fields:
            if req_field not in obj_value:
                result.valid = False
                result.errors.append(f"{field_name}.{req_field}: required field missing")

        # Check each property in the object
        properties = obj_schema.get("properties", {})
        for prop_name, prop_value in obj_value.items():
            if prop_name not in properties:
                # Check additionalProperties
                additional_schema = obj_schema.get("additionalProperties")
                if isinstance(additional_schema, dict):
                    # additionalProperties defines schema for any additional fields
                    self._validate_field(
                        f"{field_name}.{prop_name}",
                        prop_value,
                        additional_schema,
                        result,
                        config_path,
                    )
                elif not additional_schema:
                    # additionalProperties: false means no extra fields allowed
                    result.valid = False
                    result.errors.append(f"{field_name}: unexpected property '{prop_name}'")
                continue

            # Validate against property schema
            prop_schema = properties[prop_name]
            self._validate_field(f"{field_name}.{prop_name}", prop_value, prop_schema, result, config_path)

        # Check for missing optional properties and warn
        for prop_name, prop_schema in properties.items():
            if prop_name not in obj_value and prop_name not in required_fields:
                if "default" not in prop_schema:
                    result.warnings.append(f"{field_name}.{prop_name}: optional field missing")

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """
        Check if value matches the expected JSON type.

        Args:
            value: Value to check
            expected_type: Expected type name (string, number, integer, boolean, array, object, null)

        Returns:
            True if type matches, False otherwise
        """
        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "number":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif expected_type == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "array":
            return isinstance(value, list)
        elif expected_type == "object":
            return isinstance(value, dict)
        elif expected_type == "null":
            return value is None
        return True


def validate_from_config() -> Optional[ValidationResult]:
    """
    Convenience function for calling from HumanPersonaBase.from_config() methods.

    This allows derived classes to easily validate their configs after loading.
    Should be called in derived class from_config() classmethods.

    Returns:
        ValidationResult if validation is performed, None if no schema available
    """
    # This is a placeholder for integration with HumanPersonaBase
    # Actual usage would be in the from_config() classmethod
    return None
