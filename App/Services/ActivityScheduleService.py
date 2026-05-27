from typing import List, Optional, Tuple
from App.Models.Airport import Airport
from App.Models.Graph import Graph


class ActivityScheduleService:
    """
    Manages all activities, jobs, and mandatory costs at airports.
    Coordinates activity scheduling, job availability, and cost calculations.
    """

    def __init__(self, graph: Graph) -> None:
        """
        Initialize the activity schedule service.

        Args:
            graph: Graph object containing airport network data
        """
        self._graph: Graph = graph

    # ==================== Mandatory Cost Calculations ====================

    def calculate_mandatory_costs(
        self,
        airport: Airport,
        hours_since_accommodation: float,
        hours_since_meal: float,
        initial_budget: float
    ) -> dict:
        """
        Calculate mandatory costs (accommodation and meals) based on time elapsed.

        Accommodation rule: required if 20 hours have passed since last accommodation
        Meal rule: required if 8 hours have passed since last meal

        Args:
            airport: Current airport
            hours_since_accommodation: Hours elapsed since last accommodation
            hours_since_meal: Hours elapsed since last meal
            initial_budget: Initial budget (used to check if work is needed)

        Returns:
            Dictionary with mandatory costs and requirements
        """
        accommodation_needed = hours_since_accommodation >= 20.0
        meal_needed = hours_since_meal >= 8.0

        accommodation_cost = 0.0
        meal_cost = 0.0

        # Calculate accommodation cost if needed
        if accommodation_needed:
            accommodation_cost = airport.get_accommodation_cost()

        # Calculate meal cost if needed
        if meal_needed:
            meal_cost = airport.get_alimentation_cost()

        # Determine if work is urgently needed (budget below 35% of initial)
        budget_critical = (accommodation_cost + meal_cost) > initial_budget * 0.35

        return {
            "accommodation": {
                "needed": accommodation_needed,
                "cost": accommodation_cost,
                "hours_until_needed": max(0, 20.0 - hours_since_accommodation)
            },
            "meal": {
                "needed": meal_needed,
                "cost": meal_cost,
                "hours_until_needed": max(0, 8.0 - hours_since_meal)
            },
            "total_mandatory_cost": accommodation_cost + meal_cost,
            "budget_critical": budget_critical
        }

    # ==================== Activity Availability ====================

    def get_available_activities(self, airport: Airport) -> List[dict]:
        """
        Get all optional activities available at an airport.

        Args:
            airport: The airport

        Returns:
            List of available activities with their details
        """
        activities = []

        for activity in airport.get_activities():
            # Only return optional activities (skip mandatory ones)
            if activity.get_type() == "mandatory":
                continue

            activity_dict = {
                "id": f"act_{len(activities)}",
                "name": activity.get_name(),
                "type": activity.get_type(),
                "duration_min": activity.get_duration_per_minutes(),
                "cost": activity.get_cost_in_USD(),
                "description": f"{activity.get_name()} - "
                              f"{activity.get_duration_per_minutes()} min "
                              f"(${activity.get_cost_in_USD():.2f})"
            }
            activities.append(activity_dict)

        return activities

    def get_available_jobs(self, airport: Airport, current_budget: float, initial_budget: float) -> List[dict]:
        """
        Get all job opportunities available at an airport.

        Args:
            airport: The airport
            current_budget: Current traveler budget
            initial_budget: Initial traveler budget

        Returns:
            List of available jobs with their details
        """
        jobs = []
        is_locked = current_budget >= (initial_budget * 0.35)

        for job in airport.get_jobs():
            job_dict = {
                "id": f"job_{len(jobs)}",
                "name": job.get_name(),
                "hourly_rate": job.get_hourly_rate(),
                "max_hours": job.get_max_hours(),
                "is_locked": is_locked,
                "lock_reason": "Budget must be below 35% to work" if is_locked else None,
                "description": f"{job.get_name()} - "
                              f"${job.get_hourly_rate():.2f}/hour "
                              f"(max {job.get_max_hours()}h)"
            }
            jobs.append(job_dict)

        return jobs

    # ==================== Time Availability ====================

    def calculate_available_time_at_airport(
        self,
        minimum_stay_minutes: int,
        scheduled_items_duration_minutes: int = 0
    ) -> dict:
        """
        Calculate available time for activities/work at an airport.

        Args:
            minimum_stay_minutes: Minimum time required to stay
            scheduled_items_duration_minutes: Minutes already scheduled

        Returns:
            Dictionary with time availability information
        """
        available_minutes = minimum_stay_minutes - scheduled_items_duration_minutes
        available_hours = available_minutes / 60

        return {
            "minimum_stay_minutes": minimum_stay_minutes,
            "minimum_stay_hours": minimum_stay_minutes / 60,
            "scheduled_minutes": scheduled_items_duration_minutes,
            "scheduled_hours": scheduled_items_duration_minutes / 60,
            "available_minutes": max(0, available_minutes),
            "available_hours": max(0, available_hours),
            "time_remaining_percentage": (available_minutes / minimum_stay_minutes * 100)
                                        if minimum_stay_minutes > 0 else 0
        }

    # ==================== Activity Combination Suggestions ====================

    def suggest_activity_combinations(
        self,
        available_time_minutes: int,
        current_budget: float,
        optional_activities: List[dict]
    ) -> List[dict]:
        """
        Suggest feasible combinations of activities using dynamic programming (knapsack).

        Goal: Maximize activity count within time and budget constraints.

        Args:
            available_time_minutes: Available time for activities
            current_budget: Available budget
            optional_activities: List of available activities

        Returns:
            List of suggested combinations, sorted by feasibility
        """
        if not optional_activities or available_time_minutes <= 0 or current_budget <= 0:
            return []

        # Filter activities that fit budget and time constraints
        feasible = [
            act for act in optional_activities
            if act["cost"] <= current_budget and act["duration_min"] <= available_time_minutes
        ]

        if not feasible:
            return []

        # Generate single-activity suggestions (greedy approach)
        suggestions = []

        # Sort by cost efficiency (lowest cost first)
        sorted_by_cost = sorted(feasible, key=lambda x: x["cost"])

        for activity in sorted_by_cost:
            suggestion = {
                "activities": [activity["name"]],
                "activity_ids": [activity["id"]],
                "total_cost": activity["cost"],
                "total_time_minutes": activity["duration_min"],
                "free_time_remaining": available_time_minutes - activity["duration_min"],
                "activity_count": 1,
                "efficiency_score": activity["duration_min"] / max(0.1, activity["cost"])
            }
            suggestions.append(suggestion)

        # Generate multi-activity combinations (simple pairing)
        for i, act1 in enumerate(sorted_by_cost):
            for act2 in sorted_by_cost[i + 1:]:
                total_cost = act1["cost"] + act2["cost"]
                total_time = act1["duration_min"] + act2["duration_min"]

                if total_cost <= current_budget and total_time <= available_time_minutes:
                    suggestion = {
                        "activities": [act1["name"], act2["name"]],
                        "activity_ids": [act1["id"], act2["id"]],
                        "total_cost": total_cost,
                        "total_time_minutes": total_time,
                        "free_time_remaining": available_time_minutes - total_time,
                        "activity_count": 2,
                        "efficiency_score": total_time / max(0.1, total_cost)
                    }
                    suggestions.append(suggestion)

        # Sort suggestions by activity count (descending) then by cost (ascending)
        suggestions.sort(
            key=lambda x: (-x["activity_count"], x["total_cost"])
        )

        return suggestions[:10]  # Return top 10 suggestions

    # ==================== Job Selection ====================

    def select_best_job(
        self,
        available_jobs: List[dict],
        available_time_hours: float
    ) -> Optional[dict]:
        """
        Select the best job based on hourly rate.

        Args:
            available_jobs: List of available jobs
            available_time_hours: Hours available for work

        Returns:
            Best job with max hours capped to available time, or None
        """
        if not available_jobs or available_time_hours <= 0:
            return None

        # Select job with highest hourly rate
        best_job = max(available_jobs, key=lambda j: j["hourly_rate"])

        # Cap work hours to what's available
        actual_hours = min(best_job["max_hours"], available_time_hours)

        if actual_hours <= 0:
            return None

        return {
            "job_name": best_job["name"],
            "hourly_rate": best_job["hourly_rate"],
            "hours_to_work": actual_hours,
            "total_earnings": actual_hours * best_job["hourly_rate"],
            "time_minutes": int(actual_hours * 60)
        }

    # ==================== Next Flight Options ====================

    def calculate_next_flight_options(
        self,
        origin_airport_code: str,
        current_budget: float,
        max_suggestions: int = 10
    ) -> List[dict]:
        """
        Calculate available flight options from current airport.
        Returns direct routes with all available aircraft options.

        Args:
            origin_airport_code: IATA code of current airport
            current_budget: Current budget
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of feasible flight options with aircraft details
        """
        origin_airport = self._graph.find_airport_by_iata(origin_airport_code)
        if not origin_airport:
            return []

        flights = []

        # In interactive mode, we typically look at direct connections (adjacencies)
        for route in origin_airport.get_adjacencies():
            if route.is_blocked():
                continue
                
            destination = route.get_destiny_airport()
            dest_code = destination.get_IATA_code()

            aircraft_options = []
            for aircraft in route.get_aircraft():
                cost = route._calculate_cost(aircraft)
                time_mins = route._calculate_time(aircraft)
                
                # Only include if traveler can afford it
                if cost <= current_budget:
                    aircraft_options.append({
                        "id": aircraft.get_id(),
                        "type": aircraft.get_type(),
                        "cost": round(cost, 2),
                        "time_mins": round(time_mins, 2),
                        "time_hours": round(time_mins / 60, 2)
                    })

            if not aircraft_options:
                continue

            flight_dict = {
                "destination": dest_code,
                "destination_name": destination.get_name(),
                "distance_km": route.get_distance_in_km(),
                "city": destination.get_city(),
                "country": destination.get_country(),
                "minimum_stay_hours": round(route.get_minimum_stay() / 60, 2),
                "is_subsidized": route.get_is_subsidized(),
                "aircraft_options": aircraft_options
            }

            flights.append(flight_dict)

        # Sort by distance or destination name
        flights.sort(key=lambda f: f["destination"])

        return flights[:max_suggestions]

    # ==================== Subsidized Route Validation ====================

    def validate_subsidized_distance_limit(
        self,
        total_distance_traveled: float,
        subsidized_distance_traveled: float
    ) -> dict:
        """
        Validate that subsidized routes don't exceed 20% of total distance.
        Restriction: Max 20% of total journey distance can use subsidized (free) routes.

        Args:
            total_distance_traveled: Total kilometers traveled
            subsidized_distance_traveled: Kilometers traveled on subsidized routes

        Returns:
            Dictionary with validation result and percentage used
        """
        if total_distance_traveled == 0:
            return {
                "is_valid": True,
                "percentage_used": 0,
                "limit_exceeded": False,
                "message": "No distance traveled yet"
            }

        percentage_used = (subsidized_distance_traveled / total_distance_traveled) * 100
        limit_exceeded = percentage_used > 20.0

        return {
            "is_valid": not limit_exceeded,
            "percentage_used": round(percentage_used, 2),
            "limit_exceeded": limit_exceeded,
            "subsidized_distance": round(subsidized_distance_traveled, 2),
            "total_distance": round(total_distance_traveled, 2),
            "message": (
                f"Subsidized routes: {percentage_used:.1f}% (limit: 20%)"
                if not limit_exceeded
                else f"Cannot use subsidized route - would exceed 20% limit ({percentage_used:.1f}%)"
            )
        }

    def get_aircraft_for_distance(
        self,
        route_distance_km: float,
        available_aircraft: List[dict]
    ) -> List[dict]:
        """
        Filter aircraft by distance restrictions (Regional max 2000km, Hélice max 1000km).

        Args:
            route_distance_km: Distance of the route in kilometers
            available_aircraft: List of available aircraft with costs

        Returns:
            Filtered list of aircraft that can handle this distance
        """
        filtered_aircraft = []

        for aircraft in available_aircraft:
            aircraft_type = aircraft.get("type")

            if aircraft_type == "Avion Comercial":
                # No distance limit
                filtered_aircraft.append(aircraft)
            elif aircraft_type == "Avion Regional" and route_distance_km <= 2000:
                filtered_aircraft.append(aircraft)
            elif aircraft_type == "Helice" and route_distance_km <= 1000:
                filtered_aircraft.append(aircraft)

        return filtered_aircraft

    # ==================== Helper Methods ====================

    def _find_route(
        self,
        origin_code: str,
        destination_code: str
    ) -> Optional:
        """
        Find direct route between two airports.

        Args:
            origin_code: Origin airport IATA code
            destination_code: Destination airport IATA code

        Returns:
            Route object if found, None otherwise
        """
        # Use Dijkstra to find connection cost (more reliable than direct route lookup)
        result = self._graph.dijkstra(origin_code, destination_code, criterion="cost")

        if result.get("path"):
            return {
                "origin": origin_code,
                "destination": destination_code,
                "cost": result.get("totalWeight", 0),
                "distance_km": result.get("distance", 0)
            }

        return None

    def get_service_summary(self) -> str:
        """
        Get summary of service capabilities.

        Returns:
            String describing service capabilities
        """
        return (
            "ActivityScheduleService - Manages airport activities, jobs, and costs\n"
            "- Calculate mandatory costs (accommodation, meals)\n"
            "- List optional activities and job opportunities\n"
            "- Calculate available time at airport\n"
            "- Suggest activity combinations\n"
            "- Select best job for income generation\n"
            "- Find next flight options"
        )
