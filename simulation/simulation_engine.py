import simpy

class SimulationEngine:
    """
    Classe SimulationEngine - Operação Atlas
    Motor central de gerenciamento de estados da malha offshore. Coordena a 
    evolução temporal dos ativos, a execução dos monitores dinâmicos e o 
    cálculo contínuo de disponibilidade da rede.
    """

    def __init__(self, env, assets, queue_system, metrics):
        self.env = env
        self.assets = assets
        self.queue_system = queue_system
        self.metrics = metrics
        
        # Sincronização inicial do estado amostral do MetricsCollector
        self.metrics.log_queue_size(0)
        self.metrics.log_operational_assets(self.assets)

    def update_assets(self):
        """
        Processo contínuo que governa a evolução do relógio de degradação interna 
        e a transição de estados de falha das plataformas na timeline do SimPy.
        """
        while True:
            for asset in self.assets:
                # Executa a atualização discreta do estado de usura (Cadeia de Markov)
                state_changed = asset.update_degradation_state(self.env.now)
                
                # Se o ativo migrou para o estado crítico de falha (current_state == 4)
                if state_changed and asset.current_state == 4:
                    # Registra o evento estocástico de falha associado à usura contínua
                    self.metrics.log_failure(asset, "MARKOV_DEGRADATION", self.env.now)
                    
                    # Injeta o ativo na PriorityStore do sistema de filas inteligente
                    self.queue_system.add_failure(asset, self.env.now)
                    
                    # REGRA DA INTEGRAL: Notifica imediatamente o coletor sobre a mudança na malha
                    self.metrics.log_operational_assets(self.assets)
                    
                    # CORREÇÃO CRÍTICA 1: Acesso correto aos itens da PriorityStore do SimPy
                    self.metrics.log_queue_size(len(self.queue_system.queue.items))

            # Avança uma unidade de tempo discreta (1 hora) antes da próxima varredura
            yield self.env.timeout(1)

    def monitor_system(self):
        """
        Processo de auditoria cronológica contínua. Executa o campionamento 
        periódico de segurança para capturar a estabilidade das filas e ativos.
        """
        while True:
            # CORREÇÃO CRÍTICA 2: Acesso correto aos itens da PriorityStore do SimPy
            self.metrics.log_queue_size(len(self.queue_system.queue.items))
            
            # Registra o número instantâneo de ativos em operação plena para a integral de Uptime
            self.metrics.log_operational_assets(self.assets)
            
            # Intervalo regular de amostragem (1 unidade de tempo) para alta fidelidade estatística
            yield self.env.timeout(1)
