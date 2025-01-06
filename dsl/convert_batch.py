#!/usr/bin/env python3
"""
Main conversion script that orchestrates the DSL to SQLAlchemy model conversion process.
Uses existing conversion tools in their new locations.
"""
import os
import sys
import json
import re
from pathlib import Path
from collections import defaultdict

# Add parent directory to path so we can import our modules
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from dsl.converter_01.dsl_convert.validate_dsl import validate_dsl
from dsl.converter_01.dsl_convert.convert_dsl import convert_dsl_to_json
from dsl.converter_01.sqlalchemy import load_json_to_models

def get_config():
    """
    Get configuration settings.
    This could be loaded from a config file.
    """
    return {
        'paths': {
            'schema_dir': 'schemas/shipping/current',
            'schema_file': 'schema.dsl',
            'output_json_dir': 'output/json',
            'output_json_file': 'shipping.json',
            'output_models_dir': 'output/models',
            'output_models_file': 'shipping.py',
            'flask_models_dir': '../app/models',
            'flask_models_file': 'shipping.py'
        },
        'table_naming': {
            'format': 'lower',  # Options: lower, upper, original
            'prefix': '',       # Optional prefix for all table names
            'suffix': ''        # Optional suffix for all table names
        },
        'column_constraints': {
            'primary_key': 'primary_key=True',
            'auto_increment': 'autoincrement=True',
            'nullable': 'nullable=False',
            'unique': 'unique=True'
        }
    }

def get_field_type_mapping():
    """
    Get the mapping of DSL types to SQLAlchemy types.
    This could be loaded from a config file if needed.
    """
    return {
        'String': lambda length=255: f'db.String({length})',
        'Integer': lambda: 'db.Integer',
        'Float': lambda: 'db.Float',
        'DateTime': lambda: 'db.DateTime',
        'Boolean': lambda: 'db.Boolean',
        'Text': lambda: 'db.Text',  # For unlimited length strings
        'Date': lambda: 'db.Date',
        'Time': lambda: 'db.Time',
        'Decimal': lambda precision=10, scale=2: f'db.Decimal(precision={precision}, scale={scale})',
        'Int': lambda: 'db.Integer'  # Alias for Integer
    }

def get_required_imports():
    """
    Get the list of required imports for the models.
    This could be loaded from a config file if needed.
    """
    return [
        'from app import db',
        'from datetime import datetime, date, time',
        'from decimal import Decimal',
        'from sqlalchemy import Index',
        '',
        '# Auto-generated models using Flask-SQLAlchemy',
        ''
    ]

def get_table_name(model_name, config):
    """
    Generate table name based on configuration.
    """
    name = model_name
    if config['table_naming']['format'] == 'lower':
        name = name.lower()
    elif config['table_naming']['format'] == 'upper':
        name = name.upper()
    
    return f"{config['table_naming']['prefix']}{name}{config['table_naming']['suffix']}"

def get_constraint_str(constraint_name, config):
    """
    Get constraint string from configuration.
    """
    return config['column_constraints'].get(constraint_name, '')

def validate_dsl_file(file_path):
    """
    Validate DSL file and exit if validation fails.
    """
    try:
        with open(file_path, "r") as f:
            dsl_content = f.read()
        
        # Basic validation - check if it's a valid DSL file
        if not dsl_content.strip().startswith('table '):
            print("DSL validation failed: DSL file must start with table definitions")
            sys.exit(1)
        
        # Check for balanced braces
        if dsl_content.count('{') != dsl_content.count('}'):
            print("DSL validation failed: Unbalanced braces in DSL file")
            sys.exit(1)
        
        print("DSL validation passed successfully!")
        return True

    except Exception as e:
        print(f"DSL validation failed: {e}")
        sys.exit(1)

def clean_model_name(name):
    """
    Remove AXXX_ prefix from name (where A is any letter, XXX are digits).
    Returns the cleaned name in lowercase.
    Also handles special cases and compound words.
    """
    name = re.sub(r'^[A-Za-z]\d{3}_', '', name).lower()
    # Handle special cases
    name = name.replace('portpair', 'port_pair')
    name = name.replace('lineitem', 'line_item')
    name = name.replace('containerhistory', 'container_history')
    return name

