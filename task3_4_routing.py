"""
EcoCart Route Optimisation Prototype
Tasks 3 & 4 — BFS, DFS, A*, IDA* on a weighted delivery network
              + Green Routing mode (CO2-weighted edges for sustainability)

NCI MSCAI | Fundamentals of AI TABA 2026

Run:  python3 task3_4_routing.py
Out:  network_map.png, algo_comparison.png, green_vs_fast.png
"""

import heapq, math, time, tracemalloc, statistics
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

# ── 1. Network ──────────────────────────────────────────────
NODES = {
    # Urban cluster (dense, short edges)
    "U1":(1.0,1.0,"urban"),"U2":(2.0,1.5,"urban"),"U3":(3.0,1.0,"urban"),
    "U4":(1.5,2.5,"urban"),"U5":(2.5,3.0,"urban"),"U6":(3.5,2.0,"urban"),
    "U7":(1.0,3.5,"urban"),"U8":(2.0,4.0,"urban"),"U9":(3.0,4.0,"urban"),
    "U10":(4.0,3.5,"urban"),
    # Rural cluster (sparse, long edges)
    "R1":(6.0,1.0,"rural"),"R2":(8.0,2.0,"rural"),"R3":(10.0,1.5,"rural"),
    "R4":(7.0,4.0,"rural"),"R5":(9.0,4.5,"rural"),"R6":(11.0,3.5,"rural"),
    "R7":(6.5,6.0,"rural"),"R8":(9.0,7.0,"rural"),"R9":(11.0,6.0,"rural"),
    "R10":(8.0,5.5,"rural"),
}

def _dist(a, b):
    return math.hypot(NODES[a][0]-NODES[b][0], NODES[a][1]-NODES[b][1])

_PAIRS = [
    ("U1","U2"),("U2","U3"),("U1","U4"),("U2","U4"),("U2","U5"),
    ("U3","U6"),("U4","U5"),("U5","U6"),("U4","U7"),("U5","U8"),
    ("U6","U10"),("U7","U8"),("U8","U9"),("U9","U10"),("U5","U9"),
    ("R1","R2"),("R2","R3"),("R1","R4"),("R2","R4"),("R3","R6"),
    ("R4","R5"),("R5","R6"),("R4","R7"),("R5","R10"),("R7","R10"),
    ("R7","R8"),("R8","R9"),("R6","R9"),("R8","R10"),("R5","R8"),
    ("U3","R1"),("U10","R4"),("U6","R1"),("U9","R7"),
]

# Road distance ≈ 1.15× straight-line
EDGES = [(a, b, round(_dist(a,b)*1.15, 2)) for a, b in _PAIRS]

# CO2 cost per edge: urban roads have traffic → higher emissions per km
# Rural roads: 0.12 kg CO2/km;  Urban roads: 0.21 kg CO2/km
def _co2(a, b, km):
    za, zb = NODES[a][2], NODES[b][2]
    rate = 0.28 if za == "urban" and zb == "urban" else 0.18 if za != zb else 0.10
    return round(km * rate, 3)

CO2_EDGES = [(a, b, _co2(a, b, w)) for a, b, w in EDGES]

ADJ_KM = {n: [] for n in NODES}
ADJ_CO2 = {n: [] for n in NODES}
for i, (a, b, w) in enumerate(EDGES):
    ADJ_KM[a].append((b, w))
    ADJ_KM[b].append((a, w))
    co2 = CO2_EDGES[i][2]
    ADJ_CO2[a].append((b, co2))
    ADJ_CO2[b].append((a, co2))

# ── 2. Algorithms ───────────────────────────────────────────
def heuristic(n, goal, scale=1.0):
    return _dist(n, goal) * scale

