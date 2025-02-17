from flask import Blueprint, render_template, jsonify
from app import db
from app.models.shipping import (
    Manifest, Container, Voyage, Client, 
    ContainerStatus, Commodity, LineItem,
    ContainerHistory, Leg
)
from sqlalchemy import func, desc
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Get counts for quick stats
    manifest_count = Manifest.query.count()
    container_count = Container.query.count()
    voyage_count = Voyage.query.join(Leg).filter(
        Leg.eta > datetime.now()
    ).distinct().count()
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
