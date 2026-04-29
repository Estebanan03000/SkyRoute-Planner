from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING
from Models.Airline import Airline

if TYPE_CHECKING:
    from Models.Airport import Airport

class Route:
    def __init__(self, destiny_airport: Airport, distance_in_km: float, minimum_stay: int, is_subsidized: bool, base_cost: float, airlines: Optional[List[Airline]] = None) -> None:
        self._destiny_airport = destiny_airport
        self._distance_in_km = distance_in_km
        self._minimum_stay = minimum_stay
        self._is_subsidized = is_subsidized
        if is_subsidized:
            self._base_cost = 0
        else:
            self._base_cost = base_cost
        self._airlines = list(airlines) if airlines is not None else []

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

    def get_airlines(self) -> List[Airline]:
        return self._airlines
    
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

    def set_airlines(self, airlines: List[Airline]) -> None:
        self._airlines = list(airlines)