def bfs(start, goal, adj=ADJ_KM):
    expanded = 0
    q = deque([(start, [start])])
    seen = {start}
    while q:
        node, path = q.popleft()
        expanded += 1
        if node == goal:
            cost = sum(_edge_w(path[i], path[i+1], adj) for i in range(len(path)-1))
            return path, round(cost, 2), expanded
        for nb, _ in adj[node]:
            if nb not in seen:
                seen.add(nb)
                q.append((nb, path + [nb]))
    return None, math.inf, expanded

def dfs(start, goal, adj=ADJ_KM, depth_limit=50):
    expanded = 0
    stack = [(start, [start])]
    seen = {start}
    while stack:
        node, path = stack.pop()
        expanded += 1
        if node == goal:
            cost = sum(_edge_w(path[i], path[i+1], adj) for i in range(len(path)-1))
            return path, round(cost, 2), expanded
        if len(path) > depth_limit:
            continue
        for nb, _ in adj[node]:
            if nb not in seen:
                seen.add(nb)
                stack.append((nb, path + [nb]))
    return None, math.inf, expanded

def astar(start, goal, adj=ADJ_KM, h_scale=1.0):
    expanded, counter = 0, 0
    heap = [(heuristic(start, goal, h_scale), 0.0, counter, start, [start])]
    best = {start: 0.0}
    while heap:
        f, g, _, node, path = heapq.heappop(heap)
        if node == goal:
            return path, round(g, 2), expanded
        if g > best.get(node, math.inf):
            continue
        expanded += 1
        for nb, w in adj[node]:
            ng = g + w
            if ng < best.get(nb, math.inf):
                best[nb] = ng
                counter += 1
                heapq.heappush(heap, (ng + heuristic(nb, goal, h_scale), ng, counter, nb, path + [nb]))
    return None, math.inf, expanded

def ida_star(start, goal, adj=ADJ_KM, h_scale=1.0):
    expanded = [0]
    def _dfs(node, g, bound, path, visited):
        f = g + heuristic(node, goal, h_scale)
        if f > bound:
            return None, f
        expanded[0] += 1
        if node == goal:
            return list(path), g
        nxt = math.inf
        for nb, w in adj[node]:
            if nb in visited:
                continue
            visited.add(nb)
            path.append(nb)
            r, t = _dfs(nb, g + w, bound, path, visited)
            if r is not None:
                return r, t
            if t < nxt:
                nxt = t
            path.pop()
            visited.remove(nb)
        return None, nxt

    bound = heuristic(start, goal, h_scale)
    while True:
        r, t = _dfs(start, 0.0, bound, [start], {start})
        if r is not None:
            return r, round(t, 2), expanded[0]
        if t == math.inf:
            return None, math.inf, expanded[0]
        bound = t

def _edge_w(a, b, adj):
    for nb, w in adj[a]:
        if nb == b:
            return w
    return math.inf

# ── 3. Benchmark ────────────────────────────────────────────
def benchmark(algo, start, goal, adj=ADJ_KM, repeats=20):
    times, mems = [], []
    path = cost = expanded = None
    for _ in range(repeats):
        tracemalloc.start()
        t0 = time.perf_counter()
        path, cost, expanded = algo(start, goal, adj)
        t1 = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        times.append((t1 - t0) * 1000)
        mems.append(peak / 1024)
    return {
        "ms": round(statistics.mean(times), 3),
        "kb": round(statistics.mean(mems), 2),
        "expanded": expanded,
        "cost": cost,
        "path": path,
    }

OD_URBAN = [("U1","U10"),("U7","U6"),("U2","U9"),("U1","U9"),("U3","U8")]
OD_RURAL = [("R1","R9"),("R2","R8"),("R3","R10"),("R1","R6"),("R4","R9")]

