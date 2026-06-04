"Main flask application routes for the SkyRoute package."
from flask import Blueprint, request, jsonify
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
        traveler_name = data.get("traveler_name", "Anonymous Traveler")

        if not origin:
            return jsonify({"error": "Origin airport code is required"}), 400

        if initial_budget <= 0:
            return jsonify({"error": "Initial budget must be positive"}), 400

        # Start journey
        success, travel_state, message = _journey_simulator.start_journey(
            origin, initial_budget, traveler_name
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


def initialize_planning_service() -> None:
    """Initialize internal service instances for app startup."""
    _initialize_services()