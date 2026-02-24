class MetabolicState:
    def __init__(self, heart_rate, temperature, respiration_rate):
        self.heart_rate = heart_rate  # in beats per minute
        self.temperature = temperature  # in degrees Celsius
        self.respiration_rate = respiration_rate  # in breaths per minute
        self.vital_signs_history = []
        self.entropy_decay = 0.0
        self.death_conditions = []
        self.divergence_metrics = []

    def track_vital_signs(self):
        vital_signs = {
            'heart_rate': self.heart_rate,
            'temperature': self.temperature,
            'respiration_rate': self.respiration_rate,
        }
        self.vital_signs_history.append(vital_signs)

    def calculate_entropy_decay(self):
        # Implement entropy decay calculation.
        self.entropy_decay += 0.01  # Example increment. Replace with actual logic.

    def assess_death_conditions(self):
        if self.heart_rate < 20 or self.temperature < 30:
            self.death_conditions.append('Critical condition')
        # Add more conditions as necessary.

    def calculate_divergence_metrics(self):
        # Placeholder for divergence metrics calculation.
        metric = abs(self.heart_rate - 70) / 70  # Example metric calculation.
        self.divergence_metrics.append(metric)

    def update_state(self, heart_rate, temperature, respiration_rate):
        self.heart_rate = heart_rate
        self.temperature = temperature
        self.respiration_rate = respiration_rate
        self.track_vital_signs()
        self.calculate_entropy_decay()
        self.assess_death_conditions()
        self.calculate_divergence_metrics()

    def __str__(self):
        return (f'MetabolicState(heart_rate={self.heart_rate}, temperature={self.temperature}, ' 
                f'respiration_rate={self.respiration_rate}, entropy_decay={self.entropy_decay})')