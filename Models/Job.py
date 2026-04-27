class Job:
    def __init__(self, name: str, hourly_rate: float, max_hours: int) -> None:
        self._name = name
        self._hourly_rate = hourly_rate
        self._max_hours = max_hours

    def get_name(self) -> str:
        return self._name

    def get_hourly_rate(self) -> float:
        return self._hourly_rate

    def get_max_hours(self) -> int:
        return self._max_hours

    def set_name(self, name: str) -> None:
        self._name = name

    def set_hourly_rate(self, hourly_rate: float) -> None:
        self._hourly_rate = hourly_rate

    def set_max_hours(self, max_hours: int) -> None:
        self._max_hours = max_hours