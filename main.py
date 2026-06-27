import simpy  
import random 

from models.asset import Asset  
from models.team import Team  
from simulation.simulation_engine import SimulationEngine  
from simulation.failure_generator import FailureProcess  
from simulation.queue_system import QueueSystem  
from simulation.dispatcher import Dispatcher  
from graph.offshore_graph import OffshoreGraph  
from metrics.metrics_collector import MetricsCollector  
from metrics.plotter import Plotter 
from metrics.pdf_generator import PDFGenerator  

def run_simulation():
    ### Configuração da semente para reprodutibilidade dos testes iniciais
    ###random.seed(42) 

    ### Primeira simulação: Execução única para geração dos gráficos de desempenho
    env = simpy.Environment()  

    # CONFIGURAÇÃO SOLICITADA: 6 Instalações Petrolíferas Offshore
    assets = [Asset(f"A{a}") for a in range(6)] 

    # CONFIGURAÇÃO SOLICITADA: 4 Equipes Especializadas (Unidades Logísticas)
    teams = [Team(t, speed=random.uniform(5, 10), membros=4) for t in range(4)]
    metrics = MetricsCollector(env)
    queue_system = QueueSystem(env)  
    graph = OffshoreGraph() 

    engine = SimulationEngine(env, assets, queue_system, metrics) 

    ### Taxa de falha balanceada em 0.05 para manter a utilização do sistema estável
    failure_process = FailureProcess(env, failure_rate=0.05, engine=engine)  
    dispatcher = Dispatcher(env, queue_system, teams, graph, metrics) 

    ### Registro de todos os processos independentes na mesma linha do tempo do SimPy
    env.process(engine.update_assets())  
    env.process(failure_process.run())  
    env.process(dispatcher.run())  
    env.process(engine.monitor_system()) 

    ### Tempo  2190 unidades =  3 meses
    env.run(until=2190) 

    # Salvaguarda estável dos dados analíticos estruturais da primeira rodada
    primeiras_estatisticas = metrics.compute_statistics() 

    print("\n===== STATISTICS =====")  
    for k, v in primeiras_estatisticas.items():  
        print(f"{k}: {v:.2f}") 

    ### Impressão detalhada dos indicadores de desempenho da primeira execução
    print("\n===== SYSTEM PERFORMANCE =====")  
    print(f"Avg Queue Length: {primeiras_estatisticas['avg_queue']:.2f}")  
    print(f"Max Queue Length: {primeiras_estatisticas['max_queue']:.2f}")  
    print(f"Avg Operational Assets: {primeiras_estatisticas['avg_operational']:.2f}") 

    print("\n===== QUEUEING THEORY & VALIDATION (FINITE SOURCE) =====")  
    print(f"Lambda Effective (Arrival Rate λ_eff): {primeiras_estatisticas['lambda_sim']:.3f} failures/time")  
    print(f"Mu (Service Rate μ): {primeiras_estatisticas['mu_sim']:.3f} repairs/time")  
    print(f"Rho (System Utilization ρ): {primeiras_estatisticas['rho_sim']:.2%}") 

    print("\n===== LITTLE'S LAW VALIDATION (L = λ_eff * W) =====")  
    print(f"L (Avg Entities in System - Simulated): {primeiras_estatisticas['L_sim_real']:.3f}")  
    print(f"L (Calculated via Little's Law λ*W): {primeiras_estatisticas['L_from_Little_Law']:.3f}")  
    print(f"Validation Error: {primeiras_estatisticas['little_error_pct']:.2f}%") 

    ### Renderização gráfica dos resultados operacionais
    Plotter.plot_response_times(metrics)  
    Plotter.plot_queue(metrics)  
    Plotter.plot_operational(metrics)  
    Plotter.plot_histogram_response(metrics) 

    ### Segunda parte: Validação estatística robusta via Simulação de Monte Carlo
    results = [] 

    for i in range(20):  
        random.seed(i) 

        env = simpy.Environment() 

        # Sincronização estrita (6 ativos) no Monte Carlo
        assets = [Asset(f"A{a}") for a in range(6)]  
        # Sincronização estrita (4 equipes) no Monte Carlo
        teams = [Team(t, speed=random.uniform(5, 10)) for t in range(4)] 

        metrics_mc = MetricsCollector(env) 
        queue_system = QueueSystem(env)  
        graph = OffshoreGraph() 

        engine = SimulationEngine(env, assets, queue_system, metrics_mc)  
        failure_process = FailureProcess(env, 0.05, engine=engine)  
        dispatcher = Dispatcher(env, queue_system, teams, graph, metrics_mc) 

        env.process(engine.update_assets())  
        env.process(engine.monitor_system())  
        env.process(failure_process.run())  
        env.process(dispatcher.run()) 

        env.run(until=2190) 

        stats_mc = metrics_mc.compute_statistics()  
        results.append(stats_mc["avg_response"]) 

    ### Média final obtida através das 20 múltiplas iterações estocásticas
    mc_avg_response = sum(results) / len(results)
    print("\nMonte Carlo Avg Response:", mc_avg_response) 

    # Gera o PDF passando os novos dados dinâmicos do cenário solicitado
    PDFGenerator.generate_report(primeiras_estatisticas, mc_avg_response)
    
    return {
        "statistics": primeiras_estatisticas,
        "monte_carlo_avg_response": mc_avg_response
    }

if __name__ == "__main__":
    run_simulation()
