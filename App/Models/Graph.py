"""Graph algorithms and visualization utilities for the SkyRoute planner."""

import io
import math
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')

from typing import List, Optional
from App.Models.Airport import Airport
from App.Models.Route import Route
from App.Models.Queue import Queue
from App.Models.Stack import Stack


class Graph:
    """Represents the airport network and implements traversal and optimization algorithms."""
    def __init__(self) -> None:
        self._airports: List[Airport] = []

    def get_airports(self) -> List[Airport]:
        return self._airports

    def set_airports(self, airports: List[Airport]) -> None:
        self._airports = list(airports)

    def add_airport(self, airport: Airport) -> None:
        self._airports.append(airport)

    def find_airport_by_iata(self, iata_code: str) -> Optional[Airport]:
        for airport in self._airports:
            if airport.get_IATA_code() == iata_code:
                return airport
        return None

    def get_route(self, origin_iata: str, destination_iata: str) -> Optional[Route]:
        origin_airport = self.find_airport_by_iata(origin_iata)

        if origin_airport is None:
            return None

        for route in origin_airport.get_adjacencies():
            if route.get_destiny_airport().get_IATA_code() == destination_iata:
                return route

        return None

    def block_route(self, origin_iata: str, destination_iata: str) -> bool:
        route = self.get_route(origin_iata, destination_iata)

        if route is None:
            return False

        route.block_route()
        return True

    def unblock_route(self, origin_iata: str, destination_iata: str) -> bool:
        route = self.get_route(origin_iata, destination_iata)

        if route is None:
            return False

        route.unblock_route()
        return True

    def BFS(self, start_airport: Airport) -> List[Airport]:
        visited = [start_airport]
        queue = Queue()
        queue.enqueue(start_airport)

        while not queue.is_empty():
            current_airport = queue.dequeue()

            for route in current_airport.get_adjacencies():
                next_airport = route.get_destiny_airport()

                if next_airport not in visited:
                    visited.append(next_airport)
                    queue.enqueue(next_airport)

        return visited

    def DFS(self, start_airport: Airport) -> List[Airport]:
        visited = [start_airport]
        stack = Stack()
        stack.push(start_airport)

        while not stack.is_empty():
            current_airport = stack.pop()

            for route in current_airport.get_adjacencies():
                next_airport = route.get_destiny_airport()

                if next_airport not in visited:
                    visited.append(next_airport)
                    stack.push(next_airport)

        return visited

    def dijkstra(
        self,
        start_iata: str,
        end_iata: str,
        criterion: str,
        include_secondary_airports: bool = True,
        allowed_aircraft_types: Optional[List[str]] = None
    ) -> dict:
        if criterion not in ["cost", "time", "distance"]:
            raise ValueError("Criterion must be: cost, time or distance.")

        start_airport = self.find_airport_by_iata(start_iata)
        end_airport = self.find_airport_by_iata(end_iata)

        if start_airport is None:
            raise ValueError(f"Start airport '{start_iata}' does not exist.")

        if end_airport is None:
            raise ValueError(f"End airport '{end_iata}' does not exist.")

        valid_airports = self._get_valid_airports(include_secondary_airports)

        if start_iata not in valid_airports or end_iata not in valid_airports:
            return {
                "totalWeight": math.inf,
                "path": [],
                "segments": []
            }

        distances = {
            iata_code: math.inf
            for iata_code in valid_airports
        }

        previous_airport: dict[str, Optional[str]] = {
            iata_code: None
            for iata_code in valid_airports
        }

        previous_route: dict[str, Optional[Route]] = {
            iata_code: None
            for iata_code in valid_airports
        }

        distances[start_iata] = 0
        unvisited = set(valid_airports)

        while unvisited:
            current_iata = min(
                unvisited,
                key=lambda iata_code: distances[iata_code]
            )

            if distances[current_iata] == math.inf:
                break

            unvisited.remove(current_iata)

            if current_iata == end_iata:
                break

            current_airport = self.find_airport_by_iata(current_iata)

            if current_airport is None:
                continue

            for route in current_airport.get_adjacencies():
                if route.is_blocked():
                    continue

                neighbor_iata = route.get_destiny_airport().get_IATA_code()

                if neighbor_iata not in unvisited:
                    continue

                route_weight = route.get_weight_by_criterion(
                    criterion,
                    allowed_aircraft_types
                )

                if route_weight == math.inf:
                    continue

                new_distance = distances[current_iata] + route_weight

                if new_distance < distances[neighbor_iata]:
                    distances[neighbor_iata] = new_distance
                    previous_airport[neighbor_iata] = current_iata
                    previous_route[neighbor_iata] = route

        path = self._reconstruct_path(
            start_iata,
            end_iata,
            previous_airport
        )

        segments = self._build_segments(
            path,
            previous_route,
            criterion,
            allowed_aircraft_types
        )

        return {
            "totalWeight": distances[end_iata],
            "path": path,
            "segments": segments
        }

    def dijkstra_by_cost(self, start_iata: str, end_iata: str) -> dict:
        return self.dijkstra(start_iata, end_iata, "cost")

    def dijkstra_by_time(self, start_iata: str, end_iata: str) -> dict:
        return self.dijkstra(start_iata, end_iata, "time")

    def dijkstra_by_distance(self, start_iata: str, end_iata: str) -> dict:
        return self.dijkstra(start_iata, end_iata, "distance")

    def _get_valid_airports(self, include_secondary_airports: bool) -> List[str]:
        valid_airports = []

        for airport in self._airports:
            if include_secondary_airports or airport.get_isHub():
                valid_airports.append(airport.get_IATA_code())
        
        return valid_airports

    def _reconstruct_path(
        self,
        start_iata: str,
        end_iata: str,
        previous_airport: dict
    ) -> List[str]:
        path = []
        current_iata = end_iata

        while current_iata is not None:
            path.insert(0, current_iata)
            current_iata = previous_airport[current_iata]

        if len(path) == 0 or path[0] != start_iata:
            return []

        return path

    def _build_segments(
        self,
        path: List[str],
        previous_route: dict,
        criterion: str,
        allowed_aircraft_types: Optional[List[str]]
    ) -> List[dict]:
        segments = []

        for index in range(1, len(path)):
            origin_iata = path[index - 1]
            destination_iata = path[index]
            route = previous_route[destination_iata]

            selected_aircraft = route.get_best_aircraft_by_criterion(
                criterion,
                allowed_aircraft_types
            )

            segments.append({
                "origin": origin_iata,
                "destination": destination_iata,
                "aircraft": selected_aircraft.get_type() if selected_aircraft else None,
                "distanceKm": route.get_distance_in_km(),
                "cost": route.get_weight_by_criterion("cost", allowed_aircraft_types),
                "time": route.get_weight_by_criterion("time", allowed_aircraft_types),
                "criterionWeight": route.get_weight_by_criterion(
                    criterion,
                    allowed_aircraft_types
                )
            })

        return segments

    def visualize(self) -> None:
        graph = nx.DiGraph()

        for airport in self._airports:
            graph.add_node(airport.get_IATA_code())

            for route in airport.get_adjacencies():
                graph.add_edge(
                    airport.get_IATA_code(),
                    route.get_destiny_airport().get_IATA_code()
                )

        positions = nx.spring_layout(graph)

        nx.draw_networkx(
            graph,
            positions,
            with_labels=True,
            node_color="lightblue",
            node_size=1500,
            font_size=12,
            font_weight="bold",
            arrows=True
        )

        plt.title("Graph Visualization of Airports and Routes", fontsize=14)
        plt.show()

    def visualize_to_png(self, highlight_path: Optional[List[str]] = None, criterion: str = "cost") -> bytes:
        graph = nx.DiGraph()
        route_weights: dict[tuple[str, str], float] = {}

        for airport in self._airports:
            graph.add_node(airport.get_IATA_code())
            for route in airport.get_adjacencies():
                origin = airport.get_IATA_code()
                destination = route.get_destiny_airport().get_IATA_code()
                graph.add_edge(origin, destination)
                route_weights[(origin, destination)] = route.get_weight_by_criterion(
                    criterion,
                    None
                )

        positions = nx.spring_layout(graph, seed=42)
        highlight_edges = set()

        if highlight_path and len(highlight_path) > 1:
            highlight_edges = {
                (highlight_path[i], highlight_path[i + 1])
                for i in range(len(highlight_path) - 1)
            }

        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_axis_off()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)

        for edge in graph.edges():
            x1, y1 = positions[edge[0]]
            x2, y2 = positions[edge[1]]
            edge_color = "red" if edge in highlight_edges else "#888"
            linewidth = 2.8 if edge in highlight_edges else 1.0
            ax.plot([x1, x2], [y1, y2], color=edge_color, alpha=0.6, linewidth=linewidth, zorder=1)

            midpoint_x = (x1 + x2) / 2
            midpoint_y = (y1 + y2) / 2
            weight = route_weights.get(edge, None)
            if weight is not None and weight != math.inf:
                ax.text(
                    midpoint_x,
                    midpoint_y,
                    f"{weight:.1f}",
                    fontsize=8,
                    color="#334155",
                    ha="center",
                    va="center",
                    bbox=dict(boxstyle="round,pad=0.18", fc=("#fde68a" if edge in highlight_edges else "#f8fafc"), ec="none", alpha=0.9),
                    zorder=4
                )

        node_positions = [positions[node] for node in graph.nodes()]
        ax.scatter(
            [pos[0] for pos in node_positions],
            [pos[1] for pos in node_positions],
            s=760,
            color="lightblue",
            edgecolors="black",
            linewidths=0.8,
            zorder=2
        )

        for node, (x, y) in positions.items():
            ax.text(
                x,
                y,
                node,
                fontsize=10,
                fontweight="bold",
                ha="center",
                va="center",
                zorder=3
            )

        fig.suptitle(f"Grafo de rutas ({criterion})", fontsize=16)
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", bbox_inches="tight")
        plt.close(fig)
        buffer.seek(0)
        return buffer.getvalue()