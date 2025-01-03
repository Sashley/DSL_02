#!/usr/bin/env python3
"""
Script to validate DSL schema files.
"""
import sys
from pathlib import Path

# Add project root directory to path so we can import our modules
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from dsl.converter_01.validation import validate_dsl

def main():
    base_dir = Path(__file__).parent.parent
    schema_file = base_dir / 'schemas' / 'shipping' / 'current' / 'schema.dsl'
    
    if not schema_file.exists():
        print(f"Error: Schema file not found at {schema_file}")
        sys.exit(1)
    
    print(f"Validating schema file: {schema_file}")
    is_valid, errors = validate_dsl(schema_file)
    
    if is_valid:
        print("✓ Schema validation passed")
        sys.exit(0)
    else:
        print("✗ Schema validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

if __name__ == '__main__':
    main()
