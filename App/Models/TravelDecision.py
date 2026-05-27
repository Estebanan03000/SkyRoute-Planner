import uuid
from datetime import datetime
from typing import Optional


class TravelDecision:
    """
    Represents a single decision made by a traveler during their journey.
    Records what was chosen, when, and its impact on budget/time.
    """

    def __init__(
        self,
        decision_type: str,
        airport_code: str,
        item_name: str
    ) -> None:
        """
        Initialize a new travel decision record.

        Args:
            decision_type: Type of decision (ACTIVITY, JOB, FLIGHT, SKIP, ACCOMMODATION, MEAL)
            airport_code: IATA code of airport where decision was made
            item_name: Name of item chosen (activity name, job name, destination, etc)
        """
        self._decision_id: str = str(uuid.uuid4())
        self._timestamp: datetime = datetime.now()
        self._decision_type: str = decision_type
        self._airport_code: str = airport_code
        self._item_name: str = item_name

        # Impact metrics
        self._cost_impact: float = 0.0  # Negative for expenses, positive for earnings
        self._time_spent_minutes: int = 0
        self._details: dict = {}

    # ==================== Getters ====================

    def get_decision_id(self) -> str:
        """Get unique decision identifier."""
        return self._decision_id

    def get_timestamp(self) -> datetime:
        """Get when decision was made."""
        return self._timestamp

    def get_decision_type(self) -> str:
        """Get type of decision."""
        return self._decision_type

    def get_airport_code(self) -> str:
        """Get airport code where decision was made."""
        return self._airport_code

    def get_item_name(self) -> str:
        """Get name of item selected."""
        return self._item_name

    def get_cost_impact(self) -> float:
        """Get cost impact (negative=expense, positive=earning)."""
        return self._cost_impact

    def get_time_spent_minutes(self) -> int:
        """Get time spent on this decision (in minutes)."""
        return self._time_spent_minutes

    def get_details(self) -> dict:
        """Get additional details about the decision."""
        return self._details.copy()

    # ==================== Setters ====================

    def set_cost_impact(self, cost: float) -> None:
        """Set the cost impact of this decision."""
        self._cost_impact = cost

    def set_time_spent_minutes(self, minutes: int) -> None:
        """Set time spent on this activity/job."""
        self._time_spent_minutes = minutes

    def add_detail(self, key: str, value) -> None:
        """
        Add a detail to the decision record.

        Args:
            key: Detail key
            value: Detail value
        """
        self._details[key] = value

    def add_details(self, details_dict: dict) -> None:
        """
        Add multiple details to the decision record.

        Args:
            details_dict: Dictionary of details to add
        """
        self._details.update(details_dict)

    # ==================== Summary Methods ====================

    def get_summary(self) -> str:
        """
        Get human-readable summary of the decision.

        Returns:
            Formatted string describing the decision
        """
        summary = f"[{self._decision_type}] {self._item_name}"

        if self._cost_impact != 0:
            symbol = "+" if self._cost_impact > 0 else "-"
            summary += f" ({symbol}${abs(self._cost_impact):.2f})"

        if self._time_spent_minutes > 0:
            hours = self._time_spent_minutes / 60
            summary += f" ({hours:.1f}h)"

        return summary

    def get_detailed_summary(self) -> str:
        """
        Get detailed summary with all information.

        Returns:
            Detailed string representation
        """
        lines = [
            f"Decision: {self._decision_type}",
            f"Item: {self._item_name}",
            f"Airport: {self._airport_code}",
            f"Time: {self._timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        ]

        if self._cost_impact != 0:
            symbol = "earned" if self._cost_impact > 0 else "spent"
            lines.append(f"Budget impact: {symbol} ${abs(self._cost_impact):.2f}")

        if self._time_spent_minutes > 0:
            hours = self._time_spent_minutes / 60
            lines.append(f"Time invested: {hours:.1f} hours")

        if self._details:
            lines.append("Details:")
            for key, value in self._details.items():
                lines.append(f"  - {key}: {value}")

        return "\n".join(lines)

    # ==================== Serialization ====================

    def to_dict(self) -> dict:
        """
        Convert decision to dictionary for storage/transmission.

        Returns:
            Dictionary representation of the decision
        """
        return {
            "decision_id": self._decision_id,
            "timestamp": self._timestamp.isoformat(),
            "type": self._decision_type,
            "airport_code": self._airport_code,
            "item_name": self._item_name,
            "cost_impact": self._cost_impact,
            "time_spent_minutes": self._time_spent_minutes,
            "summary": self.get_summary(),
            "details": self._details.copy()
        }

    def __repr__(self) -> str:
        """String representation of the decision."""
        return (
            f"TravelDecision({self._decision_type}: {self._item_name} "
            f"@ {self._airport_code} | "
            f"Cost: ${self._cost_impact:.2f}, Time: {self._time_spent_minutes}min)"
        )

    # ==================== Classification ====================

    def is_financial_decision(self) -> bool:
        """Check if this decision has financial impact."""
        return self._cost_impact != 0.0

    def is_time_consuming(self) -> bool:
        """Check if this decision consumes time."""
        return self._time_spent_minutes > 0

    def is_income_generating(self) -> bool:
        """Check if this decision generates income."""
        return self._cost_impact > 0

    def is_expense(self) -> bool:
        """Check if this decision is an expense."""
        return self._cost_impact < 0

    def is_flight(self) -> bool:
        """Check if this is a flight decision."""
        return self._decision_type == "FLIGHT"

    def is_work(self) -> bool:
        """Check if this is a job/work decision."""
        return self._decision_type == "JOB"

    def is_activity(self) -> bool:
        """Check if this is an optional activity decision."""
        return self._decision_type == "ACTIVITY"

    def is_mandatory(self) -> bool:
        """Check if this is a mandatory activity (meal, accommodation)."""
        return self._decision_type in ["MEAL", "ACCOMMODATION"]
