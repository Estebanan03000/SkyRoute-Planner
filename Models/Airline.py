from Models.Aircraft import Aircraft
from typing import List

class Airline:
    def __init__(self, name: str, aircraft: List[Aircraft] = []) -> None:
        self._name = name
        self._aircraft = aircraft