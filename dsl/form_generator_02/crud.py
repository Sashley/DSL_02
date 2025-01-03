from pathlib import Path
import json
from typing import Dict, Any, List, Tuple

def get_display_fields(fields: Dict[str, Any], max_fields: int = 5) -> List[str]:
    """Get the first N fields excluding id for display in list view."""
    all_fields = list(fields.keys())
    # Remove 'id' if it's present
    if 'id' in all_fields:
        all_fields.remove('id')
    return all_fields[:max_fields]

def get_input_type(field_name: str, field_data: Dict[str, Any]) -> str:
    """Determine the appropriate HTML input type for a field."""
    field_type = field_data.get("type", "String")
    
    if field_type == "DateTime":
        return "datetime-local"
    elif field_type == "Integer" and not field_data.get("foreign_key"):
        return "number"
    elif field_type == "Float":
        return "number"
    elif field_type == "String" and field_name == "email":
        return "email"
    elif field_type == "String" and "password" in field_name.lower():
        return "password"
    return "text"

def should_include_field(field_name: str, field_data: Dict[str, Any]) -> bool:
    """Determine if a field should be included in the form."""
    # Exclude auto-generated fields
    if field_name == "id":
        return False
    if field_data.get("primary_key", False):
        return False
    if field_data.get("auto_increment", False):
        return False
    
    return True

def get_relationship_fields(fields: Dict[str, Any]) -> List[Tuple[str, str, str]]:
    """Get fields that represent relationships."""
    relationship_fields = []
    for field_name, field_data in fields.items():
        if "relationship" in field_data:
            rel = field_data["relationship"]
            # Handle special cases for shared target models
            if rel["target_model"] == "S015_Client":
                plural_name = "clients"  # Both shipper and consignee use clients
            elif rel["target_model"] == "S012_Port":
                plural_name = "ports"    # Both port_of_loading and port_of_discharge use ports
            else:
                # Use target model name for template variable
                # e.g. S009_Vessel -> vessels
                plural_name = rel["target_model"].split('_')[1].lower() + 's'
            relationship_fields.append((field_name, plural_name, rel["target_model"]))
    return relationship_fields

def generate_form_fields(fields: Dict[str, Any], relationship_fields: List[Tuple[str, str, str]]) -> str:
    """Generate the form fields HTML."""
    fields_html = []
    for field_name, field_data in fields.items():
        # Skip excluded fields
        if not should_include_field(field_name, field_data):
            continue
            
        is_relationship = any(field_name == rel[0] for rel in relationship_fields)
        input_type = get_input_type(field_name, field_data)
        
        if is_relationship:
            rel_name = next(rel[1] for rel in relationship_fields if field_name == rel[0])
            # Remove _id from field name for display
            display_name = field_name[:-3] if field_name.endswith('_id') else field_name
            field_html = f"""
            <div class="flex flex-col">
                <label for="{field_name}" class="text-sm font-semibold text-gray-600 mb-1">{display_name.title().replace('_', ' ')}</label>
                <select id="{field_name}" 
                        name="{field_name}"
                        class="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option value="">Select...</option>
                    {{% for related in {rel_name} %}}
                    <option value="{{{{ related.id }}}}" {{{{ 'selected' if edit and item.{field_name} == related.id else '' }}}}>
                        {{{{ related.name if hasattr(related, 'name') else related.id }}}}
                    </option>
                    {{% endfor %}}
                </select>
            </div>"""
        else:
            field_html = f"""
            <div class="flex flex-col">
                <label for="{field_name}" class="text-sm font-semibold text-gray-600 mb-1">{field_name.title().replace('_', ' ')}</label>
                <input type="{input_type}" 
                       id="{field_name}" 
                       name="{field_name}"
                       class="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                       value="{{{{ item.{field_name} if edit else '' }}}}">
            </div>"""
        fields_html.append(field_html)
    return ''.join(fields_html)

