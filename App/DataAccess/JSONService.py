import json
from App.Models.Graph import Graph
from App.Models.Airport import Airport
from App.Models.Route import Route
from App.Models.Aircraft import Aircraft
from App.Models.Activity import Activity
from App.Models.Job import Job


class JSONService:
    DEFAULT_AIRCRAFT_CONFIG = {
        "Avion Comercial": {"costKm": 0.18, "timeKm": 0.7},
        "Avion Regional": {"costKm": 0.25, "timeKm": 1.1},
        "Helice": {"costKm": 0.12, "timeKm": 2.5}
    }

    def __init__(self, file_path: str) -> None:
        self._file_path = file_path
        self._global_config = {}

    def load_graph(self) -> Graph:
        data = self._read_json_file()

        self._global_config = data.get("configuracionGlobal", {})

        aircraft_config = self._build_aircraft_config(data)
        graph = Graph()

        airports_map = self._load_airports(data)
        for airport in airports_map.values():
            graph.add_airport(airport)

        self._load_routes(data, airports_map, aircraft_config)

        return graph

    def get_global_config(self) -> dict:
        return self._global_config

    def _read_json_file(self) -> dict:
        with open(self._file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _build_aircraft_config(self, data: dict) -> dict:
        aircraft_config = self.DEFAULT_AIRCRAFT_CONFIG.copy()

        custom_config = data.get("configuracionGlobal", {}).get("aeronaves", {})

        for aircraft_name, values in custom_config.items():
            aircraft_config[aircraft_name] = {
                "costKm": values.get("costKm", aircraft_config.get(aircraft_name, {}).get("costKm", 0)),
                "timeKm": values.get("timeKm", aircraft_config.get(aircraft_name, {}).get("timeKm", 0))
            }

        return aircraft_config

    def _load_airports(self, data: dict) -> dict:
        airports_map = {}

        for airport_data in data.get("airports", []):
            activities = self._load_activities(airport_data)
            jobs = self._load_jobs(airport_data)

            airport = Airport(
                IATA_code=airport_data.get("id"),
                name=airport_data.get("nombre"),
                city=airport_data.get("ciudad"),
                country=airport_data.get("pais"),
                time_zone=airport_data.get("zonaHoraria"),
                isHub=airport_data.get("esHub", False),
                accommodation_cost=float(airport_data.get("costoAlojamiento", 0)),
                alimentation_cost=float(airport_data.get("costoAlimentacion", 0)),
                activities=activities,
                jobs=jobs
            )

            airports_map[airport.get_IATA_code()] = airport

        return airports_map

    def _load_activities(self, airport_data: dict) -> list[Activity]:
        activities = []

        for activity_data in airport_data.get("actividades", []):
            activity = Activity(
                name=activity_data.get("nombre"),
                type=activity_data.get("tipo"),
                duration_per_minutes=int(activity_data.get("duracionMin", 0)),
                cost_in_USD=float(activity_data.get("costoUSD", 0))
            )

            activities.append(activity)

        return activities

    def _load_jobs(self, airport_data: dict) -> list[Job]:
        jobs = []

        for job_data in airport_data.get("trabajos", []):
            job = Job(
                name=job_data.get("nombre"),
                hourly_rate=float(job_data.get("tarifaHora", 0)),
                max_hours=int(job_data.get("maxHoras", 0))
            )

            jobs.append(job)

        return jobs

    def _load_routes(
        self,
        data: dict,
        airports_map: dict,
        aircraft_config: dict
    ) -> None:
        for route_data in data.get("routes", []):
            origin_code = route_data.get("origen")
            destination_code = route_data.get("destino")

            origin_airport = airports_map.get(origin_code)
            destination_airport = airports_map.get(destination_code)

            if origin_airport is None or destination_airport is None:
                continue

            aircraft_list = self._load_aircraft_for_route(
                route_data,
                aircraft_config
            )

            route = Route(
                destiny_airport=destination_airport,
                distance_in_km=float(route_data.get("distanciaKm", 0)),
                minimum_stay=int(route_data.get("estanciaMinima", 0)),
                is_subsidized=float(route_data.get("costoBase", 1)) == 0,
                base_cost=float(route_data.get("costoBase", 1)),
                aircraft=aircraft_list
            )

            origin_airport.add_adjacencies(route)

    def _load_aircraft_for_route(
        self,
        route_data: dict,
        aircraft_config: dict
    ) -> list[Aircraft]:
        aircraft_list = []

        for index, aircraft_name in enumerate(route_data.get("aeronaves", [])):
            config = aircraft_config.get(aircraft_name)

            if config is None:
                continue

            aircraft = Aircraft(
                id=f"{aircraft_name}_{index}",
                type=aircraft_name,
                cost_per_km=float(config.get("costKm", 0)),
                time_per_km=int(config.get("timeKm", 0))
            )

            aircraft_list.append(aircraft)

        return aircraft_list