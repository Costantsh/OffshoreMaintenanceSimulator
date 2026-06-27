class Dispatcher:  
    """
    Classe Dispatcher - Operação Atlas  
    Coordena a alocação dinâmica das equipes de manutenção offshore  
    com base nas prioridades calculadas e na disponibilidade de recursos.  
    """

    def __init__(self, env, queue_system, teams, graph, metrics):  
        self.env = env  
        self.queue_system = queue_system  
        self.teams = teams  
        self.graph = graph  
        self.metrics = metrics 

    def run(self):  
        """  
        Ciclo principal do Dispatcher como um processo contínuo na linha do tempo.  
        """  
        while True:  
            # Recupera a falha com maior prioridade que representa o menor valor numérico no SimPy.  
            # O parâmetro fault_time é essencial para rastrear o momento exato em que o ativo falhou.  
            # O caractere underscore é utilizado para ignorar as variáveis de controle interno do SimPy.  
            _, fault_time, _, asset = yield self.queue_system.get_next_failure() 

            # Busca por uma equipe técnica que esteja livre no momento.  
            team = self.get_available_team() 

            # Gerenciamento do gargalo operacional.  
            # Caso todas as equipes estejam ocupadas, o Dispatcher aguarda a liberação dos recursos.  
            while team is None:  
                yield self.env.timeout(1) # Avança uma unidade de tempo antes de verificar novamente.  
                team = self.get_available_team() 

            # Aloca a equipe disponível e inicia o processo de reparo independente.  
            self.env.process(self.handle_repair(team, asset, fault_time)) 

    def get_available_team(self):  
        """  
        Varredura dos agentes autônomos para encontrar a primeira equipe disponível.  
        """  
        for t in self.teams:  
            if t.available:  
                return t  
        return None 

    def handle_repair(self, team, asset, fault_time):
        """Gerencia o ciclo logístico completo de atendimento offshore."""
        team.available = False 

        # 1. NAVEGAÇÃO DE IDA
        distance = self.graph.route_distance("BASE", asset.name)  
        travel_time = distance / team.speed  
        yield self.env.timeout(travel_time) 

        # 2. REPARO FÍSICO
        repair_time = asset.get_repair_time()  
        yield self.env.timeout(repair_time) 
        asset.repair() # O ativo volta a operar aqui

        # 3. NAVEGAÇÃO DE RETORNO À BASE
        travel_back_time = distance / team.speed  
        yield self.env.timeout(travel_back_time) 

        # O ciclo logístico se encerra univocamente aqui (Equipe pronta na base)
        end_time = self.env.now  
        
        # Dispara o decremento do inventário e calcula o W síncrono
        self.metrics.log_response_time(fault_time, end_time) 

        team.distance_travelled += (distance * 2)  
        team.busy_time += (travel_time + repair_time + travel_back_time)  
        team.finish_job() 
        team.available = True
