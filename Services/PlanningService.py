class PlanningService:
    def __init__(self, actualAirports):
        self._actualAirports = actualAirports
        self.selected_job = None

    def setSelectedJob(self, job):
        self.selected_job = job
        
    def applyJobs(self, budget, actualBudget, hours):
        if actualBudget < 0 or budget < 0:
            raise Exception("Budget cannot be negative")
        
        if actualBudget < (budget * 0.35):
            if self.selected_job is not None:
                raise Exception("You cannot apply a job when the actual budget is over 35% of the total budget")
            if hours > self._actualAirports.getJobs()[self.selected_job].get_max_hours():
                raise Exception("You cannot apply a job when the hours exceed the maximum hours for that job")
            self._work(actualBudget, hours)
    
    def _work(self, actualBudget, hours):
        works = self._actualAirports.getJobs()
        if self.selected_job in works:
            workedHours = works[self.selected_job].get_hourly_rate() * hours
            actualBudget += workedHours
            return actualBudget
            