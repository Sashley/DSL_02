from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from app.models.shipping import S015_Client, S014_Country
from app import db
from sqlalchemy import or_, func

bp = Blueprint('s015_client', __name__)

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
    text_fields = ['id', 'name', 'address', 'town', 'country_id']
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
def list_s015_client():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # Build query with eager loading of relationships
    query = S015_Client.query
    if relationships:  # Only add joinedload if there are relationships
        query = query.options(*[
            db.joinedload(getattr(S015_Client, rel["relationship_field"]))
            for rel in relationships
        ])
    
    # Apply search filter if provided
    search_filter = get_search_filter(S015_Client, search)
    if search_filter is not None:
        query = query.filter(search_filter)
    
    # Get paginated results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    # If this is an HTMX request, return only the rows
    if request.headers.get('HX-Request'):
        return render_template('crud/s015_client/_rows.html', 
                            items=items,
                            has_more=pagination.has_next,
                            page=page)
    
    # For full page request, return complete template
    return render_template('crud/s015_client/list.html', 
                         items=items,
                         has_more=pagination.has_next,
                         page=page,
                         per_page=per_page)

@bp.route('/create', methods=['GET', 'POST'])
def create_s015_client():
    if request.method == 'POST':
        try:
            item = S015_Client()
            
            if 'name' in request.form:
                item.name = request.form['name']
            if 'address' in request.form:
                item.address = request.form['address']
            if 'town' in request.form:
                item.town = request.form['town']
            if 'country_id' in request.form:
                item.country_id = request.form['country_id']
            if 'contact_person' in request.form:
                item.contact_person = request.form['contact_person']
            if 'email' in request.form:
                item.email = request.form['email']
            if 'phone' in request.form:
                item.phone = request.form['phone']
            db.session.add(item)
            db.session.commit()
            flash('Created successfully', 'success')
            return redirect(url_for("crud.s015_client.list_s015_client")) 
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/s015_client/form.html', 
                                edit=False, 
                                form_action=url_for('crud.s015_client.create_s015_client')
                                )
    
    return render_template('crud/s015_client/form.html', 
                         edit=False, 
                         form_action=url_for('crud.s015_client.create_s015_client')
                         )

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_s015_client(id):
    item = S015_Client.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            
            if 'name' in request.form:
                item.name = request.form['name']
            if 'address' in request.form:
                item.address = request.form['address']
            if 'town' in request.form:
                item.town = request.form['town']
            if 'country_id' in request.form:
                item.country_id = request.form['country_id']
            if 'contact_person' in request.form:
                item.contact_person = request.form['contact_person']
            if 'email' in request.form:
                item.email = request.form['email']
            if 'phone' in request.form:
                item.phone = request.form['phone']
            db.session.commit()
            flash('Updated successfully', 'success')
            return redirect(url_for("crud.s015_client.list_s015_client"))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/s015_client/form.html', 
                                edit=True, 
                                item=item,
                                form_action=url_for('crud.s015_client.edit_s015_client', id=id)
                                )
    
    return render_template('crud/s015_client/form.html', 
                         edit=True, 
                         item=item,
                         form_action=url_for('crud.s015_client.edit_s015_client', id=id)
                         )

@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_s015_client(id):
    try:
        item = S015_Client.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        success = True
        return '', 204 if success else 500
    except Exception as e:
        db.session.rollback()
        return str(e), 500
