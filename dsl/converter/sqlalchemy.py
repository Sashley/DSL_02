import json
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, DateTime, Text, Index
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import text

# Mapping from JSON field types to SQLAlchemy column types
TYPE_MAPPING = {
    "Integer": Integer,
    "String": String,
    "Boolean": Boolean,
    "Float": Float,
    "DateTime": DateTime,
    "Text": Text
}

def create_model(name, model_data, base_cls=None, deferred_relationships=None):
    """
    Dynamically create a SQLAlchemy model class.
    
    Args:
        name: Name of the model/table
        model_data: Model definition data
        base_cls: SQLAlchemy declarative base class to use (optional)
        deferred_relationships: Dict to store relationships that need to be added after all models are created
    """
    if base_cls is None:
        base_cls = declarative_base()
        
    if deferred_relationships is None:
        deferred_relationships = {}
        
    attrs = {
        "__tablename__": name.lower(),
        "__table_args__": {"extend_existing": True}
    }
    
    has_primary_key = False
    columns = {}  # Store columns temporarily to reference in relationships

    fields = model_data.get("Fields", {})
    
    # First pass: create all columns
    for field_name, field_def in fields.items():
        column_args = []

        # Map the type
        column_type = TYPE_MAPPING.get(field_def["type"], String)
        
        # Handle length for String type
        if field_def["type"] == "String" and field_def.get("length"):
            column_args.append(column_type(field_def["length"]))
        else:
            column_args.append(column_type)

        # Handle foreign key
        if field_def.get("foreign_key"):
            column_args.append(ForeignKey(field_def["foreign_key"]))

        # Add constraints
        column_kwargs = {}
        
        # Handle primary key
        if field_def.get("primary_key", False):
            column_kwargs["primary_key"] = True
            has_primary_key = True
            if field_def.get("auto_increment", False):
                column_kwargs["autoincrement"] = True
        
        # Handle nullable
        column_kwargs["nullable"] = field_def.get("nullable", True)

        # Handle unique constraint
        if field_def.get("unique", False):
            column_kwargs["unique"] = True

        # Create column
        column = Column(*column_args, **column_kwargs)
        attrs[field_name] = column
        columns[field_name] = column

    # Store relationships to be created after all models exist
    if fields:
        relationships_info = {}
        for field_name, field_def in fields.items():
            if field_def.get("foreign_key"):
                # Create relationship name with _rel suffix
                rel_name = f"{field_name}_rel"
                
                # Create a unique back reference name based on the relationship context
                back_ref_name = f"{name.split('_', 1)[1].lower()}s"
                
                relationships_info[rel_name] = {
                    "target": field_def["foreign_key"].split('.')[0],
                    "foreign_keys": [field_name],
                    "back_populates": back_ref_name
                }
        
        if relationships_info:
            deferred_relationships[name] = {
                "relationships": relationships_info,
                "columns": columns
            }

    if not has_primary_key:
        raise ValueError(f"Table '{name}' must have at least one primary key.")

    # Create the model class
    model = type(name, (base_cls,), attrs)

    # Add indexes if defined
    if "Indices" in model_data:
        for index_name, index_columns in model_data["Indices"].items():
            Index(
                index_name,
                *[getattr(model, col_name) for col_name in index_columns],
            )

    return model

def load_json_to_models(json_file, base_cls=None):
    """
    Load JSON and convert to SQLAlchemy models.
    
    Args:
        json_file: Path to the JSON file
        base_cls: SQLAlchemy declarative base class to use (optional)
    """
    with open(json_file, "r") as f:
        data = json.load(f)

    deferred_relationships = {}
    models = {}
    
    # First pass: Create all models without relationships
    for model_name, model_data in data["Models"].items():
        model = create_model(model_name, model_data, base_cls, deferred_relationships)
        models[model_name] = model

    # Second pass: Add relationships now that all models exist
    for model_name, rel_data in deferred_relationships.items():
        model = models[model_name]
        relationships = rel_data["relationships"]
        columns = rel_data["columns"]
        
        for rel_name, rel_def in relationships.items():
            # Find the target model by matching case-insensitive name
            target_name = None
            target_table = rel_def["target"]
            
            # Try case-insensitive match
            for name in models.keys():
                if name.lower() == target_table or name.lower() == target_table.upper():
                    target_name = name
                    break
                
            if not target_name:
                raise KeyError(f"Could not find model {target_table}")
                
            target_model = models[target_name]
            
            # Create relationship kwargs
            rel_kwargs = {
                "back_populates": rel_def["back_populates"]
            }
            
            # Add foreign keys
            if "foreign_keys" in rel_def:
                rel_kwargs["foreign_keys"] = [columns[fk] for fk in rel_def["foreign_keys"]]
            
            # Create the relationship
            setattr(model, rel_name, relationship(target_name, **rel_kwargs))
            
            # Create back reference on target model if it doesn't exist
            back_ref_name = rel_def["back_populates"]
            if not hasattr(target_model, back_ref_name):
                back_rel_kwargs = {
                    "back_populates": rel_name,
                    "foreign_keys": rel_kwargs.get("foreign_keys")
                }
                setattr(target_model, back_ref_name, 
                    relationship(model_name, **back_rel_kwargs))

    return models
