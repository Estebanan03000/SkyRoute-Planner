"Main flask application routes for the SkyRoute package."
from io import BytesIO
from flask import Blueprint, request, jsonify, send_file
from typing import Optional, Tuple
from App.Models.Graph import Graph
from App.Models.TravelState import TravelState
from App.Services.InteractiveJourneySimulator import InteractiveJourneySimulator
from App.Services.PlanningService import PlanningService
from App.Services.DetailedJourneyReportService import DetailedJourneyReportService
from App.DataAccess.JSONService import JSONService

main_routes = Blueprint("main_routes", __name__)

# ==================== Global Service Instances ====================
# Initialize services on application startup
_graph: Optional[Graph] = None
_journey_simulator: Optional[InteractiveJourneySimulator] = None
_planning_service: Optional[PlanningService] = None

# Active journeys storage (in-memory for demo, could use database)
_active_journeys: dict = {}


def _initialize_services() -> None:
    """Initialize all services (called on first request)."""
    global _graph, _journey_simulator, _planning_service

    if _graph is None:
        json_service = JSONService("App/Models/airport.json")
        _graph = json_service.load_graph()

    if _planning_service is None:
        _planning_service = PlanningService(_graph)

    if _journey_simulator is None:
        _journey_simulator = InteractiveJourneySimulator(_graph, _planning_service)


def _serialize_graph() -> dict:
    airports = []
    routes = []

    for airport in _graph.get_airports():
        airports.append({
            "iata": airport.get_IATA_code(),
            "name": airport.get_name(),
            "city": airport.get_city(),
            "country": airport.get_country(),
            "time_zone": airport.get_time_zone(),
            "is_hub": airport.get_isHub(),
            "accommodation_cost": airport.get_accommodation_cost(),
            "alimentation_cost": airport.get_alimentation_cost(),
            "activities": [
                {
                    "name": activity.get_name(),
                    "type": activity.get_type(),
                    "duration_minutes": activity.get_duration_per_minutes(),
                    "cost_usd": activity.get_cost_in_USD()
                }
                for activity in airport.get_activities()
            ],
            "jobs": [
                {
                    "name": job.get_name(),
                    "hourly_rate": job.get_hourly_rate(),
                    "max_hours": job.get_max_hours()
                }
                for job in airport.get_jobs()
            ]
        })

        for route in airport.get_adjacencies():
            route_data = route.to_dict()
            route_data["origin"] = airport.get_IATA_code()
            routes.append(route_data)

    return {
        "airports": airports,
        "routes": routes
    }


