import math
import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Optional
from Models.Airport import Airport

class Graph:
    def __init__(self):
        self._airports = []

    def get_airports(self) -> List[Airport]:
        return self._airports
    
    def set_airports(self, airports: List[Airport]) -> None:
        self._airports = list(airports)

    def add_airport(self, airport: Airport) -> None:
        self._airports.append(airport)

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