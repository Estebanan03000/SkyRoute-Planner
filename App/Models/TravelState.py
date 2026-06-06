from typing import List, Optional
from datetime import datetime
from App.Models.Airport import Airport


class TravelState:
    """
    Represents the complete state of a traveler at any point during their journey.
    Tracks location, budget, time, and journey history.
    """

    def __init__(
        self,
        current_airport: Airport,
        initial_budget: float,
        traveler_name: str,
        initial_time_hours: float = 0.0
    ) -> None:
        """
        Initialize a new journey state.

        Args:
            current_airport: The starting airport
            initial_budget: Initial money available for the trip
            traveler_name: Name of the traveler
            initial_time_hours: Initial available travel time in hours
        """
        self._current_airport: Airport = current_airport
        self._initial_budget: float = initial_budget
        self._current_budget: float = initial_budget
        self._initial_time_hours: float = initial_time_hours
        self._total_spent: float = 0.0
        self._total_earned: float = 0.0
        self._traveler_name: str = traveler_name

        # Time tracking (in hours)
        self._journey_start_time: datetime = datetime.now()
        self._time_at_current_airport: float = 0.0
        self._hours_since_last_accommodation: float = 0.0
        self._hours_since_last_meal: float = 0.0
        self._total_journey_time: float = 0.0

        # Distance tracking (in km) - Part C
        self._total_distance_traveled: float = 0.0
        self._subsidized_distance_traveled: float = 0.0

        # Journey history
        self._destinations_visited: List[str] = [current_airport.get_IATA_code()]
        self._journey_events: List[dict] = []
        self._travel_decisions: List[dict] = []

    # ==================== Getters ====================

    def get_current_airport(self) -> Airport:
        """Get the airport where the traveler is currently located."""
        return self._current_airport

    def get_current_budget(self) -> float:
        """Get available money."""
        return self._current_budget

    def get_initial_budget(self) -> float:
        """Get the initial budget at journey start."""
        return self._initial_budget

    def get_total_spent(self) -> float:
        """Get total amount spent during journey."""
        return self._total_spent

    def get_total_earned(self) -> float:
        """Get total amount earned from jobs."""
        return self._total_earned

    def get_initial_time_hours(self) -> float:
        """Get the initial available travel time in hours."""
        return self._initial_time_hours

    def get_remaining_time_hours(self) -> float:
        """Get how many hours remain from initial time after time events."""
        remaining = self._initial_time_hours - self._total_journey_time
        return max(0.0, remaining)

    def get_initial_time_minutes(self) -> float:
        """Get the initial available travel time in minutes."""
        return self._initial_time_hours * 60

    def get_remaining_time_minutes(self) -> float:
        """Get how many minutes remain from initial time after time events."""
        return self.get_remaining_time_hours() * 60

    def get_traveler_name(self) -> str:
        """Get traveler's name."""
        return self._traveler_name

    def get_time_at_current_airport(self) -> float:
        """Get hours spent at current airport."""
        return self._time_at_current_airport

    def get_hours_since_last_accommodation(self) -> float:
        """Get hours elapsed since last accommodation."""
        return self._hours_since_last_accommodation

    def get_hours_since_last_meal(self) -> float:
        """Get hours elapsed since last meal."""
        return self._hours_since_last_meal

    def get_total_journey_time(self) -> float:
        """Get total time spent in entire journey."""
        return self._total_journey_time

    def get_destinations_visited(self) -> List[str]:
        """Get list of airport codes visited."""
        return self._destinations_visited.copy()

    def get_journey_events(self) -> List[dict]:
        """Get list of all events during journey."""
        return self._journey_events.copy()

    def get_travel_decisions(self) -> List[dict]:
        """Get list of all decisions made by traveler."""
        return self._travel_decisions.copy()

    # ==================== Budget Management ====================

    def update_budget(self, amount: float) -> None:
        """
        Update budget after a transaction (expense or income).

        Args:
            amount: Positive for income, negative for expense
        """
        self._current_budget += amount
        if amount < 0:
            self._total_spent += abs(amount)
        else:
            self._total_earned += amount

    def get_budget_remaining_percentage(self) -> float:
        """Get budget as percentage of initial budget."""
        if self._initial_budget == 0:
            return 0.0
        return (self._current_budget / self._initial_budget) * 100

    # ==================== Time Management ====================

    def is_accommodation_required(self) -> bool:
        """
        Check if accommodation is required (20 hours since last stay).

        Returns:
            True if accommodation is needed, False otherwise
        """
        return self._hours_since_last_accommodation >= 20.0

    def is_meal_required(self) -> bool:
        """
        Check if meal is required (8 hours since last meal).

        Returns:
            True if meal is needed, False otherwise
        """
        return self._hours_since_last_meal >= 8.0

    def add_time_at_current_airport(self, hours: float) -> None:
        """
        Add time spent at current airport (activities, jobs, rest).

        Args:
            hours: Hours to add
        """
        self._time_at_current_airport += hours
        self._hours_since_last_meal += hours
        self._hours_since_last_accommodation += hours
        self._total_journey_time += hours

    def add_flight_time(self, flight_duration_hours: float) -> None:
        """
        Add time for a flight (updates meal and accommodation timers).

        Args:
            flight_duration_hours: Duration of flight in hours
        """
        self._hours_since_last_meal += flight_duration_hours
        self._hours_since_last_accommodation += flight_duration_hours
        self._total_journey_time += flight_duration_hours

    def reset_accommodation_timer(self) -> None:
        """Reset accommodation timer after lodging."""
        self._hours_since_last_accommodation = 0.0

    def reset_meal_timer(self) -> None:
        """Reset meal timer after eating."""
        self._hours_since_last_meal = 0.0

    def reset_airport_timer(self) -> None:
        """Reset airport stay timer when moving to new airport."""
        self._time_at_current_airport = 0.0

    # ==================== Event Management ====================

    def add_event(
        self,
        event_type: str,
        description: str,
        cost: float = 0.0,
        time_minutes: float = 0.0
    ) -> None:
        """
        Record an event during the journey.

        Args:
            event_type: Type of event (FLIGHT, MEAL, ACCOMMODATION, ACTIVITY, JOB)
            description: Description of the event
            cost: Cost associated with event (0 if none)
            time_minutes: Time spent on event
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "description": description,
            "cost": cost,
            "time_minutes": time_minutes,
            "current_budget": self._current_budget
        }
        self._journey_events.append(event)

    def add_decision(self, decision_record: dict) -> None:
        """
        Record a decision made by the traveler.

        Args:
            decision_record: Dictionary with decision details
        """
        self._travel_decisions.append(decision_record)

    # ==================== Airport Management ====================

    def fly_to_airport(
        self,
        destination_airport: Airport,
        flight_cost: float,
        flight_duration_hours: float
    ) -> None:
        """
        Execute a flight to a new airport.

        Args:
            destination_airport: Airport to fly to
            flight_cost: Cost of the flight
            flight_duration_hours: Duration of flight
        """
        # Deduct flight cost
        self.update_budget(-flight_cost)

        # Add flight time (affects meal and accommodation timers)
        self.add_flight_time(flight_duration_hours)

        # Update location and reset airport timer
        self._current_airport = destination_airport
        self.reset_airport_timer()

        # Record destination visit
        airport_code = destination_airport.get_IATA_code()
        if airport_code not in self._destinations_visited:
            self._destinations_visited.append(airport_code)

        # Record event
        self.add_event(
            event_type="FLIGHT",
            description=f"Flight to {destination_airport.get_IATA_code()} "
                       f"({destination_airport.get_city()})",
            cost=flight_cost,
            time_minutes=flight_duration_hours * 60
        )

    # ==================== State Snapshot ====================

    def to_dict(self) -> dict:
        """
        Convert current state to dictionary for serialization.

        Returns:
            Dictionary representation of travel state
        """
        return {
            "traveler_name": self._traveler_name,
            "current_airport": {
                "code": self._current_airport.get_IATA_code(),
                "name": self._current_airport.get_name(),
                "city": self._current_airport.get_city(),
                "country": self._current_airport.get_country()
            },
            "budget": {
                "initial": self._initial_budget,
                "current": self._current_budget,
                "total_spent": self._total_spent,
                "total_earned": self._total_earned,
                "percentage_remaining": self.get_budget_remaining_percentage()
            },
            "time": {
                "initial_time_hours": self._initial_time_hours,
                "initial_time_minutes": self.get_initial_time_minutes(),
                "remaining_time_hours": self.get_remaining_time_hours(),
                "remaining_time_minutes": self.get_remaining_time_minutes(),
                "total_journey_hours": self._total_journey_time,
                "total_journey_minutes": self.get_total_journey_time() * 60,
                "at_current_airport_hours": self._time_at_current_airport,
                "at_current_airport_minutes": self._time_at_current_airport * 60,
                "hours_since_last_accommodation": self._hours_since_last_accommodation,
                "minutes_since_last_accommodation": self._hours_since_last_accommodation * 60,
                "hours_since_last_meal": self._hours_since_last_meal,
                "minutes_since_last_meal": self._hours_since_last_meal * 60
            },
            "journey": {
                "destinations_visited": self._destinations_visited.copy(),
                "destinations_count": len(self._destinations_visited),
                "events": len(self._journey_events),
                "decisions": len(self._travel_decisions)
            },
            "status": {
                "needs_accommodation": self.is_accommodation_required(),
                "needs_meal": self.is_meal_required(),
                "budget_critical": self.get_budget_remaining_percentage() < 35
            }
        }

    def __repr__(self) -> str:
        """String representation of travel state."""
        return (
            f"TravelState(traveler='{self._traveler_name}', "
            f"airport={self._current_airport.get_IATA_code()}, "
            f"budget=${self._current_budget:.2f}, "
            f"destinations={len(self._destinations_visited)})"
        )

    # ==================== Distance Tracking (Part C) ====================

    def get_total_distance_traveled(self) -> float:
        """Get total kilometers traveled during journey."""
        return self._total_distance_traveled

    def get_subsidized_distance_traveled(self) -> float:
        """Get kilometers traveled on subsidized (free) routes."""
        return self._subsidized_distance_traveled

    def add_distance_traveled(self, distance_km: float) -> None:
        """Record distance traveled in a flight."""
        if distance_km > 0:
            self._total_distance_traveled += distance_km

    def add_subsidized_distance(self, distance_km: float) -> None:
        """Record distance traveled on subsidized route."""
        if distance_km > 0:
            self._subsidized_distance_traveled += distance_km

    def get_subsidized_distance_percentage(self) -> float:
        """Calculate percentage of journey using subsidized routes."""
        if self._total_distance_traveled == 0:
            return 0.0
        return (self._subsidized_distance_traveled / self._total_distance_traveled) * 100

