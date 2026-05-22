from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING
from App.Models.Aircraft import Aircraft

if TYPE_CHECKING:
    from App.Models.Airport import Airport


class Route:
    def __init__(
        self,
        destiny_airport: Airport,
        distance_in_km: float,
        minimum_stay: int,
        is_subsidized: bool,
        base_cost: float,
        aircraft: Optional[List[Aircraft]] = None
    ) -> None:
        self._destiny_airport = destiny_airport
        self._distance_in_km = distance_in_km
        self._minimum_stay = minimum_stay
        self._is_subsidized = is_subsidized
        self._base_cost = 0 if is_subsidized else base_cost
        self._aircraft = list(aircraft) if aircraft is not None else []
        self._is_blocked = False

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

    def is_blocked(self) -> bool:
        return self._is_blocked

    def block_route(self) -> None:
        self._is_blocked = True

    def unblock_route(self) -> None:
        self._is_blocked = False

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

    def _has_aircraft(self, aircraft: Aircraft) -> bool:
        return aircraft in self._aircraft

    def _calculate_cost(self, aircraft: Aircraft) -> float:
        if not self._has_aircraft(aircraft):
            raise ValueError(
                f"The aircraft with id '{aircraft.get_id()}' is not available for this route."
            )

        if self._is_subsidized:
            return 0

        return self._distance_in_km * aircraft.get_cost_per_km()


    def _calculate_time(self, aircraft: Aircraft) -> float:
        if not self._has_aircraft(aircraft):
            raise ValueError(
                f"The aircraft with id '{aircraft.get_id()}' is not available for this route."
            )

        return self._distance_in_km * aircraft.get_time_per_km()

    def get_available_aircraft(
        self,
        allowed_aircraft_types: Optional[List[str]] = None
    ) -> List[Aircraft]:
        if allowed_aircraft_types is None or len(allowed_aircraft_types) == 0:
            return self._aircraft

        return [
            aircraft
            for aircraft in self._aircraft
            if aircraft.get_type() in allowed_aircraft_types
        ]

    def get_best_aircraft_by_criterion(
        self,
        criterion: str,
        allowed_aircraft_types: Optional[List[str]] = None
    ) -> Optional[Aircraft]:
        available_aircraft = self.get_available_aircraft(allowed_aircraft_types)

        if len(available_aircraft) == 0:
            return None

        if criterion == "cost":
            return min(available_aircraft, key=lambda aircraft: self._calculate_cost(aircraft))

        if criterion == "time":
            return min(available_aircraft, key=lambda aircraft: self._calculate_time(aircraft))

        if criterion == "distance":
            return available_aircraft[0]

        raise ValueError(f"Invalid criterion: {criterion}")

    def get_weight_by_criterion(
        self,
        criterion: str,
        allowed_aircraft_types: Optional[List[str]] = None
    ) -> float:
        if self._is_blocked:
            return float("inf")

        best_aircraft = self.get_best_aircraft_by_criterion(
            criterion,
            allowed_aircraft_types
        )

        if best_aircraft is None:
            return float("inf")

        if criterion == "cost":
            return self._calculate_cost(best_aircraft)

        if criterion == "time":
            return self._calculate_time(best_aircraft)

        if criterion == "distance":
            return self._distance_in_km

        raise ValueError(f"Invalid criterion: {criterion}")

    def get_minimum_weight_by_cost(self) -> float:
        return self.get_weight_by_criterion("cost")

    def get_minimum_weight_by_time(self) -> float:
        return self.get_weight_by_criterion("time")

    def to_dict(self) -> dict:
        return {
            "destination": self._destiny_airport.get_IATA_code(),
            "distanceKm": self._distance_in_km,
            "minimumStay": self._minimum_stay,
            "isSubsidized": self._is_subsidized,
            "baseCost": self._base_cost,
            "isBlocked": self._is_blocked,
            "aircraft": [
                {
                    "id": aircraft.get_id(),
                    "type": aircraft.get_type(),
                    "costPerKm": aircraft.get_cost_per_km(),
                    "timePerKm": aircraft.get_time_per_km()
                }
                for aircraft in self._aircraft
            ]
        }