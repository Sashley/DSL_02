#!/usr/bin/env python3
"""
Script to convert shipping_modules_03.dsl to models.py
"""
import os
import json
from dsl.converter_01.dsl import first_pass_create_model_map, second_pass_generate_models
from dsl.converter_01.sqlalchemy import load_json_to_models
from sqlalchemy import Column
from sqlalchemy.orm import declarative_base

def convert_dsl_to_json(dsl_file, json_file):
    """
    Convert DSL file to JSON format
    """
    print(f"Converting {dsl_file} to JSON...")
    model_map = first_pass_create_model_map(dsl_file)
    dsl_json = second_pass_generate_models(dsl_file, model_map)
    
    # Save JSON
    with open(json_file, "w") as f:
        json.dump(dsl_json, f, indent=4)
    print(f"JSON saved to {json_file}")

def main():
    # Get directory of current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Input/output files
    dsl_file = os.path.join(current_dir, "shipping_modules_03.dsl")
    json_file = os.path.join(current_dir, "shipping_converted.json")
    output_file = os.path.join(current_dir, "models_converted.py")
    
    # Convert DSL to JSON
    print(f"Converting {dsl_file} to JSON...")
    model_map = first_pass_create_model_map(dsl_file)
    dsl_json = second_pass_generate_models(dsl_file, model_map)
    
    # Save intermediate JSON for inspection
    with open(json_file, "w") as f:
        json.dump(dsl_json, f, indent=4)
    print(f"JSON saved to {json_file}")
    
    # Convert JSON to SQLAlchemy models
    print("Converting JSON to SQLAlchemy models...")
    Base = declarative_base()
    models = load_json_to_models(json_file, Base)
    
    # Generate models.py content
    content = [
        "from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, DateTime, Text, Index",
        "from sqlalchemy.orm import declarative_base, relationship\n",
        "Base = declarative_base()\n"
    ]
    
    # Sort models by name for consistent output
    for model_name in sorted(models.keys()):
        model = models[model_name]
        # Get model source code by inspecting class attributes
        attrs = []
        # Add tablename
        attrs.append(f'    __tablename__ = "{model.__tablename__}"')
        attrs.append('    __table_args__ = {"extend_existing": True}')
        
        # Add columns
        for name, column in model.__dict__.items():
            if isinstance(column, Column) and not name.startswith('_'):
                attrs.append(f"    {name} = {column}")
        
        # Add relationships
        for name, rel in model.__dict__.items():
            if name.endswith('_rel'):
                # Get target model from foreign key
                field_name = name[:-4]  # Remove _rel suffix
                for fname, field_def in model.__dict__.items():
                    if isinstance(field_def, Column) and fname == field_name:
                        if hasattr(field_def, 'foreign_keys'):
                            fk = list(field_def.foreign_keys)[0]
                            target_model = fk.column.table.name
                            attrs.append(f"    {name} = relationship('{target_model}', foreign_keys=[{field_name}])")
        
        # Combine into class definition
        class_def = [f"class {model_name}(Base):"]
        class_def.extend(attrs)
        content.extend(class_def)
        content.append("")  # Empty line between classes
    
    # Write to models file
    with open(output_file, "w") as f:
        f.write("\n".join(content))
    print(f"Models generated successfully in {output_file}")

if __name__ == "__main__":
    main()
