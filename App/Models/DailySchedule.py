from typing import List, Optional
from datetime import datetime
from App.Models.Airport import Airport


class DailySchedule:
    """
    Manages the schedule of activities and jobs during a stay at an airport.
    Tracks time availability, costs, and helps plan feasible combinations.
    """

    def __init__(
        self,
        airport: Airport,
        arrival_time: datetime,
        minimum_stay_hours: int
    ) -> None:
        """
        Initialize daily schedule for an airport stay.

        Args:
            airport: The airport where the traveler is staying
            arrival_time: When the traveler arrived at the airport
            minimum_stay_hours: Minimum hours required to stay at the airport
        """
        self._airport: Airport = airport
        self._arrival_time: datetime = arrival_time
        self._minimum_stay_hours: int = minimum_stay_hours

        # Scheduled items: list of {type, name, duration_min, cost}
        self._scheduled_items: List[dict] = []
        self._total_cost: float = 0.0
        self._total_time_scheduled_minutes: int = 0

    # ==================== Getters ====================

    def get_airport(self) -> Airport:
        """Get the airport for this schedule."""
        return self._airport

    def get_arrival_time(self) -> datetime:
        """Get arrival time at airport."""
        return self._arrival_time

    def get_minimum_stay_hours(self) -> int:
        """Get minimum hours required at airport."""
        return self._minimum_stay_hours

    def get_scheduled_items(self) -> List[dict]:
        """Get list of scheduled items."""
        return self._scheduled_items.copy()

    def get_total_cost(self) -> float:
        """Get total cost of all scheduled items."""
        return self._total_cost

    def get_total_time_scheduled_minutes(self) -> int:
        """Get total time scheduled in minutes."""
        return self._total_time_scheduled_minutes

    def get_total_time_scheduled_hours(self) -> float:
        """Get total time scheduled in hours."""
        return self._total_time_scheduled_minutes / 60

    # ==================== Time Calculations ====================

    def get_remaining_time_minutes(self) -> int:
        """
        Calculate remaining time available for more activities.

        Returns:
            Available minutes (minimum_stay - scheduled_time)
        """
        minimum_stay_minutes = self._minimum_stay_hours * 60
        return max(0, minimum_stay_minutes - self._total_time_scheduled_minutes)

    def get_remaining_time_hours(self) -> float:
        """
        Calculate remaining time available in hours.

        Returns:
            Available hours
        """
        return self.get_remaining_time_minutes() / 60

    def can_fit_activity(self, duration_minutes: int) -> bool:
        """
        Check if an activity can fit in remaining time.

        Args:
            duration_minutes: Duration of the activity

        Returns:
            True if activity fits, False otherwise
        """
        return duration_minutes <= self.get_remaining_time_minutes()

    # ==================== Schedule Management ====================

    def add_activity(
        self,
        activity_name: str,
        duration_minutes: int,
        cost_usd: float
    ) -> bool:
        """
        Add an optional activity to the schedule.

        Args:
            activity_name: Name of the activity
            duration_minutes: Duration in minutes
            cost_usd: Cost in USD

        Returns:
            True if added successfully, False if it doesn't fit
        """
        # Check if activity fits in remaining time
        if not self.can_fit_activity(duration_minutes):
            return False

        item = {
            "type": "ACTIVITY",
            "name": activity_name,
            "duration_minutes": duration_minutes,
            "cost": cost_usd
        }

        self._scheduled_items.append(item)
        self._total_time_scheduled_minutes += duration_minutes
        self._total_cost += cost_usd

        return True

    def add_meal(
        self,
        meal_cost: float,
        meal_duration_minutes: int = 30
    ) -> None:
        """
        Add a meal to the schedule.

        Args:
            meal_cost: Cost of the meal
            meal_duration_minutes: Duration of meal (default: 30 min)
        """
        item = {
            "type": "MEAL",
            "name": "Meal",
            "duration_minutes": meal_duration_minutes,
            "cost": meal_cost
        }

        self._scheduled_items.append(item)
        self._total_time_scheduled_minutes += meal_duration_minutes
        self._total_cost += meal_cost

    def add_accommodation(
        self,
        accommodation_cost: float,
        accommodation_duration_hours: int = 8
    ) -> None:
        """
        Add accommodation to the schedule.

        Args:
            accommodation_cost: Cost of accommodation
            accommodation_duration_hours: Hours for accommodation (default: 8)
        """
        item = {
            "type": "ACCOMMODATION",
            "name": "Accommodation",
            "duration_minutes": accommodation_duration_hours * 60,
            "cost": accommodation_cost
        }

        self._scheduled_items.append(item)
        self._total_time_scheduled_minutes += accommodation_duration_hours * 60
        self._total_cost += accommodation_cost

    def add_job(
        self,
        job_name: str,
        hours_worked: float,
        hourly_rate: float
    ) -> bool:
        """
        Add a job/work to the schedule.

        Args:
            job_name: Name of the job
            hours_worked: Hours to work
            hourly_rate: Hourly rate of pay

        Returns:
            True if added successfully, False if not enough time
        """
        job_duration_minutes = int(hours_worked * 60)

        # Check if job fits in remaining time
        if not self.can_fit_activity(job_duration_minutes):
            return False

        earnings = hours_worked * hourly_rate

        item = {
            "type": "JOB",
            "name": job_name,
            "duration_minutes": job_duration_minutes,
            "cost": -earnings,  # Negative cost = earnings
            "hours_worked": hours_worked,
            "hourly_rate": hourly_rate
        }

        self._scheduled_items.append(item)
        self._total_time_scheduled_minutes += job_duration_minutes
        self._total_cost -= earnings  # Subtract from cost (add to budget)

        return True

    # ==================== Schedule Analysis ====================

    def get_activity_count(self) -> int:
        """Get count of optional activities scheduled."""
        return sum(1 for item in self._scheduled_items if item["type"] == "ACTIVITY")

    def get_job_count(self) -> int:
        """Get count of jobs scheduled."""
        return sum(1 for item in self._scheduled_items if item["type"] == "JOB")

    def get_total_earnings(self) -> float:
        """
        Get total earnings from jobs.

        Returns:
            Sum of earnings from all jobs
        """
        total = 0.0
        for item in self._scheduled_items:
            if item["type"] == "JOB":
                total += abs(item["cost"])  # Job cost is negative (earnings)
        return total

    def get_activity_cost(self) -> float:
        """
        Get total cost of optional activities.

        Returns:
            Sum of activity costs
        """
        return sum(
            item["cost"]
            for item in self._scheduled_items
            if item["type"] == "ACTIVITY"
        )

    def get_free_time_after_minimum_stay(self) -> float:
        """
        Get free time remaining after minimum stay and scheduled items.

        Returns:
            Hours of free time
        """
        return self.get_remaining_time_hours()

    def has_free_time(self) -> bool:
        """Check if there is any free time remaining."""
        return self.get_remaining_time_minutes() > 0

    # ==================== Suggestion Engine ====================

    def suggest_feasible_combinations(
        self,
        available_budget: float,
        optional_activities: List[dict]
    ) -> List[dict]:
        """
        Suggest feasible combinations of activities that fit in available time and budget.

        Uses greedy algorithm to maximize activity count within constraints.

        Args:
            available_budget: Budget available for activities
            optional_activities: List of available activities

        Returns:
            List of suggested combinations, each with activities, cost, and free time
        """
        remaining_time = self.get_remaining_time_minutes()
        remaining_budget = available_budget

        # Sort activities by time efficiency (cost per minute)
        sorted_activities = sorted(
            optional_activities,
            key=lambda a: (a.get("cost", 0) / max(1, a.get("duration_min", 1)))
        )

        suggestions = []

        # Greedy approach: try to fit maximum activities
        for activity in sorted_activities:
            activity_cost = activity.get("cost", 0)
            activity_duration = activity.get("duration_min", 0)
            activity_name = activity.get("name", "Unknown")

            if (activity_cost <= remaining_budget and
                    activity_duration <= remaining_time):

                # Create a suggestion with this activity
                suggestion = {
                    "activities": [activity_name],
                    "activity_objects": [activity],
                    "total_cost": activity_cost,
                    "total_time_minutes": activity_duration,
                    "free_time_remaining": remaining_time - activity_duration
                }

                suggestions.append(suggestion)

                # Try combinations with this activity
                remaining_budget -= activity_cost
                remaining_time -= activity_duration

        return suggestions

    # ==================== Serialization ====================

    def to_dict(self) -> dict:
        """
        Convert schedule to dictionary for serialization.

        Returns:
            Dictionary representation of the schedule
        """
        return {
            "airport": {
                "code": self._airport.get_IATA_code(),
                "name": self._airport.get_name()
            },
            "arrival_time": self._arrival_time.isoformat(),
            "minimum_stay_hours": self._minimum_stay_hours,
            "scheduled_items": self._scheduled_items.copy(),
            "summary": {
                "total_cost": self._total_cost,
                "total_time_minutes": self._total_time_scheduled_minutes,
                "total_time_hours": self.get_total_time_scheduled_hours(),
                "remaining_time_hours": self.get_remaining_time_hours(),
                "activity_count": self.get_activity_count(),
                "job_count": self.get_job_count(),
                "total_earnings": self.get_total_earnings()
            }
        }

    def __repr__(self) -> str:
        """String representation of the schedule."""
        return (
            f"DailySchedule({self._airport.get_IATA_code()} | "
            f"Time: {self.get_total_time_scheduled_hours():.1f}/{self._minimum_stay_hours}h | "
            f"Cost: ${self._total_cost:.2f} | "
            f"Items: {len(self._scheduled_items)})"
        )
