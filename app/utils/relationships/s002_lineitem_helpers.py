from flask import flash
from app.models.shipping import S002_LineItem, S004_PackType, S003_Commodity, S005_Container, S001_Manifest
from app import db

def get_related_data():
    """Get all related data needed for S002_LineItem forms."""
    return {
        
        'pack_types': S004_PackType.query.all(),
        'commoditys': S003_Commodity.query.all(),
        'containers': S005_Container.query.all(),
        'manifests': S001_Manifest.query.all(),
    }

def create_s002_lineitem(form_data):
    """Create a new S002_LineItem with related data."""
    try:
        item = S002_LineItem()
        
        if 'pack_type_id' in form_data:
            item.pack_type_id = form_data['pack_type_id']
        if 'commodity_id' in form_data:
            item.commodity_id = form_data['commodity_id']
        if 'container_id' in form_data:
            item.container_id = form_data['container_id']
        if 'manifest_id' in form_data:
            item.manifest_id = form_data['manifest_id']
        
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

def update_s002_lineitem(item, form_data):
    """Update an existing S002_LineItem with related data."""
    try:
        
        if 'pack_type_id' in form_data:
            item.pack_type_id = form_data['pack_type_id']
        if 'commodity_id' in form_data:
            item.commodity_id = form_data['commodity_id']
        if 'container_id' in form_data:
            item.container_id = form_data['container_id']
        if 'manifest_id' in form_data:
            item.manifest_id = form_data['manifest_id']
        
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

def delete_s002_lineitem(item):
    """Delete a S002_LineItem and handle relationships."""
    try:
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return False
