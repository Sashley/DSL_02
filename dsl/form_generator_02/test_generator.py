import json
import sys
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

# Import crud.py directly without going through app package
CRUD_PATH = Path(__file__).parent / "crud.py"
spec = spec_from_file_location("crud", CRUD_PATH)
crud_module = module_from_spec(spec)
spec.loader.exec_module(crud_module)
generate_crud_templates = crud_module.generate_crud_templates

def test_generate_crud_templates(tmp_path):
    """Test CRUD template generation with a sample schema"""
    # Sample JSON schema
    json_content = {
        "Models": {
            "Customer": {
                "Fields": {
                    "name": "string",
                    "email": "string",
                    "phone": "string"
                }
            }
        }
    }
    
    # Create test JSON file
    json_file = tmp_path / "test_schema.json"
    json_file.write_text(json.dumps(json_content))
    
    # Generate templates
    output_dir = tmp_path / "templates"
    generate_crud_templates(json_file, output_dir)
    
    # Verify files were created
    customer_dir = output_dir / "customer"
    assert customer_dir.exists()
    assert (customer_dir / "list.html").exists()
    assert (customer_dir / "_row.html").exists()
    assert (customer_dir / "form.html").exists()

    # Verify template content
    list_html = (customer_dir / "list.html").read_text()
    assert "Customer List" in list_html
    assert 'hx-target="closest tr"' in list_html
    assert "name" in list_html
    assert "email" in list_html
    assert "phone" in list_html

    row_html = (customer_dir / "_row.html").read_text()
    assert "hx-delete" in row_html
    assert "hx-get" in row_html
    assert "item.name" in row_html
    assert "item.email" in row_html
    assert "item.phone" in row_html

    form_html = (customer_dir / "form.html").read_text()
    assert "hx-post" in form_html
    assert "hx-target" in form_html
    assert 'id="name"' in form_html
    assert 'id="email"' in form_html
    assert 'id="phone"' in form_html

if __name__ == "__main__":
    import tempfile
    from pathlib import Path
    
    # Manual test
    with tempfile.TemporaryDirectory() as tmpdir:
        test_generate_crud_templates(Path(tmpdir))
        print("Test completed successfully!")
