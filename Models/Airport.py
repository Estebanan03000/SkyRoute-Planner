from Models.Activity import Activity
from Models.Job import Job
from typing import List

class Airport:
    def __init__(self, IATA_code: str, name: str, city: str, country: str, time_zone: str, isHub: bool, accommodation_cost: float, alimentation_cost: float, activities: List[Activity] = [], jobs: List[Job] = []) -> None:
        self._IATA_code = IATA_code
        self._name = name
        self._city = city
        self._country = country
        self._time_zone = time_zone
        self._isHub = isHub
        self._accommodation_cost = accommodation_cost
        self._alimentation_cost = alimentation_cost
        self._activities = activities
        self._jobs = jobs