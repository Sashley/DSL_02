from flask import flash
from app.models.shipping import LineItem, Commodity, Container, Manifest, PackType, User
from app import db

def get_related_data():
    """Get all related data needed for LineItem forms."""
    return {
        
        'manifests': Manifest.query.all(),
        'pack_types': PackType.query.all(),
        'commoditys': Commodity.query.all(),
        'containers': Container.query.all(),
        'users': User.query.all(),
    }

def create_lineitem(form_data):
    """Create a new LineItem with related data."""
    try:
        item = LineItem()
        
        if 'manifest_id' in form_data:
            item.manifest_id = form_data['manifest_id']
        if 'pack_type_id' in form_data:
            item.pack_type_id = form_data['pack_type_id']
        if 'commodity_id' in form_data:
            item.commodity_id = form_data['commodity_id']
        if 'container_id' in form_data:
            item.container_id = form_data['container_id']
        if 'user_id' in form_data:
            item.user_id = form_data['user_id']
        
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

def update_lineitem(item, form_data):
    """Update an existing LineItem with related data."""
    try:
        
        if 'manifest_id' in form_data:
            item.manifest_id = form_data['manifest_id']
        if 'pack_type_id' in form_data:
            item.pack_type_id = form_data['pack_type_id']
        if 'commodity_id' in form_data:
            item.commodity_id = form_data['commodity_id']
        if 'container_id' in form_data:
            item.container_id = form_data['container_id']
        if 'user_id' in form_data:
            item.user_id = form_data['user_id']
        
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

def delete_lineitem(item):
    """Delete a LineItem and handle relationships."""
    try:
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return False
