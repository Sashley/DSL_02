import os
from flask import Flask
from sqlalchemy import inspect
from app import db, create_app
from app.models.shipping import (
    Client, Port, User, Vessel, Voyage, Manifest, LineItem,
    Commodity, PackType, Container, ContainerHistory,
    ContainerStatus, ShippingCompany, PortPair, Country, Rate
)

app = create_app()

with app.app_context():
    print("\nChecking database connection and contents:")
    print("-" * 50)

    # Check database configuration
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    db_dir = os.path.dirname(db_path)
    print(f"\nDatabase configuration:")
    print(f"  Full path: {db_path}")
    print(f"  Directory: {db_dir}")
    print(f"  Directory exists: {os.path.exists(db_dir)}")
    print(f"  Database exists: {os.path.exists(db_path)}")
    print(f"  Database size: {os.path.getsize(db_path) if os.path.exists(db_path) else 'N/A'} bytes")

    # Check tables
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\nAvailable tables: {tables}")
    
    # Check each table's contents with detailed queries
    tables_to_check = {
        'Client': Client,
        'Port': Port,
        'Vessel': Vessel,
        'Voyage': Voyage,
        'User': User,
        'Manifest': Manifest,
        'LineItem': LineItem,
        'Commodity': Commodity,
        'PackType': PackType,
        'Container': Container,
        'ContainerHistory': ContainerHistory,
        'ContainerStatus': ContainerStatus,
        'ShippingCompany': ShippingCompany,
        'PortPair': PortPair,
        'Country': Country,
        'Rate': Rate
    }

    for table_name, model in tables_to_check.items():
        try:
            print(f"\n{table_name}:")
            
            # Get total count
            count = model.query.count()
            print(f"  Total records: {count}")
            
            if count > 0:
                # Get first few records with all relationships loaded
                query = model.query.options(db.joinedload('*')).limit(3)
                records = query.all()
                
                print("  Sample records:")
                for i, record in enumerate(records, 1):
                    print(f"    Record {i}:")
                    print(f"      ID: {record.id}")
                    
                    # Print all non-relationship attributes
                    attrs = {k: v for k, v in record.__dict__.items() 
                           if not k.startswith('_') and not isinstance(v, (db.Model, list))}
                    for attr, value in attrs.items():
                        print(f"      {attr}: {value}")
                    
                    # Print relationship counts
                    relationships = {k: v for k, v in record.__dict__.items() 
                                  if not k.startswith('_') and isinstance(v, (db.Model, list))}
                    if relationships:
                        print("      Relationships:")
                        for rel_name, rel_value in relationships.items():
                            if isinstance(rel_value, list):
                                print(f"        {rel_name}: {len(rel_value)} items")
                            else:
                                print(f"        {rel_name}: {rel_value.id if rel_value else 'None'}")
            else:
                print("  No records found")
                
        except Exception as e:
            print(f"  Error querying {table_name}:")
            print(f"    {type(e).__name__}: {str(e)}")
