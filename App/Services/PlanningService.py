import math
from typing import List, Optional
from collections import deque

from App.Models.Graph import Graph
from App.Models.TravelDecision import TravelDecision
from App.Models.TravelState import TravelState
from App.Services.DetailedJourneyReportService import DetailedJourneyReportService


class PlanningService:
    """
    Service responsible for route planning, optimization,
    budget/time-constrained travel simulation, and job management.
    """

    def __init__(self, graph: Graph) -> None:
        """
        Initializes the planning service with a graph instance.

        Args:
            graph (Graph): Graph containing airports and routes.
        """
        self._graph = graph

    def calculate_best_route(
        self,
        origin_iata: str,
        destination_iata: str,
        criteria: List[str],
        include_secondary_airports: bool = True,
        allowed_aircraft_types: Optional[List[str]] = None
    ) -> dict:
        """
        Calculates the best route between two airports using multiple criteria.

        Each criterion is evaluated independently using Dijkstra's algorithm.

        Args:
            origin_iata (str): Starting airport IATA code.
            destination_iata (str): Destination airport IATA code.
            criteria (List[str]): Optimization criteria (e.g., cost, time).
            include_secondary_airports (bool): Whether to include non-hub airports.
            allowed_aircraft_types (Optional[List[str]]): Filter by aircraft types.

        Returns:
            dict: Dictionary containing results per optimization criterion.
        """
        results = {}

        for criterion in criteria:
            results[criterion] = self._graph.dijkstra(
                origin_iata,
                destination_iata,
                criterion,
                include_secondary_airports,
                allowed_aircraft_types
            )

        return results

    def calculate_max_destinations_by_budget(
        self,
        origin_iata: str,
        initial_budget: float,
        include_secondary_airports: bool = True,
        allowed_aircraft_types: Optional[List[str]] = None
    ) -> dict:
        """
        Calculates the maximum number of destinations reachable within a budget constraint.

        Args:
            origin_iata (str): Starting airport IATA code.
            initial_budget (float): Maximum allowed budget.
            include_secondary_airports (bool): Whether to include non-hub airports.
            allowed_aircraft_types (Optional[List[str]]): Aircraft restrictions.

        Returns:
            dict: Travel simulation results under budget constraint.
        """
        return self._calculate_max_destinations(
            origin_iata=origin_iata,
            limit=initial_budget,
            criterion="cost",
            include_secondary_airports=include_secondary_airports,
            allowed_aircraft_types=allowed_aircraft_types
        )

    def calculate_max_destinations_by_time(
        self,
        origin_iata: str,
        available_hours: float,
        include_secondary_airports: bool = True,
        allowed_aircraft_types: Optional[List[str]] = None
    ) -> dict:
        """
        Calculates the maximum number of destinations reachable within a time constraint.

        Args:
            origin_iata (str): Starting airport IATA code.
            available_hours (float): Total available travel time in hours.
            include_secondary_airports (bool): Whether to include non-hub airports.
            allowed_aircraft_types (Optional[List[str]]): Aircraft restrictions.

        Returns:
            dict: Travel simulation results under time constraint.
        """
        available_minutes = available_hours * 60

        return self._calculate_max_destinations(
            origin_iata=origin_iata,
            limit=available_minutes,
            criterion="time",
            include_secondary_airports=include_secondary_airports,
            allowed_aircraft_types=allowed_aircraft_types
        )

    def interrupt_route_and_recalculate(
        self,
        blocked_origin_iata: str,
        blocked_destination_iata: str,
        current_origin_iata: str,
        final_destination_iata: str,
        criterion: str,
        include_secondary_airports: bool = True,
        allowed_aircraft_types: Optional[List[str]] = None
    ) -> dict:
        """
        Blocks a route and recalculates a new optimal path.

        Args:
            blocked_origin_iata (str): Origin of blocked route.
            blocked_destination_iata (str): Destination of blocked route.
            current_origin_iata (str): Current position of the traveler.
            final_destination_iata (str): Final travel destination.
            criterion (str): Optimization criterion (cost or time).
            include_secondary_airports (bool): Include non-hub airports.
            allowed_aircraft_types (Optional[List[str]]): Aircraft restrictions.

        Returns:
            dict: Status of block operation and new computed route.
        """
        was_blocked = self._graph.block_route(
            blocked_origin_iata,
            blocked_destination_iata
        )

        if not was_blocked:
            return {
                "wasBlocked": False,
                "message": "The selected route does not exist.",
                "newRoute": None
            }

        new_route = self._graph.dijkstra(
            current_origin_iata,
            final_destination_iata,
            criterion,
            include_secondary_airports,
            allowed_aircraft_types
        )

        return {
            "wasBlocked": True,
            "message": "The route was blocked and the itinerary was recalculated.",
            "newRoute": new_route
        }

    def _calculate_max_destinations(
        self,
        origin_iata: str,
        limit: float,
        criterion: str,
        include_secondary_airports: bool,
        allowed_aircraft_types: Optional[List[str]]
    ) -> dict:
        """
        Internal greedy algorithm to maximize reachable destinations
        under a budget or time constraint.

        Args:
            origin_iata (str): Starting airport.
            limit (float): Maximum allowed cost/time.
            criterion (str): Optimization criterion.
            include_secondary_airports (bool): Include non-hub airports.
            allowed_aircraft_types (Optional[List[str]]): Aircraft restrictions.

        Returns:
            dict: Travel simulation result including visited nodes and total cost.
        """
        origin_airport = self._graph.find_airport_by_iata(origin_iata)

        if origin_airport is None:
            raise ValueError(f"Origin airport '{origin_iata}' does not exist.")

        visited = [origin_iata]
        segments = []
        total_weight = 0.0
        current_iata = origin_iata

        while True:
            best_option = self._find_best_next_destination(
                current_iata=current_iata,
                visited=visited,
                remaining_limit=limit - total_weight,
                criterion=criterion,
                include_secondary_airports=include_secondary_airports,
                allowed_aircraft_types=allowed_aircraft_types
            )

            if best_option is None:
                break

            route_result = best_option["routeResult"]
            destination_iata = best_option["destination"]

            total_weight += route_result["totalWeight"]
            visited.append(destination_iata)
            segments.extend(route_result["segments"])
            current_iata = destination_iata

        return {
            "origin": origin_iata,
            "criterion": criterion,
            "visitedDestinations": visited,
            "totalVisited": len(visited) - 1,
            "totalWeight": total_weight,
            "remainingLimit": limit - total_weight,
            "segments": segments
        }

    def _find_best_next_destination(
        self,
        current_iata: str,
        visited: List[str],
        remaining_limit: float,
        criterion: str,
        include_secondary_airports: bool,
        allowed_aircraft_types: Optional[List[str]]
    ) -> Optional[dict]:
        """
        Finds the best next destination using a greedy selection strategy
        based on the selected optimization criterion.

        Args:
            current_iata (str): Current airport.
            visited (List[str]): Already visited airports.
            remaining_limit (float): Remaining budget/time.
            criterion (str): Optimization criterion.
            include_secondary_airports (bool): Include non-hub airports.
            allowed_aircraft_types (Optional[List[str]]): Aircraft restrictions.

        Returns:
            Optional[dict]: Best next destination and its route data.
        """
        best_option = None
        best_weight = math.inf

        for airport in self._graph.get_airports():
            destination_iata = airport.get_IATA_code()

            if destination_iata in visited:
                continue

            if not include_secondary_airports and not airport.get_isHub():
                continue

            route_result = self._graph.dijkstra(
                current_iata,
                destination_iata,
                criterion,
                include_secondary_airports,
                allowed_aircraft_types
            )

            total_weight = route_result["totalWeight"]

            if total_weight == math.inf:
                continue

            if total_weight > remaining_limit:
                continue

            if total_weight < best_weight:
                best_weight = total_weight
                best_option = {
                    "destination": destination_iata,
                    "routeResult": route_result
                }

        return best_option

    # ==================== Dynamic Budget Route Planning ====================

    def find_optimal_destination_sequence(
        self,
        origin_airport_code: str,
        initial_budget: float,
        max_destinations: int = 10,
        exploration_depth: int = 50
    ) -> List[dict]:
        """
        Find optimal destination sequences given an origin and a budget.

        Uses a breadth-first exploration through the airport graph and prunes
        infeasible or dominated paths based on budget constraints.
        """
        origin = self._graph.find_airport_by_iata(origin_airport_code)
        if not origin:
            return []

        queue = deque([
            (origin_airport_code, [origin_airport_code], 0.0, 0)
        ])
        suggested_routes = []
        iterations = 0

        while queue and iterations < exploration_depth:
            current_airport, visited, spent, depth = queue.popleft()

            if depth >= max_destinations:
                iterations += 1
                continue

            current_airport_obj = self._graph.find_airport_by_iata(current_airport)
            if not current_airport_obj:
                iterations += 1
                continue

            for destination in self._graph.get_airports():
                dest_code = destination.get_IATA_code()
                if dest_code in visited:
                    continue

                flight_result = self._graph.dijkstra(
                    current_airport,
                    dest_code,
                    criterion="cost"
                )

                if not flight_result.get("path"):
                    continue

                flight_cost = flight_result.get("totalWeight", 0)
                new_spent = spent + flight_cost

                if new_spent > initial_budget:
                    continue

                new_visited = visited + [dest_code]
                route_score = self._evaluate_route(new_visited, new_spent, initial_budget)

                suggested_routes.append({
                    "route": new_visited,
                    "destinations_visited": len(new_visited),
                    "total_cost": new_spent,
                    "remaining_budget": initial_budget - new_spent,
                    "score": route_score,
                    "efficiency": len(new_visited) / max(1, new_spent)
                })

                if depth < max_destinations - 1:
                    queue.append((dest_code, new_visited, new_spent, depth + 1))

            iterations += 1

        suggested_routes.sort(key=lambda r: r["score"], reverse=True)
        return suggested_routes[:10]

    def _evaluate_route(
        self,
        route: List[str],
        total_cost: float,
        initial_budget: float
    ) -> float:
        destinations_count = len(route)
        base_score = (destinations_count * 10) - (total_cost / 100)
        budget_efficiency = ((initial_budget - total_cost) / initial_budget) if initial_budget > 0 else 0
        efficiency_bonus = budget_efficiency * 5
        destinations_bonus = destinations_count * 2
        return base_score + efficiency_bonus + destinations_bonus

    def suggest_budget_checkpoints(
        self,
        route: List[str],
        initial_budget: float
    ) -> List[dict]:
        checkpoints = []
        current_budget = initial_budget
        critical_threshold = initial_budget * 0.35

        for i, airport_code in enumerate(route):
            airport = self._graph.find_airport_by_iata(airport_code)
            if not airport:
                continue

            min_accommodation = airport.get_accommodation_cost()
            min_meal = airport.get_alimentation_cost()
            estimated_minimum = min_accommodation + min_meal

            if current_budget < critical_threshold:
                jobs = airport.get_jobs()
                best_job = max(jobs, key=lambda j: j.get_hourly_rate()) if jobs else None

                checkpoints.append({
                    "airport": airport_code,
                    "position": i,
                    "budget_level": current_budget,
                    "is_critical": True,
                    "recommendation": f"Work at {airport_code}" if best_job else "Consider staying longer",
                    "best_job": best_job.get_name() if best_job else None,
                    "hourly_rate": best_job.get_hourly_rate() if best_job else 0
                })

                if best_job:
                    earnings = best_job.get_hourly_rate() * 5
                    current_budget += earnings

            current_budget -= estimated_minimum

        return checkpoints

    def calculate_mandatory_costs(
        self,
        airport,
        hours_since_accommodation: float,
        hours_since_meal: float,
        initial_budget: float
    ) -> dict:
        accommodation_needed = hours_since_accommodation >= 20.0
        meal_needed = hours_since_meal >= 8.0

        accommodation_cost = airport.get_accommodation_cost() if accommodation_needed else 0.0
        meal_cost = airport.get_alimentation_cost() if meal_needed else 0.0

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

    def get_available_activities(self, airport) -> List[dict]:
        activities = []

        for activity in airport.get_activities():
            if activity.get_type() == "mandatory":
                continue

            activities.append({
                "id": f"act_{len(activities)}",
                "name": activity.get_name(),
                "type": activity.get_type(),
                "duration_min": activity.get_duration_per_minutes(),
                "cost": activity.get_cost_in_USD(),
                "description": (
                    f"{activity.get_name()} - "
                    f"{activity.get_duration_per_minutes()} min "
                    f"(${activity.get_cost_in_USD():.2f})"
                )
            })

        return activities

    def get_available_jobs(self, airport, current_budget: float, initial_budget: float) -> List[dict]:
        jobs = []
        is_locked = current_budget >= (initial_budget * 0.35)

        for job in airport.get_jobs():
            jobs.append({
                "id": f"job_{len(jobs)}",
                "name": job.get_name(),
                "hourly_rate": job.get_hourly_rate(),
                "max_hours": job.get_max_hours(),
                "is_locked": is_locked,
                "lock_reason": "Budget must be below 35% to work" if is_locked else None,
                "description": (
                    f"{job.get_name()} - ${job.get_hourly_rate():.2f}/hour "
                    f"(max {job.get_max_hours()}h)"
                )
            })

        return jobs

    def calculate_available_time_at_airport(
        self,
        minimum_stay_minutes: int,
        scheduled_items_duration_minutes: int = 0
    ) -> dict:
        available_minutes = minimum_stay_minutes - scheduled_items_duration_minutes
        available_hours = available_minutes / 60

        return {
            "minimum_stay_minutes": minimum_stay_minutes,
            "minimum_stay_hours": minimum_stay_minutes / 60,
            "scheduled_minutes": scheduled_items_duration_minutes,
            "scheduled_hours": scheduled_items_duration_minutes / 60,
            "available_minutes": max(0, available_minutes),
            "available_hours": max(0, available_hours),
            "time_remaining_percentage": (
                available_minutes / minimum_stay_minutes * 100
                if minimum_stay_minutes > 0 else 0
            )
        }

    def suggest_activity_combinations(
        self,
        available_time_minutes: int,
        current_budget: float,
        optional_activities: List[dict]
    ) -> List[dict]:
        if not optional_activities or available_time_minutes <= 0 or current_budget <= 0:
            return []

        feasible = [
            act for act in optional_activities
            if act["cost"] <= current_budget and act["duration_min"] <= available_time_minutes
        ]

        if not feasible:
            return []

        suggestions = []
        sorted_by_cost = sorted(feasible, key=lambda x: x["cost"])

        for activity in sorted_by_cost:
            suggestions.append({
                "activities": [activity["name"]],
                "activity_ids": [activity["id"]],
                "total_cost": activity["cost"],
                "total_time_minutes": activity["duration_min"],
                "free_time_remaining": available_time_minutes - activity["duration_min"],
                "activity_count": 1,
                "efficiency_score": activity["duration_min"] / max(0.1, activity["cost"])
            })

        for i, act1 in enumerate(sorted_by_cost):
            for act2 in sorted_by_cost[i + 1:]:
                total_cost = act1["cost"] + act2["cost"]
                total_time = act1["duration_min"] + act2["duration_min"]

                if total_cost <= current_budget and total_time <= available_time_minutes:
                    suggestions.append({
                        "activities": [act1["name"], act2["name"]],
                        "activity_ids": [act1["id"], act2["id"]],
                        "total_cost": total_cost,
                        "total_time_minutes": total_time,
                        "free_time_remaining": available_time_minutes - total_time,
                        "activity_count": 2,
                        "efficiency_score": total_time / max(0.1, total_cost)
                    })

        suggestions.sort(key=lambda x: (-x["activity_count"], x["total_cost"]))
        return suggestions[:10]

    def select_best_job(
        self,
        available_jobs: List[dict],
        available_time_hours: float
    ) -> Optional[dict]:
        if not available_jobs or available_time_hours <= 0:
            return None

        best_job = max(available_jobs, key=lambda j: j["hourly_rate"])
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

    def calculate_next_flight_options(
        self,
        origin_airport_code: str,
        current_budget: float,
        max_suggestions: int = 10
    ) -> List[dict]:
        origin_airport = self._graph.find_airport_by_iata(origin_airport_code)
        if not origin_airport:
            return []

        flights = []

        for route in origin_airport.get_adjacencies():
            if route.is_blocked():
                continue

            destination = route.get_destiny_airport()
            dest_code = destination.get_IATA_code()
            aircraft_options = []

            for aircraft in route.get_aircraft():
                cost = route._calculate_cost(aircraft)
                time_mins = route._calculate_time(aircraft)
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

            flights.append({
                "destination": dest_code,
                "destination_name": destination.get_name(),
                "distance_km": route.get_distance_in_km(),
                "city": destination.get_city(),
                "country": destination.get_country(),
                "minimum_stay_hours": round(route.get_minimum_stay() / 60, 2),
                "is_subsidized": route.get_is_subsidized(),
                "aircraft_options": aircraft_options
            })

        flights.sort(key=lambda f: f["destination"])
        return flights[:max_suggestions]

    def validate_subsidized_distance_limit(
        self,
        total_distance_traveled: float,
        subsidized_distance_traveled: float
    ) -> dict:
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
        filtered_aircraft = []

        for aircraft in available_aircraft:
            aircraft_type = aircraft.get("type")
            if aircraft_type == "Avion Comercial":
                filtered_aircraft.append(aircraft)
            elif aircraft_type == "Avion Regional" and route_distance_km <= 2000:
                filtered_aircraft.append(aircraft)
            elif aircraft_type == "Helice" and route_distance_km <= 1000:
                filtered_aircraft.append(aircraft)

        return filtered_aircraft

    def simulate_trip(
        self,
        origin_iata: str,
        destination_iata: str,
        initial_budget: float,
        available_hours: float,
        selected_job=None,
        hours_worked: float = 0,
        criterion: str = "cost",
        include_secondary_airports: bool = True,
        allowed_aircraft_types: Optional[List[str]] = None
    ) -> dict:
        """
        Simulate a trip from origin to destination under budget and time constraints.

        Uses TravelState to record flights, activities, meals, accommodation, and work,
        then generates a detailed report using DetailedJourneyReportService.
        """
        available_minutes = available_hours * 60

        origin_airport = self._graph.find_airport_by_iata(origin_iata)
        if origin_airport is None:
            return {
                "success": False,
                "message": f"Origin airport '{origin_iata}' not found.",
                "report": {}
            }

        travel_state = TravelState(
            origin_airport,
            initial_budget,
            "Simulation Traveler",
            available_hours
        )

        route_result = self._graph.dijkstra(
            origin_iata,
            destination_iata,
            criterion,
            include_secondary_airports,
            allowed_aircraft_types
        )

        if not route_result["path"]:
            return {
                "success": False,
                "message": "No available route was found.",
                "report": DetailedJourneyReportService.generate_complete_report([travel_state])
            }

        for segment in route_result["segments"]:
            if segment["cost"] > travel_state.get_current_budget():
                return {
                    "success": False,
                    "message": "The trip stopped because the budget was not enough.",
                    "report": DetailedJourneyReportService.generate_complete_report([travel_state])
                }

            if segment["time"] > available_minutes:
                return {
                    "success": False,
                    "message": "The trip stopped because the available time was not enough.",
                    "report": DetailedJourneyReportService.generate_complete_report([travel_state])
                }

            destination_airport = self._graph.find_airport_by_iata(
                segment["destination"]
            )
            if destination_airport is None:
                continue

            travel_state.fly_to_airport(
                destination_airport,
                segment["cost"],
                segment["time"] / 60
            )
            available_minutes -= segment["time"]

            destination_result = self._process_destination(
                travel_state=travel_state,
                initial_budget=initial_budget,
                available_minutes=available_minutes,
                selected_job=selected_job,
                hours_worked=hours_worked
            )

            available_minutes = destination_result["availableMinutes"]

            if available_minutes < 0:
                return {
                    "success": False,
                    "message": "The trip stopped because the available time was exhausted.",
                    "report": DetailedJourneyReportService.generate_complete_report([travel_state])
                }

        return {
            "success": True,
            "message": "The trip was completed successfully.",
            "remainingBudget": round(travel_state.get_current_budget(), 2),
            "remainingTimeMinutes": round(available_minutes, 2),
            "report": DetailedJourneyReportService.generate_complete_report([travel_state])
        }

    def _process_destination(
        self,
        travel_state: TravelState,
        initial_budget: float,
        available_minutes: float,
        selected_job=None,
        hours_worked: float = 0
    ) -> dict:
        destination_time = 0.0
        destination_cost = 0.0
        airport = travel_state.get_current_airport()

        food_result = self._apply_food_if_possible(travel_state, available_minutes)
        destination_cost += food_result["cost"]
        destination_time += food_result["time"]
        available_minutes = food_result["availableMinutes"]

        activities_result = self._apply_optional_activities(travel_state, available_minutes)
        destination_cost += activities_result["cost"]
        destination_time += activities_result["time"]
        available_minutes = activities_result["availableMinutes"]

        if selected_job is not None and self._verify_budget(initial_budget, travel_state.get_current_budget()):
            job_result = self.apply_selected_job(
                travel_state,
                selected_job,
                available_minutes,
                hours_worked
            )
            destination_time += job_result["time"]
            available_minutes = job_result["availableMinutes"]

        if destination_cost > 0 or destination_time > 0:
            travel_state.add_event(
                event_type="DESTINATION",
                description=f"Processed destination {airport.get_IATA_code()}",
                cost=destination_cost,
                time_minutes=destination_time
            )

        return {
            "currentBudget": travel_state.get_current_budget(),
            "availableMinutes": available_minutes
        }

    def apply_selected_job(
        self,
        travel_state: TravelState,
        selected_job,
        available_minutes: float,
        hours_worked: float
    ) -> dict:
        airport = travel_state.get_current_airport()

        if selected_job not in airport.get_jobs():
            return {
                "availableMinutes": available_minutes,
                "time": 0
            }

        worked_hours = min(hours_worked, selected_job.get_max_hours())
        if worked_hours <= 0 or available_minutes < worked_hours * 60:
            return {
                "availableMinutes": available_minutes,
                "time": 0
            }

        earnings = worked_hours * selected_job.get_hourly_rate()
        travel_state.add_time_at_current_airport(worked_hours)
        travel_state.update_budget(earnings)

        travel_decision = TravelDecision(
            "JOB",
            airport.get_IATA_code(),
            selected_job.get_name()
        )
        travel_decision.set_cost_impact(earnings)
        travel_decision.set_time_spent_minutes(int(worked_hours * 60))
        travel_decision.add_details({
            "hourly_rate": selected_job.get_hourly_rate(),
            "hours_worked": worked_hours,
            "earnings": earnings
        })
        travel_state.add_decision(travel_decision.to_dict())
        travel_state.add_event(
            event_type="JOB",
            description=f"Worked {selected_job.get_name()} for {worked_hours}h",
            cost=-earnings,
            time_minutes=int(worked_hours * 60)
        )

        return {
            "availableMinutes": available_minutes - worked_hours * 60,
            "time": worked_hours * 60
        }

    def _apply_food_if_possible(
        self,
        travel_state: TravelState,
        available_minutes: float
    ) -> dict:
        airport = travel_state.get_current_airport()
        food_cost = airport.get_alimentation_cost()
        food_time = 30

        if travel_state.get_current_budget() < food_cost or available_minutes < food_time:
            return {
                "availableMinutes": available_minutes,
                "cost": 0,
                "time": 0
            }

        travel_state.update_budget(-food_cost)
        travel_state.reset_meal_timer()
        travel_state.add_time_at_current_airport(food_time / 60)

        travel_decision = TravelDecision(
            "MEAL",
            airport.get_IATA_code(),
            "Food"
        )
        travel_decision.set_cost_impact(-food_cost)
        travel_decision.set_time_spent_minutes(food_time)
        travel_state.add_decision(travel_decision.to_dict())
        travel_state.add_event(
            event_type="MEAL",
            description="Meal at destination",
            cost=food_cost,
            time_minutes=food_time
        )

        return {
            "availableMinutes": available_minutes - food_time,
            "cost": food_cost,
            "time": food_time
        }

    def _apply_optional_activities(
        self,
        travel_state: TravelState,
        available_minutes: float
    ) -> dict:
        airport = travel_state.get_current_airport()
        total_cost = 0.0
        total_time = 0.0

        for activity in airport.get_activities():
            if activity.get_type() == "mandatory":
                continue

            cost = activity.get_cost_in_USD()
            duration = activity.get_duration_per_minutes()

            if travel_state.get_current_budget() >= cost and available_minutes >= duration:
                travel_state.update_budget(-cost)
                travel_state.add_time_at_current_airport(duration / 60)
                total_cost += cost
                total_time += duration

                travel_decision = TravelDecision(
                    "ACTIVITY",
                    airport.get_IATA_code(),
                    activity.get_name()
                )
                travel_decision.set_cost_impact(-cost)
                travel_decision.set_time_spent_minutes(duration)
                travel_decision.add_detail("activity_type", activity.get_type())
                travel_state.add_decision(travel_decision.to_dict())
                travel_state.add_event(
                    event_type="ACTIVITY",
                    description=activity.get_name(),
                    cost=cost,
                    time_minutes=duration
                )

                available_minutes -= duration

        return {
            "availableMinutes": available_minutes,
            "cost": total_cost,
            "time": total_time
        }

    def _verify_budget(self, budget, actual_budget) -> bool:
        return actual_budget < (budget * 0.35)

    def compare_routes(self, route1: dict, route2: dict) -> str:
        r1_destinations = route1.get("destinations_visited", 0)
        r1_cost = route1.get("total_cost", 0)
        r1_efficiency = route1.get("efficiency", 0)
        r2_destinations = route2.get("destinations_visited", 0)
        r2_cost = route2.get("total_cost", 0)
        r2_efficiency = route2.get("efficiency", 0)

        comparison = (
            f"Route 1: {r1_destinations} destinations, ${r1_cost:.2f}, "
            f"efficiency {r1_efficiency:.3f}\n"
            f"Route 2: {r2_destinations} destinations, ${r2_cost:.2f}, "
            f"efficiency {r2_efficiency:.3f}\n"
        )

        if r1_destinations > r2_destinations:
            comparison += f"Route 1 visits {r1_destinations - r2_destinations} more destinations"
        elif r2_destinations > r1_destinations:
            comparison += f"Route 2 visits {r2_destinations - r1_destinations} more destinations"
        else:
            comparison += "Both routes visit same number of destinations"

        if r1_cost < r2_cost:
            comparison += f", Route 1 is ${r2_cost - r1_cost:.2f} cheaper"
        elif r2_cost < r1_cost:
            comparison += f", Route 2 is ${r1_cost - r2_cost:.2f} cheaper"

        return comparison

    def get_service_summary(self) -> str:
        return (
            "PlanningService - Route, activity, and budget-aware travel planning\n"
            "- Calculate best routes across cost/time criteria\n"
            "- Find budget-aware destination sequences\n"
            "- Suggest budget checkpoints along a route\n"
            "- Provide activities, jobs, and flight options\n"
            "- Validate subsidized route limits and schedule costs"
        )


