





















# ══════════════════════════════════════════════════════════════════════════════
#  PrivacyLens v5.0  ·  Privacy Risk Intelligence Platform
#  OBSIDIAN EDITION — Editorial luxury dark UI
# ══════════════════════════════════════════════════════════════════════════════

import os, io, warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas    as pd
import numpy     as np
import plotly.graph_objects as go
import plotly.express       as px
import requests

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title  = "PrivacyLens",
    page_icon   = "◈",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
T = dict(
    ink0   = "#050608",
    ink1   = "#080a0e",
    ink2   = "#0c0f15",
    ink3   = "#11151d",
    ink4   = "#161c27",
    ink5   = "#1c2433",
    line   = "#1e2738",
    line2  = "#28334a",
    chalk  = "#f0f2f5",
    chalk2 = "#c8cdd6",
    chalk3 = "#8a93a3",
    chalk4 = "#4a5568",
    chalk5 = "#2d3748",
    ice    = "#e8f4fd",
    gold   = "#d4a843",
    gold2  = "#f0c96e",
    red    = "#e05252",
    red2   = "#ff6b6b",
    amber  = "#e8944a",
    amber2 = "#f0ab6e",
    lime   = "#52b788",
    lime2  = "#74c69d",
    sky    = "#4a9eda",
    sky2   = "#63b3ed",
    rose   = "#c0626e",
    rose2  = "#e07b86",
)

RISK_TIERS = [
    (20,  "PRIVATE",   T["lime"],  T["lime"]  + "14"),
    (40,  "LOW RISK",  T["sky"],   T["sky"]   + "14"),
    (60,  "MODERATE",  T["amber"], T["amber"] + "14"),
    (80,  "HIGH RISK", T["red"],   T["red"]   + "14"),
    (101, "CRITICAL",  T["rose"],  T["rose"]  + "18"),
]

RGBA0 = "rgba(0,0,0,0)"

PLOTLY_BASE = dict(
    paper_bgcolor = RGBA0,
    plot_bgcolor  = RGBA0,
    font          = dict(color=T["chalk3"], family="'DM Mono', monospace", size=10),
    margin        = dict(l=8, r=8, t=38, b=8),
    hoverlabel    = dict(
        bgcolor     = T["ink4"],
        bordercolor = T["line2"],
        font_color  = T["chalk"],
        font_size   = 11,
        font_family = "'DM Sans', sans-serif",
    ),
    legend        = dict(bgcolor=RGBA0, bordercolor=T["line"], font_size=10),
    colorway      = [T["sky"], T["lime"], T["gold"], T["amber"], T["red"], T["rose"]],
    title_font    = dict(color=T["chalk2"], size=11, family="'DM Mono', monospace"),
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — Editorial Luxury
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,200;0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300;1,9..40,400&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Fraunces:ital,opsz,wght@0,9..144,200;0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,200;1,9..144,300;1,9..144,400&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

/* ── Base ── */
html, body, [class*="css"], .stApp {{
  font-family: 'DM Sans', system-ui, sans-serif !important;
  background: {T['ink0']} !important;
  color: {T['chalk3']} !important;
}}

[data-testid="stAppViewContainer"] {{
  background: {T['ink0']} !important;
  background-image:
    radial-gradient(ellipse 60% 50% at 0% 0%, {T['sky']}08 0%, transparent 60%),
    radial-gradient(ellipse 40% 30% at 100% 100%, {T['gold']}06 0%, transparent 50%);
}}

/* ── Header ── */
[data-testid="stHeader"] {{
  background: {T['ink0']}f0 !important;
  backdrop-filter: blur(20px);
  border-bottom: 1px solid {T['line']} !important;
  height: 3rem !important;
}}

/* ── Layout ── */
.block-container {{
  padding: 1.5rem 2rem 3rem !important;
  max-width: 1600px !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
  background: {T['ink1']} !important;
  border-right: 1px solid {T['line']} !important;
}}
[data-testid="stSidebar"] > div {{
  background: {T['ink1']} !important;
}}

/* ── Typography ── */
h1 {{
  font-family: 'Fraunces', Georgia, serif !important;
  font-weight: 300 !important;
  color: {T['chalk']} !important;
  letter-spacing: -0.04em !important;
}}
h2, h3 {{
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 500 !important;
  color: {T['chalk2']} !important;
  letter-spacing: -0.02em !important;
}}

/* ── Inputs ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] input {{
  background: {T['ink3']} !important;
  border: 1px solid {T['line2']} !important;
  border-radius: 6px !important;
  color: {T['chalk2']} !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13px !important;
}}
[data-testid="stSelectbox"] > div > div:focus-within,
[data-testid="stTextInput"] input:focus {{
  border-color: {T['sky']}80 !important;
  box-shadow: 0 0 0 2px {T['sky']}18 !important;
}}

/* ── File uploader ── */
[data-testid="stFileUploader"] section {{
  background: {T['ink3']} !important;
  border: 1px dashed {T['line2']} !important;
  border-radius: 8px !important;
}}
[data-testid="stFileUploader"] section:hover {{
  border-color: {T['sky']}60 !important;
}}

/* ── Metrics ── */
[data-testid="stMetric"] {{
  background: {T['ink2']} !important;
  border: 1px solid {T['line']} !important;
  border-radius: 8px !important;
  padding: 16px 18px !important;
}}
[data-testid="stMetricValue"] {{
  color: {T['chalk']} !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 1.4rem !important;
  font-weight: 500 !important;
}}
[data-testid="stMetricLabel"] {{
  color: {T['chalk4']} !important;
  font-size: 9px !important;
  text-transform: uppercase !important;
  letter-spacing: .14em !important;
  font-weight: 500 !important;
}}
[data-testid="stMetricDelta"] {{ display: none; }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
  background: transparent !important;
  border-bottom: 1px solid {T['line']} !important;
  gap: 0 !important;
}}
.stTabs [data-baseweb="tab"] {{
  background: transparent !important;
  color: {T['chalk4']} !important;
  font-weight: 400 !important;
  font-size: 11.5px !important;
  letter-spacing: .08em !important;
  text-transform: uppercase !important;
  border-radius: 0 !important;
  padding: 10px 20px !important;
  border-bottom: 2px solid transparent !important;
  font-family: 'DM Mono', monospace !important;
}}
.stTabs [aria-selected="true"] {{
  color: {T['chalk']} !important;
  border-bottom: 2px solid {T['gold']} !important;
}}
.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {{
  color: {T['chalk3']} !important;
  background: {T['ink3']}80 !important;
}}

/* ── Buttons ── */
.stButton > button {{
  background: {T['ink4']} !important;
  color: {T['chalk2']} !important;
  border: 1px solid {T['line2']} !important;
  border-radius: 6px !important;
  font-weight: 500 !important;
  font-size: 11.5px !important;
  padding: 8px 18px !important;
  letter-spacing: .06em !important;
  text-transform: uppercase !important;
  font-family: 'DM Mono', monospace !important;
  transition: all .15s !important;
}}
.stButton > button:hover {{
  background: {T['ink5']} !important;
  border-color: {T['chalk4']} !important;
  color: {T['chalk']} !important;
}}

/* ── Alerts ── */
.stSuccess {{ background: {T['lime']}0c !important; border: 1px solid {T['lime']}30 !important; border-radius: 6px !important; }}
.stWarning {{ background: {T['amber']}0c !important; border: 1px solid {T['amber']}30 !important; border-radius: 6px !important; }}
.stInfo    {{ background: {T['sky']}0c !important; border: 1px solid {T['sky']}30 !important; border-radius: 6px !important; }}
.stError   {{ background: {T['red']}0c !important; border: 1px solid {T['red']}30 !important; border-radius: 6px !important; }}

/* ── Expander ── */
[data-testid="stExpander"] {{
  background: {T['ink2']} !important;
  border: 1px solid {T['line']} !important;
  border-radius: 8px !important;
}}
[data-testid="stExpander"] summary {{ color: {T['chalk3']} !important; font-size: 12px !important; font-family: 'DM Mono', monospace !important; letter-spacing: .06em !important; text-transform: uppercase !important; }}

/* ── Chat ── */
[data-testid="stChatMessage"] {{
  background: {T['ink2']} !important;
  border: 1px solid {T['line']} !important;
  border-radius: 8px !important;
  margin-bottom: 8px !important;
}}
[data-testid="stChatInput"] textarea {{
  background: {T['ink3']} !important;
  border: 1px solid {T['line2']} !important;
  border-radius: 8px !important;
  color: {T['chalk2']} !important;
  font-family: 'DM Sans', sans-serif !important;
}}
[data-testid="stChatInput"] textarea:focus {{
  border-color: {T['sky']}60 !important;
  box-shadow: 0 0 0 2px {T['sky']}14 !important;
}}

/* ── DataFrames ── */
[data-testid="stDataFrame"] th {{
  background: {T['ink4']} !important;
  color: {T['chalk4']} !important;
  font-size: 9px !important;
  text-transform: uppercase !important;
  letter-spacing: .12em !important;
  font-family: 'DM Mono', monospace !important;
  border-bottom: 1px solid {T['line2']} !important;
}}
[data-testid="stDataFrame"] td {{
  color: {T['chalk3']} !important;
  font-size: 12px !important;
  font-family: 'DM Mono', monospace !important;
}}

