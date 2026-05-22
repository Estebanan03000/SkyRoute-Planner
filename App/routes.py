"Main flask application routes for the SkyRoute package."
from flask import Blueprint

main_routes = Blueprint("main_routes", __name__)


@main_routes.route("/")
def home():
    return {
        "message": "SkyRoute Planner API is running"
    }