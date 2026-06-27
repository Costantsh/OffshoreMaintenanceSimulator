import random
import simpy

class FailureProcess:
    """
    Classe FailureProcess - Operação Atlas
    Responsável por governar o processo estocástico puro de Poisson (falhas por
    força maior e abruptas), injetando indisponibilidade de forma independente 
    da usura mecânica na linha do tempo do SimPy.
    """

    def __init__(self, env, failure_rate, engine):
        self.env = env
        self.failure_rate = failure_rate  # Parâmetro Lambda do processo de Poisson
        self.engine = engine  # Referência ao SimulationEngine para acessar os ativos

    def run(self):
        """
        Gera eventos de falha abrupta seguindo uma distribuição exponencial
        (tempo entre chegadas do processo de Poisson).
        """
        while True:
            # Tempo até a próxima falha abrupta global baseada em distribuição exponencial
            time_to_failure = random.expovariate(self.failure_rate)
            yield self.env.timeout(time_to_failure)

            # Seleciona aleatoriamente um ativo para sofrer a falha de Poisson
            if self.engine.assets:
                asset = random.choice(self.engine.assets)

                # Se o ativo já estiver quebrado (Estado 4), o evento de Poisson é ignorado
                if asset.current_state != 4:
                    # Configura os estados cronológicos de transição
                    asset.previous_state = asset.current_state
                    
                    # Força o ativo diretamente ao Estado 4 (Falha Total por força maior)
                    asset.current_state = 4

                    # Registra o evento de Poisson de forma isolada e científica no coletor
                    self.engine.metrics.log_failure(asset, "POISSON_ABRUPT_EVENT", self.env.now)

                    # Injeta imediatamente o ativo danificado na PriorityStore do sistema de filas
                    self.engine.queue_system.add_failure(asset, self.env.now)

                    # Atualiza as métricas integrais de área (AUC) no exato instante do guasto
                    self.engine.metrics.log_operational_assets(self.engine.assets)
                    self.engine.metrics.log_queue_size(len(self.engine.queue_system.queue.items))
