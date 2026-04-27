from Models.Activity import Activity
from Models.Job import Job
from Models.Airline import Airline
from typing import List, Optional

class Airport:
    def __init__(self, IATA_code: str, name: str, city: str, country: str, time_zone: str, isHub: bool, accommodation_cost: float, alimentation_cost: float, airlines: Optional[List[Airline]] = None, activities: Optional[List[Activity]] = None, jobs: Optional[List[Job]] = None) -> None:
        self._IATA_code = IATA_code
        self._name = name
        self._city = city
        self._country = country
        self._time_zone = time_zone
        self._isHub = isHub
        self._accommodation_cost = accommodation_cost
        self._alimentation_cost = alimentation_cost
        self._airlines = list(airlines) if airlines is not None else []
        self._activities = list(activities) if activities is not None else []
        self._jobs = list(jobs) if jobs is not None else []

    def get_IATA_code(self) -> str:
        return self._IATA_code
    
    def get_name(self) -> str:
        return self._name
    
    def get_city(self) -> str:
        return self._city
    
    def get_country(self) -> str:
        return self._country
    
    def get_time_zone(self) -> str:
        return self._time_zone
    
    def get_isHub(self) -> bool:
        return self._isHub
    
    def get_accommodation_cost(self) -> float:
        return self._accommodation_cost
    
    def get_alimentation_cost(self) -> float:
        return self._alimentation_cost
    
    def get_airlines(self) -> List[Airline]:
        return self._airlines
    
    def get_activities(self) -> List[Activity]:
        return self._activities
    
    def get_jobs(self) -> List[Job]:
        return self._jobs
    
    def set_IATA_code(self, IATA_code: str) -> None:
        self._IATA_code = IATA_code

    def set_name(self, name: str) -> None:
        self._name = name

    def set_city(self, city: str) -> None:
        self._city = city

    def set_country(self, country: str) -> None:
        self._country = country

    def set_time_zone(self, time_zone: str) -> None:
        self._time_zone = time_zone

    def set_isHub(self, isHub: bool) -> None:
        self._isHub = isHub

    def set_accommodation_cost(self, accommodation_cost: float) -> None:
        self._accommodation_cost = accommodation_cost

    def set_alimentation_cost(self, alimentation_cost: float) -> None:
        self._alimentation_cost = alimentation_cost

    def set_airlines(self, airlines: List[Airline]) -> None:
        self._airlines = list(airlines)

    def set_activities(self, activities: List[Activity]) -> None:
        self._activities = list(activities)

    def set_jobs(self, jobs: List[Job]) -> None:
        self._jobs = list(jobs)