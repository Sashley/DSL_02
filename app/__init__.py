from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets

# Initialize extensions
db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__)

    # Configure logging
    import logging
    import sys
    
    # Configure root logger
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    
    # Configure Flask logger
    app.logger.setLevel(logging.WARNING)
    
    # Configure SQLAlchemy logger
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    # Ensure all loggers propagate to root
    # for name in ['app', 'sqlalchemy', 'werkzeug']:
    #     logger = logging.getLogger(name)
    #     logger.propagate = True
    
    # Load configuration
    if test_config is None:
        # Load the default configuration
        app.config.from_object('config.DevelopmentConfig')
        app.logger.info("Loaded development configuration")
    else:
        # Load the test config if passed in
        app.config.update(test_config)
        app.logger.info("Loaded test configuration")

    # Configure SQLAlchemy
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,  # Enable connection pool pre-ping
        'pool_recycle': 300,    # Recycle connections after 5 minutes
        'pool_timeout': 30,     # Connection timeout after 30 seconds
        'echo': False,           # Enable SQL query logging
    }
    app.logger.info("SQLAlchemy configured")

    # Initialize Flask extensions
    db.init_app(app)

    with app.app_context():
        # Import models
        from app.models import shipping
        from app.models.model_setup import setup_models
        
        # Setup models and create tables
        setup_models()

        # Register blueprints
        from app.routes import main
        app.register_blueprint(main.bp)

        from app.routes.crud import bp as crud_bp
        app.register_blueprint(crud_bp, url_prefix='/crud')

        # Configure context processors
        @app.context_processor
        def utility_processor():
            return dict(
                year=datetime.now().year,
                hasattr=hasattr
            )

        # Configure error handlers
        @app.errorhandler(404)
        def not_found_error(error):
            return render_template('404.html'), 404

        @app.errorhandler(500)
        def internal_error(error):
            db.session.rollback()
            return render_template('500.html'), 500

        # Configure teardown functions
        @app.teardown_appcontext
        def shutdown_session(exception=None):
            db.session.remove()

        # Debug route to verify database connection
        @app.route('/debug/db')
        def debug_db():
            try:
                # Test database connection
                db.session.execute('SELECT 1')
                tables = db.engine.table_names()
                return {
                    'status': 'ok',
                    'tables': tables,
                    'database_uri': app.config['SQLALCHEMY_DATABASE_URI']
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'error': str(e),
                    'database_uri': app.config['SQLALCHEMY_DATABASE_URI']
                }

    return app