/* ── Radio ── */
[data-testid="stRadio"] label {{
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13px !important;
  color: {T['chalk4']} !important;
}}
[data-testid="stRadio"] label:has(input:checked) {{
  color: {T['chalk']} !important;
}}
[data-testid="stRadio"] > div > label {{
  padding: 9px 12px !important;
  border-radius: 6px !important;
  border: 1px solid transparent !important;
  transition: all .15s !important;
}}
[data-testid="stRadio"] > div > label:hover {{
  background: {T['ink3']} !important;
  border-color: {T['line']} !important;
}}
[data-testid="stRadio"] > div > label:has(input:checked) {{
  background: {T['ink3']} !important;
  border-color: {T['line2']} !important;
  color: {T['chalk']} !important;
}}

/* ── Misc ── */
hr {{ border-color: {T['line']} !important; margin: 1.2rem 0 !important; }}
[data-testid="stCaptionContainer"] p {{ color: {T['chalk5']} !important; font-size: 10.5px !important; font-family: 'DM Mono', monospace !important; }}
::-webkit-scrollbar {{ width: 3px; height: 3px; }}
::-webkit-scrollbar-track {{ background: {T['ink1']}; }}
::-webkit-scrollbar-thumb {{ background: {T['line2']}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {T['chalk4']}; }}

