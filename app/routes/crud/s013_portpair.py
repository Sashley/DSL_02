from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from app.models.shipping import S013_PortPair, S012_Port
from app import db
from sqlalchemy import or_, func

bp = Blueprint('s013_portpair', __name__)

# Define relationships for this model
relationships = [{'field_name': 'pol_id', 'target_model': 'S012_Port', 'relationship_field': 'port_of_loading'}, {'field_name': 'pod_id', 'target_model': 'S012_Port', 'relationship_field': 'port_of_discharge'}]

def get_search_filter(model, search_term):
    '''Return case-insensitive search filter for the model.'''
    if not search_term:
        return None
    
    # Convert search term to lowercase for case-insensitive search
    search_term = search_term.lower()
    
    conditions = []
    
    # Search in text fields
    text_fields = ['id', 'pol_id', 'pod_id', 'distance', 'distance_rate_code']
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
def list_s013_portpair():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # Build query with eager loading of relationships
    query = S013_PortPair.query
    if relationships:  # Only add joinedload if there are relationships
        query = query.options(*[
            db.joinedload(getattr(S013_PortPair, rel["relationship_field"]))
            for rel in relationships
        ])
    
    # Apply search filter if provided
    search_filter = get_search_filter(S013_PortPair, search)
    if search_filter is not None:
        query = query.filter(search_filter)
    
    # Get paginated results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    # If this is an HTMX request, return only the rows
    if request.headers.get('HX-Request'):
        return render_template('crud/s013_portpair/_rows.html', 
                            items=items,
                            has_more=pagination.has_next,
                            page=page)
    
    # For full page request, return complete template
    return render_template('crud/s013_portpair/list.html', 
                         items=items,
                         has_more=pagination.has_next,
                         page=page,
                         per_page=per_page)

@bp.route('/create', methods=['GET', 'POST'])
def create_s013_portpair():
    if request.method == 'POST':
        try:
            item = S013_PortPair()
            
            if 'pol_id' in request.form:
                item.pol_id = request.form['pol_id']
            if 'pod_id' in request.form:
                item.pod_id = request.form['pod_id']
            if 'distance' in request.form:
                item.distance = request.form['distance']
            if 'distance_rate_code' in request.form:
                item.distance_rate_code = request.form['distance_rate_code']
            db.session.add(item)
            db.session.commit()
            flash('Created successfully', 'success')
            return redirect(url_for("crud.s013_portpair.list_s013_portpair")) 
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/s013_portpair/form.html', 
                                edit=False, 
                                form_action=url_for('crud.s013_portpair.create_s013_portpair')
                                )
    
    return render_template('crud/s013_portpair/form.html', 
                         edit=False, 
                         form_action=url_for('crud.s013_portpair.create_s013_portpair')
                         )

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_s013_portpair(id):
    item = S013_PortPair.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            
            if 'pol_id' in request.form:
                item.pol_id = request.form['pol_id']
            if 'pod_id' in request.form:
                item.pod_id = request.form['pod_id']
            if 'distance' in request.form:
                item.distance = request.form['distance']
            if 'distance_rate_code' in request.form:
                item.distance_rate_code = request.form['distance_rate_code']
            db.session.commit()
            flash('Updated successfully', 'success')
            return redirect(url_for("crud.s013_portpair.list_s013_portpair"))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/s013_portpair/form.html', 
                                edit=True, 
                                item=item,
                                form_action=url_for('crud.s013_portpair.edit_s013_portpair', id=id)
                                )
    
    return render_template('crud/s013_portpair/form.html', 
                         edit=True, 
                         item=item,
                         form_action=url_for('crud.s013_portpair.edit_s013_portpair', id=id)
                         )

@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_s013_portpair(id):
    try:
        item = S013_PortPair.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        success = True
        return '', 204 if success else 500
    except Exception as e:
        db.session.rollback()
        return str(e), 500
