# EcoCart AI System

An interactive AI-powered logistics simulation 

🚀 **Live Demo:** [Launch on Streamlit](https://esvanth-ecocart-ai.streamlit.app)

---

## What is EcoCart?

EcoCart is a mid-sized e-commerce company facing challenges in optimising its logistics network. This project proposes an AI-based solution across five tasks — from intelligent delivery agents to demand forecasting.

---

## Tasks Covered

### Task 1 — AI Agents
Demonstrates three types of AI agents navigating a delivery map in real time:
- **Reactive Agent** — goes to the nearest stop, no planning
- **Goal-Based Agent** — plans the full route before departing (2-opt optimised)
- **Utility-Based Agent** — balances urgency vs distance to prioritise high-value stops

### Task 2 — Bias Detection & Mitigation
Uses K-Means clustering to segment customers into value tiers. Detects urban/rural bias using **Disparate Impact (DI)** analysis and applies a three-step mitigation strategy:
- Oversample rural customers to balance the dataset
- Adjust spend for delivery cost premium (+€12)
- Adjust frequency for rural order batching (×1.5)

### Task 3 — Search Algorithms for Route Optimisation
Implements all four search algorithms on a 20-node urban/rural delivery network:
- **BFS** — Breadth-First Search
- **DFS** — Depth-First Search
- **A\*** — Best-first with Euclidean heuristic
- **IDA\*** — Iterative Deepening A*

Includes a live **exploration replay slider** — drag to watch the algorithm search node by node.

### Task 4 — A* vs IDA* Comparative Analysis
Benchmarks both algorithms on 10 origin-destination pairs (5 urban, 5 rural) over multiple timing runs. Compares nodes expanded, average time, and memory behaviour.

### Task 5 — Demand Forecasting
Trains two ML models on 730 days of synthetic sales data:
- **Linear Regression** — fast and interpretable
- **Random Forest** — captures non-linear seasonal patterns

Features a **what-if predictor** — enter any day, month, and promotion flag to get an instant sales prediction.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11 | Core language |
| Streamlit | Interactive web app |
| Plotly | Interactive charts |
| scikit-learn | K-Means, LR, Random Forest |
| NumPy / Pandas | Data processing |

---

## Run Locally

```bash
git clone https://github.com/Esvanth/Ecocart-AI.git
cd Ecocart-AI
pip install -r requirements.txt
streamlit run app.py
```

---

## Project Structure

```
Ecocart-AI/
├── app.py                   # Main Streamlit app (all 5 tasks)
├── task2_segmentation.py    # Standalone Task 2 script
├── task3_4_routing.py       # Standalone Tasks 3 & 4 script
├── task5_forecasting.py     # Standalone Task 5 script
├── requirements.txt         # Python dependencies
└── README.md
```

---

## Author

**Esvanth Mohankumar**  
Student ID: 24311073  
Programme: MSc Artificial Intelligence  
Institution: National College of Ireland  
Module: Foundations  of AI 
