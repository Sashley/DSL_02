from flask import flash
from app.models.shipping import Port, Country
from app import db

def get_related_data():
    """Get all related data needed for Port forms."""
    return {
        
        'countrys': Country.query.all(),
    }

def create_port(form_data):
    """Create a new Port with related data."""
    try:
        item = Port()
        
        if 'country_id' in form_data:
            item.country_id = form_data['country_id']
        
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

def update_port(item, form_data):
    """Update an existing Port with related data."""
    try:
        
        if 'country_id' in form_data:
            item.country_id = form_data['country_id']
        
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

def delete_port(item):
    """Delete a Port and handle relationships."""
    try:
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return False
