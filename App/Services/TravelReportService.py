class TravelReportService:
    def __init__(self, initial_budget: float) -> None:
        self._initial_budget = initial_budget
        self._total_spent = 0.0
        self._total_earned = 0.0
        self._total_time_minutes = 0.0
        self._visited_destinations = []
        self._flight_segments = []
        self._completed_activities = []
        self._completed_jobs = []

    def register_destination(
        self,
        airport_name: str,
        city: str,
        country: str,
        stay_time_minutes: float,
        total_cost: float
    ) -> None:
        self._visited_destinations.append({
            "airportName": airport_name,
            "city": city,
            "country": country,
            "stayTimeMinutes": stay_time_minutes,
            "totalCost": total_cost
        })

        self._total_spent += total_cost
        self._total_time_minutes += stay_time_minutes

    def register_flight_segment(
        self,
        origin: str,
        destination: str,
        aircraft: str,
        distance_km: float,
        flight_time_minutes: float,
        cost: float
    ) -> None:
        self._flight_segments.append({
            "origin": origin,
            "destination": destination,
            "aircraft": aircraft,
            "distanceKm": distance_km,
            "flightTimeMinutes": flight_time_minutes,
            "cost": cost
        })

        self._total_spent += cost
        self._total_time_minutes += flight_time_minutes

    def register_activity(
        self,
        name: str,
        activity_type: str,
        duration_minutes: float,
        cost: float
    ) -> None:
        self._completed_activities.append({
            "name": name,
            "type": activity_type,
            "durationMinutes": duration_minutes,
            "cost": cost
        })

        self._total_spent += cost
        self._total_time_minutes += duration_minutes

    def register_job(
        self,
        name: str,
        worked_hours: float,
        hourly_rate: float
    ) -> None:
        earned_amount = worked_hours * hourly_rate

        self._completed_jobs.append({
            "name": name,
            "workedHours": worked_hours,
            "hourlyRate": hourly_rate,
            "earnedAmount": earned_amount
        })

        self._total_earned += earned_amount
        self._total_time_minutes += worked_hours * 60

    def get_current_balance(self) -> float:
        return self._initial_budget - self._total_spent + self._total_earned

    def generate_report(self) -> dict:
        return {
            "initialBudget": self._initial_budget,
            "totalSpent": self._total_spent,
            "totalEarned": self._total_earned,
            "finalBalance": self.get_current_balance(),
            "totalTimeMinutes": self._total_time_minutes,
            "totalTimeHours": self._total_time_minutes / 60,
            "visitedDestinations": self._visited_destinations,
            "flightSegments": self._flight_segments,
            "completedActivities": self._completed_activities,
            "completedJobs": self._completed_jobs
        }