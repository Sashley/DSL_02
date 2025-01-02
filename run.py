from app import create_app, db

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'app': app
    }

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
    app.run(debug=True)