def _dijkstra_response(start_iata: str, end_iata: str, criterion: str):
    if not start_iata or not end_iata:
        return jsonify({"error": "Both 'start' and 'end' query parameters are required."}), 400

    if criterion not in ["cost", "time"]:
        return jsonify({"error": "Criterion must be 'cost' or 'time'."}), 400

    try:
        if criterion == "cost":
            result = _graph.dijkstra_by_cost(start_iata, end_iata)
        else:
            result = _graph.dijkstra_by_time(start_iata, end_iata)

        return jsonify({
            "success": True,
            "start": start_iata,
            "end": end_iata,
            "criterion": criterion,
            "result": result
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# ==================== Health Check Endpoint ====================

@main_routes.route("/api/")
def api_root():
    """
    Health check endpoint for API availability.
    """
    return {
        "message": "SkyRoute Planner API is running",
        "version": "2.0",
        "endpoints": [
            "POST /api/journey/start - Start a new interactive journey",
            "GET /api/journey/<journey_id>/state - Get current journey state and options",
            "POST /api/journey/<journey_id>/decide - Execute a traveler decision",
            "GET /api/journey/<journey_id>/log - Get journey history",
            "GET /api/journey/<journey_id>/report - Generate journey report",
            "GET /api/journey/<journey_id>/suggestions - Get route suggestions",
            "GET /api/graph - Get full graph data (airports and routes)",
            "GET /api/graph/visualization - Get graph rendered as PNG image",
            "GET /api/graph/dijkstra/cost?start=<iata>&end=<iata> - Dijkstra shortest path by cost",
            "GET /api/graph/dijkstra/time?start=<iata>&end=<iata> - Dijkstra shortest path by time",
            "GET /api/graph/dijkstra/cost/visualization?start=<iata>&end=<iata> - Get Dijkstra graph image highlighted by cost",
            "GET /api/graph/dijkstra/time/visualization?start=<iata>&end=<iata> - Get Dijkstra graph image highlighted by time",
            "POST /api/journey/<journey_id>/reset - Reset journey"
        ]
    }


# ==================== Journey Management Endpoints ====================

@main_routes.route("/api/journey/start", methods=["POST"])
def start_journey():
    """
    Start a new interactive journey.

    Request JSON:
    {
        "origin": "GRU",
        "initial_budget": 500.0,
        "initial_time_minutes": 1440,
        "traveler_name": "John Doe"
    }

    Response:
    {
        "success": true,
        "journey_id": "journey_123",
        "state": {...},
        "message": "Journey started successfully"
    }
    """
    _initialize_services()

    try:
        data = request.get_json()

        # Validate request
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        origin = data.get("origin", "").upper()
        initial_budget = data.get("initial_budget", 0)
        initial_time_minutes = data.get("initial_time_minutes", data.get("initial_time", 0))
        traveler_name = data.get("traveler_name", "Anonymous Traveler")

        if not origin:
            return jsonify({"error": "Origin airport code is required"}), 400

        if initial_budget <= 0:
            return jsonify({"error": "Initial budget must be positive"}), 400

        if initial_time_minutes < 0:
            return jsonify({"error": "Initial time must be zero or positive"}), 400

        initial_time_hours = initial_time_minutes / 60.0

        # Start journey
        success, travel_state, message = _journey_simulator.start_journey(
            origin,
            initial_budget,
            traveler_name,
            initial_time_hours
        )

        if not success:
            return jsonify({"error": message}), 400

        # Create journey ID and store state
        journey_id = f"j_{hash(f'{traveler_name}{origin}{initial_budget}') % 100000}"
        _active_journeys[journey_id] = {
            "travel_state": travel_state,
            "decisions_history": [],
            "created_at": travel_state._journey_start_time.isoformat()
        }

        # Get initial options
        options = _journey_simulator.present_airport_options(travel_state)

        return jsonify({
            "success": True,
            "journey_id": journey_id,
            "message": message,
            "traveler": traveler_name,
            "initial_budget": initial_budget,
            "initial_time_minutes": initial_time_minutes,
            "origin": origin,
            "current_state": options
        }), 201

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@main_routes.route("/api/journey/<journey_id>/state", methods=["GET"])
def get_journey_state(journey_id: str):
    """
    Get current state and available options at current airport.

    Response:
    {
        "success": true,
        "current_airport": {...},
        "options": {...}
    }
    """
    _initialize_services()

    try:
        print("Journey solicitado:", journey_id)
        print("Journeys activos:", list(_active_journeys.keys()))
        if journey_id not in _active_journeys:
            return jsonify({"error": "Journey not found"}), 404

        journey = _active_journeys[journey_id]
        travel_state = journey["travel_state"]

        # Get current options
        options = _journey_simulator.present_airport_options(travel_state)

        return jsonify({
            "success": True,
            "journey_id": journey_id,
            "current_state": options
        }), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@main_routes.route("/api/journey/<journey_id>/decide", methods=["POST"])
def execute_decision(journey_id: str):
    """
    Execute a traveler decision (activity, job, flight, meal, accommodation).

    Request JSON:
    {
        "type": "ACTIVITY|JOB|FLIGHT|MEAL|ACCOMMODATION",
        "activity_id": "act_0",  // for ACTIVITY
        "job_id": "job_0",       // for JOB
        "hours": 3,              // for JOB (optional)
        "destination": "GIG"     // for FLIGHT
    }

    Response:
    {
        "success": true,
        "message": "Decision executed successfully",
        "new_state": {...},
        "can_continue": true
    }
    """
    _initialize_services()

    try:
        if journey_id not in _active_journeys:
            return jsonify({"error": "Journey not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "Decision data is required"}), 400

        journey = _active_journeys[journey_id]
        current_state = journey["travel_state"]

        # Execute decision
        success, new_state, decision_record, message = _journey_simulator.execute_traveler_decision(
            current_state, data
        )

        if not success:
            return jsonify({"error": message}), 400

        # Update journey
        _active_journeys[journey_id]["travel_state"] = new_state
        if decision_record:
            _active_journeys[journey_id]["decisions_history"].append(decision_record.to_dict())

        # Get next options
        options = _journey_simulator.present_airport_options(new_state)        

        # Check if journey can continue
        can_continue = _journey_simulator.can_continue_journey(new_state)

        return jsonify({
            "success": True,
            "message": message,
            "journey_id": journey_id,
            "decision": decision_record.to_dict() if decision_record else None,
            "new_state": options,
            "can_continue": can_continue,
            "budget": round(new_state.get_current_budget(), 2),
            "destinations": len(new_state.get_destinations_visited())
        }), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@main_routes.route("/api/journey/<journey_id>/log", methods=["GET"])
def get_journey_log(journey_id: str):
    """
    Get complete journey history and decisions made.

    Response:
    {
        "success": true,
        "journey_id": "j_123",
        "traveler": "John Doe",
        "events": [...],
        "decisions": [...],
        "summary": {...}
    }
    """
    _initialize_services()

    try:
        if journey_id not in _active_journeys:
            return jsonify({"error": "Journey not found"}), 404

        journey = _active_journeys[journey_id]
        travel_state = journey["travel_state"]
        decisions_history = journey["decisions_history"]

        # Get journey summary
        summary = _journey_simulator.get_journey_summary(travel_state)

        return jsonify({
            "success": True,
            "journey_id": journey_id,
            "traveler": travel_state.get_traveler_name(),
            "summary": summary,
            "events": travel_state.get_journey_events(),
            "decisions": decisions_history,
            "destinations": travel_state.get_destinations_visited()
        }), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@main_routes.route("/api/journey/<journey_id>/report", methods=["GET"])
def generate_journey_report(journey_id: str):
    """
    Generate comprehensive journey report with statistics and analysis.

    Response:
    {
        "success": true,
        "report": {
            "budget": {...},
            "destinations": {...},
            "efficiency": {...},
            "time": {...},
            "decisions": {...}
        }
    }
    """
    _initialize_services()

    try:
        if journey_id not in _active_journeys:
            return jsonify({"error": "Journey not found"}), 404

        journey = _active_journeys[journey_id]
        travel_state = journey["travel_state"]

        # Generate complete report
        report = DetailedJourneyReportService.generate_complete_report([travel_state])

        return jsonify({
            "success": True,
            "journey_id": journey_id,
            "report": report
        }), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@main_routes.route("/api/journey/<journey_id>/suggestions", methods=["GET"])
def get_route_suggestions(journey_id: str):
    """
    Get suggested optimal routes from current position with remaining budget.

    Query params:
    - max_destinations: maximum destinations to suggest (default: 10)
    - depth: exploration depth (default: 50)

    Response:
    {
        "success": true,
        "suggestions": [...],
        "current_position": "GRU",
        "remaining_budget": 350.50
    }
    """
    _initialize_services()

    try:
        if journey_id not in _active_journeys:
            return jsonify({"error": "Journey not found"}), 404

        journey = _active_journeys[journey_id]
        travel_state = journey["travel_state"]

        # Get parameters
        max_destinations = request.args.get("max_destinations", 10, type=int)
        exploration_depth = request.args.get("depth", 50, type=int)

        # Find suggestions
        suggestions = _planning_service.find_optimal_destination_sequence(
            travel_state.get_current_airport().get_IATA_code(),
            travel_state.get_current_budget(),
            max_destinations,
            exploration_depth
        )

        return jsonify({
            "success": True,
            "journey_id": journey_id,
            "current_airport": travel_state.get_current_airport().get_IATA_code(),
            "current_budget": round(travel_state.get_current_budget(), 2),
            "suggestions": [
                {
                    "route": s["route"],
                    "destinations": s["destinations_visited"],
                    "cost": round(s["total_cost"], 2),
                    "remaining": round(s["remaining_budget"], 2),
                    "score": round(s["score"], 2),
                    "efficiency": round(s["efficiency"], 4)
                }
                for s in suggestions[:5]  # Top 5 suggestions
            ]
        }), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@main_routes.route("/api/graph/path", methods=["GET"])
def get_graph_path():
    """Return the shortest path and airport vertex details for a graph route."""
    _initialize_services()

    start_iata = request.args.get("start", "").upper()
    end_iata = request.args.get("end", "").upper()
    criterion = request.args.get("criterion", "cost").lower()

    if not start_iata or not end_iata:
        return jsonify({"error": "Both 'start' and 'end' query parameters are required."}), 400

    if criterion not in ["cost", "time", "distance"]:
        return jsonify({"error": "Criterion must be 'cost', 'time', or 'distance'."}), 400

    try:
        route_result = _graph.dijkstra(start_iata, end_iata, criterion)
        if not route_result.get("path"):
            return jsonify({
                "success": False,
                "message": "No available route was found.",
                "path": route_result,
                "airports": []
            }), 200

        airports = []
        for iata in route_result.get("path", []):
            airport = _graph.find_airport_by_iata(iata)
            if airport is None:
                continue
            airports.append({
                "iata": airport.get_IATA_code(),
                "name": airport.get_name(),
                "city": airport.get_city(),
                "country": airport.get_country(),
                "time_zone": airport.get_time_zone(),
                "is_hub": airport.get_isHub(),
                "accommodation_cost": airport.get_accommodation_cost(),
                "alimentation_cost": airport.get_alimentation_cost(),
                "activities": [
                    {
                        "name": activity.get_name(),
                        "type": activity.get_type(),
                        "duration_minutes": activity.get_duration_per_minutes(),
                        "cost_usd": activity.get_cost_in_USD()
                    }
                    for activity in airport.get_activities()
                ],
                "jobs": [
                    {
                        "name": job.get_name(),
                        "hourly_rate": job.get_hourly_rate(),
                        "max_hours": job.get_max_hours()
                    }
                    for job in airport.get_jobs()
                ]
            })

        return jsonify({
            "success": True,
            "start": start_iata,
            "end": end_iata,
            "criterion": criterion,
            "route": route_result,
            "airports": airports
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@main_routes.route("/api/graph/dijkstra/cost", methods=["GET"])
def get_graph_dijkstra_cost():
    """Return the shortest path by cost between two airports."""
    _initialize_services()

    start_iata = request.args.get("start", "").upper()
    end_iata = request.args.get("end", "").upper()
    return _dijkstra_response(start_iata, end_iata, "cost")


@main_routes.route("/api/graph/dijkstra/time", methods=["GET"])
def get_graph_dijkstra_time():
    """Return the shortest path by time between two airports."""
    _initialize_services()

    start_iata = request.args.get("start", "").upper()
    end_iata = request.args.get("end", "").upper()
    return _dijkstra_response(start_iata, end_iata, "time")


@main_routes.route("/api/graph/dijkstra/cost/visualization", methods=["GET"])
def get_graph_dijkstra_cost_visualization():
    """Return the rendered Dijkstra graph image highlighted by cost."""
    _initialize_services()

    start_iata = request.args.get("start", "").upper()
    end_iata = request.args.get("end", "").upper()

    if not start_iata or not end_iata:
        return jsonify({"error": "Both 'start' and 'end' query parameters are required."}), 400

    try:
        result = _graph.dijkstra(start_iata, end_iata, "cost")
        highlight_path = result.get("path", [])
        image_bytes = _graph.visualize_to_png(highlight_path, criterion="cost")
        return send_file(
            BytesIO(image_bytes),
            mimetype="image/png",
            as_attachment=False,
            download_name="graph_dijkstra_cost.png"
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@main_routes.route("/api/graph/dijkstra/time/visualization", methods=["GET"])
def get_graph_dijkstra_time_visualization():
    """Return the rendered Dijkstra graph image highlighted by time."""
    _initialize_services()

    start_iata = request.args.get("start", "").upper()
    end_iata = request.args.get("end", "").upper()

    if not start_iata or not end_iata:
        return jsonify({"error": "Both 'start' and 'end' query parameters are required."}), 400

    try:
        result = _graph.dijkstra(start_iata, end_iata, "time")
        highlight_path = result.get("path", [])
        image_bytes = _graph.visualize_to_png(highlight_path, criterion="time")
        return send_file(
            BytesIO(image_bytes),
            mimetype="image/png",
            as_attachment=False,
            download_name="graph_dijkstra_time.png"
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@main_routes.route("/api/graph/visualization", methods=["GET"])
def get_graph_visualization():
    """Return the rendered graph as a PNG image."""
    _initialize_services()

    start_iata = request.args.get("start", "").upper()
    end_iata = request.args.get("end", "").upper()
    criterion = request.args.get("criterion", "").lower()
    highlight_path = None

    if start_iata and end_iata and criterion in ["cost", "time"]:
        try:
            result = _graph.dijkstra(start_iata, end_iata, criterion)
            highlight_path = result.get("path", [])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    try:
        image_bytes = _graph.visualize_to_png(highlight_path, criterion=criterion or "cost")
        return send_file(
            BytesIO(image_bytes),
            mimetype="image/png",
            as_attachment=False,
            download_name="graph.png"
        )
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@main_routes.route("/api/journey/<journey_id>/reset", methods=["POST"])
def reset_journey(journey_id: str):
    """
    Reset/end current journey and clean up.

    Response:
    {
        "success": true,
        "message": "Journey reset successfully"
    }
    """
    _initialize_services()

    try:
        if journey_id not in _active_journeys:
            return jsonify({"error": "Journey not found"}), 404

        del _active_journeys[journey_id]

        return jsonify({
            "success": True,
            "message": "Journey reset successfully"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@main_routes.route("/api/journey/<journey_id>/interrupt-route", methods=["POST"])
def interrupt_route(journey_id: str):
    _initialize_services()

    try:
        if journey_id not in _active_journeys:
            return jsonify({"error": "Journey not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        origin = data.get("origin", "").upper()
        destination = data.get("destination", "").upper()
        criterion = data.get("criterion", "cost")

        if not origin or not destination:
            return jsonify({"error": "Origin and destination are required"}), 400

        blocked = _graph.block_route(origin, destination)

        if not blocked:
            return jsonify({
                "success": False,
                "message": "Route does not exist"
            }), 404

        journey = _active_journeys[journey_id]
        travel_state = journey["travel_state"]
        current_airport = travel_state.get_current_airport().get_IATA_code()

        new_route = None

        if final_destination:
            new_route = _graph.dijkstra(
                current_airport,
                final_destination,
                criterion
            )

        travel_state.add_event(
            event_type="ROUTE_INTERRUPTION",
            description=f"Route {origin} -> {destination} was interrupted",
            cost=0,
            time_minutes=0
        )

        return jsonify({
            "success": True,
            "message": f"Route {origin} -> {destination} was blocked successfully",
            "blocked_route": {
                "origin": origin,
                "destination": destination
            },
            "current_airport": current_airport,
            "final_destination": final_destination if final_destination else None,
            "recalculated_route": new_route
        }), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@main_routes.route(
    "/api/load-graph",
    methods=["POST"]
)
def load_graph_file():

    global _graph
    global _planning_service
    global _journey_simulator

    try:

        import os

        uploaded_file = request.files["file"]

        temp_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "DataAccess",
                "temp_graph.json"
            )
        )

        uploaded_file.save(temp_path)

        json_service = JSONService(temp_path)

        _graph = json_service.load_graph()

        _planning_service = PlanningService(_graph)

        _journey_simulator = InteractiveJourneySimulator(
            _graph,
            _planning_service
        )

        return jsonify({
            "success": True,
            "message": "Graph loaded successfully"
        })

    except Exception as e:

        import traceback

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@main_routes.route(
    "/api/dijkstra",
    methods=["POST"]
)
def calculate_dijkstra():

    _initialize_services()

    try:

        data = request.get_json()

        origin = data.get(
            "origin"
        ).upper()

        destination = data.get(
            "destination"
        ).upper()

        criterion = data.get(
            "criterion",
            "cost"
        )

        include_secondary_airports = data.get(
            "include_secondary_airports",
            True
        )

        result = _graph.dijkstra(
            origin,
            destination,
            criterion,
            include_secondary_airports
        )

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@main_routes.route(
    "/api/optimize/budget",
    methods=["POST"]
)
def optimize_by_budget():

    _initialize_services()

    try:

        data = request.get_json()

        origin = data.get("origin", "").upper()
        budget = float(data.get("budget", 0))
        include_secondary_airports = data.get(
            "include_secondary_airports",
            True
        )

        if not origin:
            return jsonify({
                "success": False,
                "error": "Origin is required"
            }), 400

        if budget <= 0:
            return jsonify({
                "success": False,
                "error": "Budget must be positive"
            }), 400

        result = _planning_service.calculate_max_destinations_by_budget(
            origin,
            budget,
            include_secondary_airports
        )

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@main_routes.route(
    "/api/optimize/time",
    methods=["POST"]
)
def optimize_by_time():

    _initialize_services()

    try:

        data = request.get_json()

        origin = data.get("origin", "").upper()
        available_hours = float(data.get("available_hours", 0))
        include_secondary_airports = data.get(
            "include_secondary_airports",
            True
        )

        if not origin:
            return jsonify({
                "success": False,
                "error": "Origin is required"
            }), 400

        if available_hours <= 0:
            return jsonify({
                "success": False,
                "error": "Available hours must be positive"
            }), 400

        result = _planning_service.calculate_max_destinations_by_time(
            origin,
            available_hours,
            include_secondary_airports
        )

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@main_routes.route(
    "/api/compare-routes",
    methods=["POST"]
)
def compare_routes():

    _initialize_services()

    try:

        data = request.get_json()

        origin = data.get(
            "origin"
        ).upper()

        destination = data.get(
            "destination"
        ).upper()

        criteria = data.get(
            "criteria",
            ["cost"]
        )

        include_secondary_airports = data.get(
            "include_secondary_airports",
            True
        )

        result = _planning_service.calculate_best_route(
            origin,
            destination,
            criteria,
            include_secondary_airports
        )

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@main_routes.route("/api/graph", methods=["GET"])
def get_graph():
    _initialize_services()

    nodes = []
    edges = []

    for airport in _graph.get_airports():

        nodes.append({
            "id": airport.get_IATA_code(),
            "label": airport.get_IATA_code(),
            "shape": "dot",
            "size": 18,
            "color": "#ef4444" if airport.get_isHub() else "#3b82f6"
        })

        for route in airport.get_adjacencies():

            edges.append({
                "from": airport.get_IATA_code(),
                "to": route.get_destiny_airport().get_IATA_code(),
                "label": str(round(route.get_distance_in_km())),
                "color": "red" if route.is_blocked() else "green"
            })

    return jsonify({
        "nodes": nodes,
        "edges": edges
    })

def initialize_planning_service() -> None:
    """Initialize internal service instances for app startup."""
    _initialize_services()