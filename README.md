# Shipping Application

This is a Flask-based shipping application using SQLAlchemy, HTMX, and Tailwind CSS for styling. Tailwind is the only CSS framework used in the application.

## Getting Started

### Running the Application

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:

   ```bash
   python run.py
   ```

3. Access the application at: http://localhost:5000

### Generating SQLAlchemy Models

The application uses a DSL to generate SQLAlchemy models. To generate models:

1. Run the model generator:

   ```bash
   python c01/generate_models.py
   ```

2. The models will be generated in `app/models/`

### Generating CRUD Routines and Menus

The application includes a CRUD generator that creates routes, templates, and menus:

1. Run the CRUD generator:

   ```bash
   python app/utils/generator/generate.py
   ```

2. This will generate:
   - CRUD routes in `app/routes/crud/`
   - Templates in `app/templates/crud/`
   - Menu items in the application navigation

## Dependencies

### Core Framework

- Flask - Web framework
- Flask-SQLAlchemy - ORM integration
- SQLAlchemy - Database ORM
- Werkzeug - WSGI utilities

### Database Management

- Alembic - Database migrations
- Flask-Migrate - Migration integration

### Form Handling

- Flask-WTF - Form handling and validation
- Email-Validator - Email validation

### Development Tools

- Black - Code formatting
- Flake8 - Linting
- MyPy - Static type checking
- Pytest - Testing framework

### Configuration

- Python-dotenv - Environment variable management

## Development

- The application runs in debug mode by default
- Database changes are automatically applied when models are modified
- Use HTMX for dynamic UI components instead of JavaScript
