"""
Export the synthetic datasets used by all tasks to CSV.
Run from project root:  python data/export_data.py

Writes:
  data/customers.csv       - Task 2  (400 customers, biased urban/rural mix)
  data/sales_history.csv   - Task 5  (730 days of synthetic daily sales)
  data/network_nodes.csv   - Tasks 3/4  (20-node delivery network)
  data/network_edges.csv   - Tasks 3/4  (weighted edges + CO2 cost)

All generators use a fixed seed (42), so re-running this produces identical files.
"""

import os, sys
import pandas as pd

# Allow `python data/export_data.py` from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from task2_segmentation import generate_biased_data
from task5_forecasting import generate_sales
from task3_4_routing import _build_inline_network

OUT = os.path.dirname(os.path.abspath(__file__))


def export_customers():
    df = generate_biased_data()
    path = os.path.join(OUT, "customers.csv")
    df.to_csv(path, index=False)
    print(f"  customers.csv      ({len(df)} rows)")


def export_sales():
    df = generate_sales()
    path = os.path.join(OUT, "sales_history.csv")
    df.to_csv(path, index=False)
    print(f"  sales_history.csv  ({len(df)} rows)")


def export_network():
    nodes_dict, edges_list, co2_list = _build_inline_network()
    nodes = pd.DataFrame(
        [(n, x, y, region) for n, (x, y, region) in nodes_dict.items()],
        columns=["node", "x", "y", "region"],
    )
    nodes.to_csv(os.path.join(OUT, "network_nodes.csv"), index=False)
    print(f"  network_nodes.csv  ({len(nodes)} rows)")

    edges = pd.DataFrame(
        [(a, b, km, co2) for (a, b, km), (_, _, co2) in zip(edges_list, co2_list)],
        columns=["from", "to", "distance_km", "co2_kg"],
    )
    edges.to_csv(os.path.join(OUT, "network_edges.csv"), index=False)
    print(f"  network_edges.csv  ({len(edges)} rows)")


if __name__ == "__main__":
    print("Exporting synthetic datasets to data/:")
    export_customers()
    export_sales()
    export_network()
    print("Done.")
