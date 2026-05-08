"""Application factory helpers for the Skyrouter package."""

from flask import Flask
from App.routes import main_routes


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    # Register the main blueprint containing the API routes.
    app.register_blueprint(main_routes)
    return app