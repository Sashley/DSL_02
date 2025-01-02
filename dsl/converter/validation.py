import json
from pathlib import Path
from typing import List, Tuple
from dsl.converter.dsl import convert_dsl_to_json
from dsl.schemas.validation.schema import DSLValidation
from dsl.schemas.validation.sqlalchemy_validation import validate_sqlalchemy_schema

def validate_dsl_syntax(content: str) -> List[str]:
    """
    Validate basic DSL syntax.
    """
    errors = []
    
    # Check if file starts with table definitions
    if not content.strip().startswith('table '):
        errors.append("DSL file must start with table definitions")
    
    # Check for balanced braces
    if content.count('{') != content.count('}'):
        errors.append("Unbalanced braces in DSL file")
        
    return errors

def validate_dsl(file_path: str | Path) -> Tuple[bool, List[str]]:
    """
    Validate a DSL schema file through multiple validation steps:
    1. Basic DSL syntax validation
    2. DSL to JSON conversion validation
    3. SQLAlchemy schema validation
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    try:
        file_path = Path(file_path)
        with open(file_path, "r") as f:
            dsl_content = f.read()
        
        # Step 1: Validate DSL syntax
        syntax_errors = validate_dsl_syntax(dsl_content)
        if syntax_errors:
            return False, syntax_errors
            
        # Step 2: Convert to JSON and validate schema
        try:
            # Create a temporary file for the DSL content
            temp_file = Path(file_path).parent / "_temp_dsl.dsl"
            temp_json = Path(file_path).parent / "_temp_dsl.json"
            
            with open(temp_file, "w") as f:
                f.write(dsl_content)
                
            json_data = convert_dsl_to_json(str(temp_file), str(temp_json))
            schema = DSLValidation.parse_obj(json_data)
            
            # Cleanup temporary files
            if temp_file.exists():
                temp_file.unlink()
            if temp_json.exists():
                temp_json.unlink()
        except Exception as e:
            return False, [f"Schema validation failed: {str(e)}"]
            
        # Step 3: Validate SQLAlchemy specific rules
        sqlalchemy_errors = validate_sqlalchemy_schema(schema)
        if sqlalchemy_errors:
            return False, sqlalchemy_errors
            
        return True, []

    except Exception as e:
        return False, [f"Validation failed: {str(e)}"]

if __name__ == "__main__":
    # Example usage
    dsl_file = Path(__file__).parent.parent / "schemas" / "shipping" / "current" / "schema.dsl"
    is_valid, errors = validate_dsl(dsl_file)
    
    if is_valid:
        print("✓ All validations passed successfully!")
    else:
        print("✗ Validation failed:")
        for error in errors:
            print(f"  - {error}")
