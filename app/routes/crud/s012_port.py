from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from app.models.shipping import S012_Port, S014_Country
from app import db
from sqlalchemy import or_, func

bp = Blueprint('s012_port', __name__)

# Define relationships for this model
relationships = [{'field_name': 'country_id', 'target_model': 'S014_Country', 'relationship_field': 'country'}]

def get_search_filter(model, search_term):
    '''Return case-insensitive search filter for the model.'''
    if not search_term:
        return None
    
    # Convert search term to lowercase for case-insensitive search
    search_term = search_term.lower()
    
    conditions = []
    
    # Search in text fields
    text_fields = ['id', 'name', 'country_id', 'prefix']
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
def list_s012_port():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # Build query with eager loading of relationships
    query = S012_Port.query
    if relationships:  # Only add joinedload if there are relationships
        query = query.options(*[
            db.joinedload(getattr(S012_Port, rel["relationship_field"]))
            for rel in relationships
        ])
    
    # Apply search filter if provided
    search_filter = get_search_filter(S012_Port, search)
    if search_filter is not None:
        query = query.filter(search_filter)
    
    # Get paginated results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    # If this is an HTMX request, return only the rows
    if request.headers.get('HX-Request'):
        return render_template('crud/s012_port/_rows.html', 
                            items=items,
                            has_more=pagination.has_next,
                            page=page)
    
    # For full page request, return complete template
    return render_template('crud/s012_port/list.html', 
                         items=items,
                         has_more=pagination.has_next,
                         page=page,
                         per_page=per_page)

@bp.route('/create', methods=['GET', 'POST'])
def create_s012_port():
    if request.method == 'POST':
        try:
            item = S012_Port()
            
            if 'name' in request.form:
                item.name = request.form['name']
            if 'country_id' in request.form:
                item.country_id = request.form['country_id']
            if 'prefix' in request.form:
                item.prefix = request.form['prefix']
            db.session.add(item)
            db.session.commit()
            flash('Created successfully', 'success')
            return redirect(url_for("crud.s012_port.list_s012_port")) 
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/s012_port/form.html', 
                                edit=False, 
                                form_action=url_for('crud.s012_port.create_s012_port')
                                )
    
    return render_template('crud/s012_port/form.html', 
                         edit=False, 
                         form_action=url_for('crud.s012_port.create_s012_port')
                         )

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_s012_port(id):
    item = S012_Port.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            
            if 'name' in request.form:
                item.name = request.form['name']
            if 'country_id' in request.form:
                item.country_id = request.form['country_id']
            if 'prefix' in request.form:
                item.prefix = request.form['prefix']
            db.session.commit()
            flash('Updated successfully', 'success')
            return redirect(url_for("crud.s012_port.list_s012_port"))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/s012_port/form.html', 
                                edit=True, 
                                item=item,
                                form_action=url_for('crud.s012_port.edit_s012_port', id=id)
                                )
    
    return render_template('crud/s012_port/form.html', 
                         edit=True, 
                         item=item,
                         form_action=url_for('crud.s012_port.edit_s012_port', id=id)
                         )

@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_s012_port(id):
    try:
        item = S012_Port.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        success = True
        return '', 204 if success else 500
    except Exception as e:
        db.session.rollback()
        return str(e), 500
