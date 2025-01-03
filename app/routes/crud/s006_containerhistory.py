from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from app.models.shipping import S006_ContainerHistory, S007_ContainerStatus, S005_Container, S015_Client, S012_Port
from app import db
from sqlalchemy import or_, func

bp = Blueprint('s006_containerhistory', __name__)

# Define relationships for this model
relationships = [{'field_name': 'container_id', 'target_model': 'S005_Container', 'relationship_field': 'container'}, {'field_name': 'port_id', 'target_model': 'S012_Port', 'relationship_field': 'port'}, {'field_name': 'client_id', 'target_model': 'S015_Client', 'relationship_field': 'client'}, {'field_name': 'container_status_id', 'target_model': 'S007_ContainerStatus', 'relationship_field': 'container_status'}]

def get_search_filter(model, search_term):
    '''Return case-insensitive search filter for the model.'''
    if not search_term:
        return None
    
    # Convert search term to lowercase for case-insensitive search
    search_term = search_term.lower()
    
    conditions = []
    
    # Search in text fields
    text_fields = ['id', 'container_id', 'port_id', 'client_id', 'container_status_id']
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
def list_s006_containerhistory():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # Build query with eager loading of relationships
    query = S006_ContainerHistory.query
    if relationships:  # Only add joinedload if there are relationships
        query = query.options(*[
            db.joinedload(getattr(S006_ContainerHistory, rel["relationship_field"]))
            for rel in relationships
        ])
    
    # Apply search filter if provided
    search_filter = get_search_filter(S006_ContainerHistory, search)
    if search_filter is not None:
        query = query.filter(search_filter)
    
    # Get paginated results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    # If this is an HTMX request, return only the rows
    if request.headers.get('HX-Request'):
        return render_template('crud/s006_containerhistory/_rows.html', 
                            items=items,
                            has_more=pagination.has_next,
                            page=page)
    
    # For full page request, return complete template
    return render_template('crud/s006_containerhistory/list.html', 
                         items=items,
                         has_more=pagination.has_next,
                         page=page,
                         per_page=per_page)

@bp.route('/create', methods=['GET', 'POST'])
def create_s006_containerhistory():
    if request.method == 'POST':
        try:
            item = S006_ContainerHistory()
            
            if 'container_id' in request.form:
                item.container_id = request.form['container_id']
            if 'port_id' in request.form:
                item.port_id = request.form['port_id']
            if 'client_id' in request.form:
                item.client_id = request.form['client_id']
            if 'container_status_id' in request.form:
                item.container_status_id = request.form['container_status_id']
            if 'damage' in request.form:
                item.damage = request.form['damage']
            if 'updated' in request.form:
                item.updated = request.form['updated']
            db.session.add(item)
            db.session.commit()
            flash('Created successfully', 'success')
            return redirect(url_for("crud.s006_containerhistory.list_s006_containerhistory")) 
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/s006_containerhistory/form.html', 
                                edit=False, 
                                form_action=url_for('crud.s006_containerhistory.create_s006_containerhistory')
                                )
    
    return render_template('crud/s006_containerhistory/form.html', 
                         edit=False, 
                         form_action=url_for('crud.s006_containerhistory.create_s006_containerhistory')
                         )

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_s006_containerhistory(id):
    item = S006_ContainerHistory.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            
            if 'container_id' in request.form:
                item.container_id = request.form['container_id']
            if 'port_id' in request.form:
                item.port_id = request.form['port_id']
            if 'client_id' in request.form:
                item.client_id = request.form['client_id']
            if 'container_status_id' in request.form:
                item.container_status_id = request.form['container_status_id']
            if 'damage' in request.form:
                item.damage = request.form['damage']
            if 'updated' in request.form:
                item.updated = request.form['updated']
            db.session.commit()
            flash('Updated successfully', 'success')
            return redirect(url_for("crud.s006_containerhistory.list_s006_containerhistory"))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('crud/s006_containerhistory/form.html', 
                                edit=True, 
                                item=item,
                                form_action=url_for('crud.s006_containerhistory.edit_s006_containerhistory', id=id)
                                )
    
    return render_template('crud/s006_containerhistory/form.html', 
                         edit=True, 
                         item=item,
                         form_action=url_for('crud.s006_containerhistory.edit_s006_containerhistory', id=id)
                         )

@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_s006_containerhistory(id):
    try:
        item = S006_ContainerHistory.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        success = True
        return '', 204 if success else 500
    except Exception as e:
        db.session.rollback()
        return str(e), 500
