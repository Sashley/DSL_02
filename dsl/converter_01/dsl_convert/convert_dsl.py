#!/usr/bin/env python3
"""
DEPRECATED: This module is superseded by convert_batch.py
This module is maintained for backward compatibility but will be removed in a future version.
Please use convert_batch.py for DSL to SQLAlchemy model conversion.
"""
import os
import sys
import json
from sqlalchemy import Column
from sqlalchemy.orm import declarative_base
from dsl.converter_01.dsl import first_pass_create_model_map, second_pass_generate_models

print("Warning: Using deprecated convert_dsl.py module. Use convert_batch.py instead.",
      file=sys.stderr)

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
    """
    DEPRECATED: This script is maintained for backward compatibility.
    Please use convert_batch.py instead.
    """
    print("\nWARNING: This script is deprecated.")
    print("Please use convert_batch.py for DSL to SQLAlchemy model conversion.")
    print("Example:")
    print("  python -m dsl.convert_batch\n")
    sys.exit(1)

if __name__ == "__main__":
    main()
