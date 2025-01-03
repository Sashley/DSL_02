from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from app.models.shipping import S002_LineItem, S005_Container, S016_User, S003_Commodity, S004_PackType, S001_Manifest
from app import db
from sqlalchemy import or_, func
from app.utils.relationships import get_related_data, create_s002_lineitem, update_s002_lineitem, delete_s002_lineitem

bp = Blueprint('s002_lineitem', __name__)

# Define relationships for this model
relationships = [{'field_name': 'manifest_id', 'target_model': 'S001_Manifest', 'relationship_field': 'manifest'}, {'field_name': 'pack_type_id', 'target_model': 'S004_PackType', 'relationship_field': 'pack_type'}, {'field_name': 'commodity_id', 'target_model': 'S003_Commodity', 'relationship_field': 'commodity'}, {'field_name': 'container_id', 'target_model': 'S005_Container', 'relationship_field': 'container'}, {'field_name': 'user_id', 'target_model': 'S016_User', 'relationship_field': 'user'}]

def get_search_filter(model, search_term):
    '''Return case-insensitive search filter for the model.'''
    if not search_term:
        return None
    
    # Convert search term to lowercase for case-insensitive search
    search_term = search_term.lower()
    
    conditions = []
    
    # Search in text fields
    text_fields = ['id', 'manifest_id', 'description', 'quantity', 'weight']
    for field in text_fields:
        if hasattr(model, field):
            if field.endswith('_id'):
                # Get relationship info for this field
                rel = next((r for r in relationships if r["field_name"] == field), None)
                if rel:
                    # Add condition for relationship search
                    conditions.append(
                        getattr(model, rel["relationship_field"]).has(
                            func.lower(getattr(globals()[rel["target_model"]], 'name')).like(f'%{{search_term}}%')
                        )
                    )
            else:
                # Handle regular fields
                conditions.append(func.lower(getattr(model, field)).like(f'%{{search_term}}%'))
    
    return or_(*conditions) if conditions else None

@bp.route('/')
def list_s002_lineitem():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # Build query with eager loading of relationships
    query = S002_LineItem.query
    if relationships:  # Only add joinedload if there are relationships
        query = query.options(*[
            db.joinedload(getattr(S002_LineItem, rel["relationship_field"]))
            for rel in relationships
        ])
    
    # Apply search filter if provided
    search_filter = get_search_filter(S002_LineItem, search)
    if search_filter is not None:
        query = query.filter(search_filter)
    
    # Get paginated results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    # If this is an HTMX request, return only the rows
    if request.headers.get('HX-Request'):
        return render_template('crud/s002_lineitem/_rows.html', 
                            items=items,
                            has_more=pagination.has_next,
                            page=page)
    
    # For full page request, return complete template
    return render_template('crud/s002_lineitem/list.html', 
                         items=items,
                         has_more=pagination.has_next,
                         page=page,
                         per_page=per_page)

@bp.route('/create', methods=['GET', 'POST'])
def create_s002_lineitem():
    if request.method == 'POST':
        try:
            success, item = create_s002_lineitem(request.form)
            if success:
                return redirect(url_for("crud.s002_lineitem.list_s002_lineitem")) 
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/s002_lineitem/form.html', 
                                edit=False, 
                                form_action=url_for('crud.s002_lineitem.create_s002_lineitem')
                                , **get_related_data())
    
    return render_template('crud/s002_lineitem/form.html', 
                         edit=False, 
                         form_action=url_for('crud.s002_lineitem.create_s002_lineitem')
                         , **get_related_data())

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_s002_lineitem(id):
    item = S002_LineItem.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            if update_s002_lineitem(item, request.form):
                return redirect(url_for("crud.s002_lineitem.list_s002_lineitem"))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/s002_lineitem/form.html', 
                                edit=True, 
                                item=item,
                                form_action=url_for('crud.s002_lineitem.edit_s002_lineitem', id=id)
                                , **get_related_data())
    
    return render_template('crud/s002_lineitem/form.html', 
                         edit=True, 
                         item=item,
                         form_action=url_for('crud.s002_lineitem.edit_s002_lineitem', id=id)
                         , **get_related_data())

@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_s002_lineitem(id):
    try:
        item = S002_LineItem.query.get_or_404(id)
        success = delete_s002_lineitem(item)
        return '', 204 if success else 500
    except Exception as e:
        db.session.rollback()
        return str(e), 500
