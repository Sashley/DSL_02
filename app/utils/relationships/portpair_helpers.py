from flask import flash
from app.models.shipping import PortPair, Port
from app import db

def get_related_data():
    """Get all related data needed for PortPair forms."""
    return {
        
        'port_of_loadings': Port.query.all(),
        'port_of_discharges': Port.query.all(),
    }

def create_portpair(form_data):
    """Create a new PortPair with related data."""
    try:
        item = PortPair()
        
        if 'port_of_loading_id' in form_data:
            item.port_of_loading_id = form_data['port_of_loading_id']
        if 'port_of_discharge_id' in form_data:
            item.port_of_discharge_id = form_data['port_of_discharge_id']
        
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

def update_portpair(item, form_data):
    """Update an existing PortPair with related data."""
    try:
        
        if 'port_of_loading_id' in form_data:
            item.port_of_loading_id = form_data['port_of_loading_id']
        if 'port_of_discharge_id' in form_data:
            item.port_of_discharge_id = form_data['port_of_discharge_id']
        
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

def delete_portpair(item):
    """Delete a PortPair and handle relationships."""
    try:
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return False
