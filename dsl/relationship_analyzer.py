#!/usr/bin/env python3
"""
Analyzes and extracts relationship metadata from DSL-generated JSON data.
Creates a reviewable relationship mapping file.
"""
import json
import re
from pathlib import Path
from collections import defaultdict

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

def extract_relationship_metadata(json_data):
    """
    Extracts relationship metadata from the JSON model definitions.
    Returns a dictionary mapping each table to its relationships.
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

def save_relationship_metadata(relationships, output_path):
    """
    Saves relationship metadata to a JSON file for review.
    """
    # Ensure the output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save with nice formatting for readability
    with open(output_path, 'w') as f:
        json.dump(relationships, f, indent=2)
    
    print(f"Relationship metadata saved to: {output_path}")

def analyze_relationships(json_file_path, output_path):
    """
    Main function to analyze relationships from JSON data and save metadata.
    """
    # Load JSON data
    with open(json_file_path, 'r') as f:
        json_data = json.load(f)
    
    # Extract relationship metadata
    relationships = extract_relationship_metadata(json_data)
    
    # Save for review
    save_relationship_metadata(relationships, output_path)
    
    return relationships

if __name__ == '__main__':
    # Get paths relative to this script
    base_dir = Path(__file__).parent
    json_file = base_dir / 'output/json/shipping.json'
    output_file = base_dir / 'output/relationships/relationship_metadata.json'
    
    # Analyze and save relationships
    analyze_relationships(json_file, output_file)
