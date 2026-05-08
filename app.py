"""
Entry point for the SkyRoute Flask application.
"""
import os
from App import create_app

# Create the Flask application instance
app = create_app()

# Configure static files and templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.static_folder = os.path.join(BASE_DIR, 'Presentation')
app.static_url_path = '/static'
app.template_folder = os.path.join(BASE_DIR, 'Presentation', 'View')

# Initialize services on app startup
with app.app_context():
    from App.routes import initialize_planning_service
    initialize_planning_service()


@app.route('/')
def index():
    """Serve the main index.html page."""
    from flask import render_template
    return render_template('index.html')


if __name__ == '__main__':
    # Development server configuration
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        threaded=True
    )
