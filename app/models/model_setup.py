from app import db
from app.models.shipping import *

def setup_models():
    """
    Set up model relationships after all models are defined.
    This is now simplified since relationships are generated from DSL.
    """
    # Create tables
    db.create_all()
