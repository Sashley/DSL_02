from flask import flash
from app.models.shipping import Container, Port
from app import db

def get_related_data():
    """Get all related data needed for Container forms."""
    return {
        
        'ports': Port.query.all(),
    }

def create_container(form_data):
    """Create a new Container with related data."""
    try:
        item = Container()
        
        if 'port_id' in form_data:
            item.port_id = form_data['port_id']
        
        # Set other fields
        for field, value in form_data.items():
            if not field.endswith('_id') and hasattr(item, field):
                setattr(item, field, value)
        
        db.session.add(item)
        db.session.commit()
        flash('Created successfully', 'success')
        return True, item
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return False, None

def update_container(item, form_data):
    """Update an existing Container with related data."""
    try:
        
        if 'port_id' in form_data:
            item.port_id = form_data['port_id']
        
        # Update other fields
        for field, value in form_data.items():
            if not field.endswith('_id') and hasattr(item, field):
                setattr(item, field, value)
        
        db.session.commit()
        flash('Updated successfully', 'success')
        return True
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return False

def delete_container(item):
    """Delete a Container and handle relationships."""
    try:
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return False
