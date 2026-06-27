document.addEventListener('DOMContentLoaded', () => {
    const runBtn = document.getElementById('run-btn');
    const btnText = runBtn.querySelector('.btn-text');
    const spinner = runBtn.querySelector('.spinner');
    const dashboard = document.getElementById('results-dashboard');
    
    // KPI Elements
    const kpiW = document.getElementById('kpi-w');
    const kpiLq = document.getElementById('kpi-lq');
    const kpiRho = document.getElementById('kpi-rho');
    const kpiError = document.getElementById('kpi-error');
    const kpiMc = document.getElementById('kpi-mc');

    // Image Elements
    const img01 = document.getElementById('img-01');
    const img02 = document.getElementById('img-02');
    const img03 = document.getElementById('img-03');
    const img04 = document.getElementById('img-04');
    
    // PDF Link
    const pdfLink = document.getElementById('pdf-link');

    runBtn.addEventListener('click', async () => {
        // Set loading state
        runBtn.disabled = true;
        btnText.textContent = 'Running Simulation...';
        spinner.classList.remove('hidden');
        dashboard.classList.add('hidden');
        
        try {
            const response = await fetch('/api/simulate', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                const stats = result.data.statistics;
                const mcStats = result.data.monte_carlo_avg_response;
                
                // Update KPIs
                kpiW.textContent = stats.avg_response.toFixed(2);
                kpiLq.textContent = stats.avg_queue.toFixed(2);
                kpiRho.textContent = (stats.rho_sim * 100).toFixed(2) + '%';
                kpiError.textContent = stats.little_error_pct.toFixed(2) + '%';
                kpiMc.textContent = mcStats.toFixed(2);
                
                // Add timestamp to bypass browser cache
                const ts = new Date().getTime();
                
                // Update Images
                img01.src = `/api/images/01_tempo_resposta_W.png?t=${ts}`;
                img02.src = `/api/images/02_dinamica_fila.png?t=${ts}`;
                img03.src = `/api/images/03_confiabilidade_ativos.png?t=${ts}`;
                img04.src = `/api/images/04_distribuicao_estocastica.png?t=${ts}`;
                
                // Update PDF link
                pdfLink.href = `/api/images/Relatorio_Executivo_Atlas.pdf?t=${ts}`;
                
                // Show dashboard with a small delay for smooth transition
                setTimeout(() => {
                    dashboard.classList.remove('hidden');
                    // Scroll to dashboard smoothly
                    dashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 300);
            } else {
                alert('Simulation failed: ' + result.message);
                console.error(result.trace);
            }
        } catch (err) {
            alert('Network error while running simulation.');
            console.error(err);
        } finally {
            // Reset button state
            runBtn.disabled = false;
            btnText.textContent = 'Run Simulation';
            spinner.classList.add('hidden');
        }
    });
});
