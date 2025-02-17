from flask import flash
from app.models.shipping import ContainerHistory, Client, Container, ContainerStatus, Port
from app import db

def get_related_data():
    """Get all related data needed for ContainerHistory forms."""
    return {
        
        'containers': Container.query.all(),
        'ports': Port.query.all(),
        'clients': Client.query.all(),
        'container_statuss': ContainerStatus.query.all(),
    }

def create_containerhistory(form_data):
    """Create a new ContainerHistory with related data."""
    try:
        item = ContainerHistory()
        
        if 'container_id' in form_data:
            item.container_id = form_data['container_id']
        if 'port_id' in form_data:
            item.port_id = form_data['port_id']
        if 'client_id' in form_data:
            item.client_id = form_data['client_id']
        if 'container_status_id' in form_data:
            item.container_status_id = form_data['container_status_id']
        
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

def update_containerhistory(item, form_data):
    """Update an existing ContainerHistory with related data."""
    try:
        
        if 'container_id' in form_data:
            item.container_id = form_data['container_id']
        if 'port_id' in form_data:
            item.port_id = form_data['port_id']
        if 'client_id' in form_data:
            item.client_id = form_data['client_id']
        if 'container_status_id' in form_data:
            item.container_status_id = form_data['container_status_id']
        
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

def delete_containerhistory(item):
    """Delete a ContainerHistory and handle relationships."""
    try:
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return False
