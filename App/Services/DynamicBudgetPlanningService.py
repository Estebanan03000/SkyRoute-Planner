from typing import List, Optional
from collections import deque
from App.Models.Graph import Graph


class DynamicBudgetPlanningService:
    """
    Suggests optimal route sequences considering dynamic budget decisions.
    Uses BFS with pruning to explore feasible routes and rank them by efficiency.
    """

    def __init__(self, graph: Graph) -> None:
        """
        Initialize the dynamic budget planning service.

        Args:
            graph: Graph object containing airport network
        """
        self._graph: Graph = graph
        self._max_iterations: int = 500

    # ==================== Route Finding ====================

    def find_optimal_destination_sequence(
        self,
        origin_airport_code: str,
        initial_budget: float,
        max_destinations: int = 10,
        exploration_depth: int = 50
    ) -> List[dict]:
        """
        Find optimal destination sequences given initial budget and constraints.

        Uses BFS with dynamic programming approach to explore paths.
        Prunes paths that cannot beat current best.

        Args:
            origin_airport_code: Starting airport IATA code
            initial_budget: Starting budget
            max_destinations: Maximum destinations to visit
            exploration_depth: How many routes to explore

        Returns:
            List of suggested routes ranked by efficiency score
        """
        # Validate origin
        origin = self._graph.find_airport_by_iata(origin_airport_code)
        if not origin:
            return []

        # Initialize BFS queue: (current_airport_code, visited_list, spent_amount, path_length)
        queue = deque([
            (origin_airport_code, [origin_airport_code], 0.0, 0)
        ])

        suggested_routes = []
        iterations = 0
        best_destinations_count = 0

        # BFS exploration
        while queue and iterations < exploration_depth:
            current_airport, visited, spent, depth = queue.popleft()

            # Pruning: stop if path is too long
            if depth > max_destinations:
                continue

            # Find next flight options
            current_airport_obj = self._graph.find_airport_by_iata(current_airport)
            if not current_airport_obj:
                continue

            for destination in self._graph.get_airports():
                dest_code = destination.get_IATA_code()

                # Skip if already visited
                if dest_code in visited:
                    continue

                # Calculate flight cost
                flight_result = self._graph.dijkstra(
                    current_airport,
                    dest_code,
                    criterion="cost"
                )

                if not flight_result.get("path"):
                    continue

                flight_cost = flight_result.get("totalWeight", 0)
                new_spent = spent + flight_cost

                # Pruning: skip if over budget
                if new_spent > initial_budget:
                    continue

                # Create new visited list
                new_visited = visited + [dest_code]

                # Record this route
                destinations_count = len(new_visited)
                if destinations_count > best_destinations_count:
                    best_destinations_count = destinations_count

                route_score = self._evaluate_route(new_visited, new_spent, initial_budget)

                suggested_routes.append({
                    "route": new_visited,
                    "destinations_visited": destinations_count,
                    "total_cost": new_spent,
                    "remaining_budget": initial_budget - new_spent,
                    "score": route_score,
                    "efficiency": destinations_count / max(1, new_spent)
                })

                # Add to queue for further exploration
                if depth < max_destinations - 1:
                    queue.append((dest_code, new_visited, new_spent, depth + 1))

            iterations += 1

        # Sort routes by score and return top suggestions
        suggested_routes.sort(key=lambda r: r["score"], reverse=True)

        return suggested_routes[:10]  # Return top 10

    # ==================== Route Evaluation ====================

    def _evaluate_route(
        self,
        route: List[str],
        total_cost: float,
        initial_budget: float
    ) -> float:
        """
        Calculate efficiency score for a route.

        Formula: (destinations × 10) - (cost / 100) + efficiency_bonus

        Args:
            route: List of airport codes in route
            total_cost: Total cost of route
            initial_budget: Initial budget

        Returns:
            Score value
        """
        destinations_count = len(route)
        base_score = (destinations_count * 10) - (total_cost / 100)

        # Bonus for budget efficiency
        budget_efficiency = (initial_budget - total_cost) / initial_budget
        efficiency_bonus = budget_efficiency * 5

        # Bonus for visiting more destinations
        destinations_bonus = destinations_count * 2

        return base_score + efficiency_bonus + destinations_bonus

    def suggest_budget_checkpoints(
        self,
        route: List[str],
        initial_budget: float
    ) -> List[dict]:
        """
        Identify critical budget points in a route where work is recommended.

        Args:
            route: List of airport codes
            initial_budget: Starting budget

        Returns:
            List of checkpoints with recommendations
        """
        checkpoints = []
        current_budget = initial_budget
        critical_threshold = initial_budget * 0.35

        for i, airport_code in enumerate(route):
            airport = self._graph.find_airport_by_iata(airport_code)
            if not airport:
                continue

            # Estimate minimum costs at this airport
            min_accommodation = airport.get_accommodation_cost()
            min_meal = airport.get_alimentation_cost()
            estimated_minimum = min_accommodation + min_meal

            # Check if budget is critical
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

                # Assume work to recover budget
                if best_job:
                    earnings = best_job.get_hourly_rate() * 5  # Assume 5 hours of work
                    current_budget += earnings

            # Deduct estimated costs
            current_budget -= estimated_minimum

        return checkpoints

    # ==================== Route Comparison ====================

    def compare_routes(self, route1: dict, route2: dict) -> str:
        """
        Compare two routes and provide analysis.

        Args:
            route1: First route dictionary
            route2: Second route dictionary

        Returns:
            Comparison analysis string
        """
        r1_destinations = route1.get("destinations_visited", 0)
        r1_cost = route1.get("total_cost", 0)
        r1_efficiency = route1.get("efficiency", 0)

        r2_destinations = route2.get("destinations_visited", 0)
        r2_cost = route2.get("total_cost", 0)
        r2_efficiency = route2.get("efficiency", 0)

        comparison = f"Route 1: {r1_destinations} destinations, ${r1_cost:.2f}, "   \
                    f"efficiency {r1_efficiency:.3f}\n"
        comparison += f"Route 2: {r2_destinations} destinations, ${r2_cost:.2f}, "   \
                     f"efficiency {r2_efficiency:.3f}\n"

        if r1_destinations > r2_destinations:
            comparison += f"Route 1 visits {r1_destinations - r2_destinations} more "   \
                         "destinations"
        elif r2_destinations > r1_destinations:
            comparison += f"Route 2 visits {r2_destinations - r1_destinations} more "   \
                         "destinations"
        else:
            comparison += "Both routes visit same number of destinations"

        if r1_cost < r2_cost:
            comparison += f", Route 1 is ${r2_cost - r1_cost:.2f} cheaper"
        elif r2_cost < r1_cost:
            comparison += f", Route 2 is ${r1_cost - r2_cost:.2f} cheaper"

        return comparison

    def get_service_summary(self) -> str:
        """Get summary of service capabilities."""
        return (
            "DynamicBudgetPlanningService - Route optimization with budget constraints\n"
            "- Find optimal destination sequences\n"
            "- Evaluate route efficiency\n"
            "- Identify budget checkpoints\n"
            "- Suggest work opportunities\n"
            "- Compare route alternatives"
        )
