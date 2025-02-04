"""
DEPRECATED: This module is superseded by convert_batch.py
This module's functionality has been moved to convert_batch.py.
Please use convert_batch.validate_dsl_file() instead.
"""

import sys
from pathlib import Path
from dsl.convert_batch import validate_dsl_file

print("Warning: Using deprecated validation.py module. Use convert_batch.validate_dsl_file() instead.",
      file=sys.stderr)

def validate_dsl(file_path: str | Path):
    """
    DEPRECATED: Use convert_batch.validate_dsl_file() instead.
    This function is maintained for backward compatibility.
    """
    return validate_dsl_file(file_path)

if __name__ == "__main__":
    # Example usage showing migration path
    dsl_file = Path(__file__).parent.parent / "schemas" / "shipping" / "current" / "schema.dsl"
    is_valid, errors = validate_dsl_file(dsl_file)
    
    if is_valid:
        print("✓ All validations passed successfully!")
    else:
        print("✗ Validation failed:")
        for error in errors:
            print(f"  - {error}")
