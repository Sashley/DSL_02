from flask import flash
from app.models.shipping import Voyage, Vessel
from app import db

def get_related_data():
    """Get all related data needed for Voyage forms."""
    return {
        
        'vessels': Vessel.query.all(),
    }

def create_voyage(form_data):
    """Create a new Voyage with related data."""
    try:
        item = Voyage()
        
        if 'vessel_id' in form_data:
            item.vessel_id = form_data['vessel_id']
        
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

def update_voyage(item, form_data):
    """Update an existing Voyage with related data."""
    try:
        
        if 'vessel_id' in form_data:
            item.vessel_id = form_data['vessel_id']
        
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

def delete_voyage(item):
    """Delete a Voyage and handle relationships."""
    try:
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return False
