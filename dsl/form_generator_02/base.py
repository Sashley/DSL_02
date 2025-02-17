from pathlib import Path

def generate_base_template(output_dir: str | Path) -> None:
    """Generate base template with menu integration."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    base_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Shipping App{% endblock %}</title>
    <script src="https://unpkg.com/htmx.org@1.9.9" integrity="sha384-QFjmbokDn2DjBjq+fM+8LUIVrAgqcNW2s0PjAxHETgRn9l4fvX31ZxDxvwQnyMOX" crossorigin="anonymous"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body class="bg-gray-100">
    {% include 'components/menu_include.html' %}

    <main id="main-content" class="container mx-auto px-4 py-8">
        {% block content %}{% endblock %}
    </main>

    <script>
        // Enable HTMX debug logging
        htmx.logAll();
        
        // Add event listeners for HTMX events
        document.body.addEventListener('htmx:beforeRequest', function(evt) {
            console.log('HTMX Request:', evt.detail);
        });
        
        document.body.addEventListener('htmx:afterRequest', function(evt) {
            console.log('HTMX Response:', evt.detail);
        });
    </script>
</body>
</html>"""

    base_file = output_path / "base.html"
    base_file.write_text(base_template)
    
    print(f"Base template generated in {output_dir}")

if __name__ == "__main__":
    # Example usage
    generate_base_template("app/templates")