/* ── Utility ── */
.divider {{
  width: 100%; height: 1px;
  background: {T['line']};
  margin: 1.8rem 0;
}}
.tag {{
  display: inline-block;
  padding: 2px 10px;
  border: 1px solid currentColor;
  border-radius: 3px;
  font-family: 'DM Mono', monospace;
  font-size: 9.5px;
  letter-spacing: .1em;
  text-transform: uppercase;
  opacity: .85;
}}
.eyebrow {{
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  letter-spacing: .2em;
  text-transform: uppercase;
  color: {T['chalk4']};
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama3-70b-8192")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

LANGUAGES = {
    "English": "en", "Hindi — हिंदी": "hi", "Spanish — Español": "es",
    "French — Français": "fr", "Arabic — العربية": "ar",
    "Chinese — 中文": "zh", "Japanese — 日本語": "ja",
    "Portuguese — Português": "pt", "German — Deutsch": "de",
    "Russian — Русский": "ru",
}

def score_info(s):
    for threshold, label, color, bg in RISK_TIERS:
        if s < threshold:
            return label, color, bg
    return RISK_TIERS[-1][1], RISK_TIERS[-1][2], RISK_TIERS[-1][3]

def risk_color(v_norm):
    if v_norm < 0.25: return T["lime"]
    if v_norm < 0.50: return T["sky"]
    if v_norm < 0.75: return T["amber"]
    return T["red"]

def bar_col(v):
    if v < 0.30: return T["lime"]
    if v < 0.60: return T["amber"]
    return T["red"]

def safe_get(row, col, default=0.0):
    try:
        if isinstance(row, pd.Series):
            if col not in row.index: return default
            v = row[col]
        else:
            v = row[col]
        if pd.isna(v): return default
        if isinstance(default, (int, float)): return float(v)
        return v
    except: return default

def has_col(df_or_row, col):
    if isinstance(df_or_row, pd.Series): return col in df_or_row.index
    return col in df_or_row.columns

def safe_sample(frame, n=2000, seed=42):
    return frame.sample(min(n, len(frame)), random_state=seed)

def hex_rgba(hex6, alpha):
    h = hex6.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

def eyebrow(text):
    st.markdown(f'<p class="eyebrow" style="margin-bottom:6px">{text}</p>', unsafe_allow_html=True)

def divider():
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

def section_title(label, subtitle=""):
    sub_html = f'<div style="font-size:12px;color:{T["chalk4"]};margin-top:4px;font-family:\'DM Sans\',sans-serif">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="margin:2rem 0 1.2rem">
      <div style="display:flex;align-items:baseline;gap:12px">
        <span style="font-family:'DM Mono',monospace;font-size:9px;color:{T['chalk5']};
              letter-spacing:.18em;text-transform:uppercase;margin-top:2px">◈</span>
        <div>
          <span style="font-family:'Fraunces',serif;font-size:20px;font-weight:300;
                color:{T['chalk2']};letter-spacing:-.02em">{label}</span>
          {sub_html}
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

def signal_bar(label, value, explanation):
    v = float(np.clip(value, 0, 1))
    pct = int(v * 100)
    col = bar_col(v)
    return f"""
    <div style="padding:14px 0;border-bottom:1px solid {T['line']}">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <span style="font-size:12px;color:{T['chalk3']};font-family:'DM Sans',sans-serif;
              font-weight:500">{label}</span>
        <span style="font-family:'DM Mono',monospace;font-size:11px;color:{col};
              font-weight:500">{pct}%</span>
      </div>
      <div style="background:{T['ink4']};border-radius:2px;height:2px;overflow:hidden">
        <div style="width:{pct}%;background:{col};height:2px;border-radius:2px;
             transition:width .5s ease"></div>
      </div>
      <div style="font-size:11px;color:{T['chalk5']};margin-top:6px;
           font-family:'DM Sans',sans-serif;line-height:1.5">{explanation}</div>
    </div>"""

def stat_pill(label, val, color=None):
    c = color or T["chalk3"]
    return f"""<div style="display:inline-block;margin:4px 6px 4px 0;
    padding:6px 12px;background:{T['ink3']};border:1px solid {T['line2']};border-radius:4px">
      <div style="font-family:'DM Mono',monospace;font-size:9px;color:{T['chalk5']};
           text-transform:uppercase;letter-spacing:.12em;margin-bottom:3px">{label}</div>
      <div style="font-family:'DM Mono',monospace;font-size:13px;color:{c};
           font-weight:500">{val}</div>
    </div>"""

def score_badge(score, label, color):
    return f"""
    <div style="display:inline-flex;align-items:center;gap:8px;
         padding:6px 12px 6px 8px;background:{T['ink3']};
         border:1px solid {color}40;border-radius:4px">
      <div style="width:6px;height:6px;border-radius:50%;background:{color};
           box-shadow:0 0 8px {color}80"></div>
      <span style="font-family:'DM Mono',monospace;font-size:9px;color:{color};
            letter-spacing:.15em;text-transform:uppercase">{label}</span>
    </div>"""

# ─────────────────────────────────────────────────────────────────────────────
# SCORING ENGINE
# ─────────────────────────────────────────────────────────────────────────────
W = dict(
    sgeo=0.50, it2=0.30, referer_leaked=0.10,
    it1=0.05, it3=0.10, cookie_samesite_none=0.03,
    iframe=0.03, beacon=0.02,
)
TW = sum(W.values())

def compute_scores(df):
    d = df.copy()
    sig_cols = ["script","xhr","iframe","cookie_samesite_none","referer_leaked",
                "beacon","image","tracked","cookies","bad_qs","media"]
    for c in sig_cols:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0).clip(0,1)
        else:
            d[c] = 0.0
    d["sgeo"] = np.sqrt(d["script"] * d["xhr"])
    d["it1"]  = d["cookie_samesite_none"] * d["sgeo"]
    d["it2"]  = d["script"] * d["xhr"]
    d["it3"]  = d["iframe"] * d["sgeo"]
    d["privacy_score"] = (
        sum(d[c] * w for c, w in W.items()) / TW * 100
    ).clip(0, 100).round(2)
    if "requests" in d.columns and "requests_tracking" in d.columns:
        d["requests"]          = pd.to_numeric(d["requests"],          errors="coerce").fillna(0)
        d["requests_tracking"] = pd.to_numeric(d["requests_tracking"], errors="coerce").fillna(0)
        d["track_ratio"] = (d["requests_tracking"] / d["requests"].replace(0,np.nan)).fillna(0).clip(0,1)
    else:
        d["requests"] = d["requests_tracking"] = d["track_ratio"] = 0.0
    return d

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADER
# ─────────────────────────────────────────────────────────────────────────────
AUTO_PATHS = ["sites.csv", "whotracks_2026/sites.csv", "data/sites.csv"]

@st.cache_data(show_spinner="Loading dataset…")
def load_path(p):  return compute_scores(pd.read_csv(p, index_col=0))

@st.cache_data(show_spinner="Loading dataset…")
def load_bytes(b): return compute_scores(pd.read_csv(io.BytesIO(b), index_col=0))

def init_data():
    if "df" not in st.session_state or st.session_state.df is None:
        for p in AUTO_PATHS:
            if os.path.exists(p):
                st.session_state.df = load_path(p)
                return
        st.session_state.df = None

init_data()

for k, v in [("page","Score Analyzer"),("chat_msgs",[]),("last_site",None),("chat_lang","English")]:
    if k not in st.session_state:
        st.session_state[k] = v

def add_tier_col(df):
    def tier(s):
        if s < 20: return "Private"
        if s < 40: return "Low Risk"
        if s < 60: return "Moderate"
        if s < 80: return "High Risk"
        return "Critical"
    out = df.copy()
    out["tier"] = out["privacy_score"].apply(tier)
    return out

TIER_ORDER  = ["Private","Low Risk","Moderate","High Risk","Critical"]
TIER_COLORS = {"Private":T["lime"],"Low Risk":T["sky"],"Moderate":T["amber"],"High Risk":T["red"],"Critical":T["rose"]}

# ─────────────────────────────────────────────────────────────────────────────
# GROQ API
# ─────────────────────────────────────────────────────────────────────────────
def call_groq(messages, system, api_key):
    if not api_key:
        return "⚠ No API key. Add GROQ_API_KEY to your .env file."
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": GROQ_MODEL, "max_tokens": 900, "temperature": 0.6,
                  "messages": [{"role":"system","content":system}] + messages},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout: return "⚠ Request timed out."
    except requests.exceptions.HTTPError as e: return f"⚠ API error {e.response.status_code}"
    except Exception as e: return f"⚠ {e}"

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:24px 0 20px">
      <div style="font-family:'DM Mono',monospace;font-size:9px;letter-spacing:.25em;
           text-transform:uppercase;color:{T['chalk5']};margin-bottom:10px">
        Privacy Intelligence
      </div>
      <div style="font-family:'Fraunces',serif;font-size:26px;font-weight:300;
           color:{T['chalk']};letter-spacing:-.03em;line-height:1">
        Privacy<span style="color:{T['gold']}">Lens</span>
      </div>
      <div style="font-family:'DM Mono',monospace;font-size:9px;color:{T['chalk5']};
           letter-spacing:.15em;margin-top:6px">v5.0 · Risk Intelligence</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="divider"></div>', unsafe_allow_html=True)

    eyebrow("Navigation")
    page = st.radio("nav", ["Score Analyzer","Analytics Dashboard"],
                    index=0 if st.session_state.page=="Score Analyzer" else 1,
                    label_visibility="collapsed")
    st.session_state.page = page

    st.markdown(f'<div class="divider"></div>', unsafe_allow_html=True)

    df_raw = st.session_state.df
    eyebrow("Data Source")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if df_raw is None:
        uploaded = st.file_uploader("Upload sites.csv", type=["csv"], label_visibility="collapsed")
        if uploaded:
            st.session_state.df = load_bytes(uploaded.read())
            st.rerun()
        st.caption("Place sites.csv in app folder or upload above")
    else:
        n_cat = df_raw["category"].nunique() if "category" in df_raw.columns else "—"
        st.markdown(f"""
        <div style="padding:12px 14px;background:{T['ink3']};border:1px solid {T['lime']}28;
             border-radius:6px;margin-bottom:10px">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
            <div style="width:5px;height:5px;border-radius:50%;background:{T['lime']};
                 box-shadow:0 0 6px {T['lime']}"></div>
            <span style="font-family:'DM Mono',monospace;font-size:9px;color:{T['lime']};
                  letter-spacing:.14em;text-transform:uppercase">Active</span>
          </div>
          <div style="font-family:'DM Mono',monospace;font-size:11px;color:{T['chalk4']}">
            {len(df_raw):,} sites · {n_cat} categories</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Load different file", use_container_width=True):
            st.session_state.df = None
            st.session_state.chat_msgs = []
            st.rerun()

    st.markdown(f'<div class="divider"></div>', unsafe_allow_html=True)

    eyebrow("AI Key")
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    api_key_input = st.text_input("Groq API Key", type="password",
                                  placeholder="gsk_…", label_visibility="collapsed", value="")
    api_key = GROQ_API_KEY or api_key_input

    if api_key:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;padding:10px 12px;
             background:{T['ink3']};border:1px solid {T['lime']}28;border-radius:6px">
          <div style="width:5px;height:5px;border-radius:50%;background:{T['lime']};
               box-shadow:0 0 6px {T['lime']}"></div>
          <span style="font-family:'DM Mono',monospace;font-size:9px;color:{T['lime']};
                letter-spacing:.14em;text-transform:uppercase">AI Active</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.caption("Add GROQ_API_KEY=... in .env or paste above")

    st.markdown(f'<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-family:'DM Sans',sans-serif;font-size:11.5px;color:{T['chalk5']};
         line-height:1.8">
      Forensic privacy analysis<br>
      powered by WhoTracks.me data.<br><br>
      <span style="color:{T['chalk4']}">7 signals · 3 interaction terms<br>
      HTTP-level analysis only</span>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# GUARD
# ─────────────────────────────────────────────────────────────────────────────
df_raw = st.session_state.df
if df_raw is None:
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;align-items:center;
         justify-content:center;padding:100px 0;text-align:center">
      <div style="font-family:'DM Mono',monospace;font-size:9px;color:{T['chalk5']};
           letter-spacing:.25em;text-transform:uppercase;margin-bottom:20px">
        Privacy Intelligence Platform
      </div>
      <h1 style="font-family:'Fraunces',serif !important;font-size:52px;
           font-weight:300;letter-spacing:-.04em;color:{T['chalk']};
           margin:0 0 20px;line-height:1">
        Privacy<span style="color:{T['gold']}">Lens</span>
      </h1>
      <p style="font-size:14px;color:{T['chalk4']};max-width:380px;line-height:1.8;
           font-family:'DM Sans',sans-serif">
        Upload <code style="font-family:'DM Mono',monospace;color:{T['sky']};
        background:{T['ink3']};padding:2px 8px;border-radius:3px">sites.csv</code>
        via the sidebar to begin forensic privacy analysis.</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

df = df_raw

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — SCORE ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "Score Analyzer":

    # ── Page header
    st.markdown(f"""
    <div style="padding-bottom:20px;border-bottom:1px solid {T['line']};margin-bottom:24px">
      <div class="eyebrow" style="margin-bottom:8px">Score Analyzer</div>
      <h1 style="font-family:'Fraunces',serif !important;font-size:34px;font-weight:300;
           color:{T['chalk']} !important;letter-spacing:-.04em;margin:0 0 6px">
        Privacy Risk Analysis
      </h1>
      <p style="color:{T['chalk4']};font-size:13px;font-family:'DM Sans',sans-serif;margin:0">
        Forensic breakdown of every tracking signal — decoded without jargon
      </p>
    </div>""", unsafe_allow_html=True)

    # ── Filters
    f1, f2, f3 = st.columns([1, 2.4, 0.8])
    if "category" in df.columns:
        categories = ["All Categories"] + sorted(df["category"].dropna().unique().tolist())
    else:
        categories = ["All Categories"]

    with f1:
        eyebrow("Category")
        sel_cat = st.selectbox("cat", categories,
            format_func=lambda c: c if c=="All Categories" else f"{c}  ({len(df[df['category']==c]):,})",
            label_visibility="collapsed")

    filtered = df if sel_cat=="All Categories" else df[df["category"]==sel_cat]

    if "site" not in df.columns:
        st.error("Dataset missing required 'site' column.")
        st.stop()

    pop_col = "popularity" if "popularity" in df.columns else None
    if pop_col:
        site_list = filtered.sort_values("popularity", ascending=False)["site"].dropna().unique().tolist()
    else:
        site_list = filtered["site"].dropna().unique().tolist()

    if not site_list:
        st.warning("No sites found for the selected category.")
        st.stop()

    with f2:
        eyebrow("Website")
        default_idx = site_list.index("google.com") if "google.com" in site_list else 0
        sel_site = st.selectbox("site", site_list, index=default_idx, label_visibility="collapsed")

    with f3:
        try: rank = site_list.index(sel_site) + 1
        except: rank = 1
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.metric("Rank", f"#{rank:,}")

    if not sel_site: st.stop()

    matches = df[df["site"]==sel_site]
    if matches.empty:
        st.warning(f"'{sel_site}' not found.")
        st.stop()

    row   = matches.iloc[0]
    score = float(row["privacy_score"])
    label, color, bg = score_info(score)

    if st.session_state.last_site != sel_site:
        st.session_state.chat_msgs = []
        st.session_state.last_site = sel_site

    cat_val = safe_get(row,"category","—") if has_col(row,"category") else "—"
    pop_val = safe_get(row,"popularity",0.0)
    pop_str = f"{pop_val:.5f}" if pop_val > 0 else "—"

    # ── Site Header Banner
    percentile = int((df["privacy_score"] < score).mean() * 100)
    st.markdown(f"""
    <div style="padding:24px 28px;background:{T['ink2']};
         border:1px solid {T['line']};border-top:2px solid {color};
         border-radius:8px;margin:0 0 24px;
         display:flex;align-items:flex-start;justify-content:space-between;
         flex-wrap:wrap;gap:16px">
      <div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
          <h2 style="font-family:'Fraunces',serif !important;font-size:28px;
               font-weight:300;color:{T['chalk']} !important;
               letter-spacing:-.03em;margin:0">{sel_site}</h2>
          {score_badge(score, label, color)}
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:8px">
          {stat_pill("Category", str(cat_val))}
          {stat_pill("Popularity", pop_str)}
          {stat_pill("Riskier than", f"{percentile}% of sites", color)}
        </div>
      </div>
      <div style="text-align:right">
        <div class="eyebrow" style="margin-bottom:6px">Risk Score</div>
        <div style="font-family:'DM Mono',monospace;font-size:56px;font-weight:300;
             color:{color};line-height:1;letter-spacing:-.04em">{score:.0f}
          <span style="font-size:18px;color:{T['chalk5']};font-weight:400">/100</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Main layout
    left, right = st.columns([1, 1.9], gap="large")

    with left:
        # Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=score,
            number={"font":{"size":40,"color":color,"family":"DM Mono"},"suffix":""},
            domain={"x":[0,1],"y":[0,1]},
            gauge={
                "axis":{"range":[0,100],"tickwidth":0,"tickcolor":T["line2"],
                        "tickfont":{"color":T["chalk5"],"size":8}},
                "bar":{"color":color,"thickness":0.16},
                "bgcolor":T["ink3"],"borderwidth":0,
                "steps":[
                    {"range":[0,20],   "color":hex_rgba(T["lime"],  0.08)},
                    {"range":[20,40],  "color":hex_rgba(T["sky"],   0.08)},
                    {"range":[40,60],  "color":hex_rgba(T["amber"], 0.08)},
                    {"range":[60,80],  "color":hex_rgba(T["red"],   0.08)},
                    {"range":[80,100], "color":hex_rgba(T["rose"],  0.10)},
                ],
                "threshold":{"line":{"color":color,"width":1.5},"thickness":0.85,"value":score},
            }
        ))
        fig_gauge.update_layout(**{**PLOTLY_BASE,"height":240,"margin":dict(l=16,r=16,t=10,b=10)})
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar":False})

        # Category comparison
        if "category" in df.columns and has_col(row,"category"):
            cat_val_str = safe_get(row,"category","")
            if cat_val_str:
                cat_sub = df[df["category"]==cat_val_str]["privacy_score"]
                if len(cat_sub):
                    cat_mean = cat_sub.mean()
                    delta = score - cat_mean
                    delta_str = f"+{delta:.0f}" if delta >= 0 else f"{delta:.0f}"
                    delta_col = T["red"] if delta > 0 else T["lime"]
                    st.markdown(f"""
                    <div style="padding:14px 16px;background:{T['ink3']};
                         border:1px solid {T['line']};border-radius:6px;margin-bottom:14px">
                      <div class="eyebrow" style="margin-bottom:8px">vs. Category Average</div>
                      <div style="display:flex;align-items:baseline;gap:8px">
                        <span style="font-family:'DM Mono',monospace;font-size:22px;
                              color:{T['chalk']};font-weight:400">{cat_mean:.0f}</span>
                        <span style="font-family:'DM Mono',monospace;font-size:12px;
                              color:{T['chalk5']}">avg</span>
                        <span style="font-family:'DM Mono',monospace;font-size:13px;
                              color:{delta_col};margin-left:8px">{delta_str} pts</span>
                      </div>
                      <div style="font-size:11px;color:{T['chalk5']};margin-top:4px;
                           font-family:'DM Sans',sans-serif">in {cat_val_str}</div>
                    </div>""", unsafe_allow_html=True)

        # Quick stats
        eyebrow("Signal Snapshot")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        qa, qb = st.columns(2)
        qa.metric("Scripts",       f"{safe_get(row,'script'):.0%}")
        qb.metric("XHR Calls",     f"{safe_get(row,'xhr'):.0%}")
        qa.metric("Trackers",      f"{safe_get(row,'trackers',0.0):.1f}")
        qb.metric("Companies",     f"{safe_get(row,'companies',0.0):.1f}")
        qa.metric("Tracked",       f"{safe_get(row,'tracked'):.0%}")
        qb.metric("Cross-Cookies", f"{safe_get(row,'cookie_samesite_none'):.0%}")

    with right:
        tab_what, tab_how, tab_why, tab_xai = st.tabs([
            "WHAT THEY COLLECT",
            "HOW THEY DO IT",
            "WHY THEY DO IT",
            "SCORE BREAKDOWN",
        ])

        # ── TAB 1: WHAT
        with tab_what:
            st.markdown(f"""<p style="color:{T['chalk4']};font-size:12px;margin:14px 0 16px;
            font-family:'DM Sans',sans-serif;line-height:1.7">
            Data <b style="color:{T['chalk3']}">{sel_site}</b> likely collects from visitors.</p>""",
            unsafe_allow_html=True)

            items = []
            if safe_get(row,"tracked") > 0.2:
                items.append(("01","Identity Tracking",
                    f"Persistent unique ID across sessions. Active on {safe_get(row,'tracked'):.0%} of visits.",
                    T["red"]))
            if safe_get(row,"cookies",0.0) > 0.2:
                items.append(("02","Login & Preference Data",
                    f"Cookies storing identity and behavior. Detected on {safe_get(row,'cookies',0.0):.0%} of visits.",
                    T["amber"]))
            if safe_get(row,"cookie_samesite_none") > 0.15:
                items.append(("03","Cross-Site Activity",
                    f"Follows you to other websites. Active on {safe_get(row,'cookie_samesite_none'):.0%} of visits.",
                    T["red"]))
            if safe_get(row,"xhr") > 0.3:
                items.append(("04","Real-Time Behaviour",
                    f"Every click and scroll silently uploaded. Happens on {safe_get(row,'xhr'):.0%} of visits.",
                    T["amber"]))
            if safe_get(row,"referer_leaked") > 0.2:
                items.append(("05","Navigation History",
                    f"Previous URL shared with third parties. Leaked on {safe_get(row,'referer_leaked'):.0%} of visits.",
                    T["amber"]))
            if safe_get(row,"image") > 0.3:
                items.append(("06","Device Fingerprint",
                    f"Invisible pixel images record IP, browser, OS. Loaded on {safe_get(row,'image'):.0%} of visits.",
                    T["sky"]))
            if safe_get(row,"media",0.0) > 0.05:
                items.append(("07","Media Consumption",
                    f"What you watch and for how long. Active on {safe_get(row,'media',0.0):.0%} of visits.",
                    T["sky"]))
            if safe_get(row,"bad_qs",0.0) > 0.05:
                items.append(("08","URL Fingerprinting",
                    f"Unique query codes identify you cookieless. Used on {safe_get(row,'bad_qs',0.0):.0%} of visits.",
                    T["sky"]))

            if not items:
                st.success(f"✓  {sel_site} shows minimal data collection.")
            else:
                html = ""
                for num, title, desc, cl in items:
                    html += f"""
                    <div style="display:flex;gap:16px;padding:14px 0;
                         border-bottom:1px solid {T['line']};align-items:flex-start">
                      <div style="font-family:'DM Mono',monospace;font-size:9px;
                           color:{T['chalk5']};padding-top:3px;flex-shrink:0;
                           letter-spacing:.08em">{num}</div>
                      <div>
                        <div style="font-size:13px;font-weight:600;color:{T['chalk2']};
                             font-family:'DM Sans',sans-serif;margin-bottom:4px;
                             display:flex;align-items:center;gap:8px">
                          {title}
                          <span style="display:inline-block;width:5px;height:5px;
                                border-radius:50%;background:{cl};flex-shrink:0"></span>
                        </div>
                        <div style="font-size:12px;color:{T['chalk4']};
                             font-family:'DM Sans',sans-serif;line-height:1.6">{desc}</div>
                      </div>
                    </div>"""
                st.markdown(html, unsafe_allow_html=True)

        # ── TAB 2: HOW
        with tab_how:
            st.markdown(f"""<p style="color:{T['chalk4']};font-size:12px;margin:14px 0 4px;
            font-family:'DM Sans',sans-serif">Technical methods — bar = frequency of deployment.</p>""",
            unsafe_allow_html=True)

            signals = [
                ("script",               "JavaScript Execution",      "Runs in your browser — can intercept keystrokes, form data, mouse movements"),
                ("xhr",                  "Background Data Requests",   "Silently uploads data while you browse — invisible to users"),
                ("sgeo",                 "Combined Tracking Signal",   "Script × XHR combined — primary composite indicator of active tracking"),
                ("iframe",               "Embedded Hidden Frames",     "Invisible sub-pages running their own independent tracking logic"),
                ("cookie_samesite_none", "Cross-Site Cookie Drops",    "Cookies that operate across all websites, not just this domain"),
                ("beacon",               "Beacon Pings",               "Fires even after tab close — confirms page completion, ad views"),
                ("image",                "Tracking Pixels",            "1×1 invisible images that record your IP address and browser environment"),
                ("referer_leaked",       "Referrer Header Leaking",    "Your previous URL shared with third-party domains on this page"),
                ("bad_qs",               "URL-based Fingerprinting",   "Query string parameters that identify you without any cookies"),
                ("media",                "Media Interaction Tracking", "Video/audio play events, duration, and completion rates logged"),
            ]
            html = ""
            for col_key, lbl, expl in signals:
                val = safe_get(row, col_key)
                html += signal_bar(lbl, val, expl)
            st.markdown(html, unsafe_allow_html=True)

        # ── TAB 3: PURPOSE
        with tab_why:
            st.markdown(f"""<p style="color:{T['chalk4']};font-size:12px;margin:14px 0 16px;
            font-family:'DM Sans',sans-serif">What this data is used for — no euphemisms.</p>""",
            unsafe_allow_html=True)

            uses = []
            if safe_get(row,"sgeo") > 0.5:
                uses.append(("Behavioural Profile Construction",
                    "Every interaction is logged to build a psychographic model predicting interests, income, and intent.",
                    T["red"], "HIGH CONCERN"))
            if safe_get(row,"cookie_samesite_none") > 0.2:
                uses.append(("Cross-Internet Surveillance",
                    "Identity shared with ad networks to serve targeted ads across every website you visit.",
                    T["red"], "HIGH CONCERN"))
            if safe_get(row,"cookies",0.0) > 0.3 or safe_get(row,"tracked") > 0.3:
                uses.append(("Real-Time Bidding Auction",
                    "Your profile is auctioned in under 100ms to advertisers before the page loads.",
                    T["amber"], "MODERATE"))
            if safe_get(row,"referer_leaked") > 0.3:
                uses.append(("Browsing History Inference",
                    "Your navigation path is sold to data brokers who infer health, politics, and finances.",
                    T["amber"], "MODERATE"))
            if safe_get(row,"beacon") > 0.1:
                uses.append(("Ad Effectiveness Attribution",
                    "Beacon pings confirm ad exposure, conversion, and return visits for advertiser billing.",
                    T["sky"], "LOW CONCERN"))
            if safe_get(row,"media",0.0) > 0.05:
                uses.append(("Content Engagement Optimisation",
                    "Watch time and completion signals feed recommendation algorithms to maximize engagement.",
                    T["sky"], "LOW CONCERN"))
            if not uses:
                uses.append(("Minimal Data Utilisation Detected",
                    "Tracking signals are low. This site likely collects only operationally necessary data.",
                    T["lime"], "COMPLIANT"))

            html = ""
            for title, desc, cl, severity in uses:
                html += f"""
                <div style="padding:16px 18px;background:{T['ink3']};
                     border:1px solid {T['line']};border-left:2px solid {cl};
                     border-radius:0 6px 6px 0;margin-bottom:10px">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;
                       margin-bottom:8px">
                    <div style="font-size:13px;font-weight:600;color:{T['chalk2']};
                         font-family:'DM Sans',sans-serif">{title}</div>
                    <span style="font-family:'DM Mono',monospace;font-size:8.5px;color:{cl};
                          letter-spacing:.12em;padding:3px 8px;border:1px solid {cl}30;
                          border-radius:2px;flex-shrink:0;margin-left:12px">{severity}</span>
                  </div>
                  <div style="font-size:12px;color:{T['chalk4']};
                       font-family:'DM Sans',sans-serif;line-height:1.65">{desc}</div>
                </div>"""
            st.markdown(html, unsafe_allow_html=True)

        # ── TAB 4: XAI
        with tab_xai:
            st.markdown(f"""<p style="color:{T['chalk4']};font-size:12px;margin:14px 0 10px;
            font-family:'DM Sans',sans-serif">
            Signal contributions to final score of
            <span style="font-family:'DM Mono',monospace;color:{color}">{score:.0f}/100</span>.</p>""",
            unsafe_allow_html=True)

            contributions = {}
            for sig, w in W.items():
                val = safe_get(row, sig)
                contributions[sig] = round(val * w / TW * 100, 2)

            total_contrib = sum(contributions.values())
            max_contrib   = max(contributions.values()) if contributions else 1.0
            sorted_c = sorted(contributions.items(), key=lambda x: -x[1])

            contrib_vals = [c for _, c in sorted_c]
            max_cv = max(contrib_vals) if contrib_vals else 1.0
            bar_colors = [risk_color(c/max_cv if max_cv > 0 else 0) for c in contrib_vals]

            sig_labels = {
                "sgeo":"Core Signal (√JS × XHR)","it2":"Session Signal (JS × XHR)",
                "referer_leaked":"Referrer Leaked","it3":"Iframe Combo",
                "it1":"Cookie + Signal Combo","cookie_samesite_none":"Cross-Site Cookies",
                "iframe":"Hidden Iframes","beacon":"Beacon Pings",
            }

            fig_bar = go.Figure(go.Bar(
                x=contrib_vals,
                y=[sig_labels.get(s,s) for s,_ in sorted_c],
                orientation="h",
                marker=dict(color=bar_colors, line=dict(color=RGBA0), opacity=0.85),
                text=[f"+{c:.1f}" for c in contrib_vals],
                textposition="outside",
                textfont=dict(color=T["chalk4"],size=10,family="DM Mono"),
            ))
            fig_bar.update_layout(**{**PLOTLY_BASE,
                "height":290,
                "xaxis":dict(title="Points contributed",gridcolor=T["line"],
                             zeroline=False,tickfont=dict(size=9)),
                "yaxis":dict(autorange="reversed",gridcolor=RGBA0,tickfont=dict(size=10)),
                "margin":dict(l=8,r=60,t=10,b=26),
            })
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar":False})

            eyebrow("Detailed Breakdown")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            html = f"""
            <div style="background:{T['ink2']};border:1px solid {T['line']};border-radius:6px;
                 overflow:hidden;font-family:'DM Mono',monospace">
              <div style="display:grid;grid-template-columns:2fr .6fr .6fr .6fr;
                   padding:10px 16px;border-bottom:1px solid {T['line2']};
                   font-size:8.5px;color:{T['chalk5']};text-transform:uppercase;
                   letter-spacing:.14em;background:{T['ink3']}">
                <span>Signal</span><span>Value</span><span>Weight</span><span>Points</span>
              </div>"""
            for i, (sig, contrib) in enumerate(sorted_c):
                val = safe_get(row, sig)
                w   = W.get(sig, 0)
                cl  = risk_color(contrib/max_contrib if max_contrib > 0 else 0)
                rb  = T["ink3"]+"60" if i%2==0 else RGBA0
                html += f"""
              <div style="display:grid;grid-template-columns:2fr .6fr .6fr .6fr;
                   padding:9px 16px;border-bottom:1px solid {T['line']}18;background:{rb}">
                <span style="font-size:11.5px;color:{T['chalk3']}">{sig_labels.get(sig,sig)}</span>
                <span style="font-size:11px;color:{T['chalk4']}">{val:.3f}</span>
                <span style="font-size:11px;color:{T['chalk5']}">×{w:.2f}</span>
                <span style="font-size:12px;font-weight:500;color:{cl}">+{contrib:.1f}</span>
              </div>"""
            html += f"""
              <div style="display:grid;grid-template-columns:2fr .6fr .6fr .6fr;
                   padding:12px 16px;border-top:1px solid {T['line2']};
                   background:{T['ink4']}">
                <span style="font-size:12px;font-weight:500;color:{T['chalk2']};
                      letter-spacing:.04em">TOTAL</span>
                <span></span><span></span>
                <span style="font-size:14px;font-weight:500;color:{color}">{total_contrib:.0f}</span>
              </div></div>"""
            st.markdown(html, unsafe_allow_html=True)

    divider()

    # ── Protection tips
    if score > 30:
        section_title("Protective Measures", "Tools to reduce your exposure on this site")
        tips_cols = st.columns(3)
        tips = []
        if safe_get(row,"script") > 0.5:
            tips.append(("uBlock Origin","Blocks tracking scripts before execution. Most effective free privacy tool.",
                         "https://ublockorigin.com",T["lime"]))
        if safe_get(row,"cookie_samesite_none") > 0.2:
            tips.append(("Firefox + TCP","Total Cookie Protection isolates cookies per site — stops cross-site tracking completely.",
                         "https://www.mozilla.org/firefox",T["sky"]))
        if safe_get(row,"iframe") > 0.3:
            tips.append(("Privacy Badger","Learns and blocks invisible trackers automatically as you browse new sites.",
                         "https://privacybadger.org",T["amber"]))
        if safe_get(row,"referer_leaked") > 0.2:
            tips.append(("Brave Browser","Strips referrer headers and blocks fingerprinting by default.",
                         "https://brave.com",T["gold"]))
        if safe_get(row,"beacon") > 0.1:
            tips.append(("uBlock Strict Mode","Intercepts beacon and ping requests at the network request level.",
                         "https://ublockorigin.com",T["red"]))
        if not tips:
            tips.append(("Privacy Browser","Start with Brave or Firefox Enhanced Tracking Protection.",
                         "https://brave.com",T["sky"]))

        for i, (tool, desc, url, tc) in enumerate(tips[:3]):
            with tips_cols[i%3]:
                st.markdown(f"""
                <a href="{url}" target="_blank" style="text-decoration:none;display:block">
                <div style="padding:18px 18px;background:{T['ink2']};
                     border:1px solid {T['line']};border-top:2px solid {tc};
                     border-radius:0 0 6px 6px;transition:.15s">
                  <div style="font-size:13.5px;font-weight:600;color:{T['chalk2']};
                       font-family:'DM Sans',sans-serif;margin-bottom:8px">{tool}</div>
                  <div style="font-size:11.5px;color:{T['chalk4']};
                       font-family:'DM Sans',sans-serif;line-height:1.65;
                       margin-bottom:14px">{desc}</div>
                  <div style="font-family:'DM Mono',monospace;font-size:9px;
                       color:{tc};letter-spacing:.12em;text-transform:uppercase">
                    Visit →</div>
                </div></a>""", unsafe_allow_html=True)

    divider()

    # ── Raw data expander
    with st.expander("Raw Signal Values"):
        raw_cols = ["script","xhr","sgeo","iframe","cookie_samesite_none","referer_leaked",
                    "beacon","image","tracked","it1","it2","it3","privacy_score",
                    "trackers","companies","requests","requests_tracking"]
        raw = {c:[round(safe_get(row,c),4)] for c in raw_cols if c in row.index}
        if raw:
            st.dataframe(pd.DataFrame(raw), use_container_width=True)
        else:
            st.caption("No raw data available.")

    divider()

    # ── Chatbot
    section_title("AI Privacy Assistant", f"Ask anything about {sel_site}")

    lang_col, _ = st.columns([1,3])
    with lang_col:
        eyebrow("Response Language")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        chosen_lang = st.selectbox("lang", list(LANGUAGES.keys()),
                                   index=list(LANGUAGES.keys()).index(st.session_state.chat_lang),
                                   label_visibility="collapsed")
        st.session_state.chat_lang = chosen_lang

    groq_key = api_key
    cat_for_prompt = safe_get(row,"category","—") if has_col(row,"category") else "—"

    system_prompt = f"""You are PrivacyLens AI — expert privacy analyst.
Analysing: {sel_site}

DATA:
  Score     : {score:.1f}/100 — {label}
  Category  : {cat_for_prompt}
  Scripts   : {safe_get(row,'script'):.1%}
  XHR       : {safe_get(row,'xhr'):.1%}
  Core sig  : {safe_get(row,'sgeo'):.1%}
  Cross-cook: {safe_get(row,'cookie_samesite_none'):.1%}
  Iframes   : {safe_get(row,'iframe'):.1%}
  Referrer  : {safe_get(row,'referer_leaked'):.1%}
  Beacons   : {safe_get(row,'beacon'):.1%}
  Pixels    : {safe_get(row,'image'):.1%}
  Trackers  : {safe_get(row,'trackers',0.0):.1f}
  Companies : {safe_get(row,'companies',0.0):.1f}

Reply in {chosen_lang}. Be concise. Use bullets for lists. Plain language only."""

    if not groq_key:
        st.markdown(f"""
        <div style="padding:20px 24px;background:{T['ink3']};border:1px solid {T['line2']};
             border-radius:6px;text-align:center">
          <div style="font-family:'DM Mono',monospace;font-size:11px;color:{T['chalk4']};
               line-height:2">
            Add <code style="color:{T['sky']};background:{T['ink4']};padding:2px 8px;
            border-radius:3px">GROQ_API_KEY=gsk_...</code> to your
            <code style="color:{T['sky']};background:{T['ink4']};padding:2px 8px;
            border-radius:3px">.env</code> to enable the AI assistant.
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        if not st.session_state.chat_msgs:
            eyebrow("Quick Prompts")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            qc = st.columns(3)
            quick = [
                f"What is the biggest risk on {sel_site}?",
                f"Is {sel_site} safe to use?",
                f"How do I protect myself on {sel_site}?",
            ]
            for i, (col, prompt) in enumerate(zip(qc, quick)):
                with col:
                    if st.button(prompt, key=f"qp_{sel_site}_{i}", use_container_width=True):
                        st.session_state.chat_msgs.append({"role":"user","content":prompt})
                        with st.spinner("Analysing…"):
                            reply = call_groq(st.session_state.chat_msgs, system_prompt, groq_key)
                        st.session_state.chat_msgs.append({"role":"assistant","content":reply})
                        st.rerun()

        for msg in st.session_state.chat_msgs:
            with st.chat_message(msg["role"], avatar="🧑" if msg["role"]=="user" else "🔍"):
                st.markdown(msg["content"])

        if user_input := st.chat_input(f"Ask about {sel_site}…"):
            st.session_state.chat_msgs.append({"role":"user","content":user_input})
            with st.chat_message("user", avatar="🧑"):
                st.markdown(user_input)
            with st.chat_message("assistant", avatar="🔍"):
                with st.spinner("Analysing…"):
                    reply = call_groq(st.session_state.chat_msgs, system_prompt, groq_key)
                st.markdown(reply)
            st.session_state.chat_msgs.append({"role":"assistant","content":reply})
            st.rerun()

        if st.session_state.chat_msgs:
            if st.button("Clear conversation"):
                st.session_state.chat_msgs = []
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — ANALYTICS DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
else:
    dfw = add_tier_col(df)
    n_cat = dfw["category"].nunique() if "category" in dfw.columns else "—"

    st.markdown(f"""
    <div style="padding-bottom:20px;border-bottom:1px solid {T['line']};margin-bottom:24px">
      <div class="eyebrow" style="margin-bottom:8px">Intelligence Platform</div>
      <h1 style="font-family:'Fraunces',serif !important;font-size:34px;font-weight:300;
           color:{T['chalk']} !important;letter-spacing:-.04em;margin:0 0 6px">
        Analytics Dashboard
      </h1>
      <p style="color:{T['chalk4']};font-size:13px;font-family:'DM Sans',sans-serif;margin:0">
        {len(dfw):,} websites · {n_cat} categories · full visual intelligence
      </p>
    </div>""", unsafe_allow_html=True)

    # ── KPI Strip
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Sites",    f"{len(dfw):,}")
    k2.metric("Avg Risk Score", f"{dfw['privacy_score'].mean():.1f}")
    k3.metric("High Risk",      f"{(dfw['privacy_score']>60).sum():,}")
    k4.metric("Private",        f"{(dfw['privacy_score']<20).sum():,}")
    k5.metric("Avg Trackers",   f"{dfw['trackers'].mean():.1f}" if "trackers" in dfw.columns else "—")
    k6.metric("Avg Companies",  f"{dfw['companies'].mean():.1f}" if "companies" in dfw.columns else "—")

    divider()

    cat_avg = pd.Series(dtype=float)
    if "category" in dfw.columns:
        cat_avg = dfw.groupby("category")["privacy_score"].mean().sort_values(ascending=False)

    SIGNAL_LABELS = {
        "script":"JS Scripts","xhr":"XHR Calls","iframe":"Iframes",
        "cookie_samesite_none":"Cross-Site Cookies","beacon":"Beacons",
        "referer_leaked":"Ref Leaked","image":"Pixels","tracked":"Tracked",
        "cookies":"Cookies","bad_qs":"URL Fingerprint","media":"Media","sgeo":"Core Signal",
    }

    def sec(text, sub=""):
        s2 = f'<div style="font-size:12px;color:{T["chalk5"]};margin-top:3px;font-family:\'DM Sans\',sans-serif">{sub}</div>' if sub else ""
        st.markdown(f"""
        <div style="margin:1.8rem 0 1.2rem;display:flex;align-items:baseline;gap:10px">
          <span style="font-family:'DM Mono',monospace;font-size:9px;color:{T['chalk5']};
                letter-spacing:.2em">◈</span>
          <div>
            <span style="font-family:'Fraunces',serif;font-size:18px;font-weight:300;
                  color:{T['chalk2']};letter-spacing:-.02em">{text}</span>{s2}
          </div>
          <div style="flex:1;height:1px;background:{T['line']};margin-left:8px;margin-bottom:2px"></div>
        </div>""", unsafe_allow_html=True)

    # ── A: Score Overview
    sec("Score Overview")
    ra1, ra2, ra3 = st.columns(3)

    with ra1:
        fig = px.histogram(dfw, x="privacy_score", nbins=30, title="Score Distribution",
                           color_discrete_sequence=[T["sky"]])
        fig.update_layout(**PLOTLY_BASE, height=260)
        fig.update_traces(marker_line_color=T["ink0"], marker_line_width=0.3, marker_opacity=0.8)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with ra2:
        tier_counts = dfw["tier"].value_counts().reindex(TIER_ORDER).fillna(0)
        fig = go.Figure(go.Pie(
            labels=tier_counts.index.tolist(),
            values=tier_counts.values.tolist(),
            marker_colors=[TIER_COLORS[t] for t in tier_counts.index],
            hole=0.65, textinfo="label+percent",
            textfont_size=9, textfont_color=T["chalk3"],
        ))
        fig.update_layout(**{**PLOTLY_BASE,"title":{"text":"Risk Tiers","font":{"size":11}},
            "height":260,"showlegend":False,
            "annotations":[dict(text=f"{len(dfw):,}",font_size=14,showarrow=False,
                               font_color=T["chalk3"],font_family="DM Mono")],
        })
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with ra3:
        fig = go.Figure()
        for t in TIER_ORDER:
            sub = dfw[dfw["tier"]==t]["privacy_score"]
            if len(sub):
                fig.add_trace(go.Box(y=sub, name=t,
                    marker_color=TIER_COLORS[t], line_color=TIER_COLORS[t],
                    fillcolor=hex_rgba(TIER_COLORS[t], 0.08), line_width=1.2))
        fig.update_layout(**{**PLOTLY_BASE,"title":{"text":"Score by Tier","font":{"size":11}},
            "height":260,"showlegend":False,
            "xaxis":dict(gridcolor=T["line"],tickfont_size=9),
            "yaxis":dict(gridcolor=T["line"]),
        })
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # ── B: Category Analysis
    if "category" in dfw.columns and len(cat_avg):
        sec("Category Analysis")
        rb1, rb2 = st.columns(2)

        with rb1:
            colors_cat = [TIER_COLORS.get(
                "Private" if v<20 else "Low Risk" if v<40 else
                "Moderate" if v<60 else "High Risk" if v<80 else "Critical", T["red"])
                for v in cat_avg.values]
            fig = go.Figure(go.Bar(
                x=cat_avg.values, y=cat_avg.index, orientation="h",
                marker_color=colors_cat, marker_line_color=T["ink0"],
                marker_line_width=0.3, marker_opacity=0.85,
                text=[f"{v:.1f}" for v in cat_avg.values],
                textposition="outside",
                textfont=dict(color=T["chalk4"],size=9,family="DM Mono"),
            ))
            fig.update_layout(**{**PLOTLY_BASE,
                "title":{"text":"Avg Risk by Category","font":{"size":11}},
                "height":320,"xaxis":dict(gridcolor=T["line"]),
                "yaxis":dict(autorange="reversed",gridcolor=RGBA0),
            })
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        with rb2:
            fig = px.box(dfw, x="category", y="privacy_score",
                         title="Score Distribution by Category",
                         color="category",
                         color_discrete_sequence=[T["sky"],T["lime"],T["gold"],T["amber"],
                             T["red"],T["rose"],T["chalk4"],"#34d399","#fb7185","#38bdf8"])
            fig.update_layout(**{**PLOTLY_BASE,"height":320,"showlegend":False,
                "xaxis":dict(tickangle=-30,gridcolor=T["line"],tickfont_size=9),
                "yaxis":dict(gridcolor=T["line"]),
            })
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        rb3, rb4 = st.columns(2)
        with rb3:
            cat_cnt = dfw["category"].value_counts()
            palette = [T["sky"],T["lime"],T["gold"],T["amber"],T["red"],
                       T["rose"],T["chalk4"],"#34d399","#fb7185","#38bdf8"]
            fig = go.Figure(go.Bar(
                x=cat_cnt.index.tolist(), y=cat_cnt.values.tolist(),
                marker_color=palette[:len(cat_cnt)], marker_opacity=0.85,
                text=cat_cnt.values.tolist(), textposition="outside",
                textfont=dict(color=T["chalk4"],size=9),
            ))
            fig.update_layout(**{**PLOTLY_BASE,
                "title":{"text":"Sites per Category","font":{"size":11}},
                "height":270,"xaxis":dict(tickangle=-30,gridcolor=RGBA0,tickfont_size=9),
                "yaxis":dict(gridcolor=T["line"]),
            })
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        with rb4:
            top_cats = cat_avg.head(5).index.tolist()
            radar_signals = [s for s in ["script","xhr","cookie_samesite_none","beacon","iframe","referer_leaked"] if s in dfw.columns]
            fig = go.Figure()
            colors_r = [T["red"],T["amber"],T["gold"],T["lime"],T["sky"]]
            for cat, cr in zip(top_cats, colors_r):
                sub  = dfw[dfw["category"]==cat]
                vals = [sub[s].mean() for s in radar_signals]
                theta = radar_signals + [radar_signals[0]]
                r     = vals + [vals[0]]
                fig.add_trace(go.Scatterpolar(r=r, theta=theta, fill="toself", name=cat,
                    fillcolor=hex_rgba(cr, 0.08),
                    line=dict(color=cr, width=1.5)))
            fig.update_layout(**{**PLOTLY_BASE,
                "title":{"text":"Signal Radar — Top 5 Riskiest Categories","font":{"size":11}},
                "height":270,
                "polar":dict(bgcolor=RGBA0,
                    radialaxis=dict(visible=True,range=[0,1],gridcolor=T["line"],
                                   tickfont=dict(size=7,color=T["chalk5"])),
                    angularaxis=dict(gridcolor=T["line"],tickfont=dict(size=9,color=T["chalk4"]))),
            })
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # ── C: Signal Deep-Dives
    sec("Signal Deep-Dives")
    corr_cols = [c for c in ["script","xhr","sgeo","iframe","cookie_samesite_none",
                              "referer_leaked","beacon","image","tracked","cookies",
                              "bad_qs","privacy_score"] if c in dfw.columns]
    if len(corr_cols) > 1:
        corr_m = dfw[corr_cols].corr().round(2)
        labels = [SIGNAL_LABELS.get(c,c) for c in corr_cols]
        fig_hm = go.Figure(go.Heatmap(
            z=corr_m.values, x=labels, y=labels,
            colorscale=[[0,hex_rgba(T["lime"],0.6)],[0.5,hex_rgba(T["amber"],0.5)],[1,hex_rgba(T["red"],0.7)]],
            zmin=-1, zmax=1,
            text=corr_m.values.round(2), texttemplate="%{text}", textfont_size=9,
        ))
        fig_hm.update_layout(**{**PLOTLY_BASE,
            "title":{"text":"Signal Correlation Matrix","font":{"size":11}},
            "height":420,"xaxis":dict(tickangle=-40,tickfont_size=8),
            "yaxis":dict(tickfont_size=8,autorange="reversed"),
            "margin":dict(l=100,r=10,t=38,b=90),
        })
        st.plotly_chart(fig_hm, use_container_width=True, config={"displayModeBar":False})

    rc_cols = st.columns(3)
    hist_specs = [
        ("script","JS Script Intensity",T["sky"]),
        ("xhr","XHR Background Calls",T["lime"]),
        ("beacon","Beacon Pings",T["red"]),
        ("cookie_samesite_none","Cross-Site Cookies",T["amber"]),
        ("iframe","Hidden Iframes",T["gold"]),
        ("referer_leaked","Referrer Leaking",T["rose"]),
    ]
    for i, (col_key, title, clr) in enumerate(hist_specs):
        if col_key in dfw.columns:
            fig = px.histogram(dfw, x=col_key, nbins=25, title=title,
                               color_discrete_sequence=[clr])
            fig.update_layout(**{**PLOTLY_BASE,"height":230,
                "xaxis":dict(gridcolor=T["line"]),
                "yaxis":dict(gridcolor=T["line"])})
            fig.update_traces(marker_opacity=0.8)
            with rc_cols[i%3]:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # ── D: Scatter
    sec("Signal Relationships")
    rd1, rd2 = st.columns(2)
    with rd1:
        if "script" in dfw.columns and "xhr" in dfw.columns:
            sc_cols = ["script","xhr","privacy_score","site"]
            if "category" in dfw.columns: sc_cols.append("category")
            samp = safe_sample(dfw[sc_cols].dropna(subset=["script","xhr"]))
            fig = px.scatter(samp, x="script", y="xhr", color="privacy_score",
                color_continuous_scale=[[0,T["lime"]],[0.4,T["sky"]],[0.7,T["amber"]],[1,T["red"]]],
                title="Script vs XHR (coloured by risk)", opacity=0.5,
                hover_data={"site":True,"privacy_score":True})
            fig.update_layout(**{**PLOTLY_BASE,"height":290,
                "xaxis":dict(gridcolor=T["line"]),
                "yaxis":dict(gridcolor=T["line"]),
                "coloraxis_colorbar":dict(title="Score",tickfont_color=T["chalk4"])})
            fig.update_traces(marker_size=3.5)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with rd2:
        if "trackers" in dfw.columns and "companies" in dfw.columns:
            tc_cols = ["trackers","companies","site"]
            if "category" in dfw.columns: tc_cols.append("category")
            samp = safe_sample(dfw[tc_cols].dropna(subset=["trackers","companies"]))
            fig = px.scatter(samp, x="trackers", y="companies",
                color="category" if "category" in samp.columns else None,
                title="Trackers vs Companies", opacity=0.5,
                hover_data={"site":True})
            fig.update_layout(**{**PLOTLY_BASE,"height":290,
                "xaxis":dict(gridcolor=T["line"]),
                "yaxis":dict(gridcolor=T["line"])})
            fig.update_traces(marker_size=3.5)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    rd3, rd4 = st.columns(2)
    with rd3:
        if "popularity" in dfw.columns:
            pop_df = dfw[dfw["popularity"]>0].copy()
            if len(pop_df):
                pop_cols = ["popularity","privacy_score","site"]
                if "category" in pop_df.columns: pop_cols.append("category")
                samp = safe_sample(pop_df[pop_cols])
                fig = px.scatter(samp, x="popularity", y="privacy_score",
                    color="category" if "category" in samp.columns else None,
                    log_x=True, title="Popularity vs Privacy Score",
                    opacity=0.55, hover_data={"site":True})
                fig.update_layout(**{**PLOTLY_BASE,"height":270,
                    "xaxis":dict(gridcolor=T["line"],title="Popularity (log)"),
                    "yaxis":dict(gridcolor=T["line"],title="Risk Score")})
                fig.update_traces(marker_size=3.5)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with rd4:
        if "requests" in dfw.columns and "requests_tracking" in dfw.columns:
            req_df = dfw[dfw["requests"]<500].copy()
            if len(req_df):
                samp = safe_sample(req_df[["requests","requests_tracking","privacy_score","site"]])
                fig = px.scatter(samp, x="requests", y="requests_tracking",
                    color="privacy_score",
                    color_continuous_scale=[[0,T["lime"]],[0.5,T["amber"]],[1,T["red"]]],
                    title="Total vs Tracking Requests", opacity=0.5, hover_data={"site":True})
                fig.update_layout(**{**PLOTLY_BASE,"height":270,
                    "xaxis":dict(gridcolor=T["line"]),
                    "yaxis":dict(gridcolor=T["line"])})
                fig.update_traces(marker_size=3.5)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # ── E: Tracker Analysis
    sec("Tracker & Company Analysis")
    re1, re2, re3 = st.columns(3)
    with re1:
        if "trackers" in dfw.columns:
            fig = px.histogram(dfw, x="trackers", nbins=30, title="Trackers per Site",
                               color_discrete_sequence=[T["sky"]])
            fig.update_layout(**{**PLOTLY_BASE,"height":230,
                "xaxis":dict(gridcolor=T["line"]), "yaxis":dict(gridcolor=T["line"])})
            fig.update_traces(marker_opacity=0.8)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with re2:
        if "companies" in dfw.columns:
            fig = px.histogram(dfw, x="companies", nbins=30, title="Companies per Site",
                               color_discrete_sequence=[T["lime"]])
            fig.update_layout(**{**PLOTLY_BASE,"height":230,
                "xaxis":dict(gridcolor=T["line"]), "yaxis":dict(gridcolor=T["line"])})
            fig.update_traces(marker_opacity=0.8)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with re3:
        if "category" in dfw.columns and "trackers" in dfw.columns:
            cat_track = dfw.groupby("category")["trackers"].mean().sort_values(ascending=False)
            fig = go.Figure(go.Bar(
                x=cat_track.index.tolist(), y=cat_track.values.tolist(),
                marker_color=T["sky"], marker_opacity=0.85,
                text=cat_track.values.round(1).tolist(), textposition="outside",
                textfont=dict(color=T["chalk4"],size=9),
            ))
            fig.update_layout(**{**PLOTLY_BASE,
                "title":{"text":"Avg Trackers by Category","font":{"size":11}},
                "height":230,"xaxis":dict(tickangle=-30,gridcolor=RGBA0,tickfont_size=9),
                "yaxis":dict(gridcolor=T["line"]),
            })
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # ── F: Heatmap
    if "category" in dfw.columns:
        sec("Category × Signal Heatmap")
        sig_cols_heat = [c for c in ["script","xhr","cookie_samesite_none","beacon",
                          "iframe","referer_leaked","image","tracked","cookies","bad_qs"]
                         if c in dfw.columns]
        if sig_cols_heat:
            heat_df = dfw.groupby("category")[sig_cols_heat].mean().round(3)
            fig_h2 = go.Figure(go.Heatmap(
                z=heat_df.values,
                x=[SIGNAL_LABELS.get(c,c) for c in sig_cols_heat],
                y=heat_df.index.tolist(),
                colorscale=[[0,hex_rgba(T["lime"],0.7)],[0.4,hex_rgba(T["amber"],0.6)],
                            [0.7,hex_rgba(T["red"],0.7)],[1,hex_rgba(T["rose"],0.8)]],
                text=heat_df.values.round(2), texttemplate="%{text}", textfont_size=9,
                colorbar=dict(title="Avg",tickfont_color=T["chalk4"]),
            ))
            fig_h2.update_layout(**{**PLOTLY_BASE,
                "title":{"text":"Avg Signal Intensity — Category × Technique","font":{"size":11}},
                "height":340,"xaxis":dict(tickangle=-30,tickfont_size=9),
                "yaxis":dict(tickfont_size=9),
                "margin":dict(l=110,r=70,t=38,b=90),
            })
            st.plotly_chart(fig_h2, use_container_width=True, config={"displayModeBar":False})

    # ── G: Rankings
    sec("Rankings & Extremes")
    rg1, rg2 = st.columns(2)

    def tier_clr(v):
        if v<20: return T["lime"]
        if v<40: return T["sky"]
        if v<60: return T["amber"]
        if v<80: return T["red"]
        return T["rose"]

    with rg1:
        rank_cols = ["site","privacy_score"]
        if "category" in dfw.columns: rank_cols.append("category")
        top20 = dfw.nlargest(20,"privacy_score")[rank_cols]
        fig = go.Figure(go.Bar(
            x=top20["privacy_score"].tolist(), y=top20["site"].tolist(), orientation="h",
            marker_color=[tier_clr(v) for v in top20["privacy_score"]],
            marker_opacity=0.85,
            text=top20["privacy_score"].round(1).tolist(), textposition="outside",
            textfont=dict(color=T["chalk4"],size=9,family="DM Mono"),
            hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>",
        ))
        fig.update_layout(**{**PLOTLY_BASE,
            "title":{"text":"Top 20 Highest Risk Sites","font":{"size":11}},
            "height":490,"xaxis":dict(range=[0,108],gridcolor=T["line"]),
            "yaxis":dict(autorange="reversed",tickfont_size=9,gridcolor=RGBA0),
        })
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with rg2:
        bot20 = dfw.nsmallest(20,"privacy_score")[["site","privacy_score"]]
        fig = go.Figure(go.Bar(
            x=bot20["privacy_score"].tolist(), y=bot20["site"].tolist(), orientation="h",
            marker_color=T["lime"], marker_opacity=0.85,
            text=bot20["privacy_score"].round(1).tolist(), textposition="outside",
            textfont=dict(color=T["chalk4"],size=9,family="DM Mono"),
        ))
        fig.update_layout(**{**PLOTLY_BASE,
            "title":{"text":"Top 20 Most Private Sites","font":{"size":11}},
            "height":490,"xaxis":dict(range=[0,30],gridcolor=T["line"]),
            "yaxis":dict(autorange="reversed",tickfont_size=9,gridcolor=RGBA0),
        })
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # ── H: Network
    sec("Network Request Analysis")
    rh1, rh2, rh3 = st.columns(3)
    with rh1:
        if "track_ratio" in dfw.columns:
            plot_data = dfw[dfw["requests"]>0]
            if len(plot_data):
                fig = px.histogram(plot_data, x="track_ratio", nbins=30,
                                   title="Tracking Request Ratio",
                                   color_discrete_sequence=[T["amber"]])
                fig.update_layout(**{**PLOTLY_BASE,"height":240,
                    "xaxis":dict(tickformat=".0%",gridcolor=T["line"]),
                    "yaxis":dict(gridcolor=T["line"])})
                fig.update_traces(marker_opacity=0.8)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with rh2:
        if "hosts" in dfw.columns:
            plot_data = dfw[dfw["hosts"]<40]
            if len(plot_data):
                fig = px.histogram(plot_data, x="hosts", nbins=30,
                                   title="Distinct Hosts per Page",
                                   color_discrete_sequence=[T["sky"]])
                fig.update_layout(**{**PLOTLY_BASE,"height":240,
                    "xaxis":dict(gridcolor=T["line"]), "yaxis":dict(gridcolor=T["line"])})
                fig.update_traces(marker_opacity=0.8)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with rh3:
        if "category" in dfw.columns and "requests_tracking" in dfw.columns:
            cat_req = dfw.groupby("category")["requests_tracking"].mean().sort_values(ascending=False)
            fig = go.Figure(go.Bar(
                x=cat_req.values.tolist(), y=cat_req.index.tolist(), orientation="h",
                marker_color=T["red"], marker_opacity=0.85,
                text=cat_req.values.round(1).tolist(), textposition="outside",
                textfont=dict(color=T["chalk4"],size=9),
            ))
            fig.update_layout(**{**PLOTLY_BASE,
                "title":{"text":"Avg Tracking Requests by Category","font":{"size":11}},
                "height":240,"xaxis":dict(gridcolor=T["line"]),
                "yaxis":dict(autorange="reversed",gridcolor=RGBA0),
            })
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # ── I: Advanced
    sec("Advanced Tracking Methods")
    ri1, ri2, ri3 = st.columns(3)
    with ri1:
        if "image" in dfw.columns:
            fig = px.histogram(dfw, x="image", nbins=25, title="Tracking Pixels",
                               color_discrete_sequence=[T["rose"]])
            fig.update_layout(**{**PLOTLY_BASE,"height":230,
                "xaxis":dict(gridcolor=T["line"]), "yaxis":dict(gridcolor=T["line"])})
            fig.update_traces(marker_opacity=0.8)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with ri2:
        if "bad_qs" in dfw.columns:
            fig = px.histogram(dfw, x="bad_qs", nbins=25, title="URL Fingerprinting",
                               color_discrete_sequence=[T["gold"]])
            fig.update_layout(**{**PLOTLY_BASE,"height":230,
                "xaxis":dict(gridcolor=T["line"]), "yaxis":dict(gridcolor=T["line"])})
            fig.update_traces(marker_opacity=0.8)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with ri3:
        if "it2" in dfw.columns:
            fig = px.histogram(dfw, x="it2", nbins=25, title="Core Combo: Script × XHR",
                               color_discrete_sequence=[T["amber"]])
            fig.update_layout(**{**PLOTLY_BASE,"height":230,
                "xaxis":dict(gridcolor=T["line"]), "yaxis":dict(gridcolor=T["line"])})
            fig.update_traces(marker_opacity=0.8)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    divider()

    # ── Full table
    eyebrow("Full Dataset")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    ts1, ts2, ts3 = st.columns([1,1,2])
    with ts1:
        sort_options = [c for c in ["privacy_score","trackers","companies","popularity"] if c in dfw.columns]
        sort_col = st.selectbox("Sort by", sort_options)
    with ts2:
        sort_asc = st.selectbox("Order", ["Highest first","Lowest first"]) == "Lowest first"
    with ts3:
        tier_filter = st.multiselect("Filter by tier", TIER_ORDER, default=TIER_ORDER)

    table_cols = [c for c in ["site","category","privacy_score","tier","script","xhr","sgeo",
                  "cookie_samesite_none","iframe","referer_leaked","beacon","image","tracked",
                  "trackers","companies","popularity"] if c in dfw.columns]
    filtered_table = dfw[dfw["tier"].isin(tier_filter)] if tier_filter else dfw
    display_df = filtered_table[table_cols].sort_values(sort_col, ascending=sort_asc).head(200)
    st.dataframe(display_df, use_container_width=True, height=400)
    st.caption(f"Showing 200 of {len(filtered_table):,} matching records")

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
divider()
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
     padding:8px 0 16px;flex-wrap:wrap;gap:10px">
  <div style="display:flex;align-items:center;gap:10px">
    <span style="font-family:'Fraunces',serif;font-size:15px;font-weight:300;
          color:{T['chalk2']}">Privacy<span style="color:{T['gold']}">Lens</span></span>
    <span style="font-family:'DM Mono',monospace;font-size:9px;color:{T['chalk5']};
          letter-spacing:.1em">v5.0</span>
  </div>
  <span style="font-family:'DM Mono',monospace;font-size:9.5px;color:{T['chalk5']};
       letter-spacing:.04em">
    WhoTracks.me · HTTP-level analysis · Does not include fingerprinting or app-level tracking
  </span>
</div>""", unsafe_allow_html=True)
