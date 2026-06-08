from typing import Optional, List, Tuple
from App.Models.TravelState import TravelState
from App.Models.TravelDecision import TravelDecision
from App.Models.Graph import Graph
from App.Services.PlanningService import PlanningService


class InteractiveJourneySimulator:
    """
    Orchestrates step-by-step interactive journey simulation.
    Presents options to traveler at each destination and executes their decisions.
    Tracks budget, time, and all decisions made during the journey.
    """

    def __init__(self, graph: Graph, planning_service: PlanningService) -> None:
        """
        Initialize the interactive journey simulator.

        Args:
            graph: Graph object containing airport network
            planning_service: Combined planning service for travel and activity logic
        """
        self._graph: Graph = graph
        self._planning_service: PlanningService = planning_service

        # Active journey tracking
        self._active_journeys: dict = {}

    def _is_valid_decision_type(self, decision_type: Optional[str]) -> bool:
        return decision_type in [
            "ACTIVITY", "JOB", "FLIGHT", "SKIP", "MEAL", "ACCOMMODATION"
        ]

    def _select_activity(self, airport, activity_id: str) -> Optional[dict]:
        for activity in self._planning_service.get_available_activities(airport):
            if activity["id"] == activity_id:
                return activity
        return None

    def _select_job(
        self,
        airport,
        job_id: str,
        current_budget: float,
        initial_budget: float
    ) -> Optional[dict]:
        for job in self._planning_service.get_available_jobs(
            airport,
            current_budget,
            initial_budget
        ):
            if job["id"] == job_id:
                return job
        return None

    def _select_aircraft(self, aircraft_options, aircraft_id: Optional[str]):
        if not aircraft_options:
            return None

        if aircraft_id:
            for aircraft in aircraft_options:
                if aircraft.get_id() == aircraft_id:
                    return aircraft
            return None

        return aircraft_options[0]

    # ==================== Journey Initialization ====================

    def start_journey(
        self,
        origin_airport_code: str,
        initial_budget: float,
        traveler_name: str,
        initial_time_hours: float = 0.0
    ) -> Tuple[bool, TravelState, str]:
        """
        Initialize a new interactive journey.

        Args:
            origin_airport_code: IATA code of starting airport
            initial_budget: Starting budget in USD
            traveler_name: Name of the traveler

        Returns:
            Tuple: (success, TravelState, message)
        """
        # Validate origin airport exists
        origin_airport = self._graph.find_airport_by_iata(origin_airport_code)
        if not origin_airport:
            return False, None, f"Airport '{origin_airport_code}' not found"

        # Validate budget
        if initial_budget <= 0:
            return False, None, "Initial budget must be positive"

        # Create initial travel state
        travel_state = TravelState(
            origin_airport,
            initial_budget,
            traveler_name,
            initial_time_hours
        )

        # Record starting event
        travel_state.add_event(
            event_type="JOURNEY_START",
            description=f"Journey begins in {origin_airport.get_IATA_code()} "
                       f"({origin_airport.get_city()})",
            cost=0,
            time_minutes=0
        )

        return True, travel_state, "Journey started successfully"

    # ==================== Present Options to Traveler ====================

    def present_airport_options(
        self,
        current_state: TravelState
    ) -> dict:
        """
        Present all available options to the traveler at current airport.

        This is the key method that shows what the traveler can do next:
        - Mandatory costs (food, accommodation)
        - Optional activities available
        - Jobs available to earn money
        - Flight options to next airports

        Args:
            current_state: Current travel state

        Returns:
            Dictionary with all available options
        """
        airport = current_state.get_current_airport()
        current_budget = current_state.get_current_budget()

        # ==================== Mandatory Costs ====================
        mandatory_costs = self._planning_service.calculate_mandatory_costs(
            airport,
            current_state.get_hours_since_last_accommodation(),
            current_state.get_hours_since_last_meal(),
            current_state.get_initial_budget()
        )

        # ==================== Available Activities ====================
        optional_activities = self._planning_service.get_available_activities(airport)

        # ==================== Available Jobs ====================
        available_jobs = self._planning_service.get_available_jobs(
            airport,
            current_budget,
            current_state.get_initial_budget()
        )

        # ==================== Flight Options ====================
        next_flights = self._planning_service.calculate_next_flight_options(
            airport.get_IATA_code(),
            current_budget
        )

        # ==================== Time Availability ====================
        # Assume minimum stay = minimum required time to legally leave airport
        min_stay_minutes = 90  # Standard minimum stay
        time_info = self._planning_service.calculate_available_time_at_airport(
            min_stay_minutes
        )

        # ==================== Assemble Response ====================
        return {
            "status": "success",
            "traveler": current_state.get_traveler_name(),
            "current_airport": {
                "code": airport.get_IATA_code(),
                "name": airport.get_name(),
                "city": airport.get_city(),
                "country": airport.get_country(),
                "is_hub": airport.get_isHub()
            },
            "budget": {
                "current": round(current_budget, 2),
                "initial": round(current_state.get_initial_budget(), 2),
                "spent": round(current_state.get_total_spent(), 2),
                "earned": round(current_state.get_total_earned(), 2),
                "percentage_remaining": round(current_state.get_budget_remaining_percentage(), 1),
                "budget_critical": current_state.get_budget_remaining_percentage() < 35
            },
            "time": {
                "initial_time_hours": round(current_state.get_initial_time_hours(), 2),
                "initial_time_minutes": round(current_state.get_initial_time_hours() * 60, 0),
                "remaining_time_hours": round(current_state.get_remaining_time_hours(), 2),
                "remaining_time_minutes": round(current_state.get_remaining_time_hours() * 60, 0),
                "at_current_airport_hours": round(current_state.get_time_at_current_airport(), 2),
                "at_current_airport_minutes": round(current_state.get_time_at_current_airport() * 60, 0),
                "hours_since_accommodation": round(
                    current_state.get_hours_since_last_accommodation(), 2
                ),
                "minutes_since_accommodation": round(
                    current_state.get_hours_since_last_accommodation() * 60, 0
                ),
                "hours_since_meal": round(
                    current_state.get_hours_since_last_meal(), 2
                ),
                "minutes_since_meal": round(
                    current_state.get_hours_since_last_meal() * 60, 0
                ),
                "total_journey_hours": round(current_state.get_total_journey_time(), 2),
                "total_journey_minutes": round(current_state.get_total_journey_time() * 60, 0)
            },
            "mandatory_requirements": mandatory_costs,
            "optional_activities": optional_activities,
            "available_jobs": available_jobs,
            "next_flights": next_flights,
            "journey_progress": {
                "destinations_visited": current_state.get_destinations_visited(),
                "destinations_count": len(current_state.get_destinations_visited()),
                "decisions_made": len(current_state.get_travel_decisions()),
                "events_recorded": len(current_state.get_journey_events())
            }
        }

    # ==================== Decision Execution ====================

    def execute_traveler_decision(
        self,
        current_state: TravelState,
        decision: dict
    ) -> Tuple[bool, TravelState, TravelDecision, str]:
        """
        Execute a traveler's decision and update journey state.

        Args:
            current_state: Current travel state
            decision: Decision dictionary with structure:
                     {"type": "ACTIVITY"|"JOB"|"FLIGHT"|"SKIP",
                      "activity_id" or "job_id" or "destination": ...}

        Returns:
            Tuple: (success, new_state, decision_record, message)
        """
        decision_type = decision.get("type")

        if not self._is_valid_decision_type(decision_type):
            return False, current_state, None, "Invalid decision type"

        if decision_type == "SKIP":
            travel_decision = TravelDecision(
                "SKIP",
                current_state.get_current_airport().get_IATA_code(),
                "No action"
            )
            current_state.add_decision(travel_decision.to_dict())
            return True, current_state, travel_decision, "No action taken"

        if decision_type == "ACTIVITY":
            return self._execute_activity_decision(current_state, decision)
        elif decision_type == "JOB":
            return self._execute_job_decision(current_state, decision)
        elif decision_type == "FLIGHT":
            return self._execute_flight_decision(current_state, decision)
        elif decision_type == "MEAL":
            return self._execute_meal_decision(current_state, decision)
        elif decision_type == "ACCOMMODATION":
            return self._execute_accommodation_decision(current_state, decision)

        return False, current_state, None, "Unknown decision type"

    # ==================== Decision Handlers ====================

    def _execute_activity_decision(
        self,
        current_state: TravelState,
        decision: dict
    ) -> Tuple[bool, TravelState, TravelDecision, str]:
        """Handle optional activity decision."""
        airport = current_state.get_current_airport()
        activity_id = decision.get("activity_id")

        selected_activity = self._select_activity(airport, activity_id)

        if not selected_activity:
            return False, current_state, None, "Activity not found"

        # Check budget
        activity_cost = selected_activity["cost"]
        if current_state.get_current_budget() < activity_cost:
            return False, current_state, None, "Insufficient budget for this activity"

        # Check time
        activity_duration_hours = selected_activity["duration_min"] / 60
        current_state.add_time_at_current_airport(activity_duration_hours)

        # Deduct cost
        current_state.update_budget(-activity_cost)

        # Record decision
        travel_decision = TravelDecision(
            "ACTIVITY",
            airport.get_IATA_code(),
            selected_activity["name"]
        )
        travel_decision.set_cost_impact(-activity_cost)
        travel_decision.set_time_spent_minutes(selected_activity["duration_min"])
        travel_decision.add_detail("activity_type", selected_activity["type"])

        current_state.add_decision(travel_decision.to_dict())
        current_state.add_event(
            event_type="ACTIVITY",
            description=selected_activity["name"],
            cost=activity_cost,
            time_minutes=selected_activity["duration_min"]
        )

        return True, current_state, travel_decision, \
               f"Activity '{selected_activity['name']}' completed (${activity_cost:.2f}, "   \
               f"{activity_duration_hours:.1f}h)"

    def _execute_job_decision(
        self,
        current_state: TravelState,
        decision: dict
    ) -> Tuple[bool, TravelState, TravelDecision, str]:
        """Handle job/work decision."""
        airport = current_state.get_current_airport()
        job_id = decision.get("job_id")
        hours_to_work = decision.get("hours", 1.0)

        selected_job = self._select_job(
            airport,
            job_id,
            current_state.get_current_budget(),
            current_state.get_initial_budget()
        )

        if not selected_job:
            return False, current_state, None, "Job not found"

        # Check if jobs are allowed (35% rule)
        if current_state.get_current_budget() >= (current_state.get_initial_budget() * 0.35):
            return False, current_state, None, "You can only work if your budget is below 35% of your initial budget"

        # Cap work hours to job maximum
        actual_hours = min(hours_to_work, selected_job["max_hours"])

        if actual_hours <= 0:
            return False, current_state, None, "Invalid work hours"

        # Calculate earnings
        earnings = actual_hours * selected_job["hourly_rate"]

        # Update state
        current_state.add_time_at_current_airport(actual_hours)
        current_state.update_budget(earnings)  # Positive = earnings

        # Record decision
        travel_decision = TravelDecision(
            "JOB",
            airport.get_IATA_code(),
            selected_job["name"]
        )
        travel_decision.set_cost_impact(earnings)
        travel_decision.set_time_spent_minutes(int(actual_hours * 60))
        travel_decision.add_details({
            "hourly_rate": selected_job["hourly_rate"],
            "hours_worked": actual_hours,
            "earnings": earnings
        })

        current_state.add_decision(travel_decision.to_dict())
        current_state.add_event(
            event_type="JOB",
            description=f"{selected_job['name']} ({actual_hours}h @ "
                       f"${selected_job['hourly_rate']:.2f}/h)",
            cost=-earnings,  # Negative cost = income
            time_minutes=int(actual_hours * 60)
        )

        return True, current_state, travel_decision, \
               f"Worked {actual_hours:.1f}h as '{selected_job['name']}' "   \
               f"(earned ${earnings:.2f})"

    def _execute_flight_decision(
        self,
        current_state: TravelState,
        decision: dict
    ) -> Tuple[bool, TravelState, TravelDecision, str]:
        """
        Handle flight decision to next airport.
        Supports aircraft selection for Part C: Medios de Transporte.
        """
        destination_code = decision.get("destination")
        aircraft_id = decision.get("aircraft_id")  # New: specify aircraft type

        # Validate destination exists
        destination_airport = self._graph.find_airport_by_iata(destination_code)
        if not destination_airport:
            return False, current_state, None, "Destination airport not found"

        current_airport_code = current_state.get_current_airport().get_IATA_code()
        current_airport = current_state.get_current_airport()

        # Find direct route to destination
        origin_route = None
        for route in current_airport.get_adjacencies():
            if route.get_destiny_airport().get_IATA_code() == destination_code:
                origin_route = route
                break

        if not origin_route:
            return False, current_state, None, "No direct flight available"

        if origin_route.is_blocked():
            return (
                False,
                current_state,
                None,
                f"The route {current_airport_code} -> {destination_code} is currently blocked"
            )
        
        # Get aircraft options for this route
        available_aircraft = origin_route.get_aircraft()
        if not available_aircraft:
            return False, current_state, None, "No aircraft available for this route"

        selected_aircraft = self._select_aircraft(available_aircraft, aircraft_id)
        if not selected_aircraft:
            return False, current_state, None, "Selected aircraft not available"

        # Validate distance restrictions for aircraft
        distance_km = origin_route.get_distance_in_km()
        aircraft_type = selected_aircraft.get_type()

        if aircraft_type == "Avion Regional" and distance_km > 2000:
            return False, current_state, None, \
                   f"Regional aircraft cannot fly {distance_km}km (max 2000km)"
        elif aircraft_type == "Helice" and distance_km > 1000:
            return False, current_state, None, \
                   f"Helicopter cannot fly {distance_km}km (max 1000km)"

        # Calculate cost and time using selected aircraft
        flight_cost = origin_route._calculate_cost(selected_aircraft)
        flight_time_minutes = origin_route._calculate_time(selected_aircraft)
        flight_time_hours = flight_time_minutes / 60

        # Validate subsidized distance limit (Part C)
        if origin_route.get_is_subsidized():
            current_subsidized = current_state.get_subsidized_distance_traveled()
            current_total = current_state.get_total_distance_traveled()
            new_subsidized = current_subsidized + distance_km
            new_total = current_total + distance_km

            subsidy_check = self._planning_service.validate_subsidized_distance_limit(
                new_total, new_subsidized
            )
            if not subsidy_check["is_valid"]:
                return False, current_state, None, subsidy_check["message"]

        # Check budget
        if current_state.get_current_budget() < flight_cost:
            return False, current_state, None, \
                   f"Insufficient budget for flight (need ${flight_cost:.2f}, "   \
                   f"have ${current_state.get_current_budget():.2f})"

        current_state.start_flight(origin_route)

        # Execute flight
        current_state.fly_to_airport(
            destination_airport,
            flight_cost,
            flight_time_hours
        )

        current_state.complete_flight()

        # Track distance and subsidized distance
        current_state.add_distance_traveled(distance_km)
        if origin_route.get_is_subsidized():
            current_state.add_subsidized_distance(distance_km)

        # Check if meal is required due to flight duration
        if current_state.get_hours_since_last_meal() >= 8.0:
            meal_cost = current_airport.get_alimentation_cost()
            current_state.update_budget(-meal_cost)
            current_state.reset_meal_timer()
            current_state.add_event(
                event_type="MEAL",
                description="In-flight meal",
                cost=meal_cost,
                time_minutes=30
            )

        # Record decision
        travel_decision = TravelDecision(
            "FLIGHT",
            current_airport_code,
            destination_code
        )
        travel_decision.set_cost_impact(-flight_cost)
        travel_decision.set_time_spent_minutes(int(flight_time_hours * 60))
        travel_decision.add_details({
            "from": current_airport_code,
            "to": destination_code,
            "distance_km": distance_km,
            "flight_time_hours": flight_time_hours,
            "aircraft_type": aircraft_type,
            "is_subsidized": origin_route.get_is_subsidized()
        })

        current_state.add_decision(travel_decision.to_dict())

        return True, current_state, travel_decision, \
               f"Flight to {destination_code} via {aircraft_type} completed "   \
               f"(${flight_cost:.2f}, {flight_time_hours:.1f}h)"

    def _execute_meal_decision(
        self,
        current_state: TravelState,
        decision: dict
    ) -> Tuple[bool, TravelState, TravelDecision, str]:
        """Handle meal (mandatory) decision."""
        airport = current_state.get_current_airport()
        meal_cost = airport.get_alimentation_cost()

        # Check budget
        if current_state.get_current_budget() < meal_cost:
            return False, current_state, None, "Insufficient budget for meal"

        # Execute meal
        current_state.update_budget(-meal_cost)
        current_state.reset_meal_timer()
        current_state.add_time_at_current_airport(0.5)  # Meal takes ~30 minutes

        # Record decision
        travel_decision = TravelDecision(
            "MEAL",
            airport.get_IATA_code(),
            "Meal"
        )
        travel_decision.set_cost_impact(-meal_cost)
        travel_decision.set_time_spent_minutes(30)

        current_state.add_decision(travel_decision.to_dict())
        current_state.add_event(
            event_type="MEAL",
            description="Meal at airport",
            cost=meal_cost,
            time_minutes=30
        )

        return True, current_state, travel_decision, \
               f"Meal purchased at {airport.get_IATA_code()} (${meal_cost:.2f})"

    def _execute_accommodation_decision(
        self,
        current_state: TravelState,
        decision: dict
    ) -> Tuple[bool, TravelState, TravelDecision, str]:
        """Handle accommodation (mandatory) decision."""
        airport = current_state.get_current_airport()
        accommodation_cost = airport.get_accommodation_cost()

        # Check budget
        if current_state.get_current_budget() < accommodation_cost:
            return False, current_state, None, "Insufficient budget for accommodation"

        # Execute accommodation
        current_state.update_budget(-accommodation_cost)
        current_state.reset_accommodation_timer()
        current_state.add_time_at_current_airport(8.0)  # Accommodation = 8 hours sleep

        # Record decision
        travel_decision = TravelDecision(
            "ACCOMMODATION",
            airport.get_IATA_code(),
            "Accommodation"
        )
        travel_decision.set_cost_impact(-accommodation_cost)
        travel_decision.set_time_spent_minutes(480)  # 8 hours

        current_state.add_decision(travel_decision.to_dict())
        current_state.add_event(
            event_type="ACCOMMODATION",
            description="Hotel/lodging at airport",
            cost=accommodation_cost,
            time_minutes=480
        )

        return True, current_state, travel_decision, \
               f"Accommodation booked at {airport.get_IATA_code()} (${accommodation_cost:.2f})"

    # ==================== Journey State Validation ====================

    def can_continue_journey(self, current_state: TravelState) -> bool:
        """
        Check if journey can continue (has budget and flights available).

        Args:
            current_state: Current travel state

        Returns:
            True if journey can continue
        """
        # Need at least some budget
        if current_state.get_current_budget() <= 0:
            return False

        # Check if flights are available
        flights = self._planning_service.calculate_next_flight_options(
            current_state.get_current_airport().get_IATA_code(),
            current_state.get_current_budget()
        )

        return len(flights) > 0

    def get_journey_summary(self, current_state: TravelState) -> dict:
        """
        Get comprehensive summary of journey so far.

        Args:
            current_state: Current travel state

        Returns:
            Dictionary with journey summary
        """
        return {
            "traveler": current_state.get_traveler_name(),
            "status": "active",
            "destination_count": len(current_state.get_destinations_visited()),
            "destinations": current_state.get_destinations_visited(),
            "budget": {
                "initial": round(current_state.get_initial_budget(), 2),
                "current": round(current_state.get_current_budget(), 2),
                "spent": round(current_state.get_total_spent(), 2),
                "earned": round(current_state.get_total_earned(), 2)
            },
            "time": {
                "total_hours": round(current_state.get_total_journey_time(), 2),
                "at_current_airport_hours": round(
                    current_state.get_time_at_current_airport(), 2
                )
            },
            "decisions": len(current_state.get_travel_decisions()),
            "events": len(current_state.get_journey_events()),
            "efficiency": {
                "destinations_per_dollar": round(
                    len(current_state.get_destinations_visited()) /
                    max(1, current_state.get_total_spent()),
                    3
                ),
                "budget_efficiency_score": round(
                    (len(current_state.get_destinations_visited()) * 10) -
                    (current_state.get_total_spent() / 100),
                    1
                )
            }
        }

    def get_service_summary(self) -> str:
        """Get summary of simulator capabilities."""
        return (
            "InteractiveJourneySimulator - Step-by-step interactive journey orchestration\n"
            "- Start journey with flexible budget\n"
            "- Present airport options to traveler\n"
            "- Execute traveler decisions (activities, jobs, flights)\n"
            "- Track budget, time, and decisions\n"
            "- Validate journey continuation\n"
            "- Generate journey summaries"
        )

    def interrupt_route(
        self,
        current_state: TravelState,
        origin_code: str,
        destination_code: str
    ) -> dict:
        self._graph.block_route(
            origin_code,
            destination_code
        )
        return {
            "routeBlocked": True,
            "recalculationRequired": False
        }