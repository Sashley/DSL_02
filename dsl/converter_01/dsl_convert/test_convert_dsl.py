import os
import pytest
import json
from sqlalchemy import inspect

def test_dsl_conversion(tmp_path):
    """Test the DSL conversion process"""
    # Get directory of current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Run the conversion script
    os.system(f"python {os.path.join(current_dir, 'convert_dsl.py')}")
    
    # Check output files exist
    json_file = os.path.join(current_dir, "shipping_converted.json")
    models_file = os.path.join(current_dir, "models_converted.py")
    
    assert os.path.exists(json_file), "JSON file not created"
    assert os.path.exists(models_file), "Models file not created"
    
    # Verify JSON structure
    with open(json_file) as f:
        json_data = json.load(f)
        assert "Models" in json_data, "JSON missing Models section"
        assert "version" in json_data, "JSON missing version"
        
        # Check a few key models exist
        models = json_data["Models"]
        assert "S001_Manifest" in models
        assert "S002_LineItem" in models
        assert "S003_Commodity" in models
    
    # Import generated models
    import importlib.util
    spec = importlib.util.spec_from_file_location("models_converted", models_file)
    models_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models_module)
    
    # Test model structure
    def verify_model(model_class, expected_columns):
        """Helper to verify model has expected columns"""
        mapper = inspect(model_class)
        actual_columns = [c.key for c in mapper.columns]
        for col in expected_columns:
            assert col in actual_columns, f"Column {col} missing from {model_class.__name__}"
    
    # Verify a few key models
    verify_model(models_module.S001_Manifest, [
        'id', 'bill_of_lading', 'shipper_id', 'consignee_id',
        'vessel_id', 'voyage_id', 'port_of_loading_id', 
        'port_of_discharge_id', 'place_of_delivery', 'place_of_receipt',
        'clauses', 'date_of_receipt'
    ])
    
    verify_model(models_module.S002_LineItem, [
        'id', 'manifest_id', 'description', 'quantity',
        'weight', 'volume', 'pack_type_id', 'commodity_id',
        'container_id'
    ])
    
    verify_model(models_module.S003_Commodity, [
        'id', 'name', 'description'
    ])

def test_model_relationships():
    """Test relationships are properly generated"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Run conversion
    os.system(f"python {os.path.join(current_dir, 'convert_dsl.py')}")
    
    # Import generated models
    models_file = os.path.join(current_dir, "models_converted.py")
    import importlib.util
    spec = importlib.util.spec_from_file_location("models_converted", models_file)
    models_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models_module)
    
    # Verify relationships
    manifest = models_module.S001_Manifest
    assert hasattr(manifest, 'shipper_id_rel'), "Missing shipper relationship"
    assert hasattr(manifest, 'consignee_id_rel'), "Missing consignee relationship"
    assert hasattr(manifest, 'vessel_id_rel'), "Missing vessel relationship"

def test_invalid_dsl(tmp_path):
    """Test handling of invalid DSL file"""
    # Create invalid DSL file
    invalid_dsl = tmp_path / "invalid.dsl"
    invalid_dsl.write_text("invalid content")
    
    # Run conversion with invalid file
    result = os.system(f"python convert_dsl.py {invalid_dsl}")
    assert result != 0, "Should fail with invalid DSL"
