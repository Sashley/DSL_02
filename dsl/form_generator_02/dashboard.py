from pathlib import Path
import json
from typing import Dict, Any

def generate_dashboard_template(json_file: str | Path, output_dir: str | Path) -> None:
    """Generate dashboard template with charts and slide-out menu."""
    json_path = Path(json_file)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(json_path, "r") as f:
        data = json.load(f)
    
    # Group models by category for slide-out menu
    categories = {
        "Operations": ["Manifest", "LineItem", "Container", "ContainerHistory"],
        "Planning": ["Voyage", "Vessel", "Port", "PortPair", "Leg"],
        "Business": ["Client", "ShippingCompany", "Rate"],
        "Reference": ["Commodity", "PackType", "ContainerStatus", "Country"],
        "System": ["User"]
    }
    
    dashboard_template = """{% extends "base.html" %}

{% block title %}Dashboard{% endblock %}

{% block content %}
<!-- Slide-out Menu Toggle -->
<button id="menu-toggle" 
        class="fixed top-4 left-4 z-50 bg-blue-500 text-white p-2 rounded-lg shadow-lg hover:bg-blue-600"
        onclick="document.getElementById('slide-menu').classList.toggle('-translate-x-64')">
    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
    </svg>
</button>

<!-- Slide-out Menu -->
<div id="slide-menu" 
     class="fixed top-0 left-0 h-full w-64 bg-gray-800 text-white transform -translate-x-64 transition-transform duration-300 ease-in-out z-40">
    <div class="p-4">
        <h2 class="text-xl font-bold mb-4">Navigation</h2>
        <!-- Menu Categories -->
"""

    # Add menu categories and items
    for category, models in categories.items():
        if any(model in data["Models"] for model in models):
            dashboard_template += f"""        <div class="mb-4">
            <h3 class="text-sm font-semibold text-gray-400 mb-2">{category}</h3>
            <ul class="space-y-2">
"""
            for model in models:
                if model in data["Models"]:
                    route_name = model.lower()
                    dashboard_template += f"""                <li>
                    <a href="{{{{ url_for('crud.{route_name}.list_{route_name}') }}}}"
                       class="block text-gray-300 hover:text-white hover:bg-gray-700 px-2 py-1 rounded">
                        {model}s
                    </a>
                </li>
"""
            dashboard_template += """            </ul>
        </div>
"""

    # Add main dashboard content with charts
    dashboard_template += """    </div>
</div>

<!-- Main Dashboard Content -->
<div class="ml-0 transition-margin duration-300 ease-in-out">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Manifest Activity Chart -->
        <div class="bg-white p-6 rounded-lg shadow-lg">
            <h3 class="text-lg font-semibold mb-4">Manifest Activity</h3>
            <canvas id="manifestChart"></canvas>
        </div>

        <!-- Container Status Chart -->
        <div class="bg-white p-6 rounded-lg shadow-lg">
            <h3 class="text-lg font-semibold mb-4">Container Status</h3>
            <canvas id="containerChart"></canvas>
        </div>

        <!-- Commodity Distribution Chart -->
        <div class="bg-white p-6 rounded-lg shadow-lg">
            <h3 class="text-lg font-semibold mb-4">Commodity Distribution</h3>
            <canvas id="commodityChart"></canvas>
        </div>

        <!-- Quick Stats -->
        <div class="bg-white p-6 rounded-lg shadow-lg">
            <h3 class="text-lg font-semibold mb-4">Quick Stats</h3>
            <div class="grid grid-cols-2 gap-4">
                <div class="text-center">
                    <p class="text-gray-600">Active Manifests</p>
                    <p class="text-2xl font-bold text-blue-600">{{ manifest_count }}</p>
                </div>
                <div class="text-center">
                    <p class="text-gray-600">Containers in Transit</p>
                    <p class="text-2xl font-bold text-green-600">{{ container_count }}</p>
                </div>
                <div class="text-center">
                    <p class="text-gray-600">Upcoming Voyages</p>
                    <p class="text-2xl font-bold text-purple-600">{{ voyage_count }}</p>
                </div>
                <div class="text-center">
                    <p class="text-gray-600">Active Clients</p>
                    <p class="text-2xl font-bold text-orange-600">{{ client_count }}</p>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Chart Initialization -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Function to initialize charts with data
    async function initializeCharts() {
        try {
            // Manifest Activity Chart
            const manifestResponse = await fetch('/api/chart/manifest-activity');
            const manifestData = await manifestResponse.json();
            new Chart(document.getElementById('manifestChart'), {
                type: 'line',
                data: {
                    labels: manifestData.labels,
                    datasets: [{
                        label: 'New Manifests',
                        data: manifestData.data,
                        borderColor: 'rgb(59, 130, 246)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });

            // Container Status Chart
            const containerResponse = await fetch('/api/chart/container-status');
            const containerData = await containerResponse.json();
            new Chart(document.getElementById('containerChart'), {
                type: 'bar',
                data: {
                    labels: containerData.labels,
                    datasets: [{
                        label: 'Containers',
                        data: containerData.data,
                        backgroundColor: [
                            'rgb(59, 130, 246)',
                            'rgb(16, 185, 129)',
                            'rgb(245, 158, 11)',
                            'rgb(139, 92, 246)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });

            // Commodity Distribution Chart
            const commodityResponse = await fetch('/api/chart/commodity-distribution');
            const commodityData = await commodityResponse.json();
            new Chart(document.getElementById('commodityChart'), {
                type: 'pie',
                data: {
                    labels: commodityData.labels,
                    datasets: [{
                        data: commodityData.data,
                        backgroundColor: [
                            'rgb(59, 130, 246)',
                            'rgb(16, 185, 129)',
                            'rgb(245, 158, 11)',
                            'rgb(139, 92, 246)',
                            'rgb(107, 114, 128)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error initializing charts:', error);
        }
    }

    // Initialize charts
    initializeCharts();
});

// Menu toggle functionality
document.getElementById('menu-toggle').addEventListener('click', function() {
    const content = document.querySelector('.ml-0');
    content.classList.toggle('md:ml-64');
});
</script>
{% endblock %}"""

    # Write dashboard template
    dashboard_file = output_path / "index.html"
    dashboard_file.write_text(dashboard_template)
    
    print(f"Dashboard template generated in {output_dir}")

if __name__ == "__main__":
    # Example usage
    generate_dashboard_template("dsl/output/json/shipping.json", "app/templates")
