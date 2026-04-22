class Aircraft:
    def __init__(self, id: str, type: str, cost_per_km: float, time_per_km: int) -> None:
        self._id = id
        self._type = type
        self._cost_per_km = cost_per_km
        self._time_per_km = time_per_km