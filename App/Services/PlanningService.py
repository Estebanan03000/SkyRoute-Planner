from Models.Graph import Graph

class PlanningService:

    def __init__(self, actualAirports):
        self._actualAirports = actualAirports
        self.selected_job = None

    def DjstrakMoney(self, origin, destiny, budget):
        if origin not in self._actualAirports or destiny not in self._actualAirports:
            return None
        else:
            distances, previous, path = Graph.dijkstra(self._actualAirports, origin, destiny)
            if distances[destiny] > budget:
                return None
            else:
                return path
        
    def DjstrakTime(self, origin, destiny, max_time):
        if origin not in self._actualAirports or destiny not in self._actualAirports:
            return None
        else:
            distances, previous, path = Graph.dijkstra_time(self._actualAirports, origin, destiny)
            if distances[destiny] > max_time:
                return None
            else:
                return path