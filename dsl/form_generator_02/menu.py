from pathlib import Path
import json
from typing import Dict, Any, List

def generate_menu_template(json_file: str | Path, output_dir: str | Path) -> None:
    """Generate menu templates from JSON schema file."""
    json_path = Path(json_file)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(json_path, "r") as f:
        data = json.load(f)
    
    # Group models by category
    categories = {
        "Operations": ["Manifest", "LineItem", "Container", "ContainerHistory"],
        "Planning": ["Voyage", "Vessel", "Port", "PortPair", "Leg"],
        "Business": ["Client", "ShippingCompany", "Rate"],
        "Reference": ["Commodity", "PackType", "ContainerStatus", "Country"],
        "System": ["User"]
    }
    
    # Generate menu template
    menu_template = """{% macro render_menu() %}
    <nav class="bg-white shadow">
        <div class="container mx-auto px-4">
            <div class="flex justify-between items-center h-16">
                <div class="flex items-center space-x-8">
                    <a href="/" class="text-blue-600 font-bold text-xl">Shipping App</a>
                    <a href="/" class="text-gray-700 hover:text-gray-900">Home</a>
                    <div class="relative" x-data="{ open: false }">
                        <button @click="open = !open" class="text-gray-700 hover:text-gray-900 group inline-flex items-center space-x-2">
                            <span>Data Management</span>
                            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                            </svg>
                        </button>
                        <div x-show="open" @click.away="open = false" class="absolute z-10 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5">
                            <div class="py-1">
"""
    
    # Add menu items by category
    for category, models in categories.items():
        if any(model in data["Models"] for model in models):
            menu_template += f"""                                <!-- {category} -->
                                <div class="px-3 py-2 text-xs font-semibold text-gray-500">{category}</div>
"""
            for model in models:
                if model in data["Models"]:
                    route_name = model.lower()
                    menu_template += f"""                                <a href="{{{{ url_for('crud.{route_name}.list_{route_name}') }}}}" 
                                   class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">{model}s</a>
"""
            menu_template += "\n"
    
    menu_template += """                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </nav>
{% endmacro %}"""
    
    # Write menu template
    menu_file = output_path / "menu.html"
    menu_file.write_text(menu_template)
    
    # Generate menu include for base template
    base_menu_include = """{% from 'menu.html' import render_menu %}
{{ render_menu() }}"""
    
    # Write menu include
    menu_include_file = output_path / "menu_include.html"
    menu_include_file.write_text(base_menu_include)
    
    print(f"Menu templates generated in {output_dir}")

if __name__ == "__main__":
    # Example usage
    generate_menu_template("dsl/output/json/shipping.json", "app/templates/components")
