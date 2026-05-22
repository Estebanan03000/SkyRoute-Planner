from typing import Optional, List
from App.Models.Graph import Graph
from App.Services.TravelReportService import TravelReportService


class AdvancedPlanningService:
    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    def simulate_trip(
        self,
        origin_iata: str,
        destination_iata: str,
        initial_budget: float,
        available_hours: float,
        criterion: str = "cost",
        include_secondary_airports: bool = True,
        allowed_aircraft_types: Optional[List[str]] = None
    ) -> dict:
        available_minutes = available_hours * 60
        current_budget = initial_budget
        report_service = TravelReportService(initial_budget)

        route_result = self._graph.dijkstra(
            origin_iata,
            destination_iata,
            criterion,
            include_secondary_airports,
            allowed_aircraft_types
        )

        if not route_result["path"]:
            return {
                "success": False,
                "message": "No available route was found.",
                "report": report_service.generate_report()
            }

        for segment in route_result["segments"]:
            if segment["cost"] > current_budget:
                return {
                    "success": False,
                    "message": "The trip stopped because the budget was not enough.",
                    "report": report_service.generate_report()
                }

            if segment["time"] > available_minutes:
                return {
                    "success": False,
                    "message": "The trip stopped because the available time was not enough.",
                    "report": report_service.generate_report()
                }

            current_budget -= segment["cost"]
            available_minutes -= segment["time"]

            report_service.register_flight_segment(
                origin=segment["origin"],
                destination=segment["destination"],
                aircraft=segment["aircraft"],
                distance_km=segment["distanceKm"],
                flight_time_minutes=segment["time"],
                cost=segment["cost"]
            )

            destination_airport = self._graph.find_airport_by_iata(
                segment["destination"]
            )

            if destination_airport is None:
                continue

            destination_result = self._process_destination(
                airport=destination_airport,
                current_budget=current_budget,
                initial_budget=initial_budget,
                available_minutes=available_minutes,
                report_service=report_service
            )

            current_budget = destination_result["currentBudget"]
            available_minutes = destination_result["availableMinutes"]

        return {
            "success": True,
            "message": "The trip was completed successfully.",
            "remainingBudget": current_budget,
            "remainingTimeMinutes": available_minutes,
            "report": report_service.generate_report()
        }

    def _process_destination(
        self,
        airport,
        current_budget: float,
        initial_budget: float,
        available_minutes: float,
        report_service: TravelReportService
    ) -> dict:
        destination_cost = 0.0
        destination_time = 0.0

        food_result = self._apply_food_if_possible(
            airport,
            current_budget,
            available_minutes,
            report_service
        )

        current_budget = food_result["currentBudget"]
        available_minutes = food_result["availableMinutes"]
        destination_cost += food_result["cost"]
        destination_time += food_result["time"]

        activities_result = self._apply_optional_activities(
            airport,
            current_budget,
            available_minutes,
            report_service
        )

        current_budget = activities_result["currentBudget"]
        available_minutes = activities_result["availableMinutes"]
        destination_cost += activities_result["cost"]
        destination_time += activities_result["time"]

        if current_budget < initial_budget * 0.35:
            job_result = self._apply_best_available_job(
                airport,
                current_budget,
                available_minutes,
                report_service
            )

            current_budget = job_result["currentBudget"]
            available_minutes = job_result["availableMinutes"]
            destination_time += job_result["time"]

        report_service.register_destination(
            airport_name=airport.get_name(),
            city=airport.get_city(),
            country=airport.get_country(),
            stay_time_minutes=destination_time,
            total_cost=destination_cost
        )

        return {
            "currentBudget": current_budget,
            "availableMinutes": available_minutes
        }

    def _apply_food_if_possible(
        self,
        airport,
        current_budget: float,
        available_minutes: float,
        report_service: TravelReportService
    ) -> dict:
        food_cost = airport.get_alimentation_cost()
        food_time = 30

        if current_budget < food_cost or available_minutes < food_time:
            return {
                "currentBudget": current_budget,
                "availableMinutes": available_minutes,
                "cost": 0,
                "time": 0
            }

        current_budget -= food_cost
        available_minutes -= food_time

        report_service.register_activity(
            name="Food",
            activity_type="mandatory",
            duration_minutes=food_time,
            cost=food_cost
        )

        return {
            "currentBudget": current_budget,
            "availableMinutes": available_minutes,
            "cost": food_cost,
            "time": food_time
        }

    def _apply_optional_activities(
        self,
        airport,
        current_budget: float,
        available_minutes: float,
        report_service: TravelReportService
    ) -> dict:
        total_cost = 0.0
        total_time = 0.0

        for activity in airport.get_activities():
            if activity.get_type() == "mandatory":
                continue

            cost = activity.get_cost_in_USD()
            duration = activity.get_duration_per_minutes()

            if current_budget >= cost and available_minutes >= duration:
                current_budget -= cost
                available_minutes -= duration
                total_cost += cost
                total_time += duration

                report_service.register_activity(
                    name=activity.get_name(),
                    activity_type=activity.get_type(),
                    duration_minutes=duration,
                    cost=cost
                )

        return {
            "currentBudget": current_budget,
            "availableMinutes": available_minutes,
            "cost": total_cost,
            "time": total_time
        }

    def _apply_best_available_job(
        self,
        airport,
        current_budget: float,
        available_minutes: float,
        report_service: TravelReportService
    ) -> dict:
        if not airport.get_jobs():
            return {
                "currentBudget": current_budget,
                "availableMinutes": available_minutes,
                "time": 0
            }

        best_job = max(
            airport.get_jobs(),
            key=lambda job: job.get_hourly_rate()
        )

        max_available_hours = available_minutes / 60
        worked_hours = min(best_job.get_max_hours(), max_available_hours)

        if worked_hours <= 0:
            return {
                "currentBudget": current_budget,
                "availableMinutes": available_minutes,
                "time": 0
            }

        earned_amount = worked_hours * best_job.get_hourly_rate()
        current_budget += earned_amount
        available_minutes -= worked_hours * 60

        report_service.register_job(
            name=best_job.get_name(),
            worked_hours=worked_hours,
            hourly_rate=best_job.get_hourly_rate()
        )

        return {
            "currentBudget": current_budget,
            "availableMinutes": available_minutes,
            "time": worked_hours * 60
        }