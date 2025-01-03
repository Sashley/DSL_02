from pathlib import Path
import json
from typing import Dict, Any
from sqlalchemy import or_, func

def get_model_relationships(model_data: Dict[str, Any]) -> list:
    """Extract relationship information from model data."""
    relationships = []
    
    # Get relationships from foreign keys
    for field_name, field_data in model_data["Fields"].items():
        if "relationship" in field_data:
            rel = field_data["relationship"]
            relationships.append({
                "field_name": field_name,
                "target_model": rel["target_model"],
                "relationship_field": rel["field_name"]
            })
    
    return relationships

def generate_crud_routes(json_file: str | Path, output_dir: str | Path) -> None:
    """Generate CRUD routes from a JSON schema file."""
    json_path = Path(json_file)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(json_path, "r") as f:
        data = json.load(f)
    
    # Generate routes for each model
    models = data["Models"]
    for model_name, model_data in models.items():
        table_name = model_name.lower()
        fields = model_data["Fields"]
        display_fields = list(fields.keys())[:5]  # First 5 fields for list view
        
        route_file = output_path / f"{table_name}.py"
        
        # Check if this is a complex model that needs relationship helpers
        is_complex = model_name in ['S001_Manifest', 'S002_LineItem']
        
        # Get relationships and build imports
        relationships = get_model_relationships(model_data)
        related_models = {rel["target_model"] for rel in relationships}
        # Build imports with proper comma handling
        model_imports = f"{model_name}"
        if related_models:
            model_imports += f", {', '.join(related_models)}"
            
        imports = f"""from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from app.models.shipping import {model_imports}
from app import db
from sqlalchemy import or_, func"""
        
        if is_complex:
            imports += f"""
from app.utils.relationships import get_related_data, create_{table_name}, update_{table_name}, delete_{table_name}"""
        
        # Route content
        route_content = f"""{imports}

bp = Blueprint('{table_name}', __name__)

# Define relationships for this model
relationships = {relationships}

def get_search_filter(model, search_term):
    '''Return case-insensitive search filter for the model.'''
    if not search_term:
        return None
    
    # Convert search term to lowercase for case-insensitive search
    search_term = search_term.lower()
    
    conditions = []
    
    # Search in text fields
    text_fields = {repr(display_fields)}
    for field in text_fields:
        if hasattr(model, field):
            if field.endswith('_id'):
                # Get relationship info for this field
                rel = next((r for r in relationships if r["field_name"] == field), None)
                if rel:
                    # Add condition for relationship search
                    conditions.append(
                        getattr(model, rel["relationship_field"]).has(
                            func.lower(getattr(globals()[rel["target_model"]], 'name')).like(f'%{{{{search_term}}}}%')
                        )
                    )
            else:
                # Handle regular fields
                conditions.append(func.lower(getattr(model, field)).like(f'%{{{{search_term}}}}%'))
    
    return or_(*conditions) if conditions else None

@bp.route('/')
def list_{table_name}():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # Build query with eager loading of relationships
    query = {model_name}.query
    if relationships:  # Only add joinedload if there are relationships
        query = query.options(*[
            db.joinedload(getattr({model_name}, rel["relationship_field"]))
            for rel in relationships
        ])
    
    # Apply search filter if provided
    search_filter = get_search_filter({model_name}, search)
    if search_filter is not None:
        query = query.filter(search_filter)
    
    # Get paginated results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    # If this is an HTMX request, return only the rows
    if request.headers.get('HX-Request'):
        return render_template('crud/{table_name}/_rows.html', 
                            items=items,
                            has_more=pagination.has_next,
                            page=page)
    
    # For full page request, return complete template
    return render_template('crud/{table_name}/list.html', 
                         items=items,
                         has_more=pagination.has_next,
                         page=page,
                         per_page=per_page)

@bp.route('/create', methods=['GET', 'POST'])
def create_{table_name}():
    if request.method == 'POST':
        try:
            {f'''success, item = create_{table_name}(request.form)
            if success:
                return redirect(url_for("crud.{table_name}.list_{table_name}"))''' if is_complex else f'''item = {model_name}()
            {"".join(f"""
            if '{field}' in request.form:
                item.{field} = request.form['{field}']""" for field in fields.keys() if field != 'id')}
            db.session.add(item)
            db.session.commit()
            flash('Created successfully', 'success')
            return redirect(url_for("crud.{table_name}.list_{table_name}"))'''} 
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {{str(e)}}', 'error')
            return render_template('crud/{table_name}/form.html', 
                                edit=False, 
                                form_action=url_for('crud.{table_name}.create_{table_name}')
                                {', **get_related_data()' if is_complex else ''})
    
    return render_template('crud/{table_name}/form.html', 
                         edit=False, 
                         form_action=url_for('crud.{table_name}.create_{table_name}')
                         {', **get_related_data()' if is_complex else ''})

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_{table_name}(id):
    item = {model_name}.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            {f'''if update_{table_name}(item, request.form):
                return redirect(url_for("crud.{table_name}.list_{table_name}"))''' if is_complex else f'''{"".join(f"""
            if '{field}' in request.form:
                item.{field} = request.form['{field}']""" for field in fields.keys() if field != 'id')}
            db.session.commit()
            flash('Updated successfully', 'success')
            return redirect(url_for("crud.{table_name}.list_{table_name}"))'''}
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {{str(e)}}', 'error')
            return render_template('crud/{table_name}/form.html', 
                                edit=True, 
                                item=item,
                                form_action=url_for('crud.{table_name}.edit_{table_name}', id=id)
                                {', **get_related_data()' if is_complex else ''})
    
    return render_template('crud/{table_name}/form.html', 
                         edit=True, 
                         item=item,
                         form_action=url_for('crud.{table_name}.edit_{table_name}', id=id)
                         {', **get_related_data()' if is_complex else ''})

@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_{table_name}(id):
    try:
        item = {model_name}.query.get_or_404(id)
        {f'success = delete_{table_name}(item)' if is_complex else 'db.session.delete(item)\n        db.session.commit()\n        success = True'}
        return '', 204 if success else 500
    except Exception as e:
        db.session.rollback()
        return str(e), 500
"""
        route_file.write_text(route_content)
    
    # Generate routes/__init__.py to register all blueprints
    init_file = output_path / "__init__.py"
    init_content = """from flask import Blueprint

bp = Blueprint('crud', __name__)

"""
    
    # Import and register each model's blueprint
    for model_name in models.keys():
        table_name = model_name.lower()
        init_content += f"""from app.routes.crud import {table_name}
bp.register_blueprint({table_name}.bp, url_prefix='/{table_name}')

"""
    
    init_file.write_text(init_content)
    
    print(f"CRUD routes generated in {output_dir}")

if __name__ == "__main__":
    # Example usage
    generate_crud_routes("dsl/output/json/shipping.json", "app/routes/crud")
