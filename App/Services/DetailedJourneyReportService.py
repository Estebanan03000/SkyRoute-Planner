from typing import List, Optional
from datetime import datetime
from App.Models.TravelState import TravelState


class DetailedJourneyReportService:
    """
    Generates comprehensive journey reports with decision timeline,
    budget tracking, statistics, and efficiency analysis.
    """

    # ==================== Report Generation ====================

    @staticmethod
    def generate_journey_timeline(
        journey_states: List[TravelState],
        start_time: Optional[datetime] = None
    ) -> List[dict]:
        """
        Create a detailed timeline of all journey events.

        Args:
            journey_states: List of travel states at each step
            start_time: Optional start time (uses first event time if not provided)

        Returns:
            List of timeline events in chronological order
        """
        if not journey_states:
            return []

        timeline = []
        base_state = journey_states[0]

        # Use start time or calculate from events
        if not start_time and base_state.get_journey_events():
            start_time = datetime.fromisoformat(base_state.get_journey_events()[0]["timestamp"])

        current_time_offset = 0  # minutes from start

        for state in journey_states:
            for event in state.get_journey_events():
                time_offset_minutes = current_time_offset
                hours_offset = time_offset_minutes / 60

                timeline.append({
                    "elapsed_minutes": time_offset_minutes,
                    "elapsed_hours": round(hours_offset, 2),
                    "event_type": event["type"],
                    "description": event["description"],
                    "cost": round(event["cost"], 2),
                    "time_spent_minutes": event["time_minutes"],
                    "budget_before": "N/A",  # Set below
                    "budget_after": round(event["current_budget"], 2),
                    "timestamp": event["timestamp"]
                })

                current_time_offset += event["time_minutes"]

        return timeline

    @staticmethod
    def generate_budget_tracking(
        journey_states: List[TravelState]
    ) -> dict:
        """
        Generate detailed budget tracking throughout journey.

        Args:
            journey_states: List of travel states

        Returns:
            Dictionary with budget evolution
        """
        if not journey_states:
            return {}

        initial_state = journey_states[0]
        final_state = journey_states[-1]

        initial_budget = initial_state.get_initial_budget()
        final_budget = final_state.get_current_budget()
        total_spent = final_state.get_total_spent()
        total_earned = final_state.get_total_earned()

        # Categorize spending by type
        spending_by_type = {
            "flights": 0.0,
            "activities": 0.0,
            "meals": 0.0,
            "accommodation": 0.0,
            "jobs": 0.0,
            "other": 0.0
        }

        # Analyze events to categorize spending
        for state in journey_states:
            for event in state.get_journey_events():
                event_type = event["type"]
                cost = abs(event["cost"])

                if event_type == "FLIGHT":
                    spending_by_type["flights"] += cost
                elif event_type == "ACTIVITY":
                    spending_by_type["activities"] += cost
                elif event_type == "MEAL":
                    spending_by_type["meals"] += cost
                elif event_type == "ACCOMMODATION":
                    spending_by_type["accommodation"] += cost
                elif event_type == "JOB":
                    spending_by_type["jobs"] -= cost  # Jobs are earnings
                else:
                    spending_by_type["other"] += cost

        return {
            "initial_budget": round(initial_budget, 2),
            "final_budget": round(final_budget, 2),
            "total_spent": round(total_spent, 2),
            "total_earned": round(total_earned, 2),
            "net_change": round(final_budget - initial_budget, 2),
            "budget_remaining_percentage": round(
                (final_budget / initial_budget * 100) if initial_budget > 0 else 0, 1
            ),
            "spending_breakdown": {
                key: round(value, 2) for key, value in spending_by_type.items()
            }
        }

    @staticmethod
    def generate_time_accounting(
        journey_states: List[TravelState]
    ) -> dict:
        """
        Generate detailed time accounting throughout journey.

        Args:
            journey_states: List of travel states

        Returns:
            Dictionary with time breakdown
        """
        if not journey_states:
            return {}

        final_state = journey_states[-1]

        # Categorize time by type
        time_by_type = {
            "flights": 0,
            "activities": 0,
            "meals": 0,
            "accommodation": 0,
            "jobs": 0,
            "free_time": 0,
            "other": 0
        }

        # Analyze events
        for state in journey_states:
            for event in state.get_journey_events():
                event_type = event["type"]
                time_minutes = event["time_minutes"]

                if event_type == "FLIGHT":
                    time_by_type["flights"] += time_minutes
                elif event_type == "ACTIVITY":
                    time_by_type["activities"] += time_minutes
                elif event_type == "MEAL":
                    time_by_type["meals"] += time_minutes
                elif event_type == "ACCOMMODATION":
                    time_by_type["accommodation"] += time_minutes
                elif event_type == "JOB":
                    time_by_type["jobs"] += time_minutes
                else:
                    time_by_type["other"] += time_minutes

        # Calculate total time based on registered events
        allocated_time = sum(time_by_type.values())

        state_total_time_minutes = int(
            round(final_state.get_total_journey_time() * 60)
        )

        total_time_minutes = max(
            allocated_time,
            state_total_time_minutes
        )

        time_by_type["free_time"] = max(
            0,
            total_time_minutes - allocated_time
        )
        
        # Convert to hours and minutes
        result = {}
        for key, minutes in time_by_type.items():
            hours = minutes / 60
            result[key] = {
                "minutes": minutes,
                "hours": round(hours, 2),
                "percentage": round((minutes / total_time_minutes * 100) if total_time_minutes > 0 else 0, 1)
            }

        result["total_hours"] = round(total_time_minutes / 60, 2)

        return result

    @staticmethod
    def generate_destination_summary(
        journey_states: List[TravelState]
    ) -> dict:
        """
        Generate summary of destinations visited.

        Args:
            journey_states: List of travel states

        Returns:
            Dictionary with destination information
        """
        if not journey_states:
            return {}

        final_state = journey_states[-1]
        destinations = final_state.get_destinations_visited()

        return {
            "total_destinations": len(destinations),
            "destinations_list": destinations,
            "route": " → ".join(destinations),
            "starting_airport": destinations[0] if destinations else None,
            "final_airport": destinations[-1] if destinations else None,
            "unique_destinations": len(set(destinations))
        }

    @staticmethod
    def generate_decision_summary(
        journey_states: List[TravelState]
    ) -> dict:
        """
        Generate summary of all decisions made.

        Args:
            journey_states: List of travel states

        Returns:
            Dictionary with decision statistics
        """
        if not journey_states:
            return {}

        all_decisions = []
        decision_counts = {
            "ACTIVITY": 0,
            "JOB": 0,
            "FLIGHT": 0,
            "MEAL": 0,
            "ACCOMMODATION": 0,
            "SKIP": 0
        }

        for state in journey_states:
            decisions = state.get_travel_decisions()
            all_decisions.extend(decisions)

            for decision in decisions:
                decision_type = decision.get("type")
                if decision_type in decision_counts:
                    decision_counts[decision_type] += 1

        return {
            "total_decisions": len(all_decisions),
            "decisions_by_type": decision_counts,
            "activity_decisions": decision_counts.get("ACTIVITY", 0),
            "work_decisions": decision_counts.get("JOB", 0),
            "flight_decisions": decision_counts.get("FLIGHT", 0),
            "mandatory_decisions": (
                decision_counts.get("MEAL", 0) + decision_counts.get("ACCOMMODATION", 0)
            ),
            "decisions": [
                {
                    "type": d.get("type"),
                    "item": d.get("item_name"),
                    "airport": d.get("airport_code"),
                    "cost_impact": round(d.get("cost_impact", 0), 2),
                    "time_spent_minutes": d.get("time_spent_minutes", 0),
                    "summary": d.get("summary")
                }
                for d in all_decisions
            ]
        }

    @staticmethod
    def generate_efficiency_metrics(
        journey_states: List[TravelState]
    ) -> dict:
        """
        Generate efficiency and performance metrics.

        Args:
            journey_states: List of travel states

        Returns:
            Dictionary with efficiency metrics
        """
        if not journey_states:
            return {}

        final_state = journey_states[-1]

        destinations_count = len(final_state.get_destinations_visited())
        total_cost = final_state.get_total_spent()
        total_earned = final_state.get_total_earned()
        initial_budget = final_state.get_initial_budget()
        final_budget = final_state.get_current_budget()

        # Calculate efficiency scores
        destinations_per_dollar = (
            destinations_count / max(1, total_cost) if total_cost > 0 else 0
        )

        budget_efficiency_score = (
            (destinations_count * 10) - (total_cost / 100)
        )

        work_earnings_ratio = (
            total_earned / total_cost if total_cost > 0 else 0
        )

        budget_utilization = (
            (initial_budget - final_budget) / initial_budget * 100
            if initial_budget > 0 else 0
        )

        return {
            "destinations_visited": destinations_count,
            "total_spending": round(total_cost, 2),
            "total_earnings": round(total_earned, 2),
            "efficiency_scores": {
                "destinations_per_dollar": round(destinations_per_dollar, 4),
                "budget_efficiency_score": round(budget_efficiency_score, 2),
                "work_earnings_ratio": round(work_earnings_ratio, 3),
                "budget_utilization_percentage": round(budget_utilization, 1)
            },
            "performance_rating": DetailedJourneyReportService._calculate_performance_rating(
                destinations_count, budget_efficiency_score
            )
        }

    @staticmethod
    def _calculate_performance_rating(destinations: int, efficiency_score: float) -> str:
        """
        Calculate performance rating based on metrics.

        Args:
            destinations: Number of destinations visited
            efficiency_score: Efficiency score

        Returns:
            Performance rating string
        """
        if efficiency_score >= 30:
            return "Excellent"
        elif efficiency_score >= 20:
            return "Very Good"
        elif efficiency_score >= 10:
            return "Good"
        elif efficiency_score >= 0:
            return "Fair"
        else:
            return "Poor"

    # ==================== Complete Report Generation ====================

    @staticmethod
    def generate_complete_report(
        journey_states: List[TravelState]
    ) -> dict:
        """
        Generate a complete, comprehensive journey report.

        Args:
            journey_states: List of all travel states during journey

        Returns:
            Complete report dictionary
        """
        if not journey_states:
            return {"error": "No journey data provided"}

        final_state = journey_states[-1]
        
        visited = final_state.get_destinations_visited()

        initial_airport = (
            visited[0]
            if visited
            else final_state.get_current_airport().get_IATA_code()
        )

        final_airport = (
            visited[-1]
            if visited
            else final_state.get_current_airport().get_IATA_code()
        )

        return {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "traveler_name": final_state.get_traveler_name(),
                "report_type": "Complete Journey Report"
            },
            "journey_overview": {
                "initial_airport": initial_airport,
                "final_airport": final_airport,
                "total_states": len(journey_states),
                "total_events": len(final_state.get_journey_events()),
                "total_decisions": len(final_state.get_travel_decisions())
            },
            "destinations": DetailedJourneyReportService.generate_destination_summary(journey_states),
            "budget": DetailedJourneyReportService.generate_budget_tracking(journey_states),
            "time": DetailedJourneyReportService.generate_time_accounting(journey_states),
            "decisions": DetailedJourneyReportService.generate_decision_summary(journey_states),
            "efficiency": DetailedJourneyReportService.generate_efficiency_metrics(journey_states),
            "timeline": DetailedJourneyReportService.generate_journey_timeline(journey_states)
        }

    @staticmethod
    def format_report_for_display(report: dict) -> str:
        """
        Format complete report for console/screen display.

        Args:
            report: Complete report dictionary

        Returns:
            Formatted string for display
        """
        output = []
        output.append("=" * 80)
        output.append(f"JOURNEY REPORT - {report['report_metadata']['traveler_name']}")
        output.append("=" * 80)
        output.append("")

        # Overview
        overview = report["journey_overview"]
        output.append("JOURNEY OVERVIEW")
        output.append("-" * 40)
        output.append(f"Start: {overview['initial_airport']} → End: {overview['final_airport']}")
        output.append("")

        # Destinations
        destinations = report["destinations"]
        output.append("DESTINATIONS")
        output.append("-" * 40)
        output.append(f"Total: {destinations['total_destinations']}")
        output.append(f"Route: {destinations['route']}")
        output.append("")

        # Budget
        budget = report["budget"]
        output.append("BUDGET SUMMARY")
        output.append("-" * 40)
        output.append(f"Initial: ${budget['initial_budget']:.2f}")
        output.append(f"Spent: ${budget['total_spent']:.2f}")
        output.append(f"Earned: ${budget['total_earned']:.2f}")
        output.append(f"Final: ${budget['final_budget']:.2f}")
        output.append(f"Remaining: {budget['budget_remaining_percentage']}%")
        output.append("")

        # Efficiency
        efficiency = report["efficiency"]
        output.append("EFFICIENCY METRICS")
        output.append("-" * 40)
        scores = efficiency["efficiency_scores"]
        output.append(f"Destinations/Dollar: {scores['destinations_per_dollar']:.4f}")
        output.append(f"Budget Efficiency Score: {scores['budget_efficiency_score']:.2f}")
        output.append(f"Performance: {efficiency['performance_rating']}")
        output.append("")

        # Time
        time_data = report["time"]
        output.append("TIME ACCOUNTING")
        output.append("-" * 40)
        output.append(f"Total Journey: {time_data['total_hours']} hours")
        for category in ["flights", "activities", "meals", "accommodation", "jobs", "free_time"]:
            if category in time_data:
                output.append(f"  {category.capitalize()}: {time_data[category]['hours']:.2f}h "
                            f"({time_data[category]['percentage']:.1f}%)")

        return "\n".join(output)

    @staticmethod
    def get_service_summary() -> str:
        """Get summary of reporting service capabilities."""
        return (
            "DetailedJourneyReportService - Comprehensive journey reporting\n"
            "- Generate journey timeline\n"
            "- Track budget evolution\n"
            "- Analyze time accounting\n"
            "- Summarize destinations\n"
            "- Review decisions\n"
            "- Calculate efficiency metrics\n"
            "- Generate complete reports\n"
            "- Format reports for display"
        )
