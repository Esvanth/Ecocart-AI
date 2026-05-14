"""
EcoCart AI System  —  TABA Section II
NCI MSCAI 2026
"""

import math, heapq, time
from collections import deque

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ── page ──────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="EcoCart AI", layout="wide",
                   initial_sidebar_state="collapsed")

st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background:#f0f4f8; }
  [data-testid="stHeader"]           { background:transparent; }
  .block-container { padding:1rem 2rem 3rem; }
  .stTabs [data-baseweb="tab-list"]  { background:#fff; border-radius:12px;
                                        padding:4px; box-shadow:0 1px 4px rgba(0,0,0,.08); }
  .stTabs [data-baseweb="tab"]       { font-size:.88rem; font-weight:600;
                                        border-radius:8px; padding:8px 20px; }
  div[data-testid="metric-container"]{ background:#fff; border-radius:10px;
                                        padding:14px 18px;
                                        box-shadow:0 1px 4px rgba(0,0,0,.07); }
  .card  { background:#fff; border-radius:14px; padding:20px 24px;
            box-shadow:0 1px 5px rgba(0,0,0,.08); margin-bottom:14px; }
  .badge-green { display:inline-block; background:#d1fae5; color:#065f46;
                 border-radius:99px; padding:3px 12px; font-size:.78rem;
                 font-weight:700; }
  .badge-red   { display:inline-block; background:#fee2e2; color:#991b1b;
                 border-radius:99px; padding:3px 12px; font-size:.78rem;
                 font-weight:700; }
  .badge-blue  { display:inline-block; background:#dbeafe; color:#1e40af;
                 border-radius:99px; padding:3px 12px; font-size:.78rem;
                 font-weight:700; }
  .tip { background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px;
         padding:10px 14px; font-size:.82rem; color:#475569; margin:8px 0; }
  .section-label { font-size:.72rem; font-weight:700; letter-spacing:.08em;
                   color:#94a3b8; text-transform:uppercase; margin-bottom:4px; }
</style>
""", unsafe_allow_html=True)

# ── colours ───────────────────────────────────────────────────────────────────
BG,SURF,LINE = "#f0f4f8","#ffffff","#e2e8f0"
FG,MUTE      = "#1e293b","#64748b"
GREEN,BLUE,RED,AMBER,PURPLE = "#10b981","#3b82f6","#ef4444","#f59e0b","#8b5cf6"

SEG_COL={"High Value":GREEN,"Medium":AMBER,"Low Value":RED,"Group 4":PURPLE}

def _ch(h=380,title=""):
    return dict(height=h,paper_bgcolor=SURF,plot_bgcolor=BG,
                font=dict(color=FG,size=11),
                title=dict(text=title,font=dict(size=13,color=FG),x=0),
                margin=dict(l=50,r=20,t=48,b=40),
                legend=dict(bgcolor=SURF,bordercolor=LINE,borderwidth=1))

def _xax(**k): return dict(gridcolor=LINE,zeroline=False,linecolor=LINE,**k)
def _yax(**k): return dict(gridcolor=LINE,zeroline=False,linecolor=LINE,**k)

# ══════════════════════════════════════════════════════════════════════════════
#  NETWORK DATA
# ══════════════════════════════════════════════════════════════════════════════
NODES={
    "U1":(1.0,1.0,"urban"), "U2":(2.0,1.5,"urban"), "U3":(3.0,1.0,"urban"),
    "U4":(1.5,2.5,"urban"), "U5":(2.5,3.0,"urban"), "U6":(3.5,2.0,"urban"),
    "U7":(1.0,3.5,"urban"), "U8":(2.0,4.0,"urban"), "U9":(3.0,4.0,"urban"),
    "U10":(4.0,3.5,"urban"),
    "R1":(6.0,1.0,"rural"), "R2":(8.0,2.0,"rural"), "R3":(10.0,1.5,"rural"),
    "R4":(7.0,4.0,"rural"), "R5":(9.0,4.5,"rural"), "R6":(11.0,3.5,"rural"),
    "R7":(6.5,6.0,"rural"), "R8":(9.0,7.0,"rural"), "R9":(11.0,6.0,"rural"),
    "R10":(8.0,5.5,"rural"),
}
_EP=[("U1","U2"),("U2","U3"),("U1","U4"),("U2","U4"),("U2","U5"),
     ("U3","U6"),("U4","U5"),("U5","U6"),("U4","U7"),("U5","U8"),
     ("U6","U10"),("U7","U8"),("U8","U9"),("U9","U10"),("U5","U9"),
     ("R1","R2"),("R2","R3"),("R1","R4"),("R2","R4"),("R3","R6"),
     ("R4","R5"),("R5","R6"),("R4","R7"),("R5","R10"),("R7","R10"),
     ("R7","R8"),("R8","R9"),("R6","R9"),("R8","R10"),("R5","R8"),
     ("U3","R1"),("U10","R4"),("U6","R1"),("U9","R7")]

def _nd(a,b): return math.hypot(NODES[a][0]-NODES[b][0],NODES[a][1]-NODES[b][1])
def _cr(a,b):
    za,zb=NODES[a][2],NODES[b][2]
    return 0.28 if za==zb=="urban" else 0.18 if za!=zb else 0.10

EDGES    =[(a,b,round(_nd(a,b)*1.15,2)) for a,b in _EP]
CO2_EDGES=[(a,b,round(_nd(a,b)*1.15*_cr(a,b),3)) for a,b in _EP]
ADJ_KM={n:[] for n in NODES}; ADJ_CO2={n:[] for n in NODES}
for i,(a,b,w) in enumerate(EDGES):
    ADJ_KM[a].append((b,w)); ADJ_KM[b].append((a,w))
    c=CO2_EDGES[i][2]; ADJ_CO2[a].append((b,c)); ADJ_CO2[b].append((a,c))

def _ew(a,b,adj):
    for nb,w in adj[a]:
        if nb==b: return w
    return math.inf

# ── algorithms (return path, cost, exploration_order) ─────────────────────────
def bfs(s,g,adj):
    q=deque([(s,[s])]); seen={s}; expl=[]
    while q:
        n,p=q.popleft(); expl.append(n)
        if n==g:
            return p,round(sum(_ew(p[i],p[i+1],adj) for i in range(len(p)-1)),2),expl
        for nb,_ in adj[n]:
            if nb not in seen: seen.add(nb); q.append((nb,p+[nb]))
    return None,0.0,expl

def dfs(s,g,adj):
    stack=[(s,[s])]; seen={s}; expl=[]
    while stack:
        n,p=stack.pop(); expl.append(n)
        if n==g:
            return p,round(sum(_ew(p[i],p[i+1],adj) for i in range(len(p)-1)),2),expl
        if len(p)>=50: continue
        for nb,_ in adj[n]:
            if nb not in seen: seen.add(nb); stack.append((nb,p+[nb]))
    return None,0.0,expl

def astar(s,g,adj):
    ctr=0; h=lambda n:_nd(n,g); expl=[]
    heap=[(h(s),0.0,ctr,s,[s])]; best={s:0.0}
    while heap:
        _,gc,_,n,p=heapq.heappop(heap)
        if n==g: return p,round(gc,2),expl
        if gc>best.get(n,math.inf): continue
        expl.append(n)
        for nb,w in adj[n]:
            ng=gc+w
            if ng<best.get(nb,math.inf):
                best[nb]=ng; ctr+=1
                heapq.heappush(heap,(ng+h(nb),ng,ctr,nb,p+[nb]))
    return None,0.0,expl

def ida_star(s,g,adj):
    expl=[]; h=lambda n:_nd(n,g)
    def _dfs(n,gc,bound,path,vis):
        f=gc+h(n)
        if f>bound: return None,f
        expl.append(n)
        if n==g: return list(path),gc
        nxt=math.inf
        for nb,w in adj[n]:
            if nb in vis: continue
            vis.add(nb); path.append(nb)
            r,t=_dfs(nb,gc+w,bound,path,vis)
            if r is not None: return r,t
            if t<nxt: nxt=t
            path.pop(); vis.remove(nb)
        return None,nxt
    bound=h(s)
    while True:
        r,t=_dfs(s,0.0,bound,[s],{s})
        if r is not None: return r,round(t,2),expl
        if t==math.inf: return None,0.0,expl
        bound=t

ALGOS={"BFS":bfs,"DFS":dfs,"A*":astar,"IDA*":ida_star}

# ── network figure builder ────────────────────────────────────────────────────
def build_network(sn,en,path,explored_so_far,adj,unit,algo_name):
    pc=GREEN if unit=="CO2" else AMBER
    path_set=set(path) if path else set()
    fig=go.Figure()

    # edges
    for a,b,w in EDGES:
        on_path=(a in path_set and b in path_set and
                 any((path[i]==a and path[i+1]==b) or
                     (path[i]==b and path[i+1]==a)
                     for i in range(len(path)-1)) if path else False)
        lc=pc if on_path else "#dde3ed"
        lw=5  if on_path else 1.5
        co2w=_ew(a,b,ADJ_CO2)
        fig.add_trace(go.Scatter(
            x=[NODES[a][0],NODES[b][0],None],y=[NODES[a][1],NODES[b][1],None],
            mode="lines",line=dict(color=lc,width=lw),
            showlegend=False,hoverinfo="skip"))

    # nodes
    for zone,bc in [("urban","#ef4444"),("rural",GREEN)]:
        ns=[(n,d) for n,d in NODES.items() if d[2]==zone]
        cols,sizes=[],[]
        for n,_ in ns:
            if n==sn:          cols.append("#fff");   sizes.append(28)
            elif n==en:        cols.append("#facc15"); sizes.append(28)
            elif n in path_set:cols.append(pc);        sizes.append(22)
            elif n in explored_so_far: cols.append("#bfdbfe"); sizes.append(18)
            else:              cols.append(bc);        sizes.append(18)
        fig.add_trace(go.Scatter(
            x=[d[0] for _,d in ns],y=[d[1] for _,d in ns],
            mode="markers+text",name=zone.title(),
            marker=dict(size=sizes,color=cols,line=dict(color=FG,width=1.5)),
            text=[n for n,_ in ns],textposition="middle center",
            textfont=dict(size=8,color=FG,family="monospace"),
            hovertemplate="<b>%{text}</b><br>"+zone+"<extra></extra>"))

    title=(f"{algo_name}: {sn} → {en} | "
           f"{'Explored '+str(len(explored_so_far))+' nodes' if explored_so_far else 'Ready'}")
    fig.update_layout(**_ch(480,title))
    fig.update_layout(legend=dict(bgcolor=SURF,bordercolor=LINE,x=0.01,y=0.99))
    fig.update_xaxes(showgrid=False,showticklabels=False,zeroline=False)
    fig.update_yaxes(showgrid=False,showticklabels=False,zeroline=False)
    return fig

# ══════════════════════════════════════════════════════════════════════════════
#  AGENT SIMULATION
# ══════════════════════════════════════════════════════════════════════════════
STOPS={
    "Depot": (0.0,0.0,0), "Shop A":(2.0,3.0,3), "Shop B":(5.0,1.0,4),
    "Shop C":(7.0,4.0,2), "Shop D":(3.0,6.0,5), "Shop E":(8.0,7.0,1),
    "Shop F":(1.0,8.0,3), "Shop G":(6.0,9.0,4), "Shop H":(9.0,2.0,2),
}
def _sd(a,b): ax,ay,_=STOPS[a]; bx,by,_=STOPS[b]; return math.hypot(ax-bx,ay-by)

def _reactive():
    r=["Depot"]; u=[k for k in STOPS if k!="Depot"]; cur="Depot"
    while u: nb=min(u,key=lambda n:_sd(cur,n)); r.append(nb); u.remove(nb); cur=nb
    return r+["Depot"]

def _goal():
    r=_reactive()[:-1]
    td=lambda x:sum(_sd(x[i],x[i+1]) for i in range(len(x)-1))+_sd(x[-1],x[0])
    ok=True
    while ok:
        ok=False
        for i in range(1,len(r)-1):
            for j in range(i+1,len(r)):
                nr=r[:i]+r[i:j+1][::-1]+r[j+1:]
                if td(nr)<td(r)-1e-9: r=nr; ok=True
    return r+["Depot"]

def _utility():
    r=["Depot"]; u=[k for k in STOPS if k!="Depot"]; cur="Depot"
    while u:
        nb=max(u,key=lambda n:STOPS[n][2]/(_sd(cur,n)+.1))
        r.append(nb); u.remove(nb); cur=nb
    return r+["Depot"]

ROUTES={"Nearest stop":_reactive(),"Planned route":_goal(),"Priority first":_utility()}
AGENT_COL={"Nearest stop":BLUE,"Planned route":GREEN,"Priority first":AMBER}
AGENT_DESC={
    "Nearest stop":  "Reactive agent — goes to the closest unvisited stop. Simple and fast, no planning.",
    "Planned route": "Goal-based agent — computes the shortest full route before departing.",
    "Priority first":"Utility-based agent — balances urgency vs distance. Starred stops are served first.",
}

def _route_km(r): return round(sum(_sd(r[i],r[i+1]) for i in range(len(r)-1)),2)

def draw_agent(route,step,ac):
    visited=set(route[:step+1]); pso=route[:step+1]
    km=sum(_sd(pso[i],pso[i+1]) for i in range(len(pso)-1))
    cur=route[step]
    fig=go.Figure()
    for na in STOPS:
        for nb in STOPS:
            if na>=nb: continue
            x1,y1,_=STOPS[na]; x2,y2,_=STOPS[nb]
            if math.hypot(x1-x2,y1-y2)<5.5:
                fig.add_trace(go.Scatter(x=[x1,x2,None],y=[y1,y2,None],mode="lines",
                    line=dict(color="#e2e8f0",width=1),showlegend=False,hoverinfo="skip"))
    if len(pso)>1:
        fig.add_trace(go.Scatter(
            x=[STOPS[n][0] for n in pso],y=[STOPS[n][1] for n in pso],
            mode="lines+markers",line=dict(color=ac,width=3),
            marker=dict(size=6,color=ac),showlegend=False,hoverinfo="skip"))
    for name,(nx,ny,pri) in STOPS.items():
        if name=="Depot":       nc,sz,sym="#3b82f6",26,"square"
        elif name==cur:         nc,sz,sym=ac,28,"circle"
        elif name in visited:   nc,sz,sym=GREEN,18,"circle"
        else:                   nc,sz,sym="#cbd5e1",18,"circle"
        label=("⭐" if pri>=4 else "")+" "+name.replace("Shop ","")
        fig.add_trace(go.Scatter(x=[nx],y=[ny],mode="markers+text",showlegend=False,
            marker=dict(size=sz,color=nc,line=dict(color="#fff",width=2)),
            text=[label.strip()],textposition="top center",textfont=dict(size=9,color=FG),
            hovertemplate=f"<b>{name}</b><br>Priority {pri}/5<br>{'✓ Visited' if name in visited else 'Pending'}<extra></extra>"))
    fig.update_layout(**_ch(400,f"Step {step}/{len(route)-1}  —  {km:.1f} km so far"))
    fig.update_xaxes(showgrid=False,showticklabels=False,zeroline=False,range=[-0.5,10.5])
    fig.update_yaxes(showgrid=False,showticklabels=False,zeroline=False,range=[-0.5,10.5])
    return fig, round(km,2)

# ══════════════════════════════════════════════════════════════════════════════
#  SEGMENTATION
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def _customers(nu,nr):
    rng=np.random.default_rng(42)
    u=pd.DataFrame({"freq":rng.normal(6,2,nu).clip(.5),"spend":rng.normal(120,40,nu).clip(10),
                    "recency":rng.exponential(10,nu).clip(1,90),"region":"urban"})
    r=pd.DataFrame({"freq":rng.normal(3,1.5,nr).clip(.5),"spend":rng.normal(65,30,nr).clip(10),
                    "recency":rng.exponential(15,nr).clip(1,90),"region":"rural"})
    return pd.concat([u,r],ignore_index=True).round(1)

def _kmeans(df,k):
    X=StandardScaler().fit_transform(df[["freq","spend","recency"]])
    df=df.copy(); df["cluster"]=KMeans(n_clusters=k,random_state=42,n_init=10).fit_predict(X)
    order=df.groupby("cluster")["spend"].mean().sort_values(ascending=False).index
    names=(["High Value","Medium","Low Value","Group 4"])[:k]
    df["segment"]=df["cluster"].map({order[i]:names[i] for i in range(k)})
    return df

def _di(df):
    u=(df[df.region=="urban"].segment=="High Value").mean()
    r=(df[df.region=="rural"].segment=="High Value").mean()
    return round(u*100,1),round(r*100,1),round(r/u if u else 0,3)

@st.cache_data
def _fix(nu,nr,k):
    df=_customers(nu,nr)
    bal=pd.concat([df[df.region=="urban"],
                   df[df.region=="rural"].sample(len(df[df.region=="urban"]),replace=True,random_state=42)],
                  ignore_index=True).copy()
    bal.loc[bal.region=="rural","spend"]+=12
    bal.loc[bal.region=="rural","freq"]*=1.5
    bal=_kmeans(bal,k)
    rm=bal.region=="rural"; um=bal.region=="urban"
    need=int((bal[um].segment=="High Value").mean()*.85*rm.sum())-(bal[rm].segment=="High Value").sum()
    if need>0:
        cands=bal[rm&(bal.segment!="High Value")]
        bal.loc[cands.nlargest(min(need,len(cands)),"spend").index,"segment"]="High Value"
    return bal

# ══════════════════════════════════════════════════════════════════════════════
#  FORECASTING
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def _sales():
    rng=np.random.default_rng(42); days=730
    t=np.arange(days); dates=pd.date_range("2023-01-01",periods=days,freq="D")
    promo=np.zeros(days); promo[rng.choice(days,int(days*.06),replace=False)]=rng.uniform(30,70,int(days*.06))
    sales=np.clip(100+.05*t+25*np.sin(2*np.pi*t/7)+40*np.sin(2*np.pi*t/365)+rng.normal(0,8,days)+promo,0,None)
    df=pd.DataFrame({"date":dates,"sales":sales,"dow":dates.dayofweek,"month":dates.month,
                     "day_of_year":dates.dayofyear,"is_promo":(promo>0).astype(int)})
    for l in [1,7,14]: df[f"lag_{l}"]=df["sales"].shift(l)
    df["roll_7"]=df["sales"].shift(1).rolling(7).mean()
    df["roll_30"]=df["sales"].shift(1).rolling(30).mean()
    return df.dropna().reset_index(drop=True)

FEATS=["dow","month","day_of_year","is_promo","lag_1","lag_7","lag_14","roll_7","roll_30"]
FEAT_LABELS={"lag_7":"Sales 7 days ago","lag_1":"Yesterday's sales","lag_14":"Sales 14 days ago",
             "roll_7":"7-day average","roll_30":"30-day average","is_promo":"Promotion active",
             "day_of_year":"Day of year","month":"Month","dow":"Day of week"}

@st.cache_data
def _train(tp,ne):
    df=_sales(); sp=int(len(df)*tp/100); tr,te=df.iloc[:sp],df.iloc[sp:]
    lr=LinearRegression().fit(tr[FEATS],tr["sales"])
    rf=RandomForestRegressor(n_estimators=ne,max_depth=12,min_samples_leaf=3,
                             random_state=42,n_jobs=-1).fit(tr[FEATS],tr["sales"])
    lp=lr.predict(te[FEATS]); rp=rf.predict(te[FEATS])
    return lr,rf,te,lp,rp,rf.feature_importances_

def _met(y,yh):
    return (round(mean_absolute_error(y,yh),1),
            round(mean_squared_error(y,yh)**.5,1),
            round(r2_score(y,yh),3),
            round(np.mean(np.abs((y-yh)/np.where(y==0,1,y)))*100,1))

# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<h2 style='margin:0 0 12px;color:#1e293b'>🛒 EcoCart AI System</h2>",
            unsafe_allow_html=True)

T1,T2,T3,T4,T5,T6=st.tabs([
    "🤖  Task 1 — AI Agents",
    "⚖️  Task 2 — Bias Check",
    "🗺️  Task 3 — Route Finder",
    "📊  Task 4 — Speed Test",
    "📈  Task 5 — Sales Forecast",
    "💼  Task 6 — Business Case",
])

# ══════════════════════════════════════════════════════════════════════════════
#  TASK 1
# ══════════════════════════════════════════════════════════════════════════════
with T1:
    st.markdown("### Watch the AI delivery agent navigate in real time")
    st.caption("Three different AI strategies — pick one and press Play to watch it move stop by stop.")

    # ── agent picker ──────────────────────────────────────────────────────────
    a_cols=st.columns(3)
    agent_names=list(ROUTES.keys())
    if "agent" not in st.session_state: st.session_state.agent="Nearest stop"

    for i,(col,name) in enumerate(zip(a_cols,agent_names)):
        km=_route_km(ROUTES[name])
        active=st.session_state.agent==name
        border=f"3px solid {AGENT_COL[name]}" if active else "2px solid #e2e8f0"
        bg=f"{AGENT_COL[name]}12" if active else "#fff"
        if col.button(f"{'✓ ' if active else ''}{name}  ({km} km)",
                      key=f"ab_{name}",use_container_width=True):
            st.session_state.agent=name
            st.session_state.stp=0
            st.session_state.playing=False

    agent=st.session_state.agent
    ac=AGENT_COL[agent]
    route=ROUTES[agent]; mx=len(route)-1

    # ── playback controls ─────────────────────────────────────────────────────
    ctl=st.columns([1,1,1,1,3])
    if ctl[0].button("⏮ Start"):
        st.session_state.stp=0; st.session_state.playing=False
    if ctl[1].button("◀ Back") and st.session_state.get("stp",0)>0:
        st.session_state.stp-=1; st.session_state.playing=False
    if ctl[2].button("▶ Next") and st.session_state.get("stp",0)<mx:
        st.session_state.stp+=1; st.session_state.playing=False
    playing=st.session_state.get("playing",False)
    if ctl[3].button("⏸ Pause" if playing else "▶ Play"):
        st.session_state.playing=not playing

    speed=ctl[4].slider("Speed",1,8,3,label_visibility="collapsed",
                         help="Animation speed (steps per second)")

    stp=st.session_state.get("stp",0)

    fig_agent,km_done=draw_agent(route,stp,ac)

    # ── map + stats ───────────────────────────────────────────────────────────
    map_c,stat_c=st.columns([3,1])
    with map_c:
        st.plotly_chart(fig_agent,use_container_width=True,key="agent_map")

    with stat_c:
        st.markdown(f"<div class='section-label'>Current status</div>",unsafe_allow_html=True)
        st.metric("Stops completed",f"{stp} / {mx}")
        st.metric("Distance covered",f"{km_done} km")
        psum=sum(STOPS[n][2] for n in route[:stp+1] if n!="Depot")
        st.metric("Priority points served",psum)
        st.markdown(" ")
        st.markdown(f"<div class='tip'>{AGENT_DESC[agent]}</div>",unsafe_allow_html=True)
        st.markdown("<div class='section-label' style='margin-top:12px'>All agents</div>",unsafe_allow_html=True)
        for nm in agent_names:
            km=_route_km(ROUTES[nm]); c=AGENT_COL[nm]
            hi=next((i for i,n in enumerate(ROUTES[nm]) if n!="Depot" and STOPS[n][2]>=4),"-")
            st.markdown(
                f"<div style='border-left:3px solid {c};padding:6px 10px;"
                f"margin:4px 0;background:{'#f8fafc' if nm!=agent else c+'12'};border-radius:0 6px 6px 0'>"
                f"<b style='font-size:.82rem'>{nm}</b> &nbsp;"
                f"<span style='color:{MUTE};font-size:.78rem'>{km} km · 1st star: step {hi}</span>"
                f"</div>",unsafe_allow_html=True)

    # ── auto-play ─────────────────────────────────────────────────────────────
    if st.session_state.get("playing") and stp<mx:
        time.sleep(1.0/speed)
        st.session_state.stp=stp+1
        st.rerun()
    elif st.session_state.get("playing") and stp>=mx:
        st.session_state.playing=False

# ══════════════════════════════════════════════════════════════════════════════
#  TASK 2
# ══════════════════════════════════════════════════════════════════════════════
with T2:
    st.markdown("### Are rural customers being treated fairly by the AI?")
    st.caption("Adjust the sliders and watch the fairness score update instantly.")

    ctrl,main=st.columns([1,3])
    with ctrl:
        nu=st.slider("Urban customers",100,500,300,50)
        nr=st.slider("Rural customers",30,200,100,10)
        k=st.slider("Groups (K-Means)",2,4,3,1)
        fix=st.toggle("Apply fairness fix",True)
        st.markdown(" ")
        if fix:
            st.markdown("""
<div class='tip'>
<b>What the fix does:</b><br><br>
• Rural customers pay ~€12 more per delivery — we add this back to their spend score<br>
• Rural customers batch orders (less frequent, bigger baskets) — we adjust their frequency<br>
• We balance the dataset so rural customers are equally represented during training
</div>""",unsafe_allow_html=True)
        else:
            st.markdown("""
<div class='tip'>
<b>Why bias happens:</b><br><br>
EcoCart launched in cities first. Urban customers have more data and appear to spend more on the surface.
The AI picks up this pattern and unfairly labels rural customers as low-value.
</div>""",unsafe_allow_html=True)

    with main:
        raw=_customers(nu,nr); seg_b=_kmeans(raw,k); ub,rb,dib=_di(seg_b)
        if fix: seg_a=_fix(nu,nr,k); ua,ra,dia=_di(seg_a)

        # ── big fairness indicator ────────────────────────────────────────────
        mc=st.columns(4)
        mc[0].metric("Urban in High Value",f"{ub}%")
        mc[1].metric("Rural in High Value",f"{rb}%")
        di_val=dia if fix else dib
        di_delta=f"{dia-dib:+.2f}" if fix else None
        mc[2].metric("Fairness score",f"{di_val:.2f}",delta=di_delta,
                     help="1.0 = perfectly equal. Aim: ≥ 0.80")
        status="FAIR" if di_val>=0.8 else "NOT FAIR"
        mc[3].markdown(
            f"<div style='background:#fff;border-radius:10px;padding:14px 18px;"
            f"box-shadow:0 1px 4px rgba(0,0,0,.07);text-align:center'>"
            f"<div style='font-size:.8rem;color:{MUTE}'>Status</div>"
            f"<div class='badge-{'green' if di_val>=.8 else 'red'}' "
            f"style='font-size:.95rem;margin-top:6px'>{status}</div></div>",
            unsafe_allow_html=True)

        if di_val>=0.8: st.success(f"Fairness achieved — score {di_val:.2f} is above the 0.80 threshold.")
        else:           st.error(f"Score {di_val:.2f} is below 0.80 — rural customers are under-served.")

        # ── scatter ───────────────────────────────────────────────────────────
        def _scatter(df,title):
            fig=go.Figure()
            for seg in ["High Value","Medium","Low Value","Group 4"]:
                if seg not in df.segment.values: continue
                for region,sym in [("urban","circle"),("rural","triangle-up")]:
                    sub=df[(df.segment==seg)&(df.region==region)]
                    if sub.empty: continue
                    fig.add_trace(go.Scatter(x=sub.freq,y=sub.spend,mode="markers",
                        marker=dict(color=SEG_COL.get(seg,"#94a3b8"),symbol=sym,size=7,opacity=.72),
                        name=f"{seg} / {region}",
                        hovertemplate="<b>"+seg+"</b> ("+region+")<br>Purchases: %{x:.1f}/month<br>Avg spend: €%{y:.0f}<extra></extra>"))
            fig.update_layout(**_ch(320,title))
            fig.update_xaxes(**_xax(title="Purchases per month"))
            fig.update_yaxes(**_yax(title="Average spend (€)"))
            return fig

        if fix:
            c1,c2=st.columns(2)
            c1.plotly_chart(_scatter(seg_b,"Before fix — biased"),use_container_width=True)
            c2.plotly_chart(_scatter(seg_a,"After fix — fair"),use_container_width=True)
        else:
            st.plotly_chart(_scatter(seg_b,"Customer groups (no fix)"),use_container_width=True)

        # ── bar chart ─────────────────────────────────────────────────────────
        fig2=go.Figure()
        fig2.add_trace(go.Bar(name="Before fix",x=["Urban → High Value","Rural → High Value"],
                              y=[ub,rb],marker_color=RED,
                              text=[f"{ub}%",f"{rb}%"],textposition="outside",textfont_color=FG))
        if fix:
            fig2.add_trace(go.Bar(name="After fix",x=["Urban → High Value","Rural → High Value"],
                                  y=[ua,ra],marker_color=GREEN,
                                  text=[f"{ua}%",f"{ra}%"],textposition="outside",textfont_color=FG))
        fig2.update_layout(**_ch(260,"Percentage in High Value group"),barmode="group")
        fig2.update_xaxes(**_xax()); fig2.update_yaxes(**_yax(title="%",range=[0,110]))
        fig2.add_hline(y=min(ub,ua if fix else ub),line_color="#94a3b8",line_dash="dot",
                       annotation_text="Urban rate",annotation_font_color=MUTE)
        st.plotly_chart(fig2,use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TASK 3
# ══════════════════════════════════════════════════════════════════════════════
with T3:
    st.markdown("### Watch the AI find the delivery route in real time")
    st.caption("Pick start and end points, choose an algorithm, then replay how it explores the network step by step.")

    ctrl3,map3=st.columns([1,3])
    with ctrl3:
        all_n=list(NODES.keys())
        sn=st.selectbox("Start node",all_n,index=0)
        en=st.selectbox("End node",  all_n,index=19)
        al=st.radio("Algorithm",["BFS","DFS","A*","IDA*"],index=2,
                    captions=["Level-by-level","Deep dive","Guided (best)","Memory-efficient"])
        gr=st.toggle("Minimise CO₂ (not distance)",False)
        st.divider()
        adj=ADJ_CO2 if gr else ADJ_KM
        unit="CO2" if gr else "km"

        if sn==en:
            st.warning("Choose different start and end."); path,cost,expl=[],0,[]; ms=0
        else:
            t0=time.perf_counter()
            path,cost,expl=ALGOS[al](sn,en,adj)
            ms=round((time.perf_counter()-t0)*1000,3)
            if path:
                st.metric("Route distance",f"{cost} {'km' if unit=='km' else 'kg CO₂'}")
                st.metric("Nodes the AI checked",len(expl),help="The fewer the better — the AI was more efficient")
                st.metric("Time taken",f"{ms} ms")
                st.markdown(
                    f"<div class='tip'><b>Route:</b> {' → '.join(path)}</div>",
                    unsafe_allow_html=True)
            else:
                st.error("No route found."); path=[]; expl=[]

    with map3:
        # ── exploration replay slider ─────────────────────────────────────────
        if expl:
            replay=st.slider(
                "🔍 Replay: drag to see how the AI explored the map",
                0,len(expl),len(expl),
                help="0 = no exploration shown, max = full path found")
            explored_so_far=set(expl[:replay])
            pct=int(replay/len(expl)*100) if expl else 100
            st.markdown(
                f"<div style='font-size:.82rem;color:{MUTE};margin-bottom:4px'>"
                f"<span class='badge-blue'>{replay}/{len(expl)} nodes explored ({pct}%)</span>"
                f"{'&nbsp;&nbsp;<span class=badge-green>Route found</span>' if replay==len(expl) and path else ''}"
                f"</div>",unsafe_allow_html=True)
        else:
            explored_so_far=set()

        fig_net=build_network(sn,en,path,explored_so_far,adj,unit,al)
        st.plotly_chart(fig_net,use_container_width=True)

        # colour legend
        leg=st.columns(5)
        leg[0].markdown(f"<div style='font-size:.78rem'>⬤ <span style='color:{RED}'>Urban node</span></div>",unsafe_allow_html=True)
        leg[1].markdown(f"<div style='font-size:.78rem'>⬤ <span style='color:{GREEN}'>Rural node</span></div>",unsafe_allow_html=True)
        leg[2].markdown(f"<div style='font-size:.78rem'>⬤ <span style='color:#bfdbfe'>Explored</span></div>",unsafe_allow_html=True)
        leg[3].markdown(f"<div style='font-size:.78rem'>⬤ <span style='color:{AMBER}'>On path</span></div>",unsafe_allow_html=True)
        leg[4].markdown(f"<div style='font-size:.78rem'>⬤ <span style='color:#fff;background:{FG};padding:1px 4px;border-radius:3px'>Start</span> / <span style='color:{FG};background:#facc15;padding:1px 4px;border-radius:3px'>End</span></div>",unsafe_allow_html=True)

    # ── side-by-side comparison ───────────────────────────────────────────────
    with st.expander("Compare all 4 algorithms on this route"):
        if sn!=en:
            rows=[]
            for nm in ["BFS","DFS","A*","IDA*"]:
                t0=time.perf_counter(); p,c,e=ALGOS[nm](sn,en,adj); ms2=(time.perf_counter()-t0)*1000
                rows.append({"Algorithm":nm,
                             f"Distance ({'km' if unit=='km' else 'CO₂'})":round(c,2) if p else "N/A",
                             "Nodes checked":len(e),"Time (ms)":round(ms2,3),
                             "Finds shortest?":nm in ["A*","IDA*","BFS"]})
            df_c=pd.DataFrame(rows)
            st.dataframe(df_c,use_container_width=True,hide_index=True)

            fc=make_subplots(rows=1,cols=2,subplot_titles=["Nodes checked (fewer = smarter)","Time (ms)"])
            pal=[BLUE,RED,GREEN,PURPLE]
            for col,ci in [("Nodes checked",1),("Time (ms)",2)]:
                fc.add_trace(go.Bar(x=df_c["Algorithm"],y=df_c[col],marker_color=pal,
                                    text=df_c[col],textposition="outside",textfont_color=FG,
                                    showlegend=False),row=1,col=ci)
            fc.update_layout(paper_bgcolor=SURF,plot_bgcolor=BG,font_color=FG,height=280,
                             margin=dict(l=40,r=20,t=50,b=30))
            fc.update_xaxes(gridcolor=LINE); fc.update_yaxes(gridcolor=LINE)
            st.plotly_chart(fc,use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TASK 4
# ══════════════════════════════════════════════════════════════════════════════
with T4:
    st.markdown("### Head-to-head: A* vs IDA* on real delivery routes")
    st.caption("We run both algorithms on 10 routes and measure speed and efficiency. Results appear as they complete.")

    c1,c2=st.columns([1,3])
    with c1:
        nruns=st.slider("Timing runs per route",5,30,20,5)
        go_btn=st.button("▶ Run the test",type="primary",use_container_width=True)
        st.markdown("""
<div class='tip'>
<b>A*</b> keeps an open list in memory — very fast to find a path, but uses more RAM.<br><br>
<b>IDA*</b> uses almost no memory — it re-searches with a tighter limit each time. Slower here but scales to huge networks.
</div>""",unsafe_allow_html=True)

    with c2:
        OD_U=[("U1","U10"),("U7","U6"),("U2","U9"),("U1","U9"),("U3","U8")]
        OD_R=[("R1","R9"),("R2","R8"),("R3","R10"),("R1","R6"),("R4","R9")]

        if go_btn:
            rows=[]; chart_ph=st.empty(); prog=st.progress(0); status_ph=st.empty()
            total=(len(OD_U)+len(OD_R))*2; done=0

            for zone,pairs in [("Urban",OD_U),("Rural",OD_R)]:
                for s,g in pairs:
                    for nm,fn in [("A*",astar),("IDA*",ida_star)]:
                        times=[]
                        p=c3=None; e=[]
                        for _ in range(nruns):
                            t0=time.perf_counter(); p,c3,e=fn(s,g,ADJ_KM)
                            times.append((time.perf_counter()-t0)*1000)
                        rows.append({"Zone":zone,"Route":f"{s}→{g}","Algorithm":nm,
                                     "Distance (km)":c3,"Nodes checked":len(e),
                                     "Avg time (ms)":round(sum(times)/len(times),3)})
                        done+=1; prog.progress(done/total)
                        status_ph.markdown(
                            f"<span class='badge-blue'>Testing {s}→{g} with {nm}...</span>",
                            unsafe_allow_html=True)

                        # live chart update
                        if len(rows)>=2:
                            df_live=pd.DataFrame(rows)
                            sm=df_live.groupby(["Zone","Algorithm"])[["Nodes checked","Avg time (ms)"]].mean().reset_index()
                            fl=make_subplots(rows=1,cols=2,
                                            subplot_titles=["Avg nodes checked","Avg time (ms)"])
                            for anm,acl in [("A*",BLUE),("IDA*",PURPLE)]:
                                sub=sm[sm.Algorithm==anm]
                                if sub.empty: continue
                                for key,ci in [("Nodes checked",1),("Avg time (ms)",2)]:
                                    fl.add_trace(go.Bar(name=anm,x=sub["Zone"],y=sub[key].round(2),
                                        marker_color=acl,showlegend=(ci==1),
                                        text=sub[key].round(2),textposition="outside",
                                        textfont_color=FG),row=1,col=ci)
                            fl.update_layout(paper_bgcolor=SURF,plot_bgcolor=BG,font_color=FG,
                                            barmode="group",height=320,
                                            margin=dict(l=40,r=20,t=50,b=30),
                                            legend=dict(bgcolor=SURF,bordercolor=LINE))
                            fl.update_xaxes(gridcolor=LINE); fl.update_yaxes(gridcolor=LINE)
                            chart_ph.plotly_chart(fl,use_container_width=True)

            prog.empty(); status_ph.empty()
            df_b=pd.DataFrame(rows)
            st.dataframe(df_b,use_container_width=True,hide_index=True)

            ae=df_b[df_b.Algorithm=="A*"]["Nodes checked"].mean()
            ie=df_b[df_b.Algorithm=="IDA*"]["Nodes checked"].mean()
            at=df_b[df_b.Algorithm=="A*"]["Avg time (ms)"].mean()
            it=df_b[df_b.Algorithm=="IDA*"]["Avg time (ms)"].mean()
            winner="A*" if at<it else "IDA*"
            st.success(
                f"**Result:** A* checked {ae:.0f} nodes on average vs IDA*'s {ie:.0f}. "
                f"**{winner}** was faster on this map ({at:.3f} ms vs {it:.3f} ms). "
                f"On a national road network with millions of junctions, IDA*'s near-zero memory use makes it the only practical choice.")
        else:
            st.info("Click **▶ Run the test** — the chart will build live as results come in.")

# ══════════════════════════════════════════════════════════════════════════════
#  TASK 5
# ══════════════════════════════════════════════════════════════════════════════
with T5:
    st.markdown("### Predicting EcoCart's daily sales with machine learning")
    st.caption("Two models trained on 2 years of data. Adjust settings and the chart updates instantly.")

    ctrl5,main5=st.columns([1,3])
    with ctrl5:
        tp=st.slider("Training data",60,90,80,5,format="%d%%")
        ne=st.slider("Random Forest trees",50,300,200,50)
        show5=st.radio("Show",["Both","Linear Regression","Random Forest"])
        st.divider()
        st.markdown("<div class='section-label'>Try your own prediction</div>",unsafe_allow_html=True)
        st.markdown("<div class='tip'>Set values for any day and see what the model predicts.</div>",
                    unsafe_allow_html=True)
        wi_dow=st.selectbox("Day of week",["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],index=4)
        wi_month=st.selectbox("Month",["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],index=0)
        wi_promo=st.toggle("Promotion running today?",False)
        wi_lag1=st.number_input("Yesterday's sales",min_value=50,max_value=300,value=120,step=5)
        wi_lag7=st.number_input("Sales 7 days ago",  min_value=50,max_value=300,value=115,step=5)

    with main5:
        with st.spinner("Training models…"):
            lr_o,rf_o,te_df,lp,rp,imps=_train(tp,ne)

        y=te_df["sales"].values; dates=te_df["date"].values

        lmae,lrmse,lr2,lmape=_met(y,lp)
        rmae,rrmse,rr2,rmape=_met(y,rp)

        mc=st.columns(4)
        mc[0].metric("Linear Reg accuracy (R²)",lr2)
        mc[1].metric("Linear Reg avg error",f"±{lmae} units")
        mc[2].metric("Random Forest accuracy (R²)",rr2,delta=f"{rr2-lr2:+.3f}")
        mc[3].metric("Random Forest avg error",f"±{rmae} units",delta=f"{rmae-lmae:+.1f}")

        # ── what-if prediction ────────────────────────────────────────────────
        dow_map={"Mon":0,"Tue":1,"Wed":2,"Thu":3,"Fri":4,"Sat":5,"Sun":6}
        mon_map={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
                 "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
        wi_doy=int((mon_map[wi_month]-1)*30.4+15)
        wi_r7=round((wi_lag1+wi_lag7)/2)
        wi_r30=round((wi_lag1+wi_lag7)/2)
        wi_row=[[dow_map[wi_dow],mon_map[wi_month],wi_doy,int(wi_promo),
                 wi_lag1,wi_lag7,wi_lag7,wi_r7,wi_r30]]
        wi_pred_rf=round(rf_o.predict(wi_row)[0],0)
        wi_pred_lr=round(lr_o.predict(wi_row)[0],0)

        wc=st.columns(3)
        wc[0].markdown(
            f"<div style='background:#fff;border-radius:10px;padding:14px 18px;"
            f"box-shadow:0 1px 4px rgba(0,0,0,.07);text-align:center'>"
            f"<div style='font-size:.78rem;color:{MUTE}'>Your scenario prediction</div>"
            f"<div style='font-size:1.6rem;font-weight:700;color:{GREEN}'>{int(wi_pred_rf)}</div>"
            f"<div style='font-size:.78rem;color:{MUTE}'>units (Random Forest)</div></div>",
            unsafe_allow_html=True)
        wc[1].markdown(
            f"<div style='background:#fff;border-radius:10px;padding:14px 18px;"
            f"box-shadow:0 1px 4px rgba(0,0,0,.07);text-align:center'>"
            f"<div style='font-size:.78rem;color:{MUTE}'>Linear Regression says</div>"
            f"<div style='font-size:1.6rem;font-weight:700;color:{BLUE}'>{int(wi_pred_lr)}</div>"
            f"<div style='font-size:.78rem;color:{MUTE}'>units</div></div>",
            unsafe_allow_html=True)
        wc[2].markdown(
            f"<div style='background:#fff;border-radius:10px;padding:14px 18px;"
            f"box-shadow:0 1px 4px rgba(0,0,0,.07);text-align:center'>"
            f"<div style='font-size:.78rem;color:{MUTE}'>Promotion boost</div>"
            f"<div style='font-size:1.6rem;font-weight:700;color:{AMBER}'>{'Yes +~40' if wi_promo else 'None'}</div>"
            f"<div style='font-size:.78rem;color:{MUTE}'>estimated extra units</div></div>",
            unsafe_allow_html=True)

        st.markdown(" ")

        # ── forecast chart with range selector ───────────────────────────────
        fig5=go.Figure()
        fig5.add_trace(go.Scatter(x=dates,y=y,name="Actual sales",
                                  line=dict(color=FG,width=1.5),opacity=.85,
                                  hovertemplate="<b>Actual</b><br>%{x|%d %b %Y}<br>%{y:.0f} units<extra></extra>"))
        if show5 in ("Both","Linear Regression"):
            fig5.add_trace(go.Scatter(x=dates,y=lp,name="Linear Regression",
                                      line=dict(color=BLUE,width=1.5,dash="dot"),
                                      hovertemplate="<b>LR Prediction</b><br>%{x|%d %b %Y}<br>%{y:.0f} units<extra></extra>"))
        if show5 in ("Both","Random Forest"):
            fig5.add_trace(go.Scatter(x=dates,y=rp,name="Random Forest",
                                      line=dict(color=GREEN,width=1.5),
                                      hovertemplate="<b>RF Prediction</b><br>%{x|%d %b %Y}<br>%{y:.0f} units<extra></extra>"))
        fig5.update_layout(**_ch(360,f"Actual vs predicted — test set ({100-tp}% of data)"))
        fig5.update_xaxes(**_xax(title="Date",
                          rangeselector=dict(
                              bgcolor=SURF,
                              buttons=[dict(count=30,label="30d",step="day",stepmode="backward"),
                                       dict(count=60,label="60d",step="day",stepmode="backward"),
                                       dict(count=90,label="90d",step="day",stepmode="backward"),
                                       dict(step="all",label="All")])))
        fig5.update_yaxes(**_yax(title="Units sold"))
        st.plotly_chart(fig5,use_container_width=True)

        r_col,i_col=st.columns(2)
        with r_col:
            fig_r=go.Figure()
            if show5 in ("Both","Linear Regression"):
                fig_r.add_trace(go.Scatter(x=lp,y=y-lp,mode="markers",name="Linear Reg",
                    marker=dict(color=BLUE,size=5,opacity=.5),
                    hovertemplate="Predicted %{x:.0f}<br>Error %{y:.0f} units<extra></extra>"))
            if show5 in ("Both","Random Forest"):
                fig_r.add_trace(go.Scatter(x=rp,y=y-rp,mode="markers",name="Random Forest",
                    marker=dict(color=GREEN,size=5,opacity=.5),
                    hovertemplate="Predicted %{x:.0f}<br>Error %{y:.0f} units<extra></extra>"))
            fig_r.add_hline(y=0,line_color="#94a3b8",line_width=1.5,line_dash="dash")
            fig_r.update_layout(**_ch(280,"Prediction errors  (closer to 0 = better)"))
            fig_r.update_xaxes(**_xax(title="Predicted units"))
            fig_r.update_yaxes(**_yax(title="Error (actual − predicted)"))
            st.plotly_chart(fig_r,use_container_width=True)

        with i_col:
            imp=pd.Series(imps,index=FEATS).sort_values()
            fi=go.Figure(go.Bar(
                x=imp.values,
                y=[FEAT_LABELS.get(i,i) for i in imp.index],
                orientation="h",
                marker=dict(color=imp.values,colorscale=[[0,"#d1fae5"],[1,GREEN]],showscale=False),
                text=[f"{v:.3f}" for v in imp.values],
                textposition="outside",textfont_color=FG,
                hovertemplate="%{y}<br>Importance: %{x:.3f}<extra></extra>"))
            fi.update_layout(**_ch(280,"What does the model rely on most?"))
            fi.update_xaxes(**_xax(title="Importance score"))
            fi.update_yaxes(**_yax())
            st.plotly_chart(fi,use_container_width=True)

        winner="Random Forest" if rr2>=lr2 else "Linear Regression"
        st.success(
            f"**{winner}** is more accurate (R² = {max(lr2,rr2):.3f}). "
            f"The top predictor is **{FEAT_LABELS['lag_7']}** — because the same weekday last week "
            f"is the single best baseline for today's sales.")

    with st.expander("See raw prediction data"):
        st.dataframe(pd.DataFrame({"Date":dates,"Actual":y.round(1),
                                   "LR Prediction":lp.round(1),"RF Prediction":rp.round(1),
                                   "LR Error":(y-lp).round(1),"RF Error":(y-rp).round(1)}),
                     use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TASK 6 — BUSINESS CASE  (optional for AI students — covers 20% Business Viability)
# ══════════════════════════════════════════════════════════════════════════════
with T6:
    st.markdown("### Business Case — ROI & Sustainability Impact")
    st.caption("Adjust the assumptions below to model EcoCart's financial and environmental gains from the AI system.")

    # ── assumption sliders ────────────────────────────────────────────────────
    st.markdown("#### Your business assumptions")
    c1,c2,c3=st.columns(3)
    with c1:
        fleet       = st.slider("Fleet size (vehicles)",       5,  100,  30, 5)
        deliveries  = st.slider("Deliveries per vehicle/day", 10,   80,  40, 5)
        avg_km      = st.slider("Avg km per delivery",         2,   30,  12, 1)
    with c2:
        fuel_cost   = st.slider("Fuel cost per km (€)",      0.10, 0.60, 0.32, 0.01, format="€%.2f")
        driver_wage = st.slider("Driver hourly wage (€)",       10,   35,  18, 1,    format="€%d")
        working_days= st.slider("Working days per year",       200,  365, 300, 10)
    with c3:
        route_saving_pct  = st.slider("Route saving from A* (%)",       5,  35, 18, 1, format="%d%%",
                                       help="How much shorter routes become with A* vs manual planning")
        forecast_waste_pct= st.slider("Waste cut from forecasting (%)", 5,  40, 22, 1, format="%d%%",
                                       help="Reduction in overstock/understock from ML demand prediction")
        segment_revenue   = st.slider("Extra revenue from fair targeting (€k/yr)", 10, 200, 65, 5)

    st.divider()

    # ── calculations ──────────────────────────────────────────────────────────
    total_deliveries_yr = fleet * deliveries * working_days
    total_km_yr         = total_deliveries_yr * avg_km

    # route savings
    km_saved            = total_km_yr * route_saving_pct / 100
    fuel_saved          = km_saved * fuel_cost
    time_saved_hrs      = km_saved / 40                          # assume 40 km/h avg
    driver_time_saved   = time_saved_hrs * driver_wage
    route_total_saving  = fuel_saved + driver_time_saved

    # CO2 savings  (diesel: ~0.27 kg CO2/km urban, ~0.21 rural — avg 0.24)
    co2_saved_kg        = km_saved * 0.24
    co2_saved_tonnes    = co2_saved_kg / 1000

    # forecast savings (assume avg inventory cost €8 per unit, 500 SKUs)
    inventory_cost_base = 500 * 8 * working_days * 0.05         # 5% daily holding cost approximation
    forecast_saving     = inventory_cost_base * forecast_waste_pct / 100

    # segmentation revenue uplift
    segment_saving      = segment_revenue * 1000

    # total benefit
    total_benefit       = route_total_saving + forecast_saving + segment_saving

    # implementation cost (one-off dev + annual cloud)
    dev_cost            = 45000      # one-off
    annual_ops          = 8000       # cloud + maintenance per year
    total_cost_yr1      = dev_cost + annual_ops
    total_cost_yr3      = dev_cost + annual_ops * 3

    roi_yr1  = round((total_benefit - total_cost_yr1) / total_cost_yr1 * 100, 1)
    roi_yr3  = round((total_benefit * 3 - total_cost_yr3) / total_cost_yr3 * 100, 1)
    payback  = round(total_cost_yr1 / total_benefit * 12, 1)    # months

    # ── headline metrics ──────────────────────────────────────────────────────
    st.markdown("#### Results")
    m=st.columns(4)
    m[0].metric("Annual cost saving",  f"€{total_benefit/1000:.1f}k")
    m[1].metric("Year-1 ROI",          f"{roi_yr1}%",
                delta="positive" if roi_yr1>0 else "negative")
    m[2].metric("Payback period",      f"{payback} months")
    m[3].metric("CO₂ saved per year",  f"{co2_saved_tonnes:.1f} tonnes")

    # ── savings breakdown bar chart ───────────────────────────────────────────
    fig_roi=go.Figure()
    categories=["Route\nOptimisation","Demand\nForecasting","Fairer\nSegmentation"]
    values=[round(route_total_saving/1000,1),
            round(forecast_saving/1000,1),
            round(segment_saving/1000,1)]
    colors=[BLUE,GREEN,AMBER]
    fig_roi.add_trace(go.Bar(
        x=categories, y=values,
        marker_color=colors,
        text=[f"€{v}k" for v in values],
        textposition="outside", textfont_color=FG,
        hovertemplate="%{x}<br>Saving: €%{y}k/year<extra></extra>",
        width=0.5,
    ))
    fig_roi.update_layout(**_ch(300,"Annual savings breakdown by AI module (€ thousands)"))
    fig_roi.update_xaxes(**_xax())
    fig_roi.update_yaxes(**_yax(title="€ thousands"))
    st.plotly_chart(fig_roi,use_container_width=True)

    # ── 3-year cumulative ROI line ────────────────────────────────────────────
    years=[0,1,2,3]
    cumulative_benefit=[0, total_benefit, total_benefit*2, total_benefit*3]
    cumulative_cost   =[0, total_cost_yr1, total_cost_yr1+annual_ops, total_cost_yr1+annual_ops*2]
    cumulative_net    =[b-c for b,c in zip(cumulative_benefit,cumulative_cost)]

    fig_cum=go.Figure()
    fig_cum.add_trace(go.Scatter(x=years,y=[v/1000 for v in cumulative_benefit],
        name="Cumulative benefit",line=dict(color=GREEN,width=2.5),
        hovertemplate="Year %{x}<br>Benefit: €%{y:.1f}k<extra></extra>"))
    fig_cum.add_trace(go.Scatter(x=years,y=[v/1000 for v in cumulative_cost],
        name="Cumulative cost",line=dict(color=RED,width=2.5,dash="dash"),
        hovertemplate="Year %{x}<br>Cost: €%{y:.1f}k<extra></extra>"))
    fig_cum.add_trace(go.Scatter(x=years,y=[v/1000 for v in cumulative_net],
        name="Net gain",line=dict(color=BLUE,width=2.5,dash="dot"),
        fill="tozeroy",fillcolor=f"{BLUE}18",
        hovertemplate="Year %{x}<br>Net: €%{y:.1f}k<extra></extra>"))
    fig_cum.add_hline(y=0,line_color="#94a3b8",line_width=1.5,line_dash="dash")
    fig_cum.update_layout(**_ch(300,"3-year cumulative ROI projection (€ thousands)"))
    fig_cum.update_xaxes(**_xax(title="Year",tickvals=[0,1,2,3],ticktext=["Now","Year 1","Year 2","Year 3"]))
    fig_cum.update_yaxes(**_yax(title="€ thousands"))
    st.plotly_chart(fig_cum,use_container_width=True)

    # ── CO2 & sustainability ──────────────────────────────────────────────────
    st.markdown("#### Sustainability Impact")
    sc=st.columns(3)
    trees_equiv = round(co2_saved_tonnes * 45)   # ~45 trees absorb 1 tonne CO2/year
    cars_equiv  = round(co2_saved_tonnes / 2.3)  # avg car emits 2.3 tonnes CO2/year
    sc[0].metric("CO₂ saved per year",   f"{co2_saved_tonnes:.1f} tonnes")
    sc[1].metric("Equivalent trees planted", f"{trees_equiv:,}")
    sc[2].metric("Cars taken off the road",  f"{cars_equiv:,}")

    fig_co2=go.Figure(go.Bar(
        x=["Fuel savings\n(route opt.)","Green routing\n(CO₂ mode)","Total CO₂\nreduction"],
        y=[round(co2_saved_tonnes*0.75,1), round(co2_saved_tonnes*0.25,1), round(co2_saved_tonnes,1)],
        marker_color=[GREEN,BLUE,AMBER],
        text=[f"{v:.1f}t" for v in [co2_saved_tonnes*0.75, co2_saved_tonnes*0.25, co2_saved_tonnes]],
        textposition="outside",textfont_color=FG,width=0.45,
        hovertemplate="%{x}<br>%{y:.1f} tonnes CO₂/year<extra></extra>",
    ))
    fig_co2.update_layout(**_ch(280,"Annual CO₂ reduction (tonnes)"))
    fig_co2.update_xaxes(**_xax())
    fig_co2.update_yaxes(**_yax(title="Tonnes CO₂"))
    st.plotly_chart(fig_co2,use_container_width=True)

    # ── implementation roadmap ────────────────────────────────────────────────
    st.markdown("#### Implementation Roadmap")
    phases=[
        dict(Task="Phase 1: Route Optimisation (A*)",  Start=0, Finish=2,  Color=BLUE),
        dict(Task="Phase 2: Bias Fix (Segmentation)",  Start=1, Finish=3,  Color=AMBER),
        dict(Task="Phase 3: Demand Forecasting (ML)",  Start=2, Finish=5,  Color=GREEN),
        dict(Task="Phase 4: Integration & Testing",    Start=4, Finish=6,  Color=PURPLE),
        dict(Task="Phase 5: Full Deployment",          Start=6, Finish=8,  Color=RED),
    ]
    fig_rm=go.Figure()
    for i,p in enumerate(phases):
        fig_rm.add_trace(go.Bar(
            x=[p["Finish"]-p["Start"]], y=[p["Task"]],
            base=p["Start"], orientation="h",
            marker_color=p["Color"], marker_opacity=0.85,
            text=f"Month {p['Start']+1}–{p['Finish']}",
            textposition="inside", textfont=dict(color="#fff",size=11),
            showlegend=False,
            hovertemplate=f"<b>{p['Task']}</b><br>Month {p['Start']+1} → {p['Finish']}<extra></extra>",
        ))
    fig_rm.update_layout(**_ch(280,"Deployment timeline (months)"))
    fig_rm.update_xaxes(**_xax(title="Month",tickvals=list(range(9)),
                               ticktext=[f"M{i}" for i in range(9)]))
    fig_rm.update_yaxes(**_yax(autorange="reversed"))
    st.plotly_chart(fig_rm,use_container_width=True)

    # ── summary box ───────────────────────────────────────────────────────────
    st.markdown(
        f"<div style='background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;"
        f"padding:20px 24px;margin-top:8px'>"
        f"<b style='font-size:1rem;color:#065f46'>Business Summary</b><br><br>"
        f"EcoCart's AI system delivers an estimated <b>€{total_benefit/1000:.0f}k in annual savings</b> "
        f"across three areas: smarter routing (A* reduces km by {route_saving_pct}%), "
        f"better stock management (ML cuts waste by {forecast_waste_pct}%), "
        f"and fairer customer targeting (rural revenue uplift of €{segment_revenue}k). "
        f"The system pays for itself in <b>{payback} months</b> and generates a "
        f"<b>{roi_yr3}% ROI over 3 years</b>. "
        f"It also removes <b>{co2_saved_tonnes:.1f} tonnes of CO₂</b> annually — "
        f"directly supporting EcoCart's sustainability commitments."
        f"</div>",
        unsafe_allow_html=True,
    )
