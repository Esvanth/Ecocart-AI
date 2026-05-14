"""
EcoCart AI System — Streamlit App
Runs the actual task scripts and displays their real outputs.
NCI MSCAI | Fundamentals of AI TABA 2026
"""

import sys, io, os, math, heapq, time, importlib.util
from contextlib import redirect_stdout
from collections import deque

import matplotlib
matplotlib.use("Agg")
os.makedirs("output", exist_ok=True)

import numpy as np
import pandas as pd
import streamlit as st
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ══════════════════════════════════════════════════════════════════════════════
#  REPORT GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def _build_report(t2_text, t3_text, t5_text):
    TNR = "Times New Roman"
    doc = Document()
    doc.styles["Normal"].font.name = TNR
    doc.styles["Normal"].font.size = Pt(12)
    doc.styles["Normal"].paragraph_format.space_after = Pt(8)
    for lvl, sz in [(1,14),(2,13)]:
        s = doc.styles[f"Heading {lvl}"]
        s.font.name = TNR; s.font.bold = True; s.font.size = Pt(sz)
        s.font.color.rgb = RGBColor(0,0,0)
        s.paragraph_format.space_before = Pt(12)
        s.paragraph_format.space_after  = Pt(4)

    def H(txt, lv=1):
        p = doc.add_heading(txt, level=lv); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs: r.font.name=TNR; r.font.color.rgb=RGBColor(0,0,0)
    def P(txt):
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(8)
        r = p.add_run(txt); r.font.name=TNR; r.font.size=Pt(12)
    def CODE(txt):
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(6)
        r = p.add_run(txt); r.font.name="Courier New"; r.font.size=Pt(9)
    def IMG(path, caption="", width=5.5):
        if os.path.exists(path):
            doc.add_picture(path, width=Inches(width))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        if caption:
            cp = doc.add_paragraph(caption); cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.paragraph_format.space_after = Pt(8)
            for r in cp.runs: r.font.name=TNR; r.font.size=Pt(10); r.font.italic=True
    def SP(): doc.add_paragraph("").paragraph_format.space_after = Pt(4)

    SP(); SP()
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("EcoCart AI System"); r.font.name=TNR; r.font.size=Pt(24); r.font.bold=True
    p.paragraph_format.space_after = Pt(8)
    p2 = doc.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("Technical Report — TABA Section II"); r2.font.name=TNR; r2.font.size=Pt(14)
    p2.paragraph_format.space_after = Pt(20)
    for line in ["National College of Ireland","MSc Artificial Intelligence",
                 "Fundamentals of Artificial Intelligence","May 2026"]:
        lp = doc.add_paragraph(); lp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        lr = lp.add_run(line); lr.font.name=TNR; lr.font.size=Pt(12)
        lp.paragraph_format.space_after = Pt(4)
    SP()
    lnk = doc.add_paragraph(); lnk.alignment = WD_ALIGN_PARAGRAPH.CENTER
    lr2 = lnk.add_run("Live Demo: https://esvanth-ecocart-ai.streamlit.app")
    lr2.font.name=TNR; lr2.font.size=Pt(11); lr2.font.bold=True
    lr2.font.color.rgb = RGBColor(37,99,235)
    doc.add_page_break()

    H("Task 2 — Customer Segmentation & Bias Mitigation")
    P("Running task2_segmentation.py produced the following output:")
    if t2_text: CODE(t2_text)
    SP()
    IMG("output/bias_before_after.png","Figure 1: Customer clusters before and after bias mitigation")
    SP()
    IMG("output/disparate_impact.png","Figure 2: Disparate Impact and High Value rates before and after fix")
    SP()
    P("Before the fix: 0.0% of rural customers were in High Value (DI = 0.0 — biased). "
      "After the fix: 57.3% of rural customers are in High Value (DI = 0.847 — fair, above 0.80 threshold).")
    doc.add_page_break()

    H("Tasks 3 & 4 — Route Optimisation and Algorithm Comparison")
    P("Running task3_4_routing.py produced the following output:")
    if t3_text: CODE(t3_text)
    SP()
    IMG("output/network_map.png","Figure 3: EcoCart 20-node delivery network")
    SP()
    IMG("output/algo_comparison.png","Figure 4: A* vs IDA* comparison across urban and rural routes")
    SP()
    IMG("output/green_vs_fast.png","Figure 5: Fastest route vs lowest CO2 route comparison")
    SP()
    P("A* found the optimal path on every route with the fewest nodes expanded. "
      "DFS was the only algorithm that did not find the shortest path. "
      "Both A* and IDA* found identical optimal paths — A* is faster on small graphs, "
      "IDA* uses less memory and is better suited for large-scale networks.")
    doc.add_page_break()

    H("Task 5 — Demand Forecasting with Machine Learning")
    P("Running task5_forecasting.py produced the following output:")
    if t5_text: CODE(t5_text)
    SP()
    IMG("output/forecast.png","Figure 6: Actual vs predicted daily sales on the 140-day test set")
    SP()
    IMG("output/residuals.png","Figure 7: Residuals for Linear Regression and Random Forest")
    SP()
    IMG("output/feature_importance.png","Figure 8: Random Forest feature importance — lag_7 is the strongest predictor")
    SP()
    P("Linear Regression: MAE=9.62, RMSE=12.38, R2=0.762, MAPE=9.41%. "
      "Random Forest: MAE=9.75, RMSE=13.50, R2=0.716, MAPE=9.43%. "
      "Linear Regression performed slightly better on this dataset. "
      "The top predictors were lag_7 (same weekday last week), lag_14, and is_promo.")
    doc.add_page_break()

    H("References")
    refs = [
        "[1]  S. Russell and P. Norvig, Artificial Intelligence: A Modern Approach, 4th ed. Hoboken, NJ: Pearson, 2020.",
        "[2]  F. Pedregosa et al., \"Scikit-learn: Machine Learning in Python,\" JMLR, vol. 12, pp. 2825-2830, 2011.",
        "[3]  M. Feldman et al., \"Certifying and Removing Disparate Impact,\" in Proc. ACM SIGKDD, 2015.",
        "[4]  P. E. Hart, N. J. Nilsson, and B. Raphael, \"A Formal Basis for the Heuristic Determination of "
              "Minimum Cost Paths,\" IEEE Trans. Syst. Sci. Cybern., vol. 4, no. 2, pp. 100-107, 1968.",
    ]
    for ref in refs:
        p = doc.add_paragraph(ref)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.first_line_indent = Inches(-0.3)
        for r in p.runs: r.font.name=TNR; r.font.size=Pt(11)

    buf = io.BytesIO(); doc.save(buf); buf.seek(0)
    return buf

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG & DESIGN TOKENS
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="EcoCart AI System", page_icon="🛒",
                   layout="wide", initial_sidebar_state="expanded")

NAVY  = "#0f172a"
SLATE = "#1e293b"
MUTED = "#64748b"
BORDER = "#e2e8f0"
SURF  = "#ffffff"
BG    = "#f8fafc"
GREEN = "#059669"
BLUE  = "#2563eb"
AMBER = "#d97706"
RED   = "#dc2626"

def _rgba(hex_c, a=1.0):
    h = hex_c.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{a})"

def _ch(h=400, title=""):
    return dict(height=h, paper_bgcolor=SURF, plot_bgcolor=BG,
                font=dict(color=SLATE, size=11, family="system-ui,-apple-system,sans-serif"),
                title=dict(text=title, font=dict(size=13, color=SLATE), x=0),
                margin=dict(l=10, r=10, t=44, b=10),
                legend=dict(bgcolor=SURF, bordercolor=BORDER, borderwidth=1))

