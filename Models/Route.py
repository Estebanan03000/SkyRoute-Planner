from typing import List
from Models.Aircraft import Aircraft

class Route:
    def __init__(self, IATA_origin: str, IATA_destiny: str, distance_in_km: float, minimum_stay: int, is_subsidized: bool, base_cost: float, aircraft: List[Aircraft] = []) -> None:
        self._IATA_origin = IATA_origin
        self._IATA_destiny = IATA_destiny
        self._distance_in_km = distance_in_km
        self._minimum_stay = minimum_stay
        self._is_subsidized = is_subsidized
        if is_subsidized:
            self._base_cost = 0
        else:
            self._base_cost = base_cost
        self._aircraft = aircraft