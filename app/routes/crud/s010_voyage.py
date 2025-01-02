from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from app.models.shipping import S010_Voyage, S015_Client, S009_Vessel
from app import db
from sqlalchemy import or_, func

bp = Blueprint('s010_voyage', __name__)

def get_search_filter(model, search_term):
    '''Return case-insensitive search filter for the model.'''
    if not search_term:
        return None
    
    # Convert search term to lowercase for case-insensitive search
    search_term = search_term.lower()
    
    conditions = []
    
    # Search in text fields
    text_fields = ['id', 'name', 'vessel_id', 'rotation_number']
    for field in text_fields:
        if hasattr(model, field):
            if field.endswith('_id'):
                # Handle relationship fields
                if field == 'shipper_id':
                    conditions.append(model.shipper.has(func.lower(S015_Client.name).like(f'%{{search_term}}%')))
                elif field == 'consignee_id':
                    conditions.append(model.consignee.has(func.lower(S015_Client.name).like(f'%{{search_term}}%')))
                elif field == 'vessel_id':
                    conditions.append(model.vessel.has(func.lower(S009_Vessel.name).like(f'%{{search_term}}%')))
            else:
                # Handle regular fields
                conditions.append(func.lower(getattr(model, field)).like(f'%{{search_term}}%'))
    
    return or_(*conditions) if conditions else None

@bp.route('/')
def list_s010_voyage():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # Build query with eager loading of relationships
    query = S010_Voyage.query
    
    
    # Apply search filter if provided
    search_filter = get_search_filter(S010_Voyage, search)
    if search_filter is not None:
        query = query.filter(search_filter)
    
    # Get paginated results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    # If this is an HTMX request, return only the rows
    if request.headers.get('HX-Request'):
        return render_template('crud/s010_voyage/_rows.html', 
                            items=items,
                            has_more=pagination.has_next,
                            page=page)
    
    # For full page request, return complete template
    return render_template('crud/s010_voyage/list.html', 
                         items=items,
                         has_more=pagination.has_next,
                         page=page,
                         per_page=per_page)

@bp.route('/create', methods=['GET', 'POST'])
def create_s010_voyage():
    if request.method == 'POST':
        try:
            item = S010_Voyage()
            
            if 'name' in request.form:
                item.name = request.form['name']
            if 'vessel_id' in request.form:
                item.vessel_id = request.form['vessel_id']
            if 'rotation_number' in request.form:
                item.rotation_number = request.form['rotation_number']
            db.session.add(item)
            db.session.commit()
            flash('Created successfully', 'success')
            return redirect(url_for("crud.s010_voyage.list_s010_voyage")) 
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/s010_voyage/form.html', 
                                edit=False, 
                                form_action=url_for('crud.s010_voyage.create_s010_voyage')
                                )
    
    return render_template('crud/s010_voyage/form.html', 
                         edit=False, 
                         form_action=url_for('crud.s010_voyage.create_s010_voyage')
                         )

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_s010_voyage(id):
    item = S010_Voyage.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            
            if 'name' in request.form:
                item.name = request.form['name']
            if 'vessel_id' in request.form:
                item.vessel_id = request.form['vessel_id']
            if 'rotation_number' in request.form:
                item.rotation_number = request.form['rotation_number']
            db.session.commit()
            flash('Updated successfully', 'success')
            return redirect(url_for("crud.s010_voyage.list_s010_voyage"))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/s010_voyage/form.html', 
                                edit=True, 
                                item=item,
                                form_action=url_for('crud.s010_voyage.edit_s010_voyage', id=id)
                                )
    
    return render_template('crud/s010_voyage/form.html', 
                         edit=True, 
                         item=item,
                         form_action=url_for('crud.s010_voyage.edit_s010_voyage', id=id)
                         )

@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_s010_voyage(id):
    try:
        item = S010_Voyage.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        success = True
        return '', 204 if success else 500
    except Exception as e:
        db.session.rollback()
        return str(e), 500
