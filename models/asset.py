import random

class Asset:
    """
    Classe Asset - Operação Atlas
    Representa a infraestrutura física offshore (Plataforma/FPSO).
    Governa os atributos de risco multicritério e a evolução temporal da
    degradação física através de uma Cadeia de Markov de 5 estados.
    """

    def __init__(self, name):
        self.name = name
        
        # --- Atributos de Risco Multicritério (Escala de 1.0 a 10.0) ---
        # Definidos dinamicamente para alimentar a PriorityStore do QueueSystem
        self.financial_risk = random.uniform(5.0, 10.0)
        self.operational_impact = random.uniform(4.0, 9.0)
        self.regulatory_criticality = random.uniform(3.0, 8.0)
        
        # --- Estados da Cadeia de Markov (0 a 4) ---
        self.current_state = 0  # Inicializa em Estado 0 (Bom)
        self.previous_state = 0
        
        # Matriz de Intensidade de Transição de Markov (Probabilidades por hora)
        # Define a taxa de degradação sequencial contínua em background
        self.transition_probabilities = {
            0: {1: 0.02, 4: 0.001},  # Probabilidade de degradar para 1 ou sofrer falha catastrófica direta (Poisson)
            1: {2: 0.04, 4: 0.002},  # Do estado Regular para Alerta
            2: {3: 0.06, 4: 0.005},  # Do estado Alerta para Crítico
            3: {4: 0.12}             # Do estado Crítico para Falha Total (Parada Crítica)
        }

    def update_degradation_state(self, current_time):
        """
        Executa a transição discreta de estados da Cadeia de Markov a cada tick.
        Retorna True caso ocorra uma mudança de estado, permitindo o gatilho
        imediato de métricas e inserção em fila.
        """
        # Se o ativo já se encontra em Falha Total (4), nenhuma nova transição ocorre até o reparo
        if self.current_state == 4:
            return False

        self.previous_state = self.current_state
        r = random.random()
        cumulative_prob = 0.0
        
        # Captura as probabilidades de saída associadas ao estado atual do ativo
        available_transitions = self.transition_probabilities.get(self.current_state, {})
        
        for next_state, prob in available_transitions.items():
            cumulative_prob += prob
            if r <= cumulative_prob:
                self.current_state = next_state
                break
                
        # Retorna True se houve mudança real na integridade do ativo
        return self.current_state != self.previous_state

    def get_repair_time(self):
        """
        Calcula o tempo físico de serviço técnico necessário para o reparo.
        Modificado por uma distribuição estocástica baseada na severidade histórica.
        """
        # Tempo de reparo estocástico (e.g., média de 8 horas, variando de 4 a 12)
        return random.uniform(4.0, 12.0)

    def repair(self):
        """
        Restaura o ativo ao seu estado de confiabilidade original (Estado 0)
        após a conclusão do ciclo de manutenção executado pelo Dispatcher.
        """
        self.previous_state = self.current_state
        self.current_state = 0  # Reset completo de integridade


    def __str__(self):
        return f"Asset {self.name} | Estado Atual: {self.current_state} | Risco: {self.financial_risk:.2f}"
