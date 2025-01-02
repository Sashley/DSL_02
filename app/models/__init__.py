from app import db

# Import models here to make them available when importing from models package
from app.models.shipping import *  # This will be created next

# All models should inherit from db.Model
class BaseModel(db.Model):
    """Base model class that includes common fields and methods."""
    __abstract__ = True
    
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime, 
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )
