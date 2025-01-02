#!/usr/bin/env python
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

def import_module(path: Path, name: str):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    # Get module paths
    generator_dir = Path(__file__).parent
    crud_path = generator_dir / "crud.py"
    routes_path = generator_dir / "routes.py"
    relationships_path = generator_dir / "relationships.py"
    
    # Import modules directly
    crud_module = import_module(crud_path, "crud")
    routes_module = import_module(routes_path, "routes")
    relationships_module = import_module(relationships_path, "relationships")
    
    # Get paths relative to project root
    project_root = Path(__file__).parent.parent.parent.parent
    json_file = project_root / "dsl" / "output" / "json" / "shipping.json"
    templates_dir = project_root / "app" / "templates" / "crud"
    routes_dir = project_root / "app" / "routes" / "crud"
    relationships_dir = project_root / "app" / "utils" / "relationships"
    
    # Generate templates and routes
    print("Generating CRUD templates...")
    crud_module.generate_crud_templates(json_file, templates_dir)
    
    print("Generating CRUD routes...")
    routes_module.generate_crud_routes(json_file, routes_dir)
    
    print("Generating relationship helpers...")
    relationships_module.generate_relationship_helpers(json_file, relationships_dir)
    
    print("\nGeneration complete!")
    print(f"Templates generated in: {templates_dir}")
    print(f"Routes generated in: {routes_dir}")
    print(f"Relationship helpers generated in: {relationships_dir}")
    print("\nTo complete setup:")
    print("1. Register the CRUD blueprint in app/__init__.py:")
    print("   from app.routes.crud import bp as crud_bp")
    print("   app.register_blueprint(crud_bp)")
    print("\n2. Start the Flask development server:")
    print("   flask run")

if __name__ == "__main__":
    main()
