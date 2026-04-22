class Activity:
    def __init__(self, name: str, type: str, duration_per_minutes: int, cost_in_USD: float) -> None:
        self._name = name
        self._type = type
        self._duration_per_minutes = duration_per_minutes
        self._cost_in_USD = cost_in_USD