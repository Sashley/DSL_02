from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from app.models.shipping import Country
from app import db
from sqlalchemy import or_, func

bp = Blueprint('country', __name__)

# Define relationships for this model
relationships = []

def get_search_filter(model, search_term):
    '''Return case-insensitive search filter for the model.'''
    if not search_term:
        return None
    
    # Convert search term to lowercase for case-insensitive search
    search_term = search_term.lower()
    
    conditions = []
    
    # Search in text fields
    text_fields = ['id', 'name']
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
def list_country():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # Build query with eager loading of relationships
    query = Country.query
    if relationships:  # Only add joinedload if there are relationships
        query = query.options(*[
            db.joinedload(getattr(Country, rel["relationship_field"]))
            for rel in relationships
        ])
    
    # Apply search filter if provided
    search_filter = get_search_filter(Country, search)
    if search_filter is not None:
        query = query.filter(search_filter)
    
    # Get paginated results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    # If this is an HTMX request, return only the rows
    if request.headers.get('HX-Request'):
        return render_template('crud/country/_rows.html', 
                            items=items,
                            has_more=pagination.has_next,
                            page=page)
    
    # For full page request, return complete template
    return render_template('crud/country/list.html', 
                         items=items,
                         has_more=pagination.has_next,
                         page=page,
                         per_page=per_page)

@bp.route('/create', methods=['GET', 'POST'])
def create_country():
    if request.method == 'POST':
        try:
            item = Country()
            
            if 'name' in request.form:
                item.name = request.form['name']
            db.session.add(item)
            db.session.commit()
            flash('Created successfully', 'success')
            return redirect(url_for("crud.country.list_country")) 
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/country/form.html', 
                                edit=False, 
                                form_action=url_for('crud.country.create_country')
                                )
    
    return render_template('crud/country/form.html', 
                         edit=False, 
                         form_action=url_for('crud.country.create_country')
                         )

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_country(id):
    item = Country.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            
            if 'name' in request.form:
                item.name = request.form['name']
            db.session.commit()
            flash('Updated successfully', 'success')
            return redirect(url_for("crud.country.list_country"))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/country/form.html', 
                                edit=True, 
                                item=item,
                                form_action=url_for('crud.country.edit_country', id=id)
                                )
    
    return render_template('crud/country/form.html', 
                         edit=True, 
                         item=item,
                         form_action=url_for('crud.country.edit_country', id=id)
                         )

@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_country(id):
    try:
        item = Country.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        success = True
        return '', 204 if success else 500
    except Exception as e:
        db.session.rollback()
        return str(e), 500
