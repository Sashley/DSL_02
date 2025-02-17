from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from app.models.shipping import Vessel, ShippingCompany
from app import db
from sqlalchemy import or_, func
from app.utils.relationships import get_related_data, create_vessel, update_vessel, delete_vessel

bp = Blueprint('vessel', __name__)

# Define relationships for this model
relationships = [{'field_name': 'shipping_company_id', 'target_model': 'ShippingCompany', 'relationship_field': 'shipping_company'}]

def get_search_filter(model, search_term):
    '''Return case-insensitive search filter for the model.'''
    if not search_term:
        return None
    
    # Convert search term to lowercase for case-insensitive search
    search_term = search_term.lower()
    
    conditions = []
    
    # Search in text fields
    text_fields = ['id', 'name', 'shipping_company_id']
    for field in text_fields:
        if hasattr(model, field):
            if field.endswith('_id'):
                # Get relationship info for this field
                rel = next((r for r in relationships if r["field_name"] == field), None)
                if rel:
                    # Add condition for relationship search
                    conditions.append(
                        getattr(model, rel["relationship_field"]).has(
                            func.lower(getattr(globals()[rel["target_model"]], 'name')).like("%" + search_term + "%")
                        )
                    )
            else:
                # Handle regular fields
                conditions.append(func.lower(getattr(model, field)).like("%" + search_term + "%"))
    
    return or_(*conditions) if conditions else None

@bp.route('/')
def list_vessel():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # Build query with eager loading of relationships
    query = Vessel.query
    if relationships:  # Only add joinedload if there are relationships
        query = query.options(*[
            db.joinedload(getattr(Vessel, rel["relationship_field"]))
            for rel in relationships
        ])
    
    # Apply search filter if provided
    search_filter = get_search_filter(Vessel, search)
    if search_filter is not None:
        query = query.filter(search_filter)
    
    # Get paginated results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    # If this is an HTMX request, return only the rows
    if request.headers.get('HX-Request'):
        return render_template('crud/vessel/_rows.html', 
                            items=items,
                            has_more=pagination.has_next,
                            page=page)
    
    # For full page request, return complete template
    return render_template('crud/vessel/list.html', 
                         items=items,
                         has_more=pagination.has_next,
                         page=page,
                         per_page=per_page)

@bp.route('/create', methods=['GET', 'POST'])
def create_vessel():
    if request.method == 'POST':
        try:
            success, item = create_vessel(request.form)
            if success:
                return redirect(url_for("crud.vessel.list_vessel")) 
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/vessel/form.html', 
                                edit=False, 
                                form_action=url_for('crud.vessel.create_vessel')
                                , **get_related_data())
    
    return render_template('crud/vessel/form.html', 
                         edit=False, 
                         form_action=url_for('crud.vessel.create_vessel')
                         , **get_related_data())

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_vessel(id):
    item = Vessel.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            if update_vessel(item, request.form):
                return redirect(url_for("crud.vessel.list_vessel"))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/vessel/form.html', 
                                edit=True, 
                                item=item,
                                form_action=url_for('crud.vessel.edit_vessel', id=id)
                                , **get_related_data())
    
    return render_template('crud/vessel/form.html', 
                         edit=True, 
                         item=item,
                         form_action=url_for('crud.vessel.edit_vessel', id=id)
                         , **get_related_data())

@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_vessel(id):
    try:
        item = Vessel.query.get_or_404(id)
        success = delete_vessel(item)
        return '', 204 if success else 500
    except Exception as e:
        db.session.rollback()
        return str(e), 500
