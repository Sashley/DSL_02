#!/usr/bin/env python3
"""
Main conversion script that orchestrates the DSL to SQLAlchemy model conversion process.
Uses existing conversion tools in their new locations.
"""
import os
import sys
import json
from pathlib import Path

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

def get_relationship_name(model_name, field_name):
    """Get the correct relationship name based on the model and field."""
    # Map of special relationship names that don't follow the standard pattern
    relationship_map = {
        'S001_Manifest': {
            'line_items': 'manifest',
            'shipper': 'manifests',
            'consignee': 'consigned_manifests',
            'vessel': 'manifests',
            'voyage': 'manifests',
            'port_of_loading': None,
            'port_of_discharge': None,
            'user': None
        },
        'S002_LineItem': {
            'manifest': 'line_items',
            'pack_type': 'line_items',
            'commodity': 'line_items',
            'container': 'line_items',
            'user': None
        },
        'S003_Commodity': {
            'line_items': 'commodity',
            'rates': 'commodity'
        },
        'S004_PackType': {
            'line_items': 'pack_type',
            'rates': 'pack_type'
        },
        'S005_Container': {
            'line_items': 'container',
            'container_histories': 'container',
            'port': 'containers'
        },
        'S006_ContainerHistory': {
            'container': 'container_histories',
            'port': None,
            'client': None,
            'container_status': 'container_histories'
        },
        'S007_ContainerStatus': {
            'container_histories': 'container_status'
        },
        'S008_ShippingCompany': {
            'vessels': 'shipping_company'
        },
        'S009_Vessel': {
            'manifests': 'vessel',
            'voyages': 'vessel',
            'shipping_company': 'vessels'
        },
        'S010_Voyage': {
            'legs': 'voyage',
            'manifests': 'voyage',
            'vessel': 'voyages'
        },
        'S011_Leg': {
            'voyage': 'legs',
            'port': 'legs'
        },
        'S012_Port': {
            'legs': 'port',
            'containers': 'port',
            'port_pairs_as_pol': 'pol',
            'port_pairs_as_pod': 'pod',
            'country': 'ports'
        },
        'S013_PortPair': {
            'pol': 'port_pairs_as_pol',
            'pod': 'port_pairs_as_pod'
        },
        'S014_Country': {
            'ports': 'country',
            'clients': 'country'
        },
        'S015_Client': {
            'manifests': 'shipper',
            'consigned_manifests': 'consignee',
            'rates': 'client',
            'country': 'clients'
        },
        'S016_User': {
            'manifests': None,
            'line_items': None
        },
        'S017_Rate': {
            'commodity': 'rates',
            'pack_type': 'rates',
            'client': 'rates'
        }
    }
    
    if model_name in relationship_map and field_name in relationship_map[model_name]:
        return relationship_map[model_name][field_name]
    
    # Default to the field name without _id suffix and model prefix
    field_name = field_name.replace('_id', '')
    if '_' in field_name:
        parts = field_name.split('_')
        if parts[0].startswith('s') and parts[0][1:].isdigit():
            field_name = '_'.join(parts[1:])
    return field_name

def generate_relationships(json_data):
    """
    Generate SQLAlchemy relationship definitions from JSON schema data.
    """
    relationships = {}
    
    for model_name, model_data in json_data['Models'].items():
        model_relationships = []
        
        # Handle explicit relationships first
        for rel in model_data.get('Relationships', []):
            # Skip if already handled by foreign key
            if any(r.startswith(f"    {rel['field_name']} = ") for r in model_relationships):
                continue
                
            relationship_str = f"    {rel['field_name']} = db.relationship('{rel['target_model']}'"
            
            # Add back_populates with the correct relationship name
            back_populates = get_relationship_name(model_name, rel['field_name'])
            if back_populates is None:
                relationship_str += ", back_populates=None"
            else:
                relationship_str += f", back_populates='{back_populates}'"
            
            # Add lazy loading for collections
            if rel['type'] == 'one-to-many':
                relationship_str += ", lazy='dynamic'"
                
            relationship_str += ")"
            model_relationships.append(relationship_str)
        
        # Handle foreign key relationships
        for field_name, field_info in model_data['Fields'].items():
            if 'relationship' in field_info:
                rel = field_info['relationship']
                # Create simple back_populates name based on the field
                relationship_str = f"    {rel['field_name']} = db.relationship('{rel['target_model']}'"
                
                # Add foreign keys if it's the same target model
                if 'foreign_key' in field_info:
                    relationship_str += f", foreign_keys=[{field_name}]"
                
                # Add back_populates with the correct relationship name
                back_populates = get_relationship_name(model_name, rel['field_name'])
                if back_populates is None:
                    relationship_str += ", back_populates=None)"
                else:
                    relationship_str += f", back_populates='{back_populates}')"
                model_relationships.append(relationship_str)
        
        if model_relationships:
            relationships[model_name] = model_relationships
            
    return relationships

def main():
    # Load configuration
    config = get_config()
    
    # Get paths relative to this script
    base_dir = Path(__file__).parent
    schema_file = base_dir / config['paths']['schema_dir'] / config['paths']['schema_file']
    json_file = base_dir / config['paths']['output_json_dir'] / config['paths']['output_json_file']
    models_file = base_dir / config['paths']['output_models_dir'] / config['paths']['output_models_file']
    flask_models_file = base_dir.parent / config['paths']['flask_models_dir'] / config['paths']['flask_models_file']
    
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
                for i, (idx_name, cols) in enumerate(index_defs):
                    if i < len(index_defs) - 1:
                        class_lines.append(f"        Index('{idx_name}', {cols}),")
                    else:
                        class_lines.append(f"        Index('{idx_name}', {cols})")
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
    with open(models_file, 'w') as f:
        f.write(content)
    
    with open(flask_models_file, 'w') as f:
        f.write(content)
    print("✓ Models generated and copied to Flask app")
    print("\nConversion process completed successfully!")
    print(f"\nGenerated files:")
    print(f"- JSON schema: {json_file}")
    print(f"- SQLAlchemy models: {models_file}")
    print(f"- Flask-SQLAlchemy models: {flask_models_file}")

if __name__ == '__main__':
    main()