def pluralize(name):
    """
    Handle special plural cases and general pluralization.
    """
    special_cases = {
        'history': 'histories',
        'country': 'countries',
        'commodity': 'commodities'
    }
    
    # Handle compound words (e.g., container_history)
    if '_' in name:
        base, last_part = name.rsplit('_', 1)
        if last_part in special_cases:
            return f"{base}_{special_cases[last_part]}"
        # Handle regular pluralization for compound words
        return f"{base}_{pluralize(last_part)}"
    
    # Check special cases
    if name in special_cases:
        return special_cases[name]
    
    # Standard rules
    if name.endswith('y') and not name.endswith(('ay', 'ey', 'oy', 'uy')):
        return name[:-1] + 'ies'
    if name.endswith('s'):
        return name
    return name + 's'

def get_collection_name(model_name, role=None):
    """
    Generate consistent collection names.
    model_name: The name of the model that owns the collection
    role: Optional role name for cases where multiple relationships exist to same target
    """
    base = clean_model_name(model_name)
    if role:
        # Handle special cases in role names
        role = clean_model_name(role)
        return f"{base}_as_{role}s"
    return pluralize(base)

def analyze_foreign_keys(json_data):
    """
    Analyze foreign key relationships to build a complete relationship map.
    Returns a dict mapping each model to its foreign key references.
    """
    relationships = {}
    
    # Initialize all models with empty relationships
    for model_name in json_data['Models'].keys():
        relationships[model_name] = {"relationships": {}}
    
    # First pass: Map all foreign keys by target to identify multiple references
    target_references = defaultdict(lambda: defaultdict(list))
    for model_name, model_data in json_data['Models'].items():
        for field_name, field_info in model_data['Fields'].items():
            if 'foreign_key' in field_info:
                target_model = field_info['relationship']['target_model']
                target_references[target_model][model_name].append({
                    'field_name': field_name,
                    'base_name': field_name.replace('_id', '')
                })
    
    # Second pass: Build relationship metadata
    for model_name, model_data in json_data['Models'].items():
        # Process foreign key fields
        for field_name, field_info in model_data['Fields'].items():
            if 'foreign_key' in field_info:
                target_model = field_info['relationship']['target_model']
                base_name = field_name.replace('_id', '')
                
                # Check if this target has multiple references from this model
                refs_from_model = target_references[target_model][model_name]
                has_multiple = len(refs_from_model) > 1
                
                # Determine collection name
                if has_multiple:
                    collection_name = get_collection_name(model_name, base_name)
                else:
                    collection_name = get_collection_name(model_name)
                
                # Add foreign key relationship
                relationships[model_name]['relationships'][base_name] = {
                    "type": "foreign_key",
                    "foreign_table": target_model,
                    "foreign_key": field_name,
                    "back_populates": collection_name
                }
                
                # Add corresponding collection to target
                relationships[target_model]['relationships'][collection_name] = {
                    "type": "one_to_many",
                    "foreign_table": model_name,
                    "foreign_key": field_name,
                    "back_populates": base_name
                }
        
        # Process explicit relationships
        for rel in model_data.get('Relationships', []):
            if rel['type'] == 'one-to-many':
                target_model = rel['target_model']
                clean_name = clean_model_name(rel['field_name'])
                
                # Find corresponding foreign key in target
                fk_field = None
                fk_name = None
                for t_rel_name, t_rel_info in relationships[target_model]['relationships'].items():
                    if (t_rel_info['type'] == 'foreign_key' and 
                        t_rel_info['foreign_table'] == model_name):
                        fk_field = t_rel_name
                        fk_name = t_rel_info['foreign_key']
                        break
                
                if fk_field and fk_name:
                    relationships[model_name]['relationships'][clean_name] = {
                        "type": "one_to_many",
                        "foreign_table": target_model,
                        "foreign_key": fk_name,
                        "back_populates": fk_field
                    }
    
    # Third pass: Verify and fix bidirectional relationships
    for model_name, model_info in relationships.items():
        for rel_name, rel_info in list(model_info['relationships'].items()):
            target = rel_info['foreign_table']
            
            # Ensure target has corresponding relationship
            if rel_info['type'] == 'foreign_key':
                collection_name = rel_info['back_populates']
                if collection_name not in relationships[target]['relationships']:
                    relationships[target]['relationships'][collection_name] = {
                        "type": "one_to_many",
                        "foreign_table": model_name,
                        "foreign_key": rel_info['foreign_key'],
                        "back_populates": rel_name
                    }
            elif rel_info['type'] == 'one_to_many':
                back_ref = rel_info['back_populates']
                if back_ref not in relationships[target]['relationships']:
                    relationships[target]['relationships'][back_ref] = {
                        "type": "foreign_key",
                        "foreign_table": model_name,
                        "foreign_key": rel_info['foreign_key'],
                        "back_populates": rel_name
                    }
    
    return relationships

