# EcoCart AI System

An interactive AI-powered logistics simulation 

 **Live Demo:** [Launch on Streamlit](https://ecocart-ai-app-live.streamlit.app)

---

## What is EcoCart?

EcoCart is a mid-sized e-commerce company facing challenges in optimising its logistics network. This project proposes an AI-based solution across six tasks — from intelligent delivery agents to demand forecasting and business ROI analysis.

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

### Task 6 — Business Case *(Voluntary — AI Student)*
Quantifies the financial and environmental impact of the AI system with fully interactive sliders:
- **ROI calculator** — adjusts fleet size, fuel cost, wage rates and shows live annual savings
- **3-year ROI projection** — cumulative benefit vs cost with breakeven line
- **CO₂ impact** — tonnes saved per year, tree and car equivalents
- **Implementation roadmap** — 5-phase Gantt chart across 8 months

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
pip install -r requirements.txt
streamlit run app.py
```

---

## Project Structure

```
FAI SIMULATION/
├── app.py                   # Main Streamlit app (all 6 tasks)
├── task2_segmentation.py    # Standalone Task 2 script
├── task3_4_routing.py       # Standalone Tasks 3 & 4 script
├── task5_forecasting.py     # Standalone Task 5 script
├── data/                    # Synthetic datasets (loaded by every task)
│   ├── customers.csv        # Task 2 — 400 customer records
│   ├── sales_history.csv    # Task 5 — 730 days of daily sales
│   ├── network_nodes.csv    # Tasks 3/4 — 20-node delivery network
│   ├── network_edges.csv    # Tasks 3/4 — edge weights + CO₂ cost
│   └── export_data.py       # Regenerates the CSVs from a fixed seed
├── requirements.txt         # Python dependencies
└── README.md
```

---

## Dataset

All data is **synthetic and reproducible**. The CSVs in `data/` are the
program's data source — every task script (`task2_segmentation.py`,
`task3_4_routing.py`, `task5_forecasting.py`) loads its inputs directly
from these files at runtime:

| File | Rows | Description |
|------|------|-------------|
| `customers.csv` | 400 | 300 urban + 100 rural customers (deliberately biased) |
| `sales_history.csv` | 730 | Daily sales with weekly + yearly seasonality + promos |
| `network_nodes.csv` | 20 | Delivery hubs (x, y, urban/rural) |
| `network_edges.csv` | 34 | Roads with distance (km) and CO₂ cost (kg) |

The CSVs themselves are generated from an inline source-of-truth with a
fixed random seed (`np.random.default_rng(42)`). To rebuild them:
`python data/export_data.py`

---

## Author

Esvanth Mohankumar
Student ID: 24311073  
Programme: MSc Artificial Intelligence  
College: National College of Ireland  
Module: Foundations of AI 
