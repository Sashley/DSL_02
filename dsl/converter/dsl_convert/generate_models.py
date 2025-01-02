import json
from typing import Dict

# Template for the SQLAlchemy models file
MODEL_TEMPLATE = """from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

{models}
"""

CLASS_TEMPLATE = """class {class_name}(Base):
    __tablename__ = '{table_name}'
{fields}
"""

FIELD_TEMPLATE = "    {field_name} = Column({type}{constraints})"

TYPE_MAPPING = {
    "Integer": "Integer",
    "String": "String",
    "Float": "Float",
    "DateTime": "DateTime",
    "Boolean": "Boolean",
    "Text": "String",  # You can add more mappings if needed
}

def map_type(json_type: str) -> str:
    """
    Map JSON field types to SQLAlchemy types.
    """
    return TYPE_MAPPING.get(json_type, "String")  # Default to String if type not found

def generate_field_definitions(fields: Dict) -> str:
    """
    Generate field definitions for a model.
    """
    field_lines = []
    for field_name, field_props in fields.items():
        field_type = map_type(field_props["type"])
        constraints = []

        if field_props.get("primary_key", False):
            constraints.append("primary_key=True")
        if not field_props.get("nullable", True):
            constraints.append("nullable=False")
        if field_props.get("unique", False):
            constraints.append("unique=True")
        if field_props.get("foreign_key"):
            constraints.append(f"ForeignKey('{field_props['foreign_key']}')")

        constraints_str = f", {', '.join(constraints)}" if constraints else ""
        field_lines.append(FIELD_TEMPLATE.format(
            field_name=field_name,
            type=field_type,
            constraints=constraints_str
        ))

    return "\n".join(field_lines)

def generate_models(json_file: str, output_file: str):
    """
    Generate SQLAlchemy models from a JSON file.
    """
    with open(json_file, "r") as f:
        data = json.load(f)

    models = []
    for model_name, model_data in data["Models"].items():
        class_name = model_name
        table_name = model_name.lower()
        fields = generate_field_definitions(model_data["Fields"])
        model_class = CLASS_TEMPLATE.format(class_name=class_name, table_name=table_name, fields=fields)
        models.append(model_class)

    full_code = MODEL_TEMPLATE.format(models="\n\n".join(models))

    with open(output_file, "w") as f:
        f.write(full_code)

    print(f"Models written to {output_file}")

# Call the function to generate models.py
generate_models("shipping_converted.json", "models.py")
