from Models.Aircraft import Aircraft
from typing import List, Optional

class Airline:
    def __init__(self, name: str, aircraft: Optional[List[Aircraft]] = None) -> None:
        self._name = name
        self._aircraft = list(aircraft) if aircraft is not None else []

    def get_name(self) -> str:
        return self._name

    def get_aircraft(self) -> List[Aircraft]:
        return self._aircraft

    def set_name(self, name: str) -> None:
        self._name = name

    def set_aircraft(self, aircraft: List[Aircraft]) -> None:
        self._aircraft = list(aircraft)