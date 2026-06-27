import numpy as np

class MetricsCollector:
    """
    Classe MetricsCollector - Operação Atlas (Abordagem Integral Estacionária)
    Responsável pela coleta de dados, cálculo de médias temporais ponderadas
    e rastreamento do inventário real em trânsito no sistema de manutenção.
    """

    def __init__(self, env=None):
        self.env = env
        self.failures = []
        self.response_times = []
        
        # --- Vetores Históricos Filtrados Necessários para o Plotter ---
        self.queue_sizes = []
        self.operational_assets = []
        self.timeline_plotter = []
        
        # --- Estruturas para Cálculo de Média Temporal Ponderada (Integrais) ---
        self.last_update_time = 0.0
        self.queue_area_post_warmup = 0.0
        self.current_queue_size = 0
        
        self.system_area_post_warmup = 0.0
        self.current_assets_in_system = 0  # Contador de inventário real no sistema (L)
        
        self.operational_area_post_warmup = 0.0
        self.current_operational_count = 6.0  
        
        self.max_queue_post_warmup = 0.0

        # --- Definição Dinâmica das Janelas de Controle Estacionário ---
        self.simulation_time_total = 2190.0  
        self.warmup_time = int(self.simulation_time_total * 0.2) # 438 horas

    def log_failure(self, asset, source, time):
        """Registra a ocorrência de falhas e incrementa o inventário no sistema."""
        if time > self.warmup_time:
            self.failures.append({"asset": asset.name, "source": source, "time": time})
        
        # Atualiza a integral do sistema (L) antes de alterar o contador
        self._update_integrals()
        self.current_assets_in_system += 1

    def log_response_time(self, start_time, end_time):
        """Registra o tempo de ciclo (W) e decrementa o inventário no sistema."""
        if start_time > self.warmup_time:
            self.response_times.append(end_time - start_time)
            
        # O ciclo logístico terminou (técnicos na base): remove o ativo do sistema de manutenção
        self._update_integrals()
        self.current_assets_in_system = max(0, self.current_assets_in_system - 1)

    def log_queue_size(self, size):
        """Armazena o histórico contínuo para o Plotter e atualiza a integral."""
        self._update_integrals()
        if self.env and self.env.now > self.warmup_time:
            self.queue_sizes.append(size)
            self.timeline_plotter.append(self.env.now)
        self.current_queue_size = size

    def log_operational_assets(self, assets):
        """Armazena o histórico de Uptime para o Plotter e atualiza a integral."""
        self._update_integrals()
        operational = sum(1 for a in assets if a.current_state == 0)
        if self.env and self.env.now > self.warmup_time:
            self.operational_assets.append(operational)
        self.current_operational_count = operational

    def _update_integrals(self):
        """Executa a integração contínua das áreas sob a curva (AUC)."""
        current_time = self.env.now if self.env else 0.0
        if current_time > self.warmup_time:
            clamped_start = max(self.warmup_time, self.last_update_time)
            effective_delta = current_time - clamped_start
            if effective_delta > 0:
                self.queue_area_post_warmup += self.current_queue_size * effective_delta
                self.system_area_post_warmup += self.current_assets_in_system * effective_delta
                self.operational_area_post_warmup += self.current_operational_count * effective_delta
                
                if self.current_queue_size > self.max_queue_post_warmup:
                    self.max_queue_post_warmup = self.current_queue_size
                    
        self.last_update_time = current_time
    
    def compute_statistics(self):
        """Consolida os KPIs aplicando a validação de Little purificada por inventário."""
        current_time = self.env.now if self.env else self.simulation_time_total
        self.warmup_time = int(current_time * 0.2)
        net_observation_time = current_time - self.warmup_time
        
        # Fecha as integrais de área no último tick da simulação
        self._update_integrals()

        stats = {
            "avg_response": 0.0,
            "std_response": 0.0,
            "avg_queue": 0.0,
            "max_queue": self.max_queue_post_warmup,
            "avg_operational": 0.0
        }

        if self.response_times:
            stats["avg_response"] = np.mean(self.response_times)
            stats["std_response"] = np.std(self.response_times)

        if net_observation_time > 0:
            stats["avg_queue"] = self.queue_area_post_warmup / net_observation_time
            stats["avg_operational"] = self.operational_area_post_warmup / net_observation_time
            # L_real empiricamente medido pelo tempo médio de permanência real no sistema
            l_sim = self.system_area_post_warmup / net_observation_time
        else:
            l_sim = 0.0
            
        c_equipes = 4.0  
        w_sim = stats["avg_response"]
        
        total_failures_post_warmup = len(self.failures)
        lambda_sim = total_failures_post_warmup / net_observation_time if net_observation_time > 0 else 0.0
        
        if w_sim > 0:
            mu_sim = 1.0 / w_sim
            rho_sim = lambda_sim / (c_equipes * mu_sim) if mu_sim > 0 else 0.0
        else:
            mu_sim = 0.0
            rho_sim = 0.0

        # Validação analítica universal da Lei de Little: L = λ * W
        l_little = lambda_sim * w_sim
        
        stats["lambda_sim"] = lambda_sim
        stats["mu_sim"] = mu_sim
        stats["rho_sim"] = rho_sim
        stats["L_sim_real"] = l_sim
        stats["L_from_Little_Law"] = l_little
        
        # Erro matemático limpo baseado no balanço rigoroso de inventário
        stats["little_error_pct"] = abs(l_sim - l_little) / l_sim * 100 if l_sim > 0 else 0.0
       
        return stats
