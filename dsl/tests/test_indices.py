import pytest
from sqlalchemy import inspect
from pathlib import Path
import json
import importlib.util

def load_json_schema():
    """Load the shipping.json schema file"""
    json_path = Path(__file__).parent.parent / 'output' / 'json' / 'shipping.json'
    with open(json_path) as f:
        return json.load(f)

def load_models():
    """Dynamically load the generated models module"""
    models_path = Path(__file__).parent.parent / 'output' / 'models' / 'shipping.py'
    spec = importlib.util.spec_from_file_location("shipping_models", models_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_indices_match_schema():
    """Test that all indices defined in the schema are present in the models"""
    schema = load_json_schema()
    models = load_models()
    
    for model_name, model_data in schema['Models'].items():
        # Skip if model has no indices defined
        if 'Indices' not in model_data:
            continue
            
        # Get the model class
        model_class = getattr(models, model_name)
        
        # Get the table args
        table_args = getattr(model_class, '__table_args__', None)
        assert table_args is not None, f"Model {model_name} should have __table_args__ defined"
        
        # Convert table_args to list if it's not already
        indices = [arg for arg in table_args if isinstance(arg, inspect(model_class).db.Index)]
        
        # Check that all schema indices are present in the model
        for index_name, columns in model_data['Indices'].items():
            # Find matching index in model
            model_index = next((idx for idx in indices if idx.name == index_name), None)
            assert model_index is not None, f"Index {index_name} not found in model {model_name}"
            
            # Check columns match
            index_columns = [col.name for col in model_index.columns]
            assert sorted(index_columns) == sorted(columns), \
                f"Columns don't match for index {index_name} in {model_name}"

def test_index_names_are_unique():
    """Test that index names are unique across all models"""
    schema = load_json_schema()
    
    # Collect all index names
    index_names = []
    for model_data in schema['Models'].values():
        if 'Indices' in model_data:
            index_names.extend(model_data['Indices'].keys())
    
    # Check for duplicates
    assert len(index_names) == len(set(index_names)), \
        "Found duplicate index names across models"

def test_foreign_key_indices():
    """Test that all foreign key fields have corresponding indices"""
    schema = load_json_schema()
    
    for model_name, model_data in schema['Models'].items():
        # Get all foreign key fields
        fk_fields = [
            field_name for field_name, field_data in model_data['Fields'].items()
            if 'foreign_key' in field_data
        ]
        
        # Get all indexed fields
        indexed_fields = []
        if 'Indices' in model_data:
            for columns in model_data['Indices'].values():
                indexed_fields.extend(columns)
        
        # Check that each foreign key has an index
        for fk_field in fk_fields:
            assert fk_field in indexed_fields, \
                f"Foreign key {fk_field} in {model_name} should have an index"

def test_index_column_references():
    """Test that index column references are valid"""
    schema = load_json_schema()
    models = load_models()
    
    for model_name, model_data in schema['Models'].items():
        if 'Indices' not in model_data:
            continue
            
        model_class = getattr(models, model_name)
        model_columns = {col.name: col for col in inspect(model_class).columns}
        
        for index_name, columns in model_data['Indices'].items():
            for col_name in columns:
                assert col_name in model_columns, \
                    f"Index {index_name} references non-existent column {col_name} in {model_name}"
