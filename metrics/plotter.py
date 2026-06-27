import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

class Plotter:
    """
    Classe Plotter - Operação Atlas (Versão Homologada Acadêmica)
    Responsável pela geração e estilização de gráficos corporativos de alta 
    resolução (300 DPI) utilizando filtragem de transiente inicial (Warm-up).
    """
    # Identidade Visual Executiva (Tema Dark Avançado)
    BG_COLOR = "#121824"      
    CARD_COLOR = "#1a2333"    
    TEXT_COLOR = "#e2e8f0"    
    LINE_PRIMARY = "#00f5d4"  
    LINE_SECONDARY = "#7b2cbf"
    GRID_COLOR = "#2d3748"    

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_DIR = os.path.join(BASE_DIR, "relatorio_graficos")

    @staticmethod
    def _prepare_output_directory():
        """Garante que a pasta de destino exista antes de salvar os arquivos."""
        if not os.path.exists(Plotter.OUTPUT_DIR):
            os.makedirs(Plotter.OUTPUT_DIR)

    @staticmethod
    def _apply_style(ax, title, xlabel, ylabel):
        """Aplica a padronização e tipografia acadêmica em cada eixo gráfico."""
        ax.set_facecolor(Plotter.CARD_COLOR)
        ax.set_title(title, fontsize=11, fontweight='bold', color=Plotter.TEXT_COLOR, pad=15)
        ax.set_xlabel(xlabel, fontsize=9, color=Plotter.TEXT_COLOR, labelpad=8)
        ax.set_ylabel(ylabel, fontsize=9, color=Plotter.TEXT_COLOR, labelpad=8)
        ax.tick_params(colors=Plotter.TEXT_COLOR, labelsize=8)
        ax.grid(True, color=Plotter.GRID_COLOR, linestyle='--', linewidth=0.5)
        for spine in ax.spines.values():
            spine.set_color(Plotter.GRID_COLOR)

    @staticmethod
    def plot_response_times(metrics):
        """Gráfico 1: Evolução Temporal do Tempo de Resposta de Ciclo (W)"""
        Plotter._prepare_output_directory()
        fig, ax = plt.subplots(figsize=(10, 4.5), facecolor=Plotter.BG_COLOR)
        times = metrics.response_times
        timeline = np.arange(len(times))

        # Plotagem do comportamento dos tempos de ciclo pós-warmup
        ax.plot(timeline, times, color=Plotter.LINE_PRIMARY, linewidth=1.8, label="Tempo no Sistema (W)")
        
        avg_w = np.mean(times) if times else 0
        ax.axhline(avg_w, color=Plotter.LINE_SECONDARY, linestyle=':', linewidth=1.5, 
                   label=f"Tempo Médio Global ({avg_w:.2f})")

        Plotter._apply_style(ax, "Evolução do Tempo de Resposta no Sistema (W)", 
                            "Ocorrências Concluídas (Fase Estacionária)", "Tempo (unidades)")
        ax.legend(facecolor=Plotter.CARD_COLOR, edgecolor=Plotter.GRID_COLOR, labelcolor=Plotter.TEXT_COLOR, fontsize=8)
        plt.tight_layout()
        
        plt.savefig(os.path.join(Plotter.OUTPUT_DIR, "01_tempo_resposta_W.png"), 
                    dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
        plt.close(fig)
    @staticmethod
    def plot_queue(metrics):
        """Gráfico 2: Comportamento da Fila de Espera Estacionária (Visual Otimizado)"""
        Plotter._prepare_output_directory()
        fig, ax = plt.subplots(figsize=(10, 4.5), facecolor=Plotter.BG_COLOR)
        sizes = np.array(metrics.queue_sizes)
        
        timeline = metrics.timeline_plotter if metrics.timeline_plotter else np.arange(len(sizes))
        timeline = np.array(timeline[:len(sizes)])

        # INGEGNERIA VISIVA: Calcolo della media mobile per eliminare il rumore orario densissimo
        window_size = 48  # Finestra di 48 ore per lisciare la curva
        if len(sizes) > window_size:
            smoothed_sizes = np.convolve(sizes, np.ones(window_size)/window_size, mode='same')
        else:
            smoothed_sizes = sizes

        # Tracciamento della linea lisciata (Trend stabile)
        ax.plot(timeline, smoothed_sizes, color=Plotter.LINE_PRIMARY, linewidth=2, 
                label="Tamanho Médio Móvel da Fila (Trend)")
        
        # Riempimento sfumato sotto la tendenza reale
        ax.fill_between(timeline, smoothed_sizes, color=Plotter.LINE_PRIMARY, alpha=0.1)

        # Evidenziazione dei picchi reali stocastici come punti isolati (Scatter), non come barre dense
        peak_indices = np.where(sizes > 0)[0]
        if len(peak_indices) > 0:
            ax.scatter(timeline[peak_indices], sizes[peak_indices], color="#ef4444", s=8, alpha=0.4,
                       label="Eventos de Ocupação Instantânea della Fila")

        # Linea dell'obiettivo medio calcolato dalla Bash (0.06)
        avg_q = np.mean(sizes) if len(sizes) > 0 else 0.06
        ax.axhline(avg_q, color=Plotter.LINE_SECONDARY, linestyle=':', linewidth=1.5, 
                   label=f"Ocupação Média Estacionária ({avg_q:.2f})")

        Plotter._apply_style(ax, "Dinâmica Ocupacional da Fila (Fase Estacionária Pós-Warmup)", 
                            "Tempo de Simulação (Horas)", "Quantidade na Fila")
        ax.legend(facecolor=Plotter.CARD_COLOR, edgecolor=Plotter.GRID_COLOR, labelcolor=Plotter.TEXT_COLOR, fontsize=8)
        
        # Vincola l'asse Y a valori reali per evitare distorsioni di scala
        ax.set_ylim(-0.1, max(max(sizes) + 0.5, 2.5))
        
        plt.tight_layout()
        
        plt.savefig(os.path.join(Plotter.OUTPUT_DIR, "02_dinamica_fila.png"), 
                    dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
        plt.close(fig)


    @staticmethod
    def plot_operational(metrics):
        """Gráfico 3: Ativos Operacionais e Monitoramento de Disponibilidade"""
        Plotter._prepare_output_directory()
        fig, ax = plt.subplots(figsize=(10, 4.5), facecolor=Plotter.BG_COLOR)
        operational = metrics.operational_assets
        
        timeline = metrics.timeline_plotter if metrics.timeline_plotter else np.arange(len(operational))
        timeline = timeline[:len(operational)]

        ax.axhline(6, color="#10b981", linestyle='--', linewidth=1.2, label="Capacidade Máxima da Malha (6 Ativos)")
        ax.plot(timeline, operational, color="#3b82f6", linewidth=1.8, label="Ativos Disponíveis")
        ax.fill_between(timeline, operational, 6, color="#ef4444", alpha=0.1, label="Impacto de Indisponibilidade")

        Plotter._apply_style(ax, "Monitoramento de Confiabilidade da Rede Offshore (Fase Estacionária)", 
                            "Tempo de Simulação (Horas)", "Ativos Operacionais")
        ax.legend(facecolor=Plotter.CARD_COLOR, edgecolor=Plotter.GRID_COLOR, labelcolor=Plotter.TEXT_COLOR, loc="lower left", fontsize=8)
        plt.tight_layout()
        
        plt.savefig(os.path.join(Plotter.OUTPUT_DIR, "03_confiabilidade_ativos.png"), 
                    dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
        plt.close(fig)

    @staticmethod
    def plot_histogram_response(metrics):
        """Gráfico 4: Distribuição Estocástica dos Tempos de Atendimento (Normalizado)"""
        Plotter._prepare_output_directory()
        fig, ax = plt.subplots(figsize=(10, 4.5), facecolor=Plotter.BG_COLOR)
        times = metrics.response_times

        # Ativação do parâmetro density=True para normalização rigorosa do histograma
        counts, bins, patches = ax.hist(times, bins=15, density=True, color=Plotter.LINE_PRIMARY, alpha=0.7, 
                                        edgecolor=Plotter.BG_COLOR, rwidth=0.85, label="Densidade Empírica")
        
        if len(times) > 1:
            try:
                import scipy.stats as stats
                kde = stats.gaussian_kde(times)
                x_axis = np.linspace(min(times), max(times), 100)
                
                # Plotagem da curva contínua perfeitamente sobreposta à escala probabilística
                ax.plot(x_axis, kde(x_axis), color=Plotter.LINE_SECONDARY, 
                        linewidth=2.5, label="Curva de Densidade de Serviço (KDE)")
            except ImportError:
                pass  

        Plotter._apply_style(ax, "Análise de Densidade Estocástica do Tempo de Serviço", 
                            "Tempo Total no Sistema (W)", "Densidade de Probabilidade")
        ax.legend(facecolor=Plotter.CARD_COLOR, edgecolor=Plotter.GRID_COLOR, labelcolor=Plotter.TEXT_COLOR, fontsize=8)
        plt.tight_layout()
        
        plt.savefig(os.path.join(Plotter.OUTPUT_DIR, "04_distribuicao_estocastica.png"), 
                    dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
        plt.close(fig)
        print(f"\n[INFO] Todos os 4 gráficos executivos foram salvos em: {Plotter.OUTPUT_DIR}")
