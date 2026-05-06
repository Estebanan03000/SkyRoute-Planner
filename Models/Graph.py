import math
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from typing import List, Optional
from Models.Airport import Airport
from Models.Queue import Queue
from Models.Stack import Stack

class Graph:
    def __init__(self):
        self._airports = []

    def get_airports(self) -> List[Airport]:
        return self._airports
    
    def set_airports(self, airports: List[Airport]) -> None:
        self._airports = list(airports)

    def add_airport(self, airport: Airport) -> None:
        self._airports.append(airport)

    def BFS(self, start_airport: Airport) -> list[Airport]:
        visited = [start_airport]
        queue = Queue()
        queue.enqueue(start_airport)
        while not queue.is_empty():
            current_airport = queue.dequeue()
            for adjacent_airport in current_airport.get_adjacencies():
                if adjacent_airport.get_destiny_airport() not in visited:
                    visited.append(adjacent_airport.get_destiny_airport())
                    queue.enqueue(adjacent_airport.get_destiny_airport())
        return visited
    
    def DFS(self, start_airport: Airport) -> list[Airport]:
        visited = [start_airport]
        stack = Stack()
        stack.push(start_airport)
        while not stack.is_empty():
            current_airport = stack.pop()
            for adjacent_airport in current_airport.get_adjacencies():
                if adjacent_airport.get_destiny_airport() not in visited:
                    visited.append(adjacent_airport.get_destiny_airport())
                    stack.push(adjacent_airport.get_destiny_airport())
        return visited

    def visualize(self) -> None:
        G = nx.DiGraph()
        for airport in self._airports:
            G.add_node(airport.get_IATA_code())
            for route in airport.get_adjacencies():
                G.add_edge(airport.get_IATA_code(), route.get_destiny_airport().get_IATA_code())
        pos = nx.spring_layout(G)
        nx.draw_networkx(G, pos, with_labels=True, node_color='lightblue', node_size=1500, font_size=12, font_weight='bold', arrows = True)
        plt.title("Graph Visualization of Airports and Routes", fontsize=14)
        plt.show()

    def dijkstra_by_cost(self, start_IATA: str, end_IATA: str) -> tuple[dict, dict, List[str]]:
        all_airports = [airport.get_IATA_code() for airport in self.get_airports()]

        distances = {airport: math.inf for airport in all_airports}
        previous_airport: dict[str, Optional[str]] = {airport: None for airport in all_airports}
        distances[start_IATA] = 0

        unvisited = set(all_airports)

        airports_map = {airport.get_IATA_code(): airport for airport in self.get_airports()}
        while unvisited:
            unvisited_airport = min(unvisited, key=lambda airport: distances[airport])
            if distances[unvisited_airport] == math.inf:
                break

            unvisited.remove(unvisited_airport)

            if unvisited_airport == end_IATA:
                break

            current_airport = airports_map[unvisited_airport]
            for route in current_airport.get_adjacencies():
                neighbor = route.get_destiny_airport().get_IATA_code()
                if neighbor in unvisited:
                    new_distance = distances[unvisited_airport] + route.get_minimum_weight_by_cost()
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous_airport[neighbor] = unvisited_airport

            for neighbor in all_airports:
                cost = "∞" if distances[neighbor] == math.inf else distances[neighbor]

        path = []
        current_airport = end_IATA
        while current_airport is not None:
            path.insert(0, current_airport)
            current_airport = previous_airport[current_airport]

        return distances, previous_airport, path


    def dijkstra_by_time(self, start_IATA: str, end_IATA: str) -> tuple[dict, dict, List[str]]:
        all_airports = [airport.get_IATA_code() for airport in self.get_airports()]

        distances = {airport: math.inf for airport in all_airports}
        previous_airport: dict[str, Optional[str]] = {airport: None for airport in all_airports}
        distances[start_IATA] = 0

        unvisited = set(all_airports)

        airports_map = {airport.get_IATA_code(): airport for airport in self.get_airports()}
        while unvisited:
            unvisited_airport = min(unvisited, key=lambda airport: distances[airport])
            if distances[unvisited_airport] == math.inf:
                break

            unvisited.remove(unvisited_airport)

            if unvisited_airport == end_IATA:
                break

            current_airport = airports_map[unvisited_airport]
            for route in current_airport.get_adjacencies():
                neighbor = route.get_destiny_airport().get_IATA_code()
                if neighbor in unvisited:
                    new_distance = distances[unvisited_airport] + route.get_minimum_weight_by_time()
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous_airport[neighbor] = unvisited_airport

            for neighbor in all_airports:
                cost = "∞" if distances[neighbor] == math.inf else distances[neighbor]

        path = []
        current_airport = end_IATA
        while current_airport is not None:
            path.insert(0, current_airport)
            current_airport = previous_airport[current_airport]

        return distances, previous_airport, path

    def _get_unique_edge_labels(self, graph: nx.DiGraph) -> dict:
        unique_labels = {}
        seen_pairs = set()
        for source, target, attributes in graph.edges(data=True):
            pair_key = tuple(sorted((source, target)))
            if pair_key not in seen_pairs:
                unique_labels[(source, target)] = attributes.get('weight')
                seen_pairs.add(pair_key)
        return unique_labels
    

    def visualize_with_route_by_cost(self, path, title: str = "Shortest Route - Dijkstra") -> None:
        G = nx.DiGraph()

        for airport in self._airports:
            for route in airport.get_adjacencies():
                G.add_edge(airport.get_IATA_code(),
                            route.get_destiny_airport().get_IATA_code(),
                            weight=route.get_minimum_weight_by_cost()
                            )
        routes = set(zip(path[:-1], path[1:]))

        route_colors = ['red' if (x, y) in routes else '#cccccc' for x, y in G.edges()]
        routes_widths = [3.5 if (x,y) in routes else 1 for x, y in G.edges()]
        airport_colors = ['orange' if node == path[0] else
                            'lightgreen' if node == path[-1] else
                            '#ff6b6b' if node in path else
                            'lightblue' for node in G.nodes()]
        pos = nx.spring_layout(G, seed=42)
        route_labels = self._get_unique_edge_labels(G)

        plt.figure(figsize=(12, 8))

        nx.draw_networkx(G, pos,
            with_labels = False,          # <-- desactivado aquí
            node_color = airport_colors,
            node_size = 2000,
            arrows = True,
            arrowsize = 20,
            edge_color = route_colors,
            width = routes_widths,
            connectionstyle = "arc3,rad=0.1")
        
        nx.draw_networkx_labels(G, pos,
                                font_size=12,
                                font_weight='bold',
                                bbox=dict(boxstyle="round,pad=0.3",
                                            fc="white",
                                            ec="none",
                                            alpha=0.8))
        
        nx.draw_networkx_edge_labels(G, pos,
                                    edge_labels=route_labels,
                                    font_size=9,
                                    font_color='black',
                                    bbox=dict(boxstyle="round,pad=0.2",
                                            fc="white",
                                            ec="none",
                                            alpha=0.9),
                                    label_pos=0.35)
        
        legend_elements = [
            Patch(color='orange',     label=f'Start ({path[0]})'),
            Patch(color='lightgreen', label=f'Destination ({path[-1]})'),
            Patch(color='#ff6b6b',    label='Airports on the route'),
            Patch(color='lightblue',    label='Another airports'),
            ]
        
        plt.legend(handles=legend_elements, loc='upper left')
        plt.title(title, fontsize=14)
        plt.tight_layout()
        plt.show()

    def visualize_with_route_by_time(self, path, title: str = "Fastest Route - Dijkstra") -> None:
        G = nx.DiGraph()

        for airport in self._airports:
            for route in airport.get_adjacencies():
                G.add_edge(airport.get_IATA_code(),
                            route.get_destiny_airport().get_IATA_code(),
                            weight=route.get_minimum_weight_by_time()
                            )
        routes = set(zip(path[:-1], path[1:]))

        route_colors = ['red' if (x, y) in routes else '#cccccc' for x, y in G.edges()]
        routes_widths = [3.5 if (x, y) in routes else 1 for x, y in G.edges()]
        airport_colors = ['orange' if node == path[0] else
                            'lightgreen' if node == path[-1] else
                            '#ff6b6b' if node in path else
                            'lightblue' for node in G.nodes()]
        pos = nx.spring_layout(G, seed=42)
        route_labels = self._get_unique_edge_labels(G)

        plt.figure(figsize=(12, 8))

        nx.draw_networkx(G, pos,
            with_labels=False,
            node_color=airport_colors,
            node_size=2000,
            arrows=True,
            arrowsize=20,
            edge_color=route_colors,
            width=routes_widths,
            connectionstyle="arc3,rad=0.1")

        nx.draw_networkx_labels(G, pos,
                                font_size=12,
                                font_weight='bold',
                                bbox=dict(boxstyle="round,pad=0.3",
                                            fc="white",
                                            ec="none",
                                            alpha=0.8))

        nx.draw_networkx_edge_labels(G, pos,
                                        edge_labels=route_labels,
                                        font_size=9,
                                        font_color='black',
                                        bbox=dict(boxstyle="round,pad=0.2",
                                                fc="white",
                                                ec="none",
                                                alpha=0.9),
                                        label_pos=0.35)

        legend_elements = [
            Patch(color='orange',    label=f'Start ({path[0]})'),
            Patch(color='lightgreen', label=f'Destination ({path[-1]})'),
            Patch(color='#ff6b6b',   label='Airports on the route'),
            Patch(color='lightblue', label='Another airports'),
        ]
        plt.legend(handles=legend_elements, loc='upper left')
        plt.title(title, fontsize=14)
        plt.tight_layout()
        plt.show()