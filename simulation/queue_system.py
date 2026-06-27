import simpy

class QueueSystem:
    """
    Classe QueueSystem - Operação Atlas
    Gerencia o armazenamento estruturado e a extração prioritária das falhas
    utilizando o componente nativo PriorityStore do SimPy sob uma abordagem 
    multicriterio de minimização de custos.
    """

    def __init__(self, env):
        self.env = env
        # Contêiner nativo que extrai prioritariamente os menores valores numéricos
        self.queue = simpy.PriorityStore(env)
        # Desempacotador unívoco para evitar colisões e comparações diretas de objetos Asset
        self.counter = 0 

    def add_failure(self, asset, fault_time):
        """
        Injeta uma nova falha na PriorityStore aplicando a fórmula de inversão
        matemática multicritério para cenários de alta criticidade offshore.
        """
        self.counter += 1 
        
        # --- MODELAGEM COMPUTACIONAL DA PRIORIDADE INVERTIDA ---
        # Coeficientes de ponderação padrão do setor de engenharia de confiabilidade
        alpha = 0.4   # Peso associado ao Custo Financeiro (C)
        beta = 0.4    # Peso associado ao Impacto Operacional (I)
        gamma = 0.2   # Peso associado à Criticidade Regulatória (R)
        
        # Atributos extraídos diretamente do objeto Asset afetado
        C = getattr(asset, 'financial_risk', 5.0)
        I = getattr(asset, 'operational_impact', 5.0)
        R = getattr(asset, 'regulatory_criticality', 5.0)
        
        # Fórmula multicritério invertida: prioridades altamente negativas saem primeiro
        # Exemplo: -9.50 (Catastrófico) < -2.10 (Leve) -> O SimPy despacha o -9.50 primeiro
        priority_score = -1.0 * (alpha * C + beta * I + gamma * R)
        
        # Estrutura unívoca da tupla de controle da PriorityStore (4 elementos):
        # 1. Score de Prioridade | 2. Timestamp do Guasto | 3. Contador | 4. Objeto Asset
        event_tuple = (priority_score, fault_time, self.counter, asset)
        
        return self.queue.put(event_tuple)

    def get_next_failure(self):
        """
        Extrai o chamado de maior prioridade (menor valor numérico) 
        retido na PriorityStore do sistema.
        """
        return self.queue.get()