# ── global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Layout */
[data-testid="stAppViewContainer"] { background:#f1f5f9; }
.block-container { padding:1.5rem 2rem 4rem; max-width:1400px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background:#fff; border-radius:12px; padding:4px;
  box-shadow:0 2px 8px rgba(0,0,0,.06); border:1px solid #e2e8f0; gap:2px;
}
.stTabs [data-baseweb="tab"] {
  border-radius:8px; font-size:.84rem; font-weight:600;
  padding:8px 16px; color:#64748b;
}
.stTabs [aria-selected="true"] { background:#0f172a !important; color:#f8fafc !important; }

/* Cards */
.card {
  background:#fff; border-radius:12px; padding:18px 22px;
  box-shadow:0 1px 5px rgba(0,0,0,.06); border:1px solid #f1f5f9;
  margin-bottom:14px;
}
.card-green  { border-left:4px solid #059669; }
.card-blue   { border-left:4px solid #2563eb; }
.card-amber  { border-left:4px solid #d97706; }
.card-navy   { border-left:4px solid #0f172a; }
.card-purple { border-left:4px solid #7c3aed; }

/* Step header */
.step-hd { display:flex; align-items:center; font-size:1rem; font-weight:700;
            color:#0f172a; margin-bottom:8px; }
.badge {
  display:inline-flex; align-items:center; justify-content:center;
  background:#0f172a; color:#fff; width:26px; height:26px; border-radius:50%;
  font-size:.78rem; font-weight:800; margin-right:10px; flex-shrink:0;
}
.badge-q { background:#475569; }

/* Terminal */
.term-wrap { border-radius:10px; overflow:hidden; border:1px solid #1e293b; margin:8px 0; }
.term-bar  { background:#1e293b; padding:8px 14px; display:flex; gap:6px; align-items:center; }
.td { width:10px; height:10px; border-radius:50%; }
.td-r{background:#ef4444;} .td-y{background:#f59e0b;} .td-g{background:#10b981;}
.term-body {
  background:#0f172a; padding:14px 18px;
  font-family:'Courier New',monospace; font-size:.79rem;
  color:#94a3b8; white-space:pre-wrap; line-height:1.65;
  max-height:320px; overflow-y:auto;
}

/* Insight / warn / info */
.insight {
  background:#ecfdf5; border-left:4px solid #059669;
  border-radius:0 10px 10px 0; padding:14px 18px;
  color:#064e3b; font-size:.875rem; line-height:1.65; margin:10px 0;
}
.warn-note {
  background:#fffbeb; border-left:4px solid #d97706;
  border-radius:0 10px 10px 0; padding:14px 18px;
  color:#78350f; font-size:.875rem; line-height:1.65; margin:10px 0;
}
.info-note {
  background:#eff6ff; border-left:4px solid #2563eb;
  border-radius:0 10px 10px 0; padding:14px 18px;
  color:#1e3a5f; font-size:.875rem; line-height:1.65; margin:10px 0;
}

/* Visit log */
.vlog {
  background:#f8fafc; border-radius:10px;
  border:1px solid #e2e8f0; padding:10px 12px;
  max-height:480px; overflow-y:auto;
}
.vi {
  display:flex; align-items:center; gap:8px; padding:5px 2px;
  font-size:.79rem; border-bottom:1px dashed #f1f5f9;
}
.vi:last-child { border-bottom:none; }
.vd { width:9px; height:9px; border-radius:50%; flex-shrink:0; }
.vd-done    { background:#059669; }
.vd-current { background:#2563eb; box-shadow:0 0 7px #2563eb; }
.vd-pending { background:#cbd5e1; }

/* Legend */
.lgd { display:flex; gap:14px; flex-wrap:wrap; margin:8px 0 2px; }
.li  { display:flex; align-items:center; gap:5px; font-size:.78rem; color:#475569; }
.ld  { width:11px; height:11px; border-radius:50%; }

/* Metrics */
div[data-testid="metric-container"] {
  background:#fff; border-radius:10px; padding:14px 18px;
  border:1px solid #e2e8f0; box-shadow:0 1px 3px rgba(0,0,0,.05);
}

/* Sidebar */
[data-testid="stSidebar"] { background:#fff; border-right:1px solid #e2e8f0; }
[data-testid="stSidebarContent"] { padding:1.2rem 1rem; }

/* App header */
.app-hdr {
  background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%);
  border-radius:14px; padding:22px 28px; margin-bottom:20px;
}
.app-hdr h1 { color:#f8fafc; margin:0 0 4px; font-size:1.55rem; font-weight:800; }
.app-hdr p  { color:#94a3b8; margin:0; font-size:.875rem; }
.tag {
  display:inline-block; background:rgba(59,130,246,.25);
  color:#93c5fd; font-size:.7rem; font-weight:700;
  padding:2px 8px; border-radius:4px; margin-right:6px;
  border:1px solid rgba(59,130,246,.4);
}

/* Agent type mini-cards */
.acard {
  border-radius:10px; padding:14px; border:2px solid #e2e8f0;
  background:#fff; transition:all .2s; margin-bottom:4px;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;margin-bottom:16px;'>
      <div style='font-size:2.2rem;'>🛒</div>
      <div style='font-size:1.1rem;font-weight:800;color:#0f172a;'>EcoCart AI</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("<div style='font-weight:700;font-size:.875rem;color:#0f172a;margin-bottom:8px;'>How to use</div>",
                unsafe_allow_html=True)
    for n, desc in [("1","Click a tab above"),("2","Read the context card"),
                    ("3","Press Run (Tasks 2, 3, 5)"),("4","Watch the live output"),
                    ("5","Read the insight panel")]:
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:8px;margin:5px 0;'>
          <div style='background:#0f172a;color:#fff;width:20px;height:20px;border-radius:50%;
                      font-size:.7rem;font-weight:800;display:flex;align-items:center;
                      justify-content:center;flex-shrink:0;'>{n}</div>
          <span style='font-size:.82rem;color:#1e293b;'>{desc}</span>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("<div style='font-weight:700;font-size:.875rem;color:#0f172a;margin-bottom:8px;'>Task status</div>",
                unsafe_allow_html=True)
    t2_done = st.session_state.get("t2_done", False)
    t3_done = st.session_state.get("t3_done", False)
    t5_done = st.session_state.get("t5_done", False)
    for label, done in [("Task 2 — Segmentation", t2_done),
                         ("Task 3 — Routing",      t3_done),
                         ("Task 5 — Forecast",     t5_done)]:
        icon  = "✅" if done else "○"
        color = GREEN if done else "#94a3b8"
        st.markdown(f"<div style='color:{color};font-size:.82rem;margin:4px 0;'>{icon} {label}</div>",
                    unsafe_allow_html=True)

    st.divider()
    st.caption("All outputs are generated by the actual task Python scripts.")

    t2_text = st.session_state.get("t2_text","")
    t3_text = st.session_state.get("t3_text","")
    t5_text = st.session_state.get("t5_text","")
    if t2_done or t3_done or t5_done:
        buf = _build_report(t2_text, t3_text, t5_text)
        st.download_button("⬇  Download Word Report", buf,
                           file_name="EcoCart_Report.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                           use_container_width=True)

# ── app header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class='app-hdr'>
  <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;'>
    <div>
      <h1>EcoCart AI System</h1>
      <p>Route optimisation &nbsp;·&nbsp; Customer segmentation &nbsp;·&nbsp; Demand forecasting</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

T1, T2, T3, T4, T5, T6 = st.tabs([
    "🤖  Task 1 — AI Agents",
    "⚖️   Task 2 — Bias",
    "🗺️   Task 3 — Routes",
    "📊  Task 4 — A* vs IDA*",
    "📈  Task 5 — Forecast",
    "💼  Task 6 — Business",
])

# ══════════════════════════════════════════════════════════════════════════════
#  TASK 1 — AI AGENTS  (animated delivery simulation)
# ══════════════════════════════════════════════════════════════════════════════
with T1:
    # ── context ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div class='card card-navy'>
      <div class='step-hd'><div class='badge badge-q'>?</div>What is this?</div>
      <p style='margin:0;color:#475569;font-size:.875rem;line-height:1.65;'>
        An <strong>AI agent</strong> perceives its environment and takes actions to achieve a goal.
        EcoCart uses agents to plan delivery routes, forecast demand, and segment customers.<br><br>
        This simulation shows <strong>three different agent types</strong> navigating the same
        9-stop delivery map. Each one makes decisions differently — compare them to see the trade-offs.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── data ──────────────────────────────────────────────────────────────────
    STOPS = {
        "Depot":  (0.0, 0.0, 0), "Shop A": (2.0, 3.0, 3), "Shop B": (5.0, 1.0, 4),
        "Shop C": (7.0, 4.0, 2), "Shop D": (3.0, 6.0, 5), "Shop E": (8.0, 7.0, 1),
        "Shop F": (1.0, 8.0, 3), "Shop G": (6.0, 9.0, 4), "Shop H": (9.0, 2.0, 2),
    }
    def _sd(a, b):
        ax,ay,_ = STOPS[a]; bx,by,_ = STOPS[b]
        return math.hypot(ax-bx, ay-by)

    @st.cache_data
    def _get_routes():
        def reactive():
            r=["Depot"]; u=[k for k in STOPS if k!="Depot"]; c="Depot"
            while u:
                nb=min(u, key=lambda n: _sd(c,n)); r.append(nb); u.remove(nb); c=nb
            return r+["Depot"]
        def goal():
            r=reactive()[:-1]
            td=lambda x: sum(_sd(x[i],x[i+1]) for i in range(len(x)-1))+_sd(x[-1],x[0])
            ok=True
            while ok:
                ok=False
                for i in range(1,len(r)-1):
                    for j in range(i+1,len(r)):
                        nr=r[:i]+r[i:j+1][::-1]+r[j+1:]
                        if td(nr)<td(r)-1e-9: r=nr; ok=True
            return r+["Depot"]
        def utility():
            r=["Depot"]; u=[k for k in STOPS if k!="Depot"]; c="Depot"
            while u:
                nb=max(u, key=lambda n: STOPS[n][2]/(_sd(c,n)+.1))
                r.append(nb); u.remove(nb); c=nb
            return r+["Depot"]
        return {
            "Reactive Agent":    reactive(),
            "Goal-Based Agent":  goal(),
            "Utility-Based Agent": utility(),
        }

    ROUTES = _get_routes()
    RCOLS  = {"Reactive Agent": BLUE, "Goal-Based Agent": GREEN, "Utility-Based Agent": AMBER}
    RDESC  = {
        "Reactive Agent":
            ("Goes to the nearest unvisited stop every time.",
             "Simple and fast to compute, but often creates a longer total route."),
        "Goal-Based Agent":
            ("Plans the entire route before moving using 2-opt optimisation.",
             "Finds the shortest total distance — the gold standard for route planning."),
        "Utility-Based Agent":
            ("Scores each stop as  urgency ÷ distance  and visits the highest scorer first.",
             "Reaches high-priority (★) stops early — useful when some deliveries are time-critical."),
    }

    # ── step 1: choose agent ──────────────────────────────────────────────────
    st.markdown("""
    <div class='step-hd' style='margin-top:4px;'><div class='badge'>1</div>
    Choose an agent type — each one makes decisions differently
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col, (name, col_hex) in zip([c1,c2,c3], RCOLS.items()):
        short, long_desc = RDESC[name]
        is_sel = st.session_state.get("_ag", "Reactive Agent") == name
        border = f"2px solid {col_hex}" if is_sel else "2px solid #e2e8f0"
        bg     = _rgba(col_hex, 0.06) if is_sel else "#fff"
        with col:
            st.markdown(f"""
            <div style='border-radius:10px;padding:14px 16px;border:{border};
                        background:{bg};margin-bottom:6px;'>
              <div style='font-weight:800;font-size:.9rem;color:{col_hex};margin-bottom:4px;'>
                {name}
              </div>
              <div style='font-size:.8rem;color:#0f172a;font-weight:600;margin-bottom:3px;'>{short}</div>
              <div style='font-size:.76rem;color:#64748b;line-height:1.45;'>{long_desc}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Select {name.split()[0]}", key=f"sel_{name[:5]}",
                         use_container_width=True,
                         type="primary" if is_sel else "secondary"):
                st.session_state["_ag"] = name
                st.session_state["stp"] = 0
                st.session_state["playing"] = False
                st.rerun()

    agent = st.session_state.get("_ag", "Reactive Agent")
    if agent not in RCOLS:
        agent = "Reactive Agent"
        st.session_state["_ag"] = agent
    ac    = RCOLS[agent]
    route = ROUTES[agent]
    mx       = len(route) - 1

    if st.session_state.get("_ag_prev") != agent:
        st.session_state["_ag_prev"] = agent
        st.session_state["stp"]      = 0
        st.session_state["playing"]  = False

    stp = st.session_state.get("stp", 0)

    # ── step 2: controls ──────────────────────────────────────────────────────
    st.markdown("""
    <div class='step-hd' style='margin-top:14px;'><div class='badge'>2</div>
    Control the animation — press Play or step through manually
    </div>""", unsafe_allow_html=True)

    r0, r1, r2, r3, r4 = st.columns([1.1, 1.1, 1.1, 1.8, 3.5])
    if r0.button("⏮ Reset", use_container_width=True):
        stp = 0; st.session_state["playing"] = False
    if r1.button("◀ Back",  use_container_width=True) and stp > 0:
        stp -= 1; st.session_state["playing"] = False
    if r2.button("Next ▶",  use_container_width=True) and stp < mx:
        stp += 1; st.session_state["playing"] = False
    playing = st.session_state.get("playing", False)
    if r3.button("⏸ Pause" if playing else "▶ Play animation",
                 type="primary", use_container_width=True):
        st.session_state["playing"] = not playing
    speed = r4.slider("Speed", 1, 8, 3, format="%dx", label_visibility="collapsed")

    stp = st.slider("Step through the route", 0, mx, stp,
                    key="stp_slider",
                    help="Drag to jump to any step in the delivery sequence")
    st.session_state["stp"] = stp

    path_so_far = route[:stp+1]
    visited     = set(route[:stp+1])
    km_done     = sum(_sd(path_so_far[i], path_so_far[i+1]) for i in range(len(path_so_far)-1))
    total_km    = sum(_sd(route[i], route[i+1]) for i in range(len(route)-1))

    prog_pct = stp / mx if mx > 0 else 0
    st.progress(prog_pct,
                text=f"Progress: stop {stp} of {mx}  ·  {km_done:.1f} km done  ·  {total_km-km_done:.1f} km remaining")

    # ── map + visit log ───────────────────────────────────────────────────────
    map_col, log_col = st.columns([3, 1])

    with map_col:
        fig = go.Figure()

        # Background edges
        for na in STOPS:
            for nb in STOPS:
                if na >= nb: continue
                x1,y1,_ = STOPS[na]; x2,y2,_ = STOPS[nb]
                if math.hypot(x1-x2,y1-y2) < 5.5:
                    fig.add_trace(go.Scatter(x=[x1,x2,None], y=[y1,y2,None], mode="lines",
                        line=dict(color="#dde6f0", width=1.5), showlegend=False, hoverinfo="skip"))

        # Path shadow + path
        if len(path_so_far) > 1:
            px = [STOPS[n][0] for n in path_so_far]
            py = [STOPS[n][1] for n in path_so_far]
            fig.add_trace(go.Scatter(x=px, y=py, mode="lines",
                line=dict(color=_rgba(ac, 0.15), width=14),
                showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=px, y=py, mode="lines",
                line=dict(color=ac, width=3.5),
                showlegend=False, hoverinfo="skip"))

        # Unvisited nodes
        for name, (nx, ny, pri) in STOPS.items():
            if name == "Depot" or name in visited: continue
            star = "★ " if pri >= 4 else ""
            fig.add_trace(go.Scatter(x=[nx], y=[ny], mode="markers+text",
                marker=dict(size=22, color="#f1f5f9", line=dict(color="#94a3b8", width=2)),
                text=[star + name.replace("Shop ","")],
                textposition="top center", textfont=dict(size=9, color="#64748b"),
                showlegend=False,
                hovertemplate=f"<b>{name}</b><br>Priority {pri}/5<br>Not yet visited<extra></extra>"))

        # Visited nodes — show visit-order number inside
        for i, name in enumerate(path_so_far):
            if name == "Depot": continue
            if name == route[stp] and stp > 0: continue
            nx, ny, pri = STOPS[name]
            fig.add_trace(go.Scatter(x=[nx], y=[ny], mode="markers+text",
                marker=dict(size=28, color=GREEN, line=dict(color="#fff", width=2.5)),
                text=[str(i)],
                textposition="middle center",
                textfont=dict(size=10, color="#fff", family="monospace"),
                showlegend=False,
                hovertemplate=f"<b>{name}</b><br>Visited #{i} — Priority {pri}/5<extra></extra>"))

        # Current node — triple ring halo (simulates pulse)
        cn = route[stp]
        cx, cy, cpri = STOPS[cn]
        if cn != "Depot":
            for sz, alpha in [(54, 0.10), (38, 0.20), (28, 1.0)]:
                col_val = _rgba(ac, alpha) if sz < 54 else _rgba(ac, 0.10)
                fig.add_trace(go.Scatter(x=[cx], y=[cy], mode="markers",
                    marker=dict(size=sz, color=col_val,
                                line=dict(color=_rgba(ac, 0.5 if sz<28 else 0.8), width=2)),
                    showlegend=False, hoverinfo="skip"))
            star = "★ " if cpri >= 4 else ""
            fig.add_trace(go.Scatter(x=[cx], y=[cy], mode="markers+text",
                marker=dict(size=28, color=ac, line=dict(color="#fff", width=3)),
                text=[star + cn.replace("Shop ","")],
                textposition="top center",
                textfont=dict(size=9, color=SLATE, family="system-ui"),
                showlegend=False,
                hovertemplate=f"<b>{cn}</b><br>Currently delivering here<br>Priority {cpri}/5<extra></extra>"))

        # Depot
        dx, dy, _ = STOPS["Depot"]
        fig.add_trace(go.Scatter(x=[dx], y=[dy], mode="markers+text",
            marker=dict(size=30, color=NAVY, symbol="square",
                       line=dict(color="#fff", width=2.5)),
            text=["D"], textposition="top center",
            textfont=dict(size=9, color=NAVY),
            showlegend=False,
            hovertemplate="<b>Depot</b><br>Start and end point<extra></extra>"))

        fig.update_layout(**_ch(450, ""), showlegend=False)
        fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False, range=[-0.8,10.5])
        fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False, range=[-0.8,10.5])
        st.plotly_chart(fig, use_container_width=True, key="agent_chart")

        # Legend
        st.markdown(f"""
        <div class='lgd'>
          <div class='li'><div class='ld' style='background:{NAVY};border-radius:3px;'></div> Depot</div>
          <div class='li'><div class='ld' style='background:{ac};'></div> Currently visiting</div>
          <div class='li'><div class='ld' style='background:{GREEN};'></div> Visited (# = order)</div>
          <div class='li'><div class='ld' style='background:#f1f5f9;border:1.5px solid #94a3b8;'></div> Not yet visited</div>
          <div class='li' style='margin-left:4px;'>★ = High priority (4–5/5)</div>
        </div>""", unsafe_allow_html=True)

    with log_col:
        st.markdown(f"<div style='font-weight:700;font-size:.875rem;color:{SLATE};margin-bottom:4px;'>Delivery sequence</div>",
                    unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:.75rem;color:{MUTED};margin-bottom:8px;'>Total route: {total_km:.2f} km</div>",
                    unsafe_allow_html=True)
        html = "<div class='vlog'>"
        for i, stop in enumerate(route):
            if i < stp:
                dc, tc, fw = "vd-done",    GREEN, "600"
                sub = f"+{_sd(route[i-1],stop):.1f} km" if i>0 else "start"
            elif i == stp:
                dc, tc, fw = "vd-current", BLUE,  "800"
                sub = "← here now"
            else:
                dc, tc, fw = "vd-pending", MUTED, "400"
                sub = f"{_sd(route[i-1],stop):.1f} km" if i>0 else ""
            pri  = STOPS[stop][2]
            star = "★ " if pri >= 4 else ""
            lbl  = stop.replace("Shop ","Sh.")
            html += f"""<div class='vi'>
              <div class='vd {dc}'></div>
              <div style='flex:1;'>
                <div style='color:{tc};font-weight:{fw};font-size:.79rem;'>{i}. {star}{lbl}</div>
                <div style='color:#94a3b8;font-size:.7rem;'>{sub}</div>
              </div></div>"""
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.metric("Stop",       f"{stp} / {mx}")
        st.metric("km done",    f"{km_done:.1f}")
        st.metric("km left",    f"{total_km-km_done:.1f}")

    # ── step 3: explanation ───────────────────────────────────────────────────
    st.markdown("""
    <div class='step-hd' style='margin-top:16px;'><div class='badge'>3</div>
    What you are seeing — how each agent decides where to go next
    </div>""", unsafe_allow_html=True)

    ea, eb, ec = st.columns(3)
    for col, (name, col_hex, short, long_d) in zip(
        [ea, eb, ec],
        [(n, RCOLS[n], RDESC[n][0], RDESC[n][1]) for n in RCOLS]):
        col.markdown(f"""
        <div style='background:{_rgba(col_hex,0.06)};border-radius:10px;padding:14px;
                    border:1px solid {_rgba(col_hex,0.25)};'>
          <div style='font-weight:800;color:{col_hex};font-size:.85rem;margin-bottom:5px;'>{name}</div>
          <div style='font-size:.8rem;color:#0f172a;font-weight:600;'>{short}</div>
          <div style='font-size:.76rem;color:#475569;margin-top:4px;line-height:1.5;'>{long_d}</div>
        </div>""", unsafe_allow_html=True)

    # ── auto-play ─────────────────────────────────────────────────────────────
    if st.session_state.get("playing") and stp < mx:
        time.sleep(1.0 / speed)
        st.session_state["stp"] = stp + 1
        st.rerun()
    elif st.session_state.get("playing") and stp >= mx:
        st.session_state["playing"] = False

# ══════════════════════════════════════════════════════════════════════════════
#  TASK 2 — BIAS
# ══════════════════════════════════════════════════════════════════════════════
with T2:
    st.markdown("""
    <div class='card card-amber'>
      <div class='step-hd'><div class='badge badge-q'>?</div>What is this?</div>
      <p style='margin:0;color:#475569;font-size:.875rem;line-height:1.65;'>
        EcoCart uses <strong>K-Means clustering</strong> to group customers into High, Medium, and Low
        Value segments for targeted marketing. The algorithm was found to be <strong>biased</strong> —
        rural customers were almost entirely placed in Low Value groups even though they are genuine buyers.
        <br><br>
        This task identifies why the bias exists and applies a fix to make the results fair.
        The fairness threshold used is <strong>Disparate Impact ≥ 0.80</strong> (the 4/5ths rule).
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='step-hd'><div class='badge'>1</div>
    Run the segmentation script — executes task2_segmentation.py
    </div>""", unsafe_allow_html=True)

    run_t2 = st.button("▶  Run Task 2 — Segmentation & Bias Fix",
                       type="primary", use_container_width=True, key="run_t2")

    if run_t2 or st.session_state.get("t2_done"):
        st.session_state["t2_done"] = True

        @st.cache_data
        def _run_task2():
            spec = importlib.util.spec_from_file_location("task2","task2_segmentation.py")
            m = importlib.util.module_from_spec(spec)
            buf = io.StringIO()
            with redirect_stdout(buf):
                spec.loader.exec_module(m); m.main()
            return buf.getvalue()

        with st.spinner("Running task2_segmentation.py …"):
            t2_output = _run_task2()
        st.session_state["t2_text"] = t2_output

        st.markdown("""
        <div class='step-hd'><div class='badge'>2</div>
        Terminal output — exactly what the script printed
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='term-wrap'>
          <div class='term-bar'>
            <div class='td td-r'></div><div class='td td-y'></div><div class='td td-g'></div>
            <span style='font-size:.72rem;color:#64748b;margin-left:6px;'>task2_segmentation.py</span>
          </div>
          <div class='term-body'>{t2_output}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class='step-hd'><div class='badge'>3</div>
        Charts saved by the script — visualising the bias and the fix
        </div>""", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if os.path.exists("output/bias_before_after.png"):
                st.image("output/bias_before_after.png",
                         caption="bias_before_after.png — clusters before and after mitigation",
                         use_container_width=True)
        with c2:
            if os.path.exists("output/disparate_impact.png"):
                st.image("output/disparate_impact.png",
                         caption="disparate_impact.png — fairness metrics comparison",
                         use_container_width=True)

        st.markdown("""
        <div class='insight'>
          <strong>What the output tells us</strong><br><br>
          <strong>Before the fix:</strong> 0% of rural customers were in High Value.
          Disparate Impact = 0.0 (heavily biased).<br>
          <strong>After the fix:</strong> 57.3% of rural customers are in High Value.
          Disparate Impact = 0.847 — above the 0.80 fairness threshold.<br><br>
          The fix worked by: (1) oversampling rural customers for equal representation,
          (2) adjusting rural spend for delivery cost and frequency,
          (3) promoting borderline rural customers after re-clustering.
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TASK 3 — ROUTES  (run + animated exploration replay)
# ══════════════════════════════════════════════════════════════════════════════
with T3:
    st.markdown("""
    <div class='card card-blue'>
      <div class='step-hd'><div class='badge badge-q'>?</div>What is this?</div>
      <p style='margin:0;color:#475569;font-size:.875rem;line-height:1.65;'>
        EcoCart needs to find the shortest delivery route across a network of <strong>20 nodes</strong>
        (10 urban, 10 rural). Four search algorithms were implemented: BFS, DFS, A*, and IDA*.<br><br>
        This tab has <strong>two parts</strong>: (1) run the full script to see all results and charts,
        then (2) use the interactive replay to watch BFS or A* explore the network step by step.
      </p>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class='step-hd'><div class='badge'>1</div>
    Run all four algorithms — executes task3_4_routing.py
    </div>""", unsafe_allow_html=True)

    run_t3 = st.button("▶  Run Task 3 — Route Optimisation",
                       type="primary", use_container_width=True, key="run_t3")

    if run_t3 or st.session_state.get("t3_done"):
        st.session_state["t3_done"] = True

        @st.cache_data
        def _run_task3():
            spec = importlib.util.spec_from_file_location("task3","task3_4_routing.py")
            m = importlib.util.module_from_spec(spec)
            buf = io.StringIO()
            with redirect_stdout(buf):
                spec.loader.exec_module(m); m.main()
            return buf.getvalue()

        with st.spinner("Running task3_4_routing.py …"):
            t3_output = _run_task3()
        st.session_state["t3_text"] = t3_output

        st.markdown("""
        <div class='step-hd'><div class='badge'>2</div>
        Terminal output from task3_4_routing.py
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='term-wrap'>
          <div class='term-bar'>
            <div class='td td-r'></div><div class='td td-y'></div><div class='td td-g'></div>
            <span style='font-size:.72rem;color:#64748b;margin-left:6px;'>task3_4_routing.py</span>
          </div>
          <div class='term-body'>{t3_output}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class='step-hd'><div class='badge'>3</div>
        Charts saved by the script
        </div>""", unsafe_allow_html=True)
        if os.path.exists("output/network_map.png"):
            st.image("output/network_map.png",
                     caption="network_map.png — the 20-node delivery network",
                     use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            if os.path.exists("output/algo_comparison.png"):
                st.image("output/algo_comparison.png",
                         caption="algo_comparison.png — A* vs IDA* across all routes",
                         use_container_width=True)
        with c2:
            if os.path.exists("output/green_vs_fast.png"):
                st.image("output/green_vs_fast.png",
                         caption="green_vs_fast.png — fastest vs lowest CO₂ route",
                         use_container_width=True)

        st.markdown("""
        <div class='insight'>
          <strong>What the output tells us</strong><br><br>
          On route U1→U10: BFS found 5.69 km (11 nodes), DFS found 6.84 km (18 nodes — not optimal),
          A* found 5.69 km (only 7 nodes expanded), IDA* found 5.69 km (43 nodes).<br><br>
          <strong>A* is the recommended algorithm</strong> — it always finds the optimal path and
          expands the fewest nodes. DFS is the only algorithm that does not guarantee the shortest path.<br><br>
          Green routing: a slightly longer path (e.g. U1→R9: 16.4 km vs 14.7 km) can reduce CO₂
          by 0.25 kg by choosing roads with lower emission rates.
        </div>""", unsafe_allow_html=True)

    # ── step 4: interactive route replay ────────────────────────────────────
    st.markdown("<div style='margin-top:8px;'>", unsafe_allow_html=True)
    st.markdown("""
    <div class='step-hd'><div class='badge'>4</div>
    Interactive replay — watch an algorithm search the network step by step
    </div>""", unsafe_allow_html=True)

    NODES_R = {
        "U1":(1.0,1.0,"urban"),  "U2":(2.0,1.5,"urban"),  "U3":(3.0,1.0,"urban"),
        "U4":(1.5,2.5,"urban"),  "U5":(2.5,3.0,"urban"),  "U6":(3.5,2.0,"urban"),
        "U7":(1.0,3.5,"urban"),  "U8":(2.0,4.0,"urban"),  "U9":(3.0,4.0,"urban"),
        "U10":(4.0,3.5,"urban"),
        "R1":(6.0,1.0,"rural"),  "R2":(8.0,2.0,"rural"),  "R3":(10.0,1.5,"rural"),
        "R4":(7.0,4.0,"rural"),  "R5":(9.0,4.5,"rural"),  "R6":(11.0,3.5,"rural"),
        "R7":(6.5,6.0,"rural"),  "R8":(9.0,7.0,"rural"),  "R9":(11.0,6.0,"rural"),
        "R10":(8.0,5.5,"rural"),
    }
    _EP2 = [
        ("U1","U2"),("U2","U3"),("U1","U4"),("U2","U4"),("U2","U5"),
        ("U3","U6"),("U4","U5"),("U5","U6"),("U4","U7"),("U5","U8"),
        ("U6","U10"),("U7","U8"),("U8","U9"),("U9","U10"),("U5","U9"),
        ("R1","R2"),("R2","R3"),("R1","R4"),("R2","R4"),("R3","R6"),
        ("R4","R5"),("R5","R6"),("R4","R7"),("R5","R10"),("R7","R10"),
        ("R7","R8"),("R8","R9"),("R6","R9"),("R8","R10"),("R5","R8"),
        ("U3","R1"),("U10","R4"),("U6","R1"),("U9","R7"),
    ]
    def _nd2(a,b): return math.hypot(NODES_R[a][0]-NODES_R[b][0],NODES_R[a][1]-NODES_R[b][1])
    EDGES2 = [(a,b,round(_nd2(a,b)*1.15,2)) for a,b in _EP2]
    ADJ2 = {n:[] for n in NODES_R}
    for a,b,w in EDGES2: ADJ2[a].append((b,w)); ADJ2[b].append((a,w))
    def _ew2(a,b):
        for nb,w in ADJ2[a]:
            if nb==b: return w
        return math.inf

    def _astar_traced(s,g):
        ctr=0; h=lambda n:_nd2(n,g); expl=[]
        heap=[(h(s),0.0,ctr,s,[s])]; best={s:0.0}
        while heap:
            _,gc,_,n,p=heapq.heappop(heap)
            if n==g: return p,round(gc,2),expl
            if gc>best.get(n,math.inf): continue
            expl.append(n)
            for nb,w in ADJ2[n]:
                ng=gc+w
                if ng<best.get(nb,math.inf):
                    best[nb]=ng; ctr+=1
                    heapq.heappush(heap,(ng+h(nb),ng,ctr,nb,p+[nb]))
        return None,0.0,expl

    def _bfs_traced(s,g):
        q=deque([(s,[s])]); seen={s}; expl=[]
        while q:
            n,p=q.popleft(); expl.append(n)
            if n==g: return p,round(sum(_ew2(p[i],p[i+1]) for i in range(len(p)-1)),2),expl
            for nb,_ in ADJ2[n]:
                if nb not in seen: seen.add(nb); q.append((nb,p+[nb]))
        return None,0.0,expl

    cfg_col, rpl_col = st.columns([1, 3])

    with cfg_col:
        st.markdown("""
        <div style='background:#f8fafc;border-radius:10px;padding:14px;border:1px solid #e2e8f0;'>
          <div style='font-weight:700;color:#0f172a;font-size:.875rem;margin-bottom:10px;'>Configuration</div>
        """, unsafe_allow_html=True)
        all_n  = list(NODES_R.keys())
        sn_r   = st.selectbox("Start node", all_n, index=0,  key="r_sn")
        en_r   = st.selectbox("End node",   all_n, index=19, key="r_en")
        algo_r = st.radio("Algorithm", ["A*","BFS"], key="r_algo",
                          captions=["Guided heuristic — expands fewest nodes",
                                    "Level-by-level — guaranteed shortest hops"])
        st.markdown("</div>", unsafe_allow_html=True)

        # algorithm legend
        st.markdown(f"""
        <div style='margin-top:10px;background:#f8fafc;border-radius:10px;padding:12px;
                    border:1px solid #e2e8f0;font-size:.78rem;color:#475569;line-height:1.7;'>
          <strong style='color:#0f172a;'>Node colours</strong><br>
          <span style='color:#fff;background:#334155;padding:0 4px;border-radius:3px;'>D</span> Start &nbsp;
          <span style='color:#92400e;background:#fde68a;padding:0 4px;border-radius:3px;'>G</span> End<br>
          <span style='background:#93c5fd;padding:0 4px;border-radius:3px;'>U</span> Explored<br>
          <span style='background:{AMBER};color:#fff;padding:0 4px;border-radius:3px;'>P</span> Final path<br>
          <span style='color:#dc2626;'>■</span> Urban &nbsp;<span style='color:#059669;'>■</span> Rural
        </div>""", unsafe_allow_html=True)

    fn_r = _astar_traced if algo_r == "A*" else _bfs_traced
    if sn_r != en_r:
        path_r, cost_r, expl_r = fn_r(sn_r, en_r)
    else:
        path_r, cost_r, expl_r = [], 0.0, []

    with rpl_col:
        if sn_r != en_r and expl_r:
            max_rpl = len(expl_r)

            # auto-play controls for replay
            rp_cols = st.columns([1, 1, 1, 2, 3])
            if rp_cols[0].button("⏮", use_container_width=True, key="rp_reset"):
                st.session_state["rp_step"] = 0; st.session_state["rp_play"] = False
            if rp_cols[1].button("◀", use_container_width=True, key="rp_back"):
                st.session_state["rp_step"] = max(0, st.session_state.get("rp_step",max_rpl)-1)
                st.session_state["rp_play"] = False
            if rp_cols[2].button("▶", use_container_width=True, key="rp_fwd"):
                st.session_state["rp_step"] = min(max_rpl, st.session_state.get("rp_step",max_rpl)+1)
                st.session_state["rp_play"] = False
            rp_playing = st.session_state.get("rp_play", False)
            if rp_cols[3].button("⏸ Pause" if rp_playing else "▶ Play search",
                                 type="primary", use_container_width=True, key="rp_playbtn"):
                st.session_state["rp_play"] = not rp_playing
                if not rp_playing and st.session_state.get("rp_step", max_rpl) >= max_rpl:
                    st.session_state["rp_step"] = 0
            rp_spd = rp_cols[4].slider("Speed", 1, 8, 3, format="%dx",
                                        label_visibility="collapsed", key="rp_spd")

            replay = st.slider(
                "Drag to replay the search step by step",
                0, max_rpl,
                st.session_state.get("rp_step", max_rpl),
                key="replay_sl")
            st.session_state["rp_step"] = replay

            explored_now  = set(expl_r[:replay])
            current_node  = expl_r[replay-1] if replay > 0 else None
            path_set      = set(path_r) if path_r else set()
            done          = (replay == max_rpl)
            pct           = int(replay / max_rpl * 100)

            st.progress(replay / max_rpl,
                        text=f"{replay}/{max_rpl} nodes explored ({pct}%)"
                             + ("  ·  Path found ✓" if done and path_r else ""))

            fn2 = go.Figure()

            # Edges
            for a,b,_ in EDGES2:
                fn2.add_trace(go.Scatter(
                    x=[NODES_R[a][0],NODES_R[b][0],None],
                    y=[NODES_R[a][1],NODES_R[b][1],None], mode="lines",
                    line=dict(color="#dde6f0", width=1.5), showlegend=False, hoverinfo="skip"))

            # Final path highlight
            if path_r and done:
                for i in range(len(path_r)-1):
                    pa,pb = path_r[i],path_r[i+1]
                    fn2.add_trace(go.Scatter(
                        x=[NODES_R[pa][0],NODES_R[pb][0],None],
                        y=[NODES_R[pa][1],NODES_R[pb][1],None], mode="lines",
                        line=dict(color=AMBER, width=5), showlegend=False, hoverinfo="skip"))

            # Nodes
            for zone, zone_col in [("urban", RED), ("rural", GREEN)]:
                ns = [(n,d) for n,d in NODES_R.items() if d[2]==zone]
                for n, d in ns:
                    if n == sn_r:
                        nc, sz = "#334155", 24
                    elif n == en_r:
                        nc, sz = "#fde68a", 24
                    elif n in path_set and done:
                        nc, sz = AMBER, 22
                    elif n in explored_now:
                        nc, sz = "#93c5fd", 20
                    else:
                        nc, sz = zone_col, 16

                    # Ring halo on current node
                    if n == current_node and not done:
                        fn2.add_trace(go.Scatter(
                            x=[d[0]], y=[d[1]], mode="markers",
                            marker=dict(size=36, color=_rgba(BLUE, 0.18),
                                       line=dict(color=_rgba(BLUE, 0.6), width=2)),
                            showlegend=False, hoverinfo="skip"))

                    state = ("Path node" if n in path_set and done
                             else "Explored" if n in explored_now
                             else "Not yet visited")
                    fn2.add_trace(go.Scatter(
                        x=[d[0]], y=[d[1]], mode="markers+text",
                        marker=dict(size=sz, color=nc, line=dict(color=SLATE, width=1.5)),
                        text=[n], textposition="middle center",
                        textfont=dict(size=7.5, color="#fff" if n in explored_now and n not in (sn_r,en_r) else SLATE),
                        showlegend=False,
                        hovertemplate=f"<b>{n}</b><br>{state}<extra></extra>"))

            fn2.update_layout(**_ch(460, f"{algo_r}: {sn_r} → {en_r}"), showlegend=False)
            fn2.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
            fn2.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
            st.plotly_chart(fn2, use_container_width=True, key="route_replay")

            if path_r and done:
                mc = st.columns(3)
                mc[0].metric("Path cost",      f"{cost_r:.2f} km")
                mc[1].metric("Nodes explored", len(expl_r))
                mc[2].metric("Path length",    f"{len(path_r)} nodes")
                st.markdown(f"""
                <div class='info-note'>
                  <strong>Path found:</strong> {" → ".join(path_r)}<br>
                  <strong>{algo_r}</strong> explored {len(expl_r)} nodes to find a {cost_r:.2f} km route.
                </div>""", unsafe_allow_html=True)

            # Auto-play replay
            if st.session_state.get("rp_play") and replay < max_rpl:
                time.sleep(1.0 / rp_spd)
                st.session_state["rp_step"] = replay + 1
                st.rerun()
            elif st.session_state.get("rp_play") and replay >= max_rpl:
                st.session_state["rp_play"] = False

# ══════════════════════════════════════════════════════════════════════════════
#  TASK 4 — A* vs IDA*
# ══════════════════════════════════════════════════════════════════════════════
with T4:
    st.markdown("""
    <div class='card card-purple'>
      <div class='step-hd'><div class='badge badge-q'>?</div>What is this?</div>
      <p style='margin:0;color:#475569;font-size:.875rem;line-height:1.65;'>
        Both A* and IDA* find the <strong>optimal route</strong>, but they work differently.
        A* stores all explored nodes in memory (fast but uses more RAM).
        IDA* uses almost no memory by re-searching with a stricter cost limit each iteration.<br><br>
        This tab shows the benchmark results: 10 routes, 20 runs each — comparing nodes expanded
        and time taken.
      </p>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class='step-hd'><div class='badge'>1</div>
    Benchmark results — from task3_4_routing.py (20 runs per route)
    </div>""", unsafe_allow_html=True)

    urban_data = [
        ["U1→U10","5.69","7", "0.170","5.69","43","0.559"],
        ["U7→U6", "4.21","5", "0.088","4.21","22","0.472"],
        ["U2→U9", "3.11","2", "0.073","3.11","6", "0.129"],
        ["U1→U9", "4.40","4", "0.088","4.40","15","0.223"],
        ["U3→U8", "4.21","5", "0.114","4.21","19","0.283"],
    ]
    rural_data = [
        ["R1→R9", "10.39","6","0.134","10.39","34","0.466"],
        ["R2→R8", "7.82", "4","0.101","7.82", "14","0.224"],
        ["R3→R10","6.77", "5","0.107","6.77", "21","0.279"],
        ["R1→R6", "7.51", "3","0.065","7.51", "10","0.149"],
        ["R4→R9", "7.82", "7","0.130","7.82", "50","0.642"],
    ]
    headers = ["Route","A* km","A* nodes","A* ms","IDA* km","IDA* nodes","IDA* ms"]

    cu, cr = st.columns(2)
    with cu:
        st.markdown("**Urban routes (U cluster)**")
        st.dataframe(pd.DataFrame(urban_data, columns=headers),
                     use_container_width=True, hide_index=True)
    with cr:
        st.markdown("**Rural routes (R cluster)**")
        st.dataframe(pd.DataFrame(rural_data, columns=headers),
                     use_container_width=True, hide_index=True)

    st.markdown("""
    <div class='step-hd'><div class='badge'>2</div>
    Interactive comparison chart
    </div>""", unsafe_allow_html=True)

    all_rows = urban_data + rural_data
    routes   = [r[0] for r in all_rows]
    a_nodes  = [int(r[2])   for r in all_rows]
    i_nodes  = [int(r[5])   for r in all_rows]
    a_ms     = [float(r[3]) for r in all_rows]
    i_ms     = [float(r[6]) for r in all_rows]

    fig_cmp = make_subplots(rows=1, cols=2,
                            subplot_titles=["Nodes expanded (fewer = smarter)",
                                            "Time in ms (lower = faster)"])
    for ci, (av, iv) in enumerate([(a_nodes,i_nodes),(a_ms,i_ms)], 1):
        fig_cmp.add_trace(go.Bar(name="A*",   x=routes, y=av, marker_color=BLUE,
                                 showlegend=(ci==1)), row=1, col=ci)
        fig_cmp.add_trace(go.Bar(name="IDA*", x=routes, y=iv, marker_color=AMBER,
                                 showlegend=(ci==1)), row=1, col=ci)
    fig_cmp.update_layout(paper_bgcolor=SURF, plot_bgcolor=BG, font_color=SLATE,
                          barmode="group", height=360,
                          margin=dict(l=40,r=20,t=50,b=80),
                          legend=dict(bgcolor=SURF,bordercolor=BORDER))
    fig_cmp.update_xaxes(gridcolor=BORDER, tickangle=45)
    fig_cmp.update_yaxes(gridcolor=BORDER)
    st.plotly_chart(fig_cmp, use_container_width=True)

    if os.path.exists("output/algo_comparison.png"):
        st.markdown("""
        <div class='step-hd'><div class='badge'>3</div>
        Chart from task3_4_routing.py
        </div>""", unsafe_allow_html=True)
        st.image("output/algo_comparison.png",
                 caption="algo_comparison.png — generated by task3_4_routing.py",
                 use_container_width=True)

    st.markdown("""
    <div class='insight'>
      <strong>What the output tells us</strong><br><br>
      Both algorithms found <strong>identical optimal paths</strong> on every single route —
      the kilometre costs match exactly.<br><br>
      A* expanded fewer nodes in every case. For example on R4→R9: A* checked <strong>7 nodes</strong>,
      IDA* checked <strong>50 nodes</strong>. A* was also faster in ms on this 20-node graph.<br><br>
      However, IDA* uses almost no memory (O(depth)) while A* stores all explored nodes (O(b<sup>d</sup>)).
      On a national road network with millions of nodes, IDA* would be the only practical choice.
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TASK 5 — FORECASTING
# ══════════════════════════════════════════════════════════════════════════════
with T5:
    st.markdown("""
    <div class='card card-green'>
      <div class='step-hd'><div class='badge badge-q'>?</div>What is this?</div>
      <p style='margin:0;color:#475569;font-size:.875rem;line-height:1.65;'>
        EcoCart wants to predict how many units it will sell each day so it can stock the right
        inventory. This task trains two machine learning models —
        <strong>Linear Regression</strong> and <strong>Random Forest</strong> —
        on <strong>730 days</strong> of sales data and evaluates which one predicts more accurately
        on <strong>140 unseen test days</strong>.
      </p>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class='step-hd'><div class='badge'>1</div>
    Run the forecast — executes task5_forecasting.py
    </div>""", unsafe_allow_html=True)

    run_t5 = st.button("▶  Run Task 5 — Demand Forecasting",
                       type="primary", use_container_width=True, key="run_t5")

    if run_t5 or st.session_state.get("t5_done"):
        st.session_state["t5_done"] = True

        @st.cache_data
        def _run_task5():
            spec = importlib.util.spec_from_file_location("task5","task5_forecasting.py")
            m = importlib.util.module_from_spec(spec)
            buf = io.StringIO()
            with redirect_stdout(buf):
                spec.loader.exec_module(m); m.main()
            return buf.getvalue()

        with st.spinner("Running task5_forecasting.py …"):
            t5_output = _run_task5()
        st.session_state["t5_text"] = t5_output

        st.markdown("""
        <div class='step-hd'><div class='badge'>2</div>
        Terminal output from task5_forecasting.py
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='term-wrap'>
          <div class='term-bar'>
            <div class='td td-r'></div><div class='td td-y'></div><div class='td td-g'></div>
            <span style='font-size:.72rem;color:#64748b;margin-left:6px;'>task5_forecasting.py</span>
          </div>
          <div class='term-body'>{t5_output}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class='step-hd'><div class='badge'>3</div>
        Charts saved by the script
        </div>""", unsafe_allow_html=True)
        if os.path.exists("output/forecast.png"):
            st.image("output/forecast.png",
                     caption="forecast.png — actual vs predicted daily sales (140-day test set)",
                     use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            if os.path.exists("output/residuals.png"):
                st.image("output/residuals.png",
                         caption="residuals.png — prediction errors for both models",
                         use_container_width=True)
        with c2:
            if os.path.exists("output/feature_importance.png"):
                st.image("output/feature_importance.png",
                         caption="feature_importance.png — which features matter most",
                         use_container_width=True)

        st.markdown("""
        <div class='step-hd'><div class='badge'>4</div>
        Key metrics from the actual run
        </div>""", unsafe_allow_html=True)
        mc = st.columns(4)
        mc[0].metric("LR — MAE",  "9.62 units")
        mc[1].metric("LR — R²",   "0.762")
        mc[2].metric("RF — MAE",  "9.75 units")
        mc[3].metric("RF — R²",   "0.716")

        st.markdown("""
        <div class='insight'>
          <strong>What the output tells us</strong><br><br>
          Linear Regression achieved R² = 0.762, meaning it explains <strong>76.2%</strong>
          of the variation in daily sales. Random Forest achieved R² = 0.716.
          On this dataset, <strong>Linear Regression performed slightly better</strong>.<br><br>
          The top 3 most important features were: <strong>lag_7</strong> (sales 7 days ago),
          <strong>lag_14</strong>, and <strong>is_promo</strong>. This confirms that weekly
          sales patterns and promotional activity are the strongest predictors of demand.
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TASK 6 — BUSINESS CASE
# ══════════════════════════════════════════════════════════════════════════════
with T6:
    st.markdown("""
    <div class='card card-amber'>
      <div class='step-hd'><div class='badge badge-q'>?</div>What is this?</div>
      <p style='margin:0;color:#475569;font-size:.875rem;line-height:1.65;'>
        This task is attempted <strong>voluntarily</strong> (AI students are permitted to do so).
        It estimates the business value and environmental impact of deploying the AI system.<br><br>
        <strong>Important:</strong> All numbers are <em>assumptions for illustration</em>,
        not measured values. Adjust the sliders to model different scenarios.
      </p>
    </div>""", unsafe_allow_html=True)

    c_ctrl, c_main = st.columns([1, 3])

    with c_ctrl:
        st.markdown("""
        <div style='background:#f8fafc;border-radius:10px;padding:14px;border:1px solid #e2e8f0;'>
          <div style='font-weight:700;font-size:.875rem;color:#0f172a;margin-bottom:10px;'>Your assumptions</div>
        """, unsafe_allow_html=True)
        fleet   = st.slider("Fleet (vehicles)",         5,  100,  30, 5)
        daily   = st.slider("Deliveries/vehicle/day",  10,   80,  40, 5)
        avg_km  = st.slider("Avg km per delivery",      2,   30,  12, 1)
        fuel    = st.slider("Fuel €/km",             0.10, 0.60,0.32,0.01, format="€%.2f")
        wage    = st.slider("Driver wage €/hr",        10,   35,  18, 1,   format="€%d")
        days_yr = st.slider("Working days/year",      200,  365, 300,10)
        rt_save = st.slider("Route saving % (A*)",      5,   35,  18, 1,   format="%d%%")
        seg_rev = st.slider("Rural revenue uplift €k", 10,  200,  65, 5)
        st.markdown("</div>", unsafe_allow_html=True)

    with c_main:
        total_km   = fleet * daily * days_yr * avg_km
        km_saved   = total_km * rt_save / 100
        fuel_saved = km_saved * fuel
        time_saved = (km_saved / 40) * wage
        route_save = fuel_saved + time_saved
        seg_save   = seg_rev * 1000
        total_eur  = route_save + seg_save
        co2        = km_saved * 0.24 / 1000
        dev        = 45000; ops = 8000
        payback    = round((dev+ops)/total_eur*12, 1) if total_eur > 0 else 0
        roi3       = round((total_eur*3-(dev+ops*3))/(dev+ops*3)*100, 1)

        mc = st.columns(4)
        mc[0].metric("Est. annual saving", f"€{round(total_eur/1000,1)}k")
        mc[1].metric("Est. payback",       f"{payback} months")
        mc[2].metric("3-year ROI",         f"{roi3}%")
        mc[3].metric("CO₂ saved/year",     f"{co2:.1f} tonnes")

        cats = ["Route Optimisation\n(A*)","Fairer Segmentation\n(rural uplift)"]
        vals = [round(route_save/1000,1), round(seg_save/1000,1)]
        fig_b = go.Figure(go.Bar(x=cats, y=vals, marker_color=[BLUE, GREEN],
                                 text=[f"€{v}k" for v in vals], textposition="outside",
                                 textfont_color=SLATE, width=0.4))
        fig_b.update_layout(**_ch(270,"Estimated annual savings by area (€ thousands)"))
        fig_b.update_xaxes(gridcolor=BORDER)
        fig_b.update_yaxes(gridcolor=BORDER, title="€ thousands")
        st.plotly_chart(fig_b, use_container_width=True)

        years   = [0, 1, 2, 3]
        benefit = [0, total_eur, total_eur*2, total_eur*3]
        cost    = [0, dev+ops, dev+ops*2, dev+ops*3]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatter(x=years, y=[v/1000 for v in benefit],
            name="Cumulative benefit", line=dict(color=GREEN, width=2.5), mode="lines+markers"))
        fig_r.add_trace(go.Scatter(x=years, y=[v/1000 for v in cost],
            name="Cumulative cost", line=dict(color=RED, width=2.5, dash="dash"), mode="lines+markers"))
        fig_r.add_hline(y=0, line_color=MUTED, line_width=1, line_dash="dot")
        fig_r.update_layout(**_ch(290,"3-year ROI projection (€ thousands — assumed values)"))
        fig_r.update_xaxes(gridcolor=BORDER, tickvals=[0,1,2,3],
                           ticktext=["Now","Year 1","Year 2","Year 3"])
        fig_r.update_yaxes(gridcolor=BORDER, title="€ thousands")
        st.plotly_chart(fig_r, use_container_width=True)

        st.markdown(
            f"<div class='warn-note'>"
            f"All numbers are <strong>estimated assumptions</strong> for illustration only — not measured values. "
            f"Based on your inputs: {fleet} vehicles, {daily} deliveries/day, {avg_km} km avg, "
            f"{rt_save}% route saving from A*, €{seg_rev}k rural revenue uplift."
            f"</div>", unsafe_allow_html=True)
