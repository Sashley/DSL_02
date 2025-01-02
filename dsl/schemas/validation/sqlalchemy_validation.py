from typing import Dict, List, Optional, Set
from pydantic import BaseModel
from dsl.schemas.validation.schema import Model, DSLValidation

class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class SQLAlchemyValidator:
    def __init__(self, schema: DSLValidation):
        self.schema = schema
        self.models = schema.Models
        self.valid_types = {
            'string', 'integer', 'float', 'boolean', 'date', 
            'datetime', 'text', 'json', 'uuid'
        }

    def validate_foreign_keys(self) -> List[str]:
        """Validate all foreign key references point to existing tables and columns"""
        errors = []
        for model_name, model in self.models.items():
            for field_name, field in model.Fields.items():
                if field.foreign_key:
                    # Expected format: table.column
                    try:
                        ref_table, ref_column = field.foreign_key.lower().split('.')
                        # Find the actual model name with correct case
                        actual_model = next(
                            (m for m in self.models.keys() if m.lower() == ref_table),
                            None
                        )
                        if not actual_model:
                            errors.append(
                                f"Invalid foreign key in {model_name}.{field_name}: "
                                f"Referenced table '{ref_table}' does not exist"
                            )
                        elif ref_column not in {k.lower(): k for k in self.models[actual_model].Fields.keys()}:
                            errors.append(
                                f"Invalid foreign key in {model_name}.{field_name}: "
                                f"Referenced column '{ref_column}' does not exist in table '{ref_table}'"
                            )
                    except ValueError:
                        errors.append(
                            f"Invalid foreign key format in {model_name}.{field_name}: "
                            f"Expected 'table.column', got '{field.foreign_key}'"
                        )
        return errors

    def validate_indices(self) -> List[str]:
        """Validate index definitions reference existing columns"""
        errors = []
        for model_name, model in self.models.items():
            if model.Indices:
                for index_name, columns in model.Indices.items():
                    for column in columns:
                        if column not in model.Fields:
                            errors.append(
                                f"Invalid index '{index_name}' in {model_name}: "
                                f"Referenced column '{column}' does not exist"
                            )
        return errors

    def validate_types(self) -> List[str]:
        """Validate field types are supported and compatible with foreign keys"""
        errors = []
        for model_name, model in self.models.items():
            for field_name, field in model.Fields.items():
                if field.type.lower() not in self.valid_types:
                    errors.append(
                        f"Invalid field type in {model_name}.{field_name}: "
                        f"Type '{field.type}' is not supported"
                    )
                
                # Check foreign key type compatibility
                if field.foreign_key:
                    ref_table, ref_column = field.foreign_key.lower().split('.')
                    actual_model = next(
                        (m for m in self.models.keys() if m.lower() == ref_table),
                        None
                    )
                    if actual_model:
                        ref_field_name = next(
                            (k for k in self.models[actual_model].Fields.keys() 
                             if k.lower() == ref_column),
                            None
                        )
                        if ref_field_name:
                            ref_field = self.models[actual_model].Fields[ref_field_name]
                            if ref_field and field.type.lower() != ref_field.type.lower():
                                errors.append(
                                f"Type mismatch in foreign key {model_name}.{field_name}: "
                                f"Expected {ref_field.type}, got {field.type}"
                            )
        return errors

    def validate_primary_keys(self) -> List[str]:
        """Validate each model has exactly one primary key"""
        errors = []
        for model_name, model in self.models.items():
            pk_count = sum(1 for field in model.Fields.values() if field.primary_key)
            if pk_count == 0:
                errors.append(f"Model {model_name} has no primary key defined")
            elif pk_count > 1:
                errors.append(f"Model {model_name} has multiple primary keys defined")
        return errors

    def validate_all(self) -> List[str]:
        """Run all validations and return combined errors"""
        all_errors = []
        all_errors.extend(self.validate_foreign_keys())
        all_errors.extend(self.validate_indices())
        all_errors.extend(self.validate_types())
        all_errors.extend(self.validate_primary_keys())
        return all_errors

def validate_sqlalchemy_schema(schema: DSLValidation) -> List[str]:
    """Main entry point for SQLAlchemy validation"""
    validator = SQLAlchemyValidator(schema)
    return validator.validate_all()
