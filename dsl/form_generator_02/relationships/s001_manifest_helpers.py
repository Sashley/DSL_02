from flask import flash
from app.models.shipping import S001_Manifest, S015_Client, S015_Client, S009_Vessel, S010_Voyage, S012_Port, S012_Port
from app import db

def get_related_data():
    """Get all related data needed for S001_Manifest forms."""
    return {
        
        'shippers': S015_Client.query.all(),
        'consignees': S015_Client.query.all(),
        'vessels': S009_Vessel.query.all(),
        'voyages': S010_Voyage.query.all(),
        'port_of_loadings': S012_Port.query.all(),
        'port_of_discharges': S012_Port.query.all(),
    }

def create_s001_manifest(form_data):
    """Create a new S001_Manifest with related data."""
    try:
        item = S001_Manifest()
        
        if 'shipper_id' in form_data:
            item.shipper_id = form_data['shipper_id']
        if 'consignee_id' in form_data:
            item.consignee_id = form_data['consignee_id']
        if 'vessel_id' in form_data:
            item.vessel_id = form_data['vessel_id']
        if 'voyage_id' in form_data:
            item.voyage_id = form_data['voyage_id']
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

def update_s001_manifest(item, form_data):
    """Update an existing S001_Manifest with related data."""
    try:
        
        if 'shipper_id' in form_data:
            item.shipper_id = form_data['shipper_id']
        if 'consignee_id' in form_data:
            item.consignee_id = form_data['consignee_id']
        if 'vessel_id' in form_data:
            item.vessel_id = form_data['vessel_id']
        if 'voyage_id' in form_data:
            item.voyage_id = form_data['voyage_id']
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

def delete_s001_manifest(item):
    """Delete a S001_Manifest and handle relationships."""
    try:
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return False
