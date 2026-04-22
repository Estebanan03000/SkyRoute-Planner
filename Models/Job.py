class Job:
    def __init__(self, name: str, hourly_rate: float, max_hours: int) -> None:
        self._name = name
        self._hourly_rate = hourly_rate
        self._max_hours = max_hours