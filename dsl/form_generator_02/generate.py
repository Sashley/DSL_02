from pathlib import Path
from dsl.form_generator_02.routes import generate_crud_routes
from dsl.form_generator_02.menu import generate_menu_template
from dsl.form_generator_02.base import generate_base_template
from dsl.form_generator_02.dashboard import generate_dashboard_template
from dsl.form_generator_02.crud import generate_crud_templates

def generate_application(json_file: str | Path, output_dir: str | Path) -> None:
    """Generate the complete application from JSON schema."""
    json_path = Path(json_file)
    output_path = Path(output_dir)
    
    # Create necessary directories
    templates_dir = output_path / "app/templates"
    components_dir = templates_dir / "components"
    routes_dir = output_path / "app/routes/crud"
    
    for dir_path in [templates_dir, components_dir, routes_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Generate all components
    print("Generating application components...")
    
    print("1. Generating base template...")
    generate_base_template(templates_dir)
    
    print("2. Generating menu components...")
    generate_menu_template(json_path, components_dir)
    
    print("3. Generating dashboard...")
    generate_dashboard_template(json_path, templates_dir)
    
    print("4. Generating CRUD routes...")
    generate_crud_routes(json_path, routes_dir)
    
    print("5. Generating CRUD templates...")
    generate_crud_templates(json_path, templates_dir / "crud")
    
    # Generate main routes file with dashboard data
    main_routes = """from flask import Blueprint, render_template, jsonify
from app import db
from app.models.shipping import (
    Manifest, Container, Voyage, Client, 
    ContainerStatus, Commodity, LineItem,
    ContainerHistory
)
from sqlalchemy import func, desc
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Get counts for quick stats
    manifest_count = Manifest.query.count()
    container_count = Container.query.count()
    voyage_count = Voyage.query.filter(
        Voyage.eta > datetime.now()
    ).count()
    client_count = Client.query.count()
    
    return render_template('index.html',
                         manifest_count=manifest_count,
                         container_count=container_count,
                         voyage_count=voyage_count,
                         client_count=client_count)

@bp.route('/api/chart/manifest-activity')
def manifest_activity():
    # Get manifest counts for the last 5 days
    today = datetime.now().date()
    dates = [(today - timedelta(days=i)) for i in range(4, -1, -1)]
    
    data = []
    labels = []
    for date in dates:
        count = Manifest.query.filter(
            func.date(Manifest.date_of_receipt) == date
        ).count()
        data.append(count)
        labels.append(date.strftime('%a'))
    
    return jsonify({
        'labels': labels,
        'data': data
    })

@bp.route('/api/chart/container-status')
def container_status():
    # Get container counts by status
    status_counts = db.session.query(
        ContainerStatus.name,
        func.count(Container.id)
    ).join(
        ContainerHistory,
        ContainerHistory.container_status_id == ContainerStatus.id
    ).join(
        Container,
        Container.id == ContainerHistory.container_id
    ).group_by(
        ContainerStatus.name
    ).all()
    
    return jsonify({
        'labels': [status for status, _ in status_counts],
        'data': [count for _, count in status_counts]
    })

@bp.route('/api/chart/commodity-distribution')
def commodity_distribution():
    # Get line item counts by commodity
    commodity_counts = db.session.query(
        Commodity.name,
        func.count(LineItem.id)
    ).join(
        LineItem,
        LineItem.commodity_id == Commodity.id
    ).group_by(
        Commodity.name
    ).order_by(
        desc(func.count(LineItem.id))
    ).limit(5).all()
    
    return jsonify({
        'labels': [commodity for commodity, _ in commodity_counts],
        'data': [count for _, count in commodity_counts]
    })
"""
    
    main_routes_file = output_path / "app/routes/main.py"
    main_routes_file.write_text(main_routes)
    
    print("\nApplication generation complete!")
    print(f"Output directory: {output_path}")

if __name__ == "__main__":
    # Example usage
    generate_application(
        "dsl/output/json/shipping.json",
        "."  # Current directory
    )
