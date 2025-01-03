from pathlib import Path
import json
from typing import Dict, Any

def generate_relationship_helpers(json_file: str | Path, output_dir: str | Path) -> None:
    """Generate helper functions for handling complex model relationships.
    
    Args:
        json_file: Path to the JSON schema file
        output_dir: Directory where helper files will be generated
    """
    json_path = Path(json_file)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(json_path, "r") as f:
        data = json.load(f)
    
    # Generate helpers for complex models
    complex_models = {
        'S001_Manifest': {
            'relationships': [
                ('shipper', 'S015_Client'),
                ('consignee', 'S015_Client'),
                ('vessel', 'S009_Vessel'),
                ('voyage', 'S010_Voyage'),
                ('port_of_loading', 'S012_Port'),
                ('port_of_discharge', 'S012_Port')
            ]
        },
        'S002_LineItem': {
            'relationships': [
                ('pack_type', 'S004_PackType'),
                ('commodity', 'S003_Commodity'),
                ('container', 'S005_Container'),
                ('manifest', 'S001_Manifest')
            ]
        }
    }
    
    for model_name, config in complex_models.items():
        helper_file = output_path / f"{model_name.lower()}_helpers.py"
        helper_content = f"""from flask import flash
from app.models.shipping import {model_name}, {', '.join(rel[1] for rel in config['relationships'])}
from app import db

def get_related_data():
    \"\"\"Get all related data needed for {model_name} forms.\"\"\"
    return {{
        {''.join(f"""
        '{rel[0]}s': {rel[1]}.query.all(),""" for rel in config['relationships'])}
    }}

def create_{model_name.lower()}(form_data):
    \"\"\"Create a new {model_name} with related data.\"\"\"
    try:
        item = {model_name}()
        {''.join(f"""
        if '{rel[0]}_id' in form_data:
            item.{rel[0]}_id = form_data['{rel[0]}_id']""" for rel in config['relationships'])}
        
        # Set other fields
        for field, value in form_data.items():
            if not field.endswith('_id') and hasattr(item, field):
                setattr(item, field, value)
        
        db.session.add(item)
        db.session.commit()
        flash('Created successfully', 'success')
        return True, item
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {{str(e)}}', 'error')
        return False, None

def update_{model_name.lower()}(item, form_data):
    \"\"\"Update an existing {model_name} with related data.\"\"\"
    try:
        {''.join(f"""
        if '{rel[0]}_id' in form_data:
            item.{rel[0]}_id = form_data['{rel[0]}_id']""" for rel in config['relationships'])}
        
        # Update other fields
        for field, value in form_data.items():
            if not field.endswith('_id') and hasattr(item, field):
                setattr(item, field, value)
        
        db.session.commit()
        flash('Updated successfully', 'success')
        return True
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {{str(e)}}', 'error')
        return False

def delete_{model_name.lower()}(item):
    \"\"\"Delete a {model_name} and handle relationships.\"\"\"
    try:
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {{str(e)}}', 'error')
        return False
"""
        helper_file.write_text(helper_content)
    
    # Generate __init__.py to make the package importable
    init_file = output_path / "__init__.py"
    init_content = ""
    for model_name in complex_models.keys():
        module_name = f"{model_name.lower()}_helpers"
        init_content += f"from .{module_name} import *\n"
    
    init_file.write_text(init_content)
    
    print(f"Relationship helpers generated in {output_dir}")

if __name__ == "__main__":
    # Example usage
    generate_relationship_helpers("dsl/output/json/shipping.json", "app/utils/relationships")