# ── 4. Plots ────────────────────────────────────────────────
def plot_network():
    G = nx.Graph()
    for n, (x, y, _) in NODES.items():
        G.add_node(n, pos=(x, y))
    for a, b, w in EDGES:
        G.add_edge(a, b, weight=w)
    pos = {n: (NODES[n][0], NODES[n][1]) for n in NODES}
    colors = ["#ef4444" if NODES[n][2] == "urban" else "#10b981" for n in NODES]

    fig, ax = plt.subplots(figsize=(13, 6))
    ax.set_facecolor("#0d1117")
    fig.patch.set_facecolor("#0d1117")
    nx.draw(G, pos, ax=ax, with_labels=True, node_color=colors, node_size=500,
            font_size=8, font_weight="bold", font_color="white",
            edge_color="#334155", width=1.2)
    labels = {(a, b): f"{w}" for a, b, w in EDGES}
    nx.draw_networkx_edge_labels(G, pos, ax=ax, edge_labels=labels,
                                 font_size=6, font_color="#94a3b8")
    urban_patch = mpatches.Patch(color="#ef4444", label="Urban node")
    rural_patch = mpatches.Patch(color="#10b981", label="Rural node")
    ax.legend(handles=[urban_patch, rural_patch], loc="upper left",
              fontsize=9, facecolor="#0d1117", edgecolor="#334155", labelcolor="white")
    ax.set_title("EcoCart 20-node delivery network (edge labels = km)",
                 color="white", fontsize=12, pad=12)
    plt.tight_layout()
    plt.savefig("output/network_map.png", dpi=150, bbox_inches="tight",
                facecolor="#0d1117")
    plt.close()


def plot_comparison(results):
    metrics = [("Runtime (ms)", "ms"), ("Nodes expanded", "expanded"), ("Peak memory (KB)", "kb")]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    fig.patch.set_facecolor("#0d1117")
    for ax, (title, key) in zip(axes, metrics):
        ax.set_facecolor("#0d1117")
        u_a = statistics.mean(r["astar"][key] for r in results["urban"])
        u_i = statistics.mean(r["ida"][key]   for r in results["urban"])
        r_a = statistics.mean(r["astar"][key] for r in results["rural"])
        r_i = statistics.mean(r["ida"][key]   for r in results["rural"])
        x = [0, 1]
        w = 0.32
        ax.bar([xi - w/2 for xi in x], [u_a, r_a], w, label="A*",   color="#3b82f6")
        ax.bar([xi + w/2 for xi in x], [u_i, r_i], w, label="IDA*", color="#8b5cf6")
        ax.set_xticks(x)
        ax.set_xticklabels(["Urban", "Rural"], color="white")
        ax.set_title(title, color="white", fontsize=11)
        ax.tick_params(colors="white")
        ax.grid(True, axis="y", alpha=0.15, color="white")
        ax.legend(fontsize=9, facecolor="#0d1117", edgecolor="#334155", labelcolor="white")
    plt.suptitle("A* vs IDA* (mean over 5 O-D pairs × 20 runs)",
                 color="white", fontsize=12)
    plt.tight_layout()
    plt.savefig("output/algo_comparison.png", dpi=150,
                bbox_inches="tight", facecolor="#0d1117")
    plt.close()


