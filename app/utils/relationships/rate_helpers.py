from flask import flash
from app.models.shipping import Rate, Client, Commodity, PackType
from app import db

def get_related_data():
    """Get all related data needed for Rate forms."""
    return {
        
        'commoditys': Commodity.query.all(),
        'pack_types': PackType.query.all(),
        'clients': Client.query.all(),
    }

def create_rate(form_data):
    """Create a new Rate with related data."""
    try:
        item = Rate()
        
        if 'commodity_id' in form_data:
            item.commodity_id = form_data['commodity_id']
        if 'pack_type_id' in form_data:
            item.pack_type_id = form_data['pack_type_id']
        if 'client_id' in form_data:
            item.client_id = form_data['client_id']
        
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

def update_rate(item, form_data):
    """Update an existing Rate with related data."""
    try:
        
        if 'commodity_id' in form_data:
            item.commodity_id = form_data['commodity_id']
        if 'pack_type_id' in form_data:
            item.pack_type_id = form_data['pack_type_id']
        if 'client_id' in form_data:
            item.client_id = form_data['client_id']
        
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

def delete_rate(item):
    """Delete a Rate and handle relationships."""
    try:
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return False
