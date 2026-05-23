import math
from typing import List, Optional

from App.Models.Graph import Graph
from App.Services.TravelReportService import TravelReportService


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



