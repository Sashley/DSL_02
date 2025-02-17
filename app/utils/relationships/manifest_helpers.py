from flask import flash, current_app, has_app_context
from app.models.shipping import Manifest, Client, Port, User, Vessel, Voyage
from app import db
from sqlalchemy import inspect
from contextlib import contextmanager

@contextmanager
def fresh_session():
    """Provide a fresh session for database operations."""
    session = db.create_scoped_session()
    try:
        yield session
    finally:
        session.remove()

def verify_table_data(model, table_name, session):
    """Helper function to verify table data exists and is accessible."""
    from flask import current_app
    logger = current_app.logger
    
    try:
        if not has_app_context():
            logger.error(f"No Flask app context for {table_name}")
            raise RuntimeError(f"No Flask app context for {table_name}")
            
        # Verify model exists in database
        inspector = inspect(db.engine)
        if table_name.lower() not in inspector.get_table_names():
            logger.error(f"Table {table_name} not found in database")
            raise RuntimeError(f"Table {table_name} not found in database")
        
        # Query with eager loading of essential attributes
        query = session.query(model).options(
            db.load_only('id', 'name'),
            db.joinedload('*')
        )
        
        # Execute query and get results
        data = query.all()
        
        if not data:
            logger.warning(f"No records found in {table_name}")
            return []
            
        logger.info(f"Successfully retrieved {len(data)} records from {table_name}")
        
        # Log details of first few records, only column values
        if data:
            for idx, record in enumerate(data[:3]):
                logger.info(f"Record {idx + 1}:")
                # Log only column values, not relationships
                for column in model.__table__.columns:
                    try:
                        value = getattr(record, column.name)
                        logger.info(f"  {column.name}: {value}")
                    except Exception as e:
                        logger.warning(f"  Failed to get {column.name}: {str(e)}")
        
        if data:
            first_item = data[0]
            logger.debug(f"  First record details:")
            logger.debug(f"    ID: {first_item.id}")
            logger.debug(f"    Name: {getattr(first_item, 'name', 'No name')}")
            
            # Log all available attributes
            attrs = [attr for attr in dir(first_item) if not attr.startswith('_')]
            logger.debug(f"    Available attributes: {attrs}")
            
            # Try to access each attribute to verify loading
            for attr in attrs:
                try:
                    value = getattr(first_item, attr)
                    logger.debug(f"    {attr} = {value}")
                except Exception as e:
                    logger.warning(f"    Failed to access {attr}: {str(e)}")
        else:
            logger.warning(f"No records found in {table_name}")
            
        return data
    except Exception as e:
        logger.error(f"Error querying {table_name}:")
        logger.error(f"  Error type: {type(e).__name__}")
        logger.error(f"  Error message: {str(e)}")
        logger.error(f"  Query attempted: {query}")
        return []

def get_related_data():
    """Get all related data needed for Manifest forms."""
    from flask import current_app
    logger = current_app.logger
    
    try:
        if not has_app_context():
            raise RuntimeError("No Flask application context")
        
        with fresh_session() as session:
            # Configure session
            session.expire_on_commit = False
            
            # Query all related data within the same session
            data = {
                'shippers': verify_table_data(Client, 'client', session),
                'consignees': verify_table_data(Client, 'client', session),
                'vessels': verify_table_data(Vessel, 'vessel', session),
                'voyages': verify_table_data(Voyage, 'voyage', session),
                'port_of_loadings': verify_table_data(Port, 'port', session),
                'port_of_discharges': verify_table_data(Port, 'port', session),
                'users': verify_table_data(User, 'user', session)
            }
                
            # Verify data integrity
            logger.debug("Verifying data integrity:")
            for key, value in data.items():
                logger.debug(f"  {key}: {len(value)} records")
                if value:
                    first_item = value[0]
                    logger.debug(f"    First item - ID: {first_item.id}, Name: {getattr(first_item, 'name', 'No name')}")
                else:
                    logger.warning(f"    No data for {key}")
            
            logger.debug("Data retrieval completed successfully")
            return data
            
    except Exception as e:
        logger.error(f"CRITICAL ERROR in get_related_data: {str(e)}")
        if not has_app_context():
            logger.error("No Flask application context")
        return {
            'shippers': [],
            'consignees': [],
            'vessels': [],
            'voyages': [],
            'port_of_loadings': [],
            'port_of_discharges': [],
            'users': [],
        }

def create_manifest(form_data):
    """Create a new Manifest with related data."""
    try:
        if not has_app_context():
            raise RuntimeError("No Flask application context")
            
        with fresh_session() as session:
            item = Manifest()
            
            # Debug print form data
            print("\nDebug - Creating manifest with data:")
            for key, value in form_data.items():
                print(f"  {key}: {value}")
            
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
            if 'user_id' in form_data:
                item.user_id = form_data['user_id']
            
            # Set other fields
            for field, value in form_data.items():
                if not field.endswith('_id') and hasattr(item, field):
                    setattr(item, field, value)
            
            session.add(item)
            session.commit()
            flash('Created successfully', 'success')
            return True, item
    except Exception as e:
        print(f"Error in create_manifest: {str(e)}")
        flash(f'Error: {str(e)}', 'error')
        return False, None

def update_manifest(item, form_data):
    """Update an existing Manifest with related data."""
    try:
        if not has_app_context():
            raise RuntimeError("No Flask application context")
            
        with fresh_session() as session:
            # Debug print form data
            print("\nDebug - Updating manifest with data:")
            for key, value in form_data.items():
                print(f"  {key}: {value}")
                
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
            if 'user_id' in form_data:
                item.user_id = form_data['user_id']
            
            # Update other fields
            for field, value in form_data.items():
                if not field.endswith('_id') and hasattr(item, field):
                    setattr(item, field, value)
            
            session.merge(item)
            session.commit()
            flash('Updated successfully', 'success')
            return True
    except Exception as e:
        print(f"Error in update_manifest: {str(e)}")
        flash(f'Error: {str(e)}', 'error')
        return False

def delete_manifest(item):
    """Delete a Manifest and handle relationships."""
    try:
        if not has_app_context():
            raise RuntimeError("No Flask application context")
            
        with fresh_session() as session:
            session.delete(item)
            session.commit()
            return True
    except Exception as e:
        print(f"Error in delete_manifest: {str(e)}")
        flash(f'Error: {str(e)}', 'error')
        return False