def generate_crud_templates(json_file: str | Path, output_dir: str | Path) -> None:
    """Generate CRUD templates from a JSON schema file."""
    json_path = Path(json_file)
    output_path = Path(output_dir)
    
    with open(json_path, "r") as f:
        data = json.load(f)
    
    models = data["Models"]
    for model_name, model_data in models.items():
        table_name = model_name.lower()
        fields = model_data["Fields"]
        display_fields = get_display_fields(fields)
        relationship_fields = get_relationship_fields(fields)

        # Create output directory for the model
        model_dir = output_path / table_name
        model_dir.mkdir(parents=True, exist_ok=True)

        # Generate List Template
        list_template = model_dir / "list.html"
        list_template.write_text(f"""\
{{% extends "base.html" %}}

{{% block content %}}
<div class="container mx-auto px-4 py-8">
    <div class="flex flex-col space-y-4">
        <div class="flex justify-between items-center">
            <h1 class="text-2xl font-bold">{model_name} List</h1>
            <a href="{{{{ url_for('crud.{table_name}.create_{table_name}') }}}}" 
               class="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-2 px-4 rounded">
                Add New {model_name}
            </a>
        </div>

        <!-- Search -->
        <div class="w-1/3">
            <input type="text"
                   class="w-full px-3 py-2 border rounded-lg"
                   placeholder="Search..."
                   hx-trigger="keyup changed delay:500ms"
                   hx-get="{{{{ url_for('crud.{table_name}.list_{table_name}') }}}}"
                   hx-target="#{table_name}-list"
                   name="search">
        </div>

        <!-- Table Container -->
        <div class="border rounded-lg overflow-hidden">
            <div class="overflow-y-auto" style="max-height: 600px;">
                <table class="min-w-full bg-white">
                    <thead class="bg-gray-100 sticky top-0 z-10">
                        <tr>
                            {''.join(f'<th class="px-4 py-2 text-left text-sm font-bold text-gray-700 border-b">{field.replace("_", " ").title()}</th>' for field in display_fields)}
                            <th class="px-4 py-2 text-left text-sm font-bold text-gray-700 border-b">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="{table_name}-list">
                        {{% include 'crud/{table_name}/_rows.html' %}}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Table Controls -->
        <div class="flex justify-between items-center mt-4">
            <div class="flex items-center space-x-2">
                <label class="text-sm text-gray-600">Records per page:</label>
                <select class="border rounded px-2 py-1"
                        hx-get="{{{{ url_for('crud.{table_name}.list_{table_name}') }}}}"
                        hx-target="#{table_name}-list"
                        name="per_page">
                    <option value="3">3</option>
                    <option value="5">5</option>
                    <option value="10" selected>10</option>
                    <option value="20">20</option>
                    <option value="50">50</option>
                </select>
            </div>
            {{% if has_more %}}
            <button hx-get="{{{{ url_for('crud.{table_name}.list_{table_name}', page=page+1) }}}}"
                    hx-target="#{table_name}-list"
                    hx-swap="beforeend"
                    class="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-2 px-4 rounded">
                Load More
            </button>
            {{% endif %}}
        </div>
    </div>
</div>
{{% endblock %}}""")

        # Generate Rows Template
        rows_template = model_dir / "_rows.html"
        rows_template.write_text(f"""\
{{% for item in items %}}
{{% include 'crud/{table_name}/_row.html' %}}
{{% endfor %}}""")

        # Generate Row Template
        row_template = model_dir / "_row.html"
        row_template.write_text(f"""\
<tr class="hover:bg-gray-50 group">
    {''.join(f'''<td class="px-4 py-1 whitespace-nowrap border-b text-sm">
        {{{{ item.{field}_name if '{field}' in item.__dict__ and '{field}'.endswith('_id') else item.{field} }}}}
    </td>''' for field in display_fields)}
    <td class="px-4 py-1 whitespace-nowrap border-b text-sm">
        <div class="invisible group-hover:visible flex justify-end space-x-2">
            <a href="{{{{ url_for('crud.{table_name}.edit_{table_name}', id=item.id) }}}}"
               class="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-1 px-2 rounded text-sm">
                Edit
            </a>
            <button hx-delete="{{{{ url_for('crud.{table_name}.delete_{table_name}', id=item.id) }}}}"
                    hx-confirm="Are you sure you want to delete this {model_name}?"
                    hx-target="closest tr"
                    class="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-1 px-2 rounded text-sm">
                Delete
            </button>
        </div>
    </td>
</tr>""")

        # Generate Form Template
        form_template = model_dir / "form.html"
        form_template.write_text(f"""\
{{% extends "base.html" %}}

{{% block content %}}
<div class="container mx-auto px-4 py-8">
    <div class="max-w-2xl mx-auto">
        <h1 class="text-2xl font-bold mb-6">{{{{ 'Edit ' if edit else 'Add New ' }}}}{model_name}</h1>

        <form hx-post="{{{{ form_action }}}}" 
              hx-target="#main-content"
              hx-swap="outerHTML"
              class="space-y-6">
            {generate_form_fields(fields, relationship_fields)}
            
            <div class="flex justify-end space-x-4 mt-8">
                <a href="{{{{ url_for('crud.{table_name}.list_{table_name}') }}}}" 
                   class="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-2 px-4 rounded">
                    Cancel
                </a>
                <button type="submit" 
                        class="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-2 px-4 rounded">
                    {{{{ 'Update' if edit else 'Create' }}}}
                </button>
            </div>
        </form>
    </div>
</div>
{{% endblock %}}""")

    print(f"CRUD templates generated in {output_dir}")

if __name__ == "__main__":
    # Example usage
    generate_crud_templates("dsl/output/json/shipping.json", "app/templates")
