class Activity:
    def __init__(self, name: str, type: str, duration_per_minutes: int, cost_in_USD: float) -> None:
        self._name = name
        self._type = type
        self._duration_per_minutes = duration_per_minutes
        self._cost_in_USD = cost_in_USD

    def get_name(self) -> str:
        return self._name

    def get_type(self) -> str:
        return self._type

    def get_duration_per_minutes(self) -> int:
        return self._duration_per_minutes

    def get_cost_in_USD(self) -> float:
        return self._cost_in_USD
    
    def set_name(self, name: str) -> None:
        self._name = name

    def set_type(self, type: str) -> None:
        self._type = type

    def set_duration_per_minutes(self, duration_per_minutes: int) -> None:
        self._duration_per_minutes = duration_per_minutes

    def set_cost_in_USD(self, cost_in_USD: float) -> None:
        self._cost_in_USD = cost_in_USD