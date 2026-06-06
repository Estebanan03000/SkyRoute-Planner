# SkyRoute Planner

SkyRoute Planner is a Flask-based route optimization and interactive travel simulation application. It loads airport, route, aircraft, activities, and job data from a JSON configuration file and exposes REST API endpoints to explore routes, simulate journeys, and generate travel reports.

## Project structure

- `app.py` - Main Flask application entrypoint.
- `App/__init__.py` - Flask application factory.
- `App/routes.py` - API endpoints and journey orchestration.
- `App/DataAccess/JSONService.py` - Loads and parses the JSON dataset into graph models.
- `App/Models/` - Domain models: airports, routes, aircraft, activities, jobs, travel state, and scheduling.
- `Presentation/` - Static UI files for the web frontend.
- `App/Models/airport.json` - The source dataset for airports and routes.

## Key concepts

- `Graph` contains airports and directed routes.
- `Route` represents a flight connection and supports cost/time calculations per aircraft.
- `TravelState` tracks the traveler's current airport, budget, time, events, and decisions.
- `InteractiveJourneySimulator` presents options and executes traveler decisions.
- `PlanningService` includes route planning and optimization logic.
- `DetailedJourneyReportService` generates journey summaries, budget analysis, and time reports.

## Running the app

1. Activate the Python virtual environment (if available):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Run the application:
   ```powershell
   python app.py
   ```
4. Open your browser and navigate to `http://127.0.0.1:5000/`.

## API Endpoints

- `GET /api/` - Health check and endpoint list.
- `POST /api/journey/start` - Start a new interactive journey.
- `GET /api/journey/<journey_id>/state` - Retrieve current traveler state and options.
- `POST /api/journey/<journey_id>/decide` - Execute a decision during the journey.
- `GET /api/journey/<journey_id>/log` - Get journey history.
- `GET /api/journey/<journey_id>/report` - Generate a journey report.
- `GET /api/graph` - Retrieve graph data for airports and routes.
- `GET /api/graph/visualization` - Get a PNG visualization of the graph.
- `GET /api/graph/dijkstra/cost?start=<iata>&end=<iata>` - Compute shortest route by cost.
- `GET /api/graph/dijkstra/time?start=<iata>&end=<iata>` - Compute shortest route by time.
- `GET /api/graph/dijkstra/cost/visualization?start=<iata>&end=<iata>` - Visualize a cost-based shortest path.
- `GET /api/graph/dijkstra/time/visualization?start=<iata>&end=<iata>` - Visualize a time-based shortest path.

## Dependencies

- `Flask==2.3.3`
- `networkx==3.1`
- `matplotlib==3.7.2`

## Documentation guidance

This project uses inline documentation in the form of module-level and method-level docstrings. The key files to inspect for implementation details are:

- `App/DataAccess/JSONService.py`
- `App/Models/Graph.py`
- `App/Models/TravelState.py`
- `App/Models/Route.py`
- `App/Services/PlanningService.py`
- `App/Services/InteractiveJourneySimulator.py`
- `App/Services/DetailedJourneyReportService.py`

To extend documentation further, add docstrings to any new helper methods and update this README with new endpoints or model relationships.
