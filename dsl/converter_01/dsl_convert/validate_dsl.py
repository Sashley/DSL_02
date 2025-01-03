import json
from dsl.schemas.validation.schema import DSLValidation

def validate_dsl(file_path):
    """
    Validate the DSL JSON output against the Pydantic schema.
    """
    try:
        with open(file_path, "r") as f:
            dsl_data = json.load(f)
        
        # Validate the loaded JSON against the Pydantic schema
        validated_dsl = DSLValidation(**dsl_data)
        print("DSL validation passed successfully!")
        return validated_dsl

    except Exception as e:
        print(f"DSL validation failed: {e}")
        return None


if __name__ == "__main__":
    # Path to the DSL JSON file
    dsl_json_file = "shipping_converted.json"

    # Validate the DSL file
    validated_data = validate_dsl(dsl_json_file)

    # Optionally, print the validated data
    # if validated_data:
    #     print(validated_data.model_dump_json(indent=4))
