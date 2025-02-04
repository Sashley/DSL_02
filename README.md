# Shipping Application

A Flask-based shipping application with DSL-driven code generation for large-scale database operations. Features HTMX for dynamic UI and Tailwind CSS for styling.

## Overview

### Core Features

- DSL-based schema definition and code generation
- Automated CRUD operations for 50-150+ database tables
- Relationship-aware form generation
- Search and pagination functionality
- Standardized display templates

## Getting Started

### Installation

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment:

   ```bash
   # Copy example environment file
   cp .env.example .env

   # Edit .env with your settings
   # Particularly update SECRET_KEY for production
   ```

3. Run the application:
   ```bash
   python run.py
   ```

Access at: http://localhost:5000

### Code Generation

The application uses a DSL to generate SQLAlchemy models and CRUD operations:

1. Define your schema in `dsl/schemas/shipping/current/schema.dsl`

2. Generate all components:
   ```bash
   python -m dsl.convert_batch
   ```

This will generate:

- SQLAlchemy models in `app/models/`
- CRUD routes in `app/routes/crud/`
- Templates in `app/templates/crud/`
- Relationship metadata in `dsl/output/relationships/`

## Configuration

### Environment Variables

The application uses `.env` files for configuration. Available settings:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/shipping.db
FLASK_ENV=development
DEBUG=True

# Application Settings
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

### Configuration Files

- `.env` - Local development settings (not in version control)
- `.env.example` - Template for environment settings
- `config.py` - Application configuration classes

## Development

### Project Structure

```
dsl/
├── schemas/            # DSL schema definitions
├── convert_batch.py    # Main conversion script
└── output/            # Generated files
    ├── json/         # Intermediate JSON
    ├── models/       # Generated models
    └── relationships/ # Relationship metadata

app/
├── models/           # SQLAlchemy models
├── routes/          # Route handlers
├── templates/       # Jinja2 templates
└── utils/          # Helper functions
```

### Best Practices

- Store schema versions in `schemas/shipping/archive/`
- Run validation before deployment
- Review generated relationship metadata
- Test relationship changes thoroughly

### Dependencies

#### Core Framework

- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- Werkzeug

#### Database Management

- Alembic
- Flask-Migrate

#### Form Handling

- Flask-WTF
- Email-Validator

#### Development Tools

- Black (formatting)
- Flake8 (linting)
- MyPy (type checking)
- Pytest (testing)

### Development Notes

- The application runs in debug mode by default
- Database changes require schema updates and regeneration
- Use HTMX for dynamic UI components
- Relationship metadata provides insight into model connections
