from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING
from Models.Aircraft import Aircraft

if TYPE_CHECKING:
    from Models.Airport import Airport

class Route:
    def __init__(self, destiny_airport: Airport, distance_in_km: float, minimum_stay: int, is_subsidized: bool, base_cost: float, aircraft: Optional[List[Aircraft]] = None) -> None:
        self._destiny_airport = destiny_airport
        self._distance_in_km = distance_in_km
        self._minimum_stay = minimum_stay
        self._is_subsidized = is_subsidized
        if is_subsidized:
            self._base_cost = 0
        else:
            self._base_cost = base_cost
        self._aircraft = list(aircraft) if aircraft is not None else []

    def get_destiny_airport(self) -> Airport:
        return self._destiny_airport

    def get_distance_in_km(self) -> float:
        return self._distance_in_km

    def get_minimum_stay(self) -> int:
        return self._minimum_stay

    def get_is_subsidized(self) -> bool:
        return self._is_subsidized

    def get_base_cost(self) -> float:
        return self._base_cost

    def get_aircraft(self) -> List[Aircraft]:
        return self._aircraft
    
    def set_destiny_airport(self, destiny_airport: Airport) -> None:
        self._destiny_airport = destiny_airport

    def set_distance_in_km(self, distance_in_km: float) -> None:
        self._distance_in_km = distance_in_km

    def set_minimum_stay(self, minimum_stay: int) -> None:
        self._minimum_stay = minimum_stay

    def set_is_subsidized(self, is_subsidized: bool) -> None:
        self._is_subsidized = is_subsidized
        if is_subsidized:
            self._base_cost = 0

    def set_base_cost(self, base_cost: float) -> None:
        if not self._is_subsidized:
            self._base_cost = base_cost

    def set_aircraft(self, aircraft: List[Aircraft]) -> None:
        self._aircraft = list(aircraft)

    def _get_weights_by_cost(self) -> dict:
        weights_by_cost = {}
        for aircraft in self.get_aircraft():
            id_aircraft = aircraft.get_id()
            weights_by_cost[id_aircraft] = self.get_distance_in_km() * aircraft.get_cost_per_km()
        return weights_by_cost
    
    def get_minimum_weight_by_cost(self) -> float:
        weights_by_cost = self._get_weights_by_cost()
        if weights_by_cost:
            return min(weights_by_cost.values())
        else:
            return float('inf')
    
    def _get_weights_by_time(self) -> dict:
        weights_by_time = {}
        for aircraft in self.get_aircraft():
            id_aircraft = aircraft.get_id()
            weights_by_time[id_aircraft] = self.get_distance_in_km() * aircraft.get_time_per_km()
        return weights_by_time
    
    def get_minimum_weight_by_time(self) -> float:
        weights_by_time = self._get_weights_by_time()
        if weights_by_time:
            return min(weights_by_time.values())
        else:
            return float('inf')