# 🚢 Offshore Maintenance Simulator (Atlas Operation)

A predictive **Digital Twin** for the simulation and logistics optimization of offshore platform maintenance.

This project models the reliability of oil installations and the allocation of specialized maintenance teams using **Discrete Event Simulation (DES)** techniques, with the goal of reducing bottlenecks and mitigating financial losses due to deferred production.

---

## ✨ Key Features
- **Stochastic Simulation Engine:** Developed in `SimPy`, it simulates randomized failures, repair times (stochastic distributions), and dispatch logic (graph theory with `NetworkX`).
- **Statistical Validation (Monte Carlo):** Includes multiple runs to verify the robustness of the results, as well as theoretical validation using *Little's Law*.
- **Advanced Reporting:** Automatic generation of analytical charts (`matplotlib`) and an Executive PDF Report (via `reportlab`).
- **Web Dashboard (UI):** A modern Web App built with **Flask** and Vanilla HTML/CSS/JS. It allows you to run the simulation and analyze the results visually (featuring dark mode and glassmorphism) in real-time without reloading the page.

---

## 🚀 Requirements

Ensure you have Python 3.9 or higher installed on your system.

### Installing Dependencies

Install the required packages using the generated `requirements.txt` file:

```bash
pip install -r requirements.txt
```

Main dependencies include:
- `simpy`
- `matplotlib`
- `numpy`, `scipy`
- `reportlab`
- `networkx`
- `flask`, `flask-cors`

---

## 🖥️ How to Run the Application (Web UI)

1. Open a terminal in the project directory.
2. Start the Flask server by running `app.py`:

```bash
python3 app.py
```

3. Open your favorite web browser and visit the dashboard at:
   👉 **http://localhost:5001**

*(Note: The default port was changed from 5000 to 5001 to avoid conflicts with the macOS AirPlay Receiver).*

4. Click on **Run Simulation** from the graphical interface to execute the calculation in real-time and view the generated reports!

---

## 📂 Project Structure

- `app.py`: Web server (Flask) and backend API.
- `main.py`: Original entry point (now contains `run_simulation()` imported by Flask).
- `models/`: Base classes for Entities (`Asset`, `Team`).
- `simulation/`: The core of the SimPy engine (`SimulationEngine`, `QueueSystem`, `Dispatcher`, `FailureProcess`).
- `graph/`: Routing logic on geographical maps (`OffshoreGraph`).
- `metrics/`: Data collection (`MetricsCollector`), plotting (`Plotter`), and PDF generation (`PDFGenerator`).
- `templates/` & `static/`: Web App frontend (HTML, CSS, and JS).
- `relatorio_graficos/`: Output folder where automatically generated images (.png) and PDFs are saved.