def plot_green_vs_fast():
    """Compare fastest route (A* on km) vs greenest route (A* on CO2)."""
    pairs = [("U1", "R9"), ("U7", "R6"), ("R1", "U10")]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor("#0d1117")

    G = nx.Graph()
    for n, (x, y, _) in NODES.items():
        G.add_node(n, pos=(x, y))
    for a, b, w in EDGES:
        G.add_edge(a, b)
    pos = {n: (NODES[n][0], NODES[n][1]) for n in NODES}

    for ax, (s, g) in zip(axes, pairs):
        ax.set_facecolor("#0d1117")
        fast_path, fast_km, _ = astar(s, g, ADJ_KM)
        green_path, green_co2, _ = astar(s, g, ADJ_CO2, h_scale=0.10)

        # Compute cross-metrics
        fast_co2 = sum(_edge_w(fast_path[i], fast_path[i+1], ADJ_CO2) for i in range(len(fast_path)-1))
        green_km = sum(_edge_w(green_path[i], green_path[i+1], ADJ_KM) for i in range(len(green_path)-1))

        colors = ["#ef4444" if NODES[n][2] == "urban" else "#10b981" for n in NODES]
        nx.draw(G, pos, ax=ax, with_labels=True, node_color=colors,
                node_size=300, font_size=7, font_weight="bold",
                font_color="white", edge_color="#1e293b", width=0.8)

        fast_edges = [(fast_path[i], fast_path[i+1]) for i in range(len(fast_path)-1)]
        green_edges = [(green_path[i], green_path[i+1]) for i in range(len(green_path)-1)]
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=fast_edges,
                               edge_color="#f59e0b", width=3, alpha=0.8)
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=green_edges,
                               edge_color="#22c55e", width=3, style="dashed", alpha=0.8)
        ax.set_title(f"{s} → {g}\nFast: {fast_km:.1f}km / {fast_co2:.2f}kg CO₂\n"
                     f"Green: {green_km:.1f}km / {green_co2:.2f}kg CO₂",
                     color="white", fontsize=9, linespacing=1.4)
    fast_patch = mpatches.Patch(color="#f59e0b", label="Fastest (min km)")
    green_patch = mpatches.Patch(color="#22c55e", label="Greenest (min CO₂)")
    fig.legend(handles=[fast_patch, green_patch], loc="lower center",
               ncol=2, fontsize=10, facecolor="#0d1117", edgecolor="#334155",
               labelcolor="white")
    plt.suptitle("Fast Route vs Green Route — same A*, different cost function",
                 color="white", fontsize=12)
    plt.tight_layout(rect=[0, 0.06, 1, 0.95])
    plt.savefig("output/green_vs_fast.png", dpi=150,
                bbox_inches="tight", facecolor="#0d1117")
    plt.close()


# ── 5. Main ─────────────────────────────────────────────────
def main():
    print("="*70)
    print("EcoCart Route Optimisation — A* vs IDA* benchmark")
    print("="*70)

    # Smoke test all four
    for name, fn in [("BFS", bfs), ("DFS", dfs), ("A*", astar), ("IDA*", ida_star)]:
        path, cost, exp = fn("U1", "U10")
        print(f"  {name:5s} U1->U10  cost={cost:.2f} km  expanded={exp}")

    # Full benchmark A* vs IDA*
    results = {"urban": [], "rural": []}
    for label, pairs in [("urban", OD_URBAN), ("rural", OD_RURAL)]:
        print(f"\n--- {label.upper()} benchmark ---")
        for s, g in pairs:
            a = benchmark(astar, s, g)
            i = benchmark(ida_star, s, g)
            results[label].append({"pair": (s, g), "astar": a, "ida": i})
            print(f"  {s}->{g}:  A* {a['cost']:.2f}km/{a['expanded']}exp/{a['ms']:.3f}ms  "
                  f"IDA* {i['cost']:.2f}km/{i['expanded']}exp/{i['ms']:.3f}ms")
            assert abs(a["cost"] - i["cost"]) < 1e-4, "Optimality mismatch"

    # Green routing demo
    print("\n--- GREEN ROUTING ---")
    for s, g in [("U1","R9"), ("U7","R6")]:
        fp, fk, _ = astar(s, g, ADJ_KM)
        gp, gc, _ = astar(s, g, ADJ_CO2, h_scale=0.10)
        fco2 = sum(_edge_w(fp[i], fp[i+1], ADJ_CO2) for i in range(len(fp)-1))
        gkm  = sum(_edge_w(gp[i], gp[i+1], ADJ_KM) for i in range(len(gp)-1))
        print(f"  {s}->{g}  Fast: {fk:.1f}km/{fco2:.2f}kgCO2  Green: {gkm:.1f}km/{gc:.2f}kgCO2")

    # Generate plots
    plot_network()
    plot_comparison(results)
    plot_green_vs_fast()
    print("\nWrote: network_map.png, algo_comparison.png, green_vs_fast.png")

if __name__ == "__main__":
    main()
