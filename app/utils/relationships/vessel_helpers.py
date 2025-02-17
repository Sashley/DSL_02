from flask import flash
from app.models.shipping import Vessel, ShippingCompany
from app import db

def get_related_data():
    """Get all related data needed for Vessel forms."""
    return {
        
        'shipping_companys': ShippingCompany.query.all(),
    }

def create_vessel(form_data):
    """Create a new Vessel with related data."""
    try:
        item = Vessel()
        
        if 'shipping_company_id' in form_data:
            item.shipping_company_id = form_data['shipping_company_id']
        
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

def update_vessel(item, form_data):
    """Update an existing Vessel with related data."""
    try:
        
        if 'shipping_company_id' in form_data:
            item.shipping_company_id = form_data['shipping_company_id']
        
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

def delete_vessel(item):
    """Delete a Vessel and handle relationships."""
    try:
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return False
