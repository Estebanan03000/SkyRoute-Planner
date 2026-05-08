class Aircraft:
    def __init__(self, id: str, type: str, cost_per_km: float, time_per_km: int) -> None:
        self._id = id
        self._type = type
        self._cost_per_km = cost_per_km
        self._time_per_km = time_per_km

    def get_id(self) -> str:
        return self._id

    def get_type(self) -> str:
        return self._type

    def get_cost_per_km(self) -> float:
        return self._cost_per_km

    def get_time_per_km(self) -> int:
        return self._time_per_km

    def set_id(self, id: str) -> None:
        self._id = id

    def set_type(self, type: str) -> None:
        self._type = type

    def set_cost_per_km(self, cost_per_km: float) -> None:
        self._cost_per_km = cost_per_km

    def set_time_per_km(self, time_per_km: int) -> None:
        self._time_per_km = time_per_km