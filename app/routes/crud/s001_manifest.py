from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from app.models.shipping import S001_Manifest, S015_Client, S016_User, S012_Port, S009_Vessel, S010_Voyage
from app import db
from sqlalchemy import or_, func
from app.utils.relationships.s001_manifest_helpers import get_related_data, create_s001_manifest, update_s001_manifest, delete_s001_manifest

bp = Blueprint('s001_manifest', __name__)

# Define relationships for this model
relationships = [{'field_name': 'shipper_id', 'target_model': 'S015_Client', 'relationship_field': 'shipper'}, {'field_name': 'consignee_id', 'target_model': 'S015_Client', 'relationship_field': 'consignee'}, {'field_name': 'vessel_id', 'target_model': 'S009_Vessel', 'relationship_field': 'vessel'}, {'field_name': 'voyage_id', 'target_model': 'S010_Voyage', 'relationship_field': 'voyage'}, {'field_name': 'port_of_loading_id', 'target_model': 'S012_Port', 'relationship_field': 'port_of_loading'}, {'field_name': 'port_of_discharge_id', 'target_model': 'S012_Port', 'relationship_field': 'port_of_discharge'}, {'field_name': 'user_id', 'target_model': 'S016_User', 'relationship_field': 'user'}]

def get_search_filter(model, search_term):
    '''Return case-insensitive search filter for the model.'''
    if not search_term:
        return None
    
    # Convert search term to lowercase for case-insensitive search
    search_term = search_term.lower()
    
    conditions = []
    
    # Search in text fields
    text_fields = ['id', 'bill_of_lading', 'shipper_id', 'consignee_id', 'vessel_id']
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
def list_s001_manifest():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # Build query with eager loading of relationships
    query = S001_Manifest.query.options(
        db.joinedload(S001_Manifest.shipper),
        db.joinedload(S001_Manifest.consignee),
        db.joinedload(S001_Manifest.vessel),
        db.joinedload(S001_Manifest.voyage),
        db.joinedload(S001_Manifest.port_of_loading),
        db.joinedload(S001_Manifest.port_of_discharge),
        db.joinedload(S001_Manifest.user)
    )
    
    # Apply search filter if provided
    search_filter = get_search_filter(S001_Manifest, search)
    if search_filter is not None:
        query = query.filter(search_filter)
    
    # Get paginated results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    # If this is an HTMX request, return only the rows
    if request.headers.get('HX-Request'):
        return render_template('crud/s001_manifest/_rows.html', 
                            items=items,
                            has_more=pagination.has_next,
                            page=page)
    
    # For full page request, return complete template
    return render_template('crud/s001_manifest/list.html', 
                         items=items,
                         has_more=pagination.has_next,
                         page=page,
                         per_page=per_page)

@bp.route('/create', methods=['GET', 'POST'])
def create_s001_manifest():
    if request.method == 'POST':
        try:
            success, item = create_s001_manifest(request.form)
            if success:
                return redirect(url_for("crud.s001_manifest.list_s001_manifest")) 
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/s001_manifest/form.html', 
                                edit=False, 
                                form_action=url_for('crud.s001_manifest.create_s001_manifest')
                                , **get_related_data())
    
    return render_template('crud/s001_manifest/form.html', 
                         edit=False, 
                         form_action=url_for('crud.s001_manifest.create_s001_manifest')
                         , **get_related_data())

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_s001_manifest(id):
    item = S001_Manifest.query.options(
        db.joinedload(S001_Manifest.shipper),
        db.joinedload(S001_Manifest.consignee),
        db.joinedload(S001_Manifest.vessel),
        db.joinedload(S001_Manifest.voyage),
        db.joinedload(S001_Manifest.port_of_loading),
        db.joinedload(S001_Manifest.port_of_discharge),
        db.joinedload(S001_Manifest.user)
    ).get_or_404(id)
    
    if request.method == 'POST':
        try:
            if update_s001_manifest(item, request.form):
                return redirect(url_for("crud.s001_manifest.list_s001_manifest"))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    related_data = get_related_data()
    print("Related data:", related_data)  # Debug print
    return render_template('crud/s001_manifest/form.html', 
                         edit=True, 
                         item=item,
                         form_action=url_for('crud.s001_manifest.edit_s001_manifest', id=id)
                         , **related_data)

@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_s001_manifest(id):
    try:
        item = S001_Manifest.query.get_or_404(id)
        success = delete_s001_manifest(item)
        return '', 204 if success else 500
    except Exception as e:
        db.session.rollback()
        return str(e), 500
