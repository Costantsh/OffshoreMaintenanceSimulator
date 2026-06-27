class PriorityOptimizer:

    ALPHA = 0.5
    BETA = 0.3
    GAMMA = 0.2

    @staticmethod
    def calculate_priority(criticality, impact, financial_risk):
        return -(
            PriorityOptimizer.ALPHA * criticality +
            PriorityOptimizer.BETA * impact +
            PriorityOptimizer.GAMMA * financial_risk
        )