def validate_relationship(model_name, field_name, target_model, json_data):
    """Validate that relationship is consistent between models."""
    if target_model not in json_data['Models']:
        raise ValueError(f"Invalid relationship target: {target_model} not found in models")
        
    # Get relationship type from model data
    relationship_type = None
    if model_name in json_data['Models']:
        model_data = json_data['Models'][model_name]
        for rel in model_data.get('Relationships', []):
            if rel['field_name'] == field_name:
                relationship_type = rel['type']
                break
                
    # Only validate foreign key for bidirectional relationships
    if relationship_type == 'many-to-one':
        # For many-to-one, the "many" side should have the foreign key
        source_fields = json_data['Models'][model_name]['Fields']
        has_source_fk = any(
            field_info.get('foreign_key', '').endswith(f'{target_model}.id') or
            field_info.get('foreign_key', '').endswith(f'{target_model.lower()}.id')
            for field_info in source_fields.values()
        )
        
        if not has_source_fk:
            raise ValueError(
                f"Missing foreign key in {model_name} for relationship with {target_model}"
            )

def generate_relationships(json_data):
    """
    Generate SQLAlchemy relationship definitions using analyzed foreign keys.
    """
    relationships_metadata = analyze_foreign_keys(json_data)
    relationships = {}
    
    print("\nProcessing relationships...")
    
    for model_name, model_info in relationships_metadata.items():
        model_relationships = []
        
        print(f"\nModel: {model_name}")
        
        for rel_name, rel_info in model_info['relationships'].items():
            if rel_info['type'] == 'foreign_key':
                relationship_str = (
                    f"    {rel_name} = db.relationship('{rel_info['foreign_table']}', "
                    f"foreign_keys=[{rel_info['foreign_key']}], "
                    f"back_populates='{rel_info['back_populates']}')"
                )
                model_relationships.append(relationship_str)
            elif rel_info['type'] == 'one_to_many':
                relationship_str = (
                    f"    {rel_name} = db.relationship('{rel_info['foreign_table']}', "
                    f"back_populates='{rel_info['back_populates']}', "
                    f"lazy='dynamic')"
                )
                model_relationships.append(relationship_str)
        
        if model_relationships:
            relationships[model_name] = model_relationships
    
    # Save relationship metadata for reference
    base_dir = Path(__file__).parent
    metadata_file = base_dir / 'output/relationships/relationship_metadata.json'
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_file, 'w') as f:
        json.dump(relationships_metadata, f, indent=2)
    print(f"\nRelationship metadata saved to: {metadata_file}")
    
    return relationships

def main():
    # Load configuration
    config = get_config()
    
    # Get paths relative to this script
    base_dir = Path(__file__).parent
    schema_file = base_dir / config['paths']['schema_dir'] / config['paths']['schema_file']
    json_file = base_dir / config['paths']['output_json_dir'] / config['paths']['output_json_file']
    models_file = base_dir / config['paths']['output_models_dir'] / config['paths']['output_models_file']
    # Print debug information about paths
    print(f"\nCurrent working directory: {os.getcwd()}")
    print(f"Base directory: {base_dir}")
    print(f"Config path: {config['paths']['flask_models_dir']}")
    
    # Calculate path relative to script location
    flask_models_file = (base_dir / config['paths']['flask_models_dir']).resolve() / config['paths']['flask_models_file']
    print(f"Resolved flask models path: {flask_models_file}")
    
    print("Starting DSL to SQLAlchemy model conversion process...")
    
    # Step 1: Validate DSL
    print("\n1. Validating DSL file...")
    if not schema_file.exists():
        print(f"Error: Schema file not found at {schema_file}")
        sys.exit(1)
    validate_dsl_file(schema_file)
    print("✓ DSL validation passed")
    
    # Step 2: Convert DSL to JSON
    print("\n2. Converting DSL to JSON...")
    convert_dsl_to_json(schema_file, json_file)
    print("✓ DSL converted to JSON")
    
    # Step 3: Load JSON data
    print("\n3. Loading JSON data...")
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    print("✓ JSON data loaded")
    
    # Step 4: Generate Flask-SQLAlchemy models
    print("\n4. Generating Flask-SQLAlchemy models...")
    content = '\n'.join(get_required_imports())
    
    # Get type mapping
    type_mapping = get_field_type_mapping()
    
    # Generate relationships from JSON data
    model_relationships = generate_relationships(json_data)
    
    # Generate Flask-SQLAlchemy models
    for model_name, model_data in json_data['Models'].items():
        table_name = get_table_name(model_name, config)
        class_lines = [f"class {model_name}(db.Model):", f"    __tablename__ = '{table_name}'"]
        
        # Add columns first
        for field_name, field_info in model_data['Fields'].items():
            field_args = []
            
            # Map field type using the type mapping
            field_type = field_info['type']
            if field_type in type_mapping:
                # Get field type specific parameters
                if field_type == 'String':
                    max_length = field_info.get('max_length', 255)
                    field_args.append(type_mapping[field_type](max_length))
                elif field_type == 'Decimal':
                    precision = field_info.get('precision', 10)
                    scale = field_info.get('scale', 2)
                    field_args.append(type_mapping[field_type](precision, scale))
                else:
                    field_args.append(type_mapping[field_type]())
            else:
                # Default to String if type not found
                field_args.append('db.String(255)')
            
            # Add constraints from config
            for constraint in ['primary_key', 'auto_increment', 'unique']:
                if field_info.get(constraint):
                    constraint_str = get_constraint_str(constraint, config)
                    if constraint_str:
                        field_args.append(constraint_str)
            
            # Special handling for nullable since it's inverted
            if not field_info.get('nullable', True):
                constraint_str = get_constraint_str('nullable', config)
                if constraint_str:
                    field_args.append(constraint_str)
            
            # Add foreign key if present
            if 'foreign_key' in field_info:
                field_args.append(f'db.ForeignKey("{field_info["foreign_key"]}")')
            
            field_def = f"    {field_name} = db.Column({', '.join(field_args)})"
            class_lines.append(field_def)
        
        # Add indices if present
        if 'Indices' in model_data:
            index_defs = []
            for index_name, index_columns in model_data['Indices'].items():
                # Make index name unique by using table name and index name
                unique_index_name = f"ix_{table_name}_{index_name[4:]}"  # Remove 'idx_' prefix
                
                # Create index definition with proper column references
                columns_str = ", ".join([f"'{col}'" for col in index_columns])
                index_defs.append((unique_index_name, columns_str))
            
            if index_defs:
                class_lines.append("")
                class_lines.append("    __table_args__ = (")
                for idx_name, cols in index_defs:
                    class_lines.append(f"        Index('{idx_name}', {cols}),")
                class_lines.append("    )")

        # Add relationships after columns and indices
        if model_name in model_relationships:
            class_lines.append("")  # Add spacing between columns and relationships
            class_lines.extend(model_relationships[model_name])
        
        class_lines.extend(["", "", ""])  # Add spacing between classes
        content += "\n".join(class_lines)
    
    # Ensure output directories exist
    flask_models_file.parent.mkdir(parents=True, exist_ok=True)
    models_file.parent.mkdir(parents=True, exist_ok=True)
    json_file.parent.mkdir(parents=True, exist_ok=True)

    # Write to both output and Flask app directories
    try:
        with open(models_file, 'w') as f:
            f.write(content)
        print(f"✓ Models written to {models_file}")
        
        try:
            with open(flask_models_file, 'w') as f:
                f.write(content)
            print(f"✓ Models written to {flask_models_file}")
        except Exception as e:
            print(f"Error writing to {flask_models_file}: {e}")
            print("Attempting to create directory and write again...")
            try:
                flask_models_file.parent.mkdir(parents=True, exist_ok=True)
                with open(flask_models_file, 'w') as f:
                    f.write(content)
                print(f"✓ Models successfully written to {flask_models_file} after creating directory")
            except Exception as e2:
                print(f"Fatal error writing to {flask_models_file}: {e2}")
                sys.exit(1)
    except Exception as e:
        print(f"Error writing to {models_file}: {e}")
        sys.exit(1)
    print("\nConversion process completed successfully!")
    print(f"\nGenerated files:")
    print(f"- JSON schema: {json_file}")
    print(f"- SQLAlchemy models: {models_file}")
    print(f"- Flask-SQLAlchemy models: {flask_models_file}")

if __name__ == '__main__':
    main()
