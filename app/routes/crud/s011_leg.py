from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from app.models.shipping import S011_Leg, S012_Port, S010_Voyage
from app import db
from sqlalchemy import or_, func

bp = Blueprint('s011_leg', __name__)

# Define relationships for this model
relationships = [{'field_name': 'voyage_id', 'target_model': 'S010_Voyage', 'relationship_field': 'voyage'}, {'field_name': 'port_id', 'target_model': 'S012_Port', 'relationship_field': 'port'}]

def get_search_filter(model, search_term):
    '''Return case-insensitive search filter for the model.'''
    if not search_term:
        return None
    
    # Convert search term to lowercase for case-insensitive search
    search_term = search_term.lower()
    
    conditions = []
    
    # Search in text fields
    text_fields = ['id', 'voyage_id', 'port_id', 'leg_number', 'eta']
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
def list_s011_leg():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # Build query with eager loading of relationships
    query = S011_Leg.query
    if relationships:  # Only add joinedload if there are relationships
        query = query.options(*[
            db.joinedload(getattr(S011_Leg, rel["relationship_field"]))
            for rel in relationships
        ])
    
    # Apply search filter if provided
    search_filter = get_search_filter(S011_Leg, search)
    if search_filter is not None:
        query = query.filter(search_filter)
    
    # Get paginated results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    # If this is an HTMX request, return only the rows
    if request.headers.get('HX-Request'):
        return render_template('crud/s011_leg/_rows.html', 
                            items=items,
                            has_more=pagination.has_next,
                            page=page)
    
    # For full page request, return complete template
    return render_template('crud/s011_leg/list.html', 
                         items=items,
                         has_more=pagination.has_next,
                         page=page,
                         per_page=per_page)

@bp.route('/create', methods=['GET', 'POST'])
def create_s011_leg():
    if request.method == 'POST':
        try:
            item = S011_Leg()
            
            if 'voyage_id' in request.form:
                item.voyage_id = request.form['voyage_id']
            if 'port_id' in request.form:
                item.port_id = request.form['port_id']
            if 'leg_number' in request.form:
                item.leg_number = request.form['leg_number']
            if 'eta' in request.form:
                item.eta = request.form['eta']
            if 'etd' in request.form:
                item.etd = request.form['etd']
            db.session.add(item)
            db.session.commit()
            flash('Created successfully', 'success')
            return redirect(url_for("crud.s011_leg.list_s011_leg")) 
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/s011_leg/form.html', 
                                edit=False, 
                                form_action=url_for('crud.s011_leg.create_s011_leg')
                                )
    
    return render_template('crud/s011_leg/form.html', 
                         edit=False, 
                         form_action=url_for('crud.s011_leg.create_s011_leg')
                         )

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_s011_leg(id):
    item = S011_Leg.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            
            if 'voyage_id' in request.form:
                item.voyage_id = request.form['voyage_id']
            if 'port_id' in request.form:
                item.port_id = request.form['port_id']
            if 'leg_number' in request.form:
                item.leg_number = request.form['leg_number']
            if 'eta' in request.form:
                item.eta = request.form['eta']
            if 'etd' in request.form:
                item.etd = request.form['etd']
            db.session.commit()
            flash('Updated successfully', 'success')
            return redirect(url_for("crud.s011_leg.list_s011_leg"))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/s011_leg/form.html', 
                                edit=True, 
                                item=item,
                                form_action=url_for('crud.s011_leg.edit_s011_leg', id=id)
                                )
    
    return render_template('crud/s011_leg/form.html', 
                         edit=True, 
                         item=item,
                         form_action=url_for('crud.s011_leg.edit_s011_leg', id=id)
                         )

@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_s011_leg(id):
    try:
        item = S011_Leg.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        success = True
        return '', 204 if success else 500
    except Exception as e:
        db.session.rollback()
        return str(e), 500
