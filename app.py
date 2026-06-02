
import warnings
# Suppress only known harmless Streamlit/Plotly deprecation noise
warnings.filterwarnings("ignore", category=FutureWarning, module="plotly")
warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")

import os, io

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas    as pd
import numpy     as np
import plotly.graph_objects as go
import plotly.express       as px
import requests

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  — must be FIRST st call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title            = "PrivacyLens · Privacy Intelligence",
    page_icon             = "🔍",
    layout                = "wide",
    initial_sidebar_state = "expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE DEFAULTS
# ─────────────────────────────────────────────────────────────────────────────
for k, v in [
    ("page",            "Score Analyzer"),
    ("chat_msgs",       []),
    ("last_site",       None),
    ("chat_lang",       "English"),
    ("chat_input_val",  ""),
    ("last_groq_call",  0),
    # data_source is set by init_data() — not listed here
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN TOKENS
# ─────────────────────────────────────────────────────────────────────────────
T = dict(
    ink0   = "#050608", ink1   = "#080a0e", ink2   = "#0c0f15",
    ink3   = "#11151d", ink4   = "#161c27", ink5   = "#1c2433",
    line   = "#1e2738", line2  = "#28334a",
    chalk  = "#f0f2f5", chalk2 = "#c8cdd6", chalk3 = "#8a93a3",
    chalk4 = "#4a5568", chalk5 = "#2d3748",
    gold   = "#d4a843", gold2  = "#f0c96e",
    red    = "#e05252", red2   = "#ff6b6b",
    amber  = "#e8944a", amber2 = "#f0ab6e",
    lime   = "#52b788", lime2  = "#74c69d",
    sky    = "#4a9eda", sky2   = "#63b3ed",
    rose   = "#c0626e", rose2  = "#e07b86",
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
    hoverlabel    = dict(bgcolor=T["ink4"], bordercolor=T["line2"],
                         font_color=T["chalk"], font_size=11,
                         font_family="'DM Sans', sans-serif"),
    legend        = dict(bgcolor=RGBA0, bordercolor=T["line"], font_size=10),
    colorway      = [T["sky"], T["lime"], T["gold"], T["amber"], T["red"], T["rose"]],
    title_font    = dict(color=T["chalk2"], size=11, family="'DM Mono', monospace"),
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,200;0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300;1,9..40,400&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Fraunces:ital,opsz,wght@0,9..144,200;0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,200;1,9..144,300;1,9..144,400&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

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

[data-testid="stHeader"] {{ display: none !important; }}
[data-testid="stBottom"] {{ display: none !important; }}

.block-container {{
  padding: 1.5rem 2rem 3rem !important;
  max-width: 1600px !important;
}}

/* ── SIDEBAR — always expanded and visible ── */
[data-testid="stSidebar"] {{
  background: {T['ink1']} !important;
  border-right: 1px solid {T['line']} !important;
  min-width: 280px !important;
  width: 280px !important;
  transform: none !important;
  visibility: visible !important;
  opacity: 1 !important;
}}
[data-testid="stSidebar"] > div {{
  background: {T['ink1']} !important;
  min-width: 280px !important;
}}
[data-testid="stSidebar"][aria-expanded="false"] {{
  min-width: 280px !important;
  width: 280px !important;
  transform: none !important;
  margin-left: 0 !important;
}}
[data-testid="stSidebarCollapsedControl"] {{
  display: flex !important;
  background: {T['ink1']} !important;
}}
[data-testid="stSidebarContent"] {{
  background: {T['ink1']} !important;
  padding-top: 0 !important;
}}

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

[data-testid="stFileUploader"] section {{
  background: {T['ink3']} !important;
  border: 1px dashed {T['line2']} !important;
  border-radius: 8px !important;
}}

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

[data-testid="stRadio"] > div {{
  display: flex !important;
  flex-direction: column !important;
  gap: 6px !important;
}}
[data-testid="stRadio"] label {{
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13px !important;
  color: {T['chalk3']} !important;
  padding: 10px 14px !important;
  border-radius: 8px !important;
  border: 1px solid {T['line']} !important;
  transition: all .2s !important;
  cursor: pointer !important;
  background: {T['ink2']} !important;
}}
[data-testid="stRadio"] label:hover {{
  background: {T['ink4']} !important;
  border-color: {T['line2']} !important;
  color: {T['chalk2']} !important;
}}
[data-testid="stRadio"] label:has(input:checked) {{
  background: linear-gradient(135deg, {T['ink4']}, {T['ink5']}) !important;
  border-color: {T['gold']}50 !important;
  color: {T['chalk']} !important;
  box-shadow: 0 0 12px {T['gold']}15, inset 0 1px 0 {T['gold']}10 !important;
}}

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

.stSuccess {{ background: {T['lime']}0c !important; border: 1px solid {T['lime']}30 !important; border-radius: 6px !important; }}
.stWarning {{ background: {T['amber']}0c !important; border: 1px solid {T['amber']}30 !important; border-radius: 6px !important; }}
.stInfo    {{ background: {T['sky']}0c !important; border: 1px solid {T['sky']}30 !important; border-radius: 6px !important; }}
.stError   {{ background: {T['red']}0c !important; border: 1px solid {T['red']}30 !important; border-radius: 6px !important; }}

[data-testid="stExpander"] {{
  background: {T['ink2']} !important;
  border: 1px solid {T['line']} !important;
  border-radius: 8px !important;
}}
[data-testid="stExpander"] summary {{
  color: {T['chalk3']} !important;
  font-size: 12px !important;
  font-family: 'DM Mono', monospace !important;
  letter-spacing: .06em !important;
  text-transform: uppercase !important;
}}

[data-testid="stChatMessage"] {{
  background: {T['ink2']} !important;
  border: 1px solid {T['line']} !important;
  border-radius: 8px !important;
  margin-bottom: 8px !important;
}}

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

hr {{ border-color: {T['line']} !important; margin: 1.2rem 0 !important; }}
[data-testid="stCaptionContainer"] p {{
  color: {T['chalk5']} !important;
  font-size: 10.5px !important;
  font-family: 'DM Mono', monospace !important;
}}
::-webkit-scrollbar {{ width: 3px; height: 3px; }}
::-webkit-scrollbar-track {{ background: {T['ink1']}; }}
::-webkit-scrollbar-thumb {{ background: {T['line2']}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {T['chalk4']}; }}

.section-sep {{
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, transparent, {T['line2']}80, transparent);
  margin: 2.4rem 0;
}}

.eyebrow {{
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  letter-spacing: .18em;
  text-transform: uppercase;
  color: {T['chalk3']};
}}
.sidebar-eyebrow {{
  font-family: 'DM Sans', sans-serif;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: .22em;
  text-transform: uppercase;
  color: {T['chalk2']};
  opacity: 0.55;
  margin-bottom: 8px;
  padding-left: 2px;
}}

.pl-section {{
  background: {T['ink2']};
  border: 1px solid {T['line']};
  border-radius: 10px;
  padding: 24px 24px 20px;
  margin-bottom: 20px;
}}
.pl-section-header {{
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid {T['line']};
}}
.pl-section-icon {{
  width: 28px; height: 28px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; flex-shrink: 0;
}}
.pl-section-label {{
  font-family: 'Fraunces', serif; font-size: 18px; font-weight: 300;
  color: {T['chalk']}; letter-spacing: -.02em;
}}
.pl-section-sub {{
  font-family: 'DM Sans', sans-serif; font-size: 13px;
  color: {T['chalk2']}; margin-top: 3px; opacity: 1;
}}
</style>
""", unsafe_allow_html=True)

# Force sidebar expanded
st.markdown("""
<script>
(function(){
  function tryExpand(){
    var sb = window.parent.document.querySelector('[data-testid="stSidebar"]');
    if(!sb){ setTimeout(tryExpand,200); return; }
    if(sb.getAttribute('aria-expanded')==='false'){
      var btn = window.parent.document.querySelector('[data-testid="stSidebarCollapsedControl"] button');
      if(btn) btn.click();
    }
  }
  setTimeout(tryExpand, 400);
})();
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
GROQ_MODEL   = os.getenv("GROQ_MODEL",   "llama3-70b-8192")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

LANGUAGES = {
    "English": "en", "Hindi — हिंदी": "hi", "Bengali — বাংলা": "bn",
    "Telugu — తెలుగు": "te", "Marathi — मराठी": "mr", "Tamil — தமிழ்": "ta",
    "Gujarati — ગુજરાતી": "gu", "Kannada — ಕನ್ನಡ": "kn", "Malayalam — മലയാളം": "ml",
    "Punjabi — ਪੰਜਾਬੀ": "pa", "Odia — ଓଡ଼ିଆ": "or", "Urdu — اردو": "ur",
    "Spanish — Español": "es", "French — Français": "fr", "Arabic — العربية": "ar",
    "Chinese — 中文": "zh", "Japanese — 日本語": "ja", "Portuguese — Português": "pt",
    "German — Deutsch": "de", "Russian — Русский": "ru",
}

def score_info(s):
    for thr, lbl, col, bg in RISK_TIERS:
        if s < thr: return lbl, col, bg
    return RISK_TIERS[-1][1], RISK_TIERS[-1][2], RISK_TIERS[-1][3]

def risk_color(v):
    if v < 0.25: return T["lime"]
    if v < 0.50: return T["sky"]
    if v < 0.75: return T["amber"]
    return T["red"]

def bar_col(v):
    if v < 0.30: return T["lime"]
    if v < 0.60: return T["amber"]
    return T["red"]

def safe_get(row, col, default=0.0):
    try:
        idx = row.index if isinstance(row, pd.Series) else row
        if col not in idx: return default
        v = row[col]
        if pd.isna(v): return default
        if isinstance(default, (int, float)): return float(v)
        return v
    except Exception:
        return default

def has_col(x, col):
    return col in (x.index if isinstance(x, pd.Series) else x.columns)

def safe_sample(frame, n=2000, seed=42):
    return frame.sample(min(n, len(frame)), random_state=seed)

def hex_rgba(h, a):
    h = h.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{a})"

def eyebrow(text):
    st.markdown(f'<p class="eyebrow" style="margin-bottom:6px">{text}</p>', unsafe_allow_html=True)

def sep():
    st.markdown('<div class="section-sep"></div>', unsafe_allow_html=True)

def card_section(icon, label, subtitle=""):
    sub = f'<div class="pl-section-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div class="pl-section-header">
      <div class="pl-section-icon" style="background:{T['ink3']}">{icon}</div>
      <div>
        <div class="pl-section-label">{label}</div>
        {sub}
      </div>
    </div>""", unsafe_allow_html=True)

def signal_bar(label, value, explanation):
    v   = float(np.clip(value, 0, 1))
    pct = int(v * 100)
    col = bar_col(v)
    return f"""
    <div style="padding:12px 0;border-bottom:1px solid {T['line']}22">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px">
        <span style="font-size:13px;color:{T['chalk2']};font-family:'DM Sans',sans-serif;font-weight:500">{label}</span>
        <span style="font-family:'DM Mono',monospace;font-size:11px;color:{col};font-weight:500">{pct}%</span>
      </div>
      <div style="background:{T['ink4']};border-radius:3px;height:3px;overflow:hidden">
        <div style="width:{pct}%;background:linear-gradient(90deg,{col}99,{col});height:3px;border-radius:3px"></div>
      </div>
      <div style="font-size:12px;color:{T['chalk3']};margin-top:5px;font-family:'DM Sans',sans-serif;line-height:1.5">{explanation}</div>
    </div>"""

def stat_pill(label, val, color=None):
    c = color or T["chalk3"]
    return f"""<div style="display:inline-block;margin:4px 6px 4px 0;padding:6px 12px;
      background:{T['ink3']};border:1px solid {T['line2']};border-radius:4px">
      <div style="font-family:'DM Mono',monospace;font-size:9px;color:{T['chalk5']};text-transform:uppercase;
           letter-spacing:.12em;margin-bottom:3px">{label}</div>
      <div style="font-family:'DM Mono',monospace;font-size:13px;color:{c};font-weight:500">{val}</div>
    </div>"""

def score_badge(score, label, color):
    return f"""<div style="display:inline-flex;align-items:center;gap:8px;padding:6px 12px 6px 8px;
      background:{T['ink3']};border:1px solid {color}40;border-radius:4px">
      <div style="width:6px;height:6px;border-radius:50%;background:{color};box-shadow:0 0 8px {color}80"></div>
      <span style="font-family:'DM Mono',monospace;font-size:9px;color:{color};letter-spacing:.15em;
           text-transform:uppercase">{label}</span>
    </div>"""

# ─────────────────────────────────────────────────────────────────────────────
# SCORING ENGINE
# ─────────────────────────────────────────────────────────────────────────────
W  = dict(sgeo=0.50, it2=0.30, referer_leaked=0.10,
          it1=0.05, it3=0.10, cookie_samesite_none=0.03,
          iframe=0.03, beacon=0.02)
TW = sum(W.values())

def compute_scores(df):
    d = df.copy()
    for c in ["script","xhr","iframe","cookie_samesite_none","referer_leaked",
              "beacon","image","tracked","cookies","bad_qs","media"]:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0).clip(0,1)
        else:
            d[c] = 0.0
    d["sgeo"] = np.sqrt(d["script"] * d["xhr"])
    d["it1"]  = d["cookie_samesite_none"] * d["sgeo"]
    d["it2"]  = d["script"] * d["xhr"]
    d["it3"]  = d["iframe"] * d["sgeo"]
    d["privacy_score"] = (sum(d[c]*w for c,w in W.items()) / TW * 100).clip(0,100).round(2)
    for rc in ["requests","requests_tracking"]:
        if rc in d.columns:
            d[rc] = pd.to_numeric(d[rc], errors="coerce").fillna(0)
        else:
            d[rc] = 0.0
    d["track_ratio"] = (d["requests_tracking"] / d["requests"].replace(0, np.nan)).fillna(0).clip(0,1)
    return d

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADER  — cache is the single source of truth; session_state stores only
# a lightweight key (path string or upload hash), never the full DataFrame.
# This means 20 concurrent users share ONE cached copy instead of 20 copies.
# ─────────────────────────────────────────────────────────────────────────────
AUTO_PATHS   = ["sites.csv","whotracks_2026/sites.csv","data/sites.csv"]
MAX_UPLOAD_MB = 50  # hard cap on uploaded file size

@st.cache_data(show_spinner="Loading dataset…")
def load_path(p: str) -> pd.DataFrame:
    return compute_scores(pd.read_csv(p, index_col=0))

@st.cache_data(show_spinner="Loading dataset…")
def load_bytes_cached(data_hash: str, raw: bytes) -> pd.DataFrame:
    """raw bytes are passed so cache can hash them; data_hash is the cache key."""
    return compute_scores(pd.read_csv(io.BytesIO(raw), index_col=0))

def validate_csv(raw: bytes) -> tuple[bool, str]:
    """Return (ok, error_message). Checks size, parsability, required columns."""
    mb = len(raw) / 1_048_576
    if mb > MAX_UPLOAD_MB:
        return False, f"File is {mb:.1f} MB — max allowed is {MAX_UPLOAD_MB} MB."
    try:
        sample = pd.read_csv(io.BytesIO(raw), index_col=0, nrows=5)
    except Exception as e:
        return False, f"Could not parse CSV: {e}"
    if "site" not in sample.columns:
        return False, "CSV is missing required column 'site'."
    return True, ""

def get_df() -> pd.DataFrame | None:
    """Always fetch from cache using the stored key — never from session_state directly."""
    src = st.session_state.get("data_source")
    if src is None:
        return None
    if src["type"] == "path":
        return load_path(src["path"])
    if src["type"] == "upload":
        return load_bytes_cached(src["hash"], src["raw"])
    return None

def init_data():
    if "data_source" not in st.session_state:
        for p in AUTO_PATHS:
            if os.path.exists(p):
                st.session_state.data_source = {"type": "path", "path": p}
                return
        st.session_state.data_source = None

init_data()

def add_tier_col(df):
    out = df.copy()
    out["tier"] = pd.cut(
        out["privacy_score"],
        bins=[-0.001, 20, 40, 60, 80, 100.001],
        labels=["Private", "Low Risk", "Moderate", "High Risk", "Critical"]
    ).astype(str)
    return out

TIER_ORDER  = ["Private","Low Risk","Moderate","High Risk","Critical"]
TIER_COLORS = {"Private":T["lime"],"Low Risk":T["sky"],"Moderate":T["amber"],
               "High Risk":T["red"],"Critical":T["rose"]}

SIGNAL_LABELS = {
    "script":"JS Scripts","xhr":"XHR Calls","iframe":"Iframes",
    "cookie_samesite_none":"Cross-Site Cookies","beacon":"Beacons",
    "referer_leaked":"Ref Leaked","image":"Pixels","tracked":"Tracked",
    "cookies":"Cookies","bad_qs":"URL Fingerprint","media":"Media","sgeo":"Core Signal"
}

# ─────────────────────────────────────────────────────────────────────────────
# GROQ API  — with chat history capped at last 20 messages to avoid token
# overflow, and a per-session cooldown to prevent request spam.
# ─────────────────────────────────────────────────────────────────────────────
CHAT_MAX_MSGS   = 20   # keep last N messages sent to API
CHAT_COOLDOWN_S = 3    # minimum seconds between requests per session

def call_groq(messages, system, api_key):
    if not api_key:
        return "⚠ No API key configured. Add GROQ_API_KEY to your .env file."
    # Rate limiting: enforce cooldown between requests
    import time
    last = st.session_state.get("last_groq_call", 0)
    if time.time() - last < CHAT_COOLDOWN_S:
        return f"⚠ Please wait {CHAT_COOLDOWN_S} seconds between messages."
    # Trim history to last CHAT_MAX_MSGS to stay within context window
    trimmed = messages[-CHAT_MAX_MSGS:]
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": GROQ_MODEL, "max_tokens": 900, "temperature": 0.6,
                "messages": [{"role": "system", "content": system}] + trimmed,
            },
            timeout=30,
        )
        r.raise_for_status()
        st.session_state["last_groq_call"] = time.time()
        return r.json()["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "⚠ Request timed out. Please try again."
    except requests.exceptions.HTTPError as e:
        return f"⚠ API error {e.response.status_code}: {e.response.text[:200]}"
    except Exception as e:
        return f"⚠ Unexpected error: {type(e).__name__}"

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:28px 0 8px">
      <div style="font-family:'DM Mono',monospace;font-size:11px;letter-spacing:.22em;
           text-transform:uppercase;color:{T['chalk3']};margin-bottom:10px">Privacy Intelligence</div>
      <div style="font-family:'Fraunces',serif;font-size:28px;font-weight:300;
           color:{T['chalk']};letter-spacing:-.03em;line-height:1">
        Privacy<span style="color:{T['gold']}">Lens</span>
      </div>
      <div style="margin-top:16px;padding:13px 15px;background:{T['ink3']};
           border:1px solid {T['line2']};border-radius:8px;border-left:2px solid {T['gold']}60">
        <div style="font-family:'DM Sans',sans-serif;font-size:12px;color:{T['chalk2']};line-height:1.8">
          Discover <b style="color:{T['chalk']}">which websites track you</b>, what data they
          collect, how they use it, and how secure your personal data really is.
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-sep"></div>', unsafe_allow_html=True)

    st.markdown(f'<p class="sidebar-eyebrow">Navigation</p>', unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    nav_options = ["Score Analyzer","Analytics Dashboard"]
    nav_icons   = ["🔍","📊"]
    page = st.radio(
        "nav", nav_options,
        index=nav_options.index(st.session_state.get("page","Score Analyzer")),
        format_func=lambda x: f"{nav_icons[nav_options.index(x)]}  {x}",
        label_visibility="collapsed"
    )
    if page != st.session_state.page:
        st.session_state.page = page
        st.rerun()

    st.markdown('<div class="section-sep"></div>', unsafe_allow_html=True)

    df_raw = get_df()
    eyebrow("Data Source")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if df_raw is None:
        uploaded = st.file_uploader("Upload sites.csv", type=["csv"], label_visibility="collapsed")
        if uploaded:
            raw = uploaded.read()
            ok, err = validate_csv(raw)
            if not ok:
                st.error(f"Upload rejected: {err}")
            else:
                import hashlib
                h = hashlib.md5(raw).hexdigest()
                st.session_state.data_source = {"type": "upload", "hash": h, "raw": raw}
                st.rerun()
        st.caption(f"Place sites.csv in app folder or upload (max {MAX_UPLOAD_MB} MB)")
    else:
        n_cat = df_raw["category"].nunique() if "category" in df_raw.columns else "—"
        st.markdown(f"""
        <div style="padding:14px 16px;background:{T['ink3']};border:1px solid {T['lime']}28;border-radius:8px">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
            <div style="width:6px;height:6px;border-radius:50%;background:{T['lime']};box-shadow:0 0 6px {T['lime']}"></div>
            <span style="font-family:'DM Mono',monospace;font-size:10px;color:{T['lime']};letter-spacing:.14em;text-transform:uppercase">Active Dataset</span>
          </div>
          <div style="font-family:'DM Mono',monospace;font-size:12px;color:{T['chalk3']}">{len(df_raw):,} sites · {n_cat} categories</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-sep"></div>', unsafe_allow_html=True)

    eyebrow("AI Key")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    api_key_input = st.text_input("Groq API Key", type="password",
                                  placeholder="gsk_…", label_visibility="collapsed", value="")
    api_key = GROQ_API_KEY or api_key_input

    if api_key:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;padding:10px 12px;
             background:{T['ink3']};border:1px solid {T['lime']}28;border-radius:6px;margin-top:6px">
          <div style="width:5px;height:5px;border-radius:50%;background:{T['lime']};box-shadow:0 0 6px {T['lime']}"></div>
          <span style="font-family:'DM Mono',monospace;font-size:10px;color:{T['lime']};letter-spacing:.14em;text-transform:uppercase">AI Active</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.caption("Add GROQ_API_KEY=... in .env or paste above")

# ─────────────────────────────────────────────────────────────────────────────
# GUARD — no data uploaded yet
# ─────────────────────────────────────────────────────────────────────────────
df_raw = get_df()
if df_raw is None:
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
         padding:100px 0;text-align:center">
      <div style="font-family:'DM Mono',monospace;font-size:11px;color:{T['chalk4']};
           letter-spacing:.25em;text-transform:uppercase;margin-bottom:20px">Privacy Intelligence Platform</div>
      <h1 style="font-family:'Fraunces',serif !important;font-size:52px;font-weight:300;
           letter-spacing:-.04em;color:{T['chalk']};margin:0 0 20px;line-height:1">
        Privacy<span style="color:{T['gold']}">Lens</span></h1>
      <p style="font-size:14px;color:{T['chalk4']};max-width:420px;line-height:1.8;font-family:'DM Sans',sans-serif">
        Upload <code style="font-family:'DM Mono',monospace;color:{T['sky']};background:{T['ink3']};
        padding:2px 8px;border-radius:3px">sites.csv</code> via the sidebar to start discovering
        which websites track you, what they collect, and how safe your data really is.</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

df = df_raw

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — SCORE ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "Score Analyzer":

    st.markdown(f"""
    <div style="padding-bottom:20px;border-bottom:1px solid {T['line']};margin-bottom:24px">
      <div class="eyebrow" style="margin-bottom:8px">🔍 Score Analyzer</div>
      <h1 style="font-family:'Fraunces',serif !important;font-size:34px;font-weight:300;
           color:{T['chalk']} !important;letter-spacing:-.04em;margin:0 0 6px">Privacy Risk Analysis</h1>
      <p style="color:{T['chalk4']};font-size:13px;font-family:'DM Sans',sans-serif;margin:0">
        See exactly what each website tracks, how they do it, and what they do with your data</p>
    </div>""", unsafe_allow_html=True)

    # ── Filters
    f1, f2, f3 = st.columns([1, 2.4, 0.8])
    categories = (["All Categories"] + sorted(df["category"].dropna().unique().tolist())
                  if "category" in df.columns else ["All Categories"])
    with f1:
        eyebrow("Category")
        sel_cat = st.selectbox("cat", categories,
            format_func=lambda c: c if c=="All Categories" else f"{c}  ({len(df[df['category']==c]):,})",
            label_visibility="collapsed")

    filtered = df if sel_cat=="All Categories" else df[df["category"]==sel_cat]

    if "site" not in df.columns:
        st.error("Dataset missing required 'site' column."); st.stop()

    site_list = (filtered.sort_values("popularity", ascending=False)["site"].dropna().unique().tolist()
                 if "popularity" in df.columns
                 else filtered["site"].dropna().unique().tolist())

    if not site_list:
        st.warning("No sites found for the selected category."); st.stop()

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
        st.warning(f"'{sel_site}' not found."); st.stop()

    row   = matches.iloc[0]
    score = float(row["privacy_score"])
    label, color, bg = score_info(score)

    if st.session_state.last_site != sel_site:
        st.session_state.chat_msgs      = []
        st.session_state.last_site      = sel_site
        st.session_state.chat_input_val = ""

    cat_val  = safe_get(row,"category","—") if has_col(row,"category") else "—"
    pop_val  = safe_get(row,"popularity",0.0)
    pop_str  = f"{pop_val:.5f}" if pop_val > 0 else "—"
    percentile = int((df["privacy_score"] < score).mean() * 100)

    # ── Hero card
    st.markdown(f"""
    <div style="padding:24px 28px;background:{T['ink2']};border:1px solid {T['line']};
         border-top:3px solid {color};border-radius:10px;margin:0 0 20px;
         display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:16px">
      <div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
          <h2 style="font-family:'Fraunces',serif !important;font-size:28px;font-weight:300;
               color:{T['chalk']} !important;letter-spacing:-.03em;margin:0">{sel_site}</h2>
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

    left, right = st.columns([1, 1.9], gap="large")

    with left:
        st.markdown(f'<div class="pl-section">', unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=score,
            number={"font":{"size":40,"color":color,"family":"DM Mono"}},
            domain={"x":[0,1],"y":[0,1]},
            gauge={
                "axis":{"range":[0,100],"tickwidth":0,"tickfont":{"color":T["chalk5"],"size":8}},
                "bar":{"color":color,"thickness":0.16},
                "bgcolor":T["ink3"],"borderwidth":0,
                "steps":[
                    {"range":[0,20],  "color":hex_rgba(T["lime"],  0.08)},
                    {"range":[20,40], "color":hex_rgba(T["sky"],   0.08)},
                    {"range":[40,60], "color":hex_rgba(T["amber"], 0.08)},
                    {"range":[60,80], "color":hex_rgba(T["red"],   0.08)},
                    {"range":[80,100],"color":hex_rgba(T["rose"],  0.10)},
                ],
                "threshold":{"line":{"color":color,"width":1.5},"thickness":0.85,"value":score},
            }
        ))
        fig_gauge.update_layout(**{**PLOTLY_BASE,"height":220,"margin":dict(l=16,r=16,t=10,b=10)})
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar":False})

        if "category" in df.columns and has_col(row,"category"):
            cvs = safe_get(row,"category","")
            if cvs:
                cat_sub = df[df["category"]==cvs]["privacy_score"]
                if len(cat_sub):
                    cm   = cat_sub.mean()
                    dlt  = score - cm
                    dstr = f"+{dlt:.0f}" if dlt>=0 else f"{dlt:.0f}"
                    dcol = T["red"] if dlt>0 else T["lime"]
                    st.markdown(f"""
                    <div style="padding:12px 14px;background:{T['ink3']};border:1px solid {T['line']};
                         border-radius:6px;margin-bottom:12px">
                      <div class="eyebrow" style="margin-bottom:7px">vs. Category Average</div>
                      <div style="display:flex;align-items:baseline;gap:8px">
                        <span style="font-family:'DM Mono',monospace;font-size:22px;color:{T['chalk']};font-weight:400">{cm:.0f}</span>
                        <span style="font-family:'DM Mono',monospace;font-size:12px;color:{T['chalk5']}">avg</span>
                        <span style="font-family:'DM Mono',monospace;font-size:13px;color:{dcol};margin-left:8px">{dstr} pts</span>
                      </div>
                      <div style="font-size:11px;color:{T['chalk5']};margin-top:4px;font-family:'DM Sans',sans-serif">in {cvs}</div>
                    </div>""", unsafe_allow_html=True)

        eyebrow("Signal Snapshot")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        qa, qb = st.columns(2)
        qa.metric("Scripts",       f"{safe_get(row,'script'):.0%}")
        qb.metric("XHR Calls",     f"{safe_get(row,'xhr'):.0%}")
        qa.metric("Trackers",      f"{safe_get(row,'trackers',0.0):.1f}")
        qb.metric("Companies",     f"{safe_get(row,'companies',0.0):.1f}")
        qa.metric("Tracked",       f"{safe_get(row,'tracked'):.0%}")
        qb.metric("Cross-Cookies", f"{safe_get(row,'cookie_samesite_none'):.0%}")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        tab_what, tab_how, tab_why, tab_xai = st.tabs([
            "WHAT THEY COLLECT","HOW THEY DO IT","WHY THEY DO IT","SCORE BREAKDOWN"])

        # ── WHAT THEY COLLECT
        with tab_what:
            # FIXED: chalk4 → chalk2, font-size 12px → 13px
            st.markdown(f"""<p style="color:{T['chalk2']};font-size:13px;margin:14px 0 16px;
            font-family:'DM Sans',sans-serif;line-height:1.7">
            Data <b style="color:{T['chalk']}">{sel_site}</b> likely collects from visitors.</p>""",
            unsafe_allow_html=True)
            items = []
            if safe_get(row,"tracked")>0.2:
                items.append(("01","Identity Tracking",f"Persistent unique ID across sessions. Active on {safe_get(row,'tracked'):.0%} of visits.",T["red"]))
            if safe_get(row,"cookies",0.0)>0.2:
                items.append(("02","Login & Preference Data",f"Cookies storing identity and behavior. Detected on {safe_get(row,'cookies',0.0):.0%} of visits.",T["amber"]))
            if safe_get(row,"cookie_samesite_none")>0.15:
                items.append(("03","Cross-Site Activity",f"Follows you to other websites. Active on {safe_get(row,'cookie_samesite_none'):.0%} of visits.",T["red"]))
            if safe_get(row,"xhr")>0.3:
                items.append(("04","Real-Time Behaviour",f"Every click and scroll silently uploaded. Happens on {safe_get(row,'xhr'):.0%} of visits.",T["amber"]))
            if safe_get(row,"referer_leaked")>0.2:
                items.append(("05","Navigation History",f"Previous URL shared with third parties. Leaked on {safe_get(row,'referer_leaked'):.0%} of visits.",T["amber"]))
            if safe_get(row,"image")>0.3:
                items.append(("06","Device Fingerprint",f"Invisible pixel images record IP, browser, OS. Loaded on {safe_get(row,'image'):.0%} of visits.",T["sky"]))
            if safe_get(row,"media",0.0)>0.05:
                items.append(("07","Media Consumption",f"What you watch and for how long. Active on {safe_get(row,'media',0.0):.0%} of visits.",T["sky"]))
            if safe_get(row,"bad_qs",0.0)>0.05:
                items.append(("08","URL Fingerprinting",f"Unique query codes identify you cookieless. Used on {safe_get(row,'bad_qs',0.0):.0%} of visits.",T["sky"]))

            if not items:
                st.success(f"✓  {sel_site} shows minimal data collection.")
            else:
                html = ""
                for num,title,desc,cl in items:
                    html += f"""<div style="display:flex;gap:16px;padding:13px 0;
                      border-bottom:1px solid {T['line']}22;align-items:flex-start">
                      <div style="font-family:'DM Mono',monospace;font-size:9px;color:{T['chalk5']};
                           padding-top:3px;flex-shrink:0;letter-spacing:.08em">{num}</div>
                      <div>
                        <div style="font-size:13px;font-weight:600;color:{T['chalk2']};
                             font-family:'DM Sans',sans-serif;margin-bottom:4px;
                             display:flex;align-items:center;gap:8px">{title}
                          <span style="display:inline-block;width:5px;height:5px;
                               border-radius:50%;background:{cl};flex-shrink:0"></span></div>
                        <div style="font-size:12px;color:{T['chalk3']};font-family:'DM Sans',sans-serif;
                             line-height:1.6">{desc}</div>
                      </div></div>"""
                st.markdown(html, unsafe_allow_html=True)

        # ── HOW THEY DO IT
        with tab_how:
            # FIXED: chalk4 → chalk2, font-size 12px → 13px
            st.markdown(f"""<p style="color:{T['chalk2']};font-size:13px;margin:14px 0 4px;
            font-family:'DM Sans',sans-serif">Technical methods — bar shows deployment frequency.</p>""",
            unsafe_allow_html=True)
            signals = [
                ("script","JavaScript Execution","Runs in your browser — intercepts keystrokes, form data, mouse movements"),
                ("xhr","Background Data Requests","Silently uploads data while you browse — invisible to users"),
                ("sgeo","Combined Tracking Signal","Script × XHR combined — primary composite indicator of active tracking"),
                ("iframe","Embedded Hidden Frames","Invisible sub-pages running independent tracking logic"),
                ("cookie_samesite_none","Cross-Site Cookie Drops","Cookies that operate across all websites, not just this domain"),
                ("beacon","Beacon Pings","Fires even after tab close — confirms page completion, ad views"),
                ("image","Tracking Pixels","1×1 invisible images that record your IP address and browser environment"),
                ("referer_leaked","Referrer Header Leaking","Your previous URL shared with third-party domains"),
                ("bad_qs","URL-based Fingerprinting","Query string parameters that identify you without any cookies"),
                ("media","Media Interaction Tracking","Video/audio play events, duration, and completion rates logged"),
            ]
            html = ""
            for ck,lbl,expl in signals:
                html += signal_bar(lbl, safe_get(row,ck), expl)
            st.markdown(html, unsafe_allow_html=True)

        # ── WHY THEY DO IT
        with tab_why:
            # FIXED: chalk4 → chalk2, font-size 12px → 13px
            st.markdown(f"""<p style="color:{T['chalk2']};font-size:13px;margin:14px 0 16px;
            font-family:'DM Sans',sans-serif">What this data is used for — no euphemisms.</p>""",
            unsafe_allow_html=True)
            uses = []
            if safe_get(row,"sgeo")>0.5:
                uses.append(("Behavioural Profile Construction","Every interaction logged to build a psychographic model predicting interests, income, and intent.",T["red"],"HIGH CONCERN"))
            if safe_get(row,"cookie_samesite_none")>0.2:
                uses.append(("Cross-Internet Surveillance","Identity shared with ad networks to serve targeted ads across every website you visit.",T["red"],"HIGH CONCERN"))
            if safe_get(row,"cookies",0.0)>0.3 or safe_get(row,"tracked")>0.3:
                uses.append(("Real-Time Bidding Auction","Your profile is auctioned in under 100ms to advertisers before the page loads.",T["amber"],"MODERATE"))
            if safe_get(row,"referer_leaked")>0.3:
                uses.append(("Browsing History Inference","Your navigation path is sold to data brokers who infer health, politics, and finances.",T["amber"],"MODERATE"))
            if safe_get(row,"beacon")>0.1:
                uses.append(("Ad Effectiveness Attribution","Beacon pings confirm ad exposure, conversion, and return visits for advertiser billing.",T["sky"],"LOW CONCERN"))
            if safe_get(row,"media",0.0)>0.05:
                uses.append(("Content Engagement Optimisation","Watch time and completion signals feed recommendation algorithms to maximize engagement.",T["sky"],"LOW CONCERN"))
            if not uses:
                uses.append(("Minimal Data Utilisation Detected","Tracking signals are low. This site likely collects only operationally necessary data.",T["lime"],"COMPLIANT"))
            html = ""
            for title,desc,cl,sev in uses:
                html += f"""<div style="padding:14px 16px;background:{T['ink3']};
                  border:1px solid {T['line']};border-left:2px solid {cl};
                  border-radius:0 6px 6px 0;margin-bottom:10px">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
                    <div style="font-size:13px;font-weight:600;color:{T['chalk2']};font-family:'DM Sans',sans-serif">{title}</div>
                    <span style="font-family:'DM Mono',monospace;font-size:8.5px;color:{cl};
                         letter-spacing:.12em;padding:3px 8px;border:1px solid {cl}30;
                         border-radius:2px;flex-shrink:0;margin-left:12px">{sev}</span>
                  </div>
                  <div style="font-size:12px;color:{T['chalk3']};font-family:'DM Sans',sans-serif;line-height:1.65">{desc}</div>
                </div>"""
            st.markdown(html, unsafe_allow_html=True)

        # ── SCORE BREAKDOWN
        with tab_xai:
            # FIXED: chalk4 → chalk2, font-size 12px → 13px
            st.markdown(f"""<p style="color:{T['chalk2']};font-size:13px;margin:14px 0 10px;
            font-family:'DM Sans',sans-serif">
            Signal contributions to final score of
            <span style="font-family:'DM Mono',monospace;color:{color}">{score:.0f}/100</span>.</p>""",
            unsafe_allow_html=True)
            contributions = {sig: round(safe_get(row,sig)*w/TW*100,2) for sig,w in W.items()}
            total_contrib = sum(contributions.values())
            max_contrib   = max(contributions.values()) if contributions else 1.0
            sorted_c      = sorted(contributions.items(), key=lambda x:-x[1])
            contrib_vals  = [c for _,c in sorted_c]
            max_cv        = max(contrib_vals) if contrib_vals else 1.0
            bar_colors    = [risk_color(c/max_cv if max_cv>0 else 0) for c in contrib_vals]
            sig_labels    = {
                "sgeo":"Core Signal (√JS × XHR)","it2":"Session Signal (JS × XHR)",
                "referer_leaked":"Referrer Leaked","it3":"Iframe Combo",
                "it1":"Cookie + Signal Combo","cookie_samesite_none":"Cross-Site Cookies",
                "iframe":"Hidden Iframes","beacon":"Beacon Pings"
            }
            fig_bar = go.Figure(go.Bar(
                x=contrib_vals, y=[sig_labels.get(s,s) for s,_ in sorted_c], orientation="h",
                marker=dict(color=bar_colors,line=dict(color=RGBA0),opacity=0.85),
                text=[f"+{c:.1f}" for c in contrib_vals], textposition="outside",
                textfont=dict(color=T["chalk4"],size=10,family="DM Mono")))
            fig_bar.update_layout(**{**PLOTLY_BASE,"height":280,
                "xaxis":dict(title="Points contributed",gridcolor=T["line"],zeroline=False,tickfont=dict(size=9)),
                "yaxis":dict(autorange="reversed",gridcolor=RGBA0,tickfont=dict(size=10)),
                "margin":dict(l=8,r=60,t=10,b=26)})
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar":False})

            eyebrow("Detailed Breakdown")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            # FIXED: table header chalk5 → chalk3, size 8.5px → 9.5px; row signal name chalk3 → chalk2, size 11.5px → 12.5px
            html = f"""<div style="background:{T['ink2']};border:1px solid {T['line']};
              border-radius:6px;overflow:hidden;font-family:'DM Mono',monospace">
              <div style="display:grid;grid-template-columns:2fr .6fr .6fr .6fr;padding:10px 16px;
                   border-bottom:1px solid {T['line2']};font-size:9.5px;color:{T['chalk3']};
                   text-transform:uppercase;letter-spacing:.14em;background:{T['ink3']}">
                <span>Signal</span><span>Value</span><span>Weight</span><span>Points</span></div>"""
            for i,(sig,contrib) in enumerate(sorted_c):
                val = safe_get(row,sig); w = W.get(sig,0)
                cl  = risk_color(contrib/max_contrib if max_contrib>0 else 0)
                rb  = T["ink3"]+"60" if i%2==0 else RGBA0
                html += f"""<div style="display:grid;grid-template-columns:2fr .6fr .6fr .6fr;
                  padding:9px 16px;border-bottom:1px solid {T['line']}18;background:{rb}">
                  <span style="font-size:12.5px;color:{T['chalk2']}">{sig_labels.get(sig,sig)}</span>
                  <span style="font-size:11px;color:{T['chalk3']}">{val:.3f}</span>
                  <span style="font-size:11px;color:{T['chalk4']}">×{w:.2f}</span>
                  <span style="font-size:12px;font-weight:500;color:{cl}">+{contrib:.1f}</span></div>"""
            html += f"""<div style="display:grid;grid-template-columns:2fr .6fr .6fr .6fr;
              padding:12px 16px;border-top:1px solid {T['line2']};background:{T['ink4']}">
              <span style="font-size:12px;font-weight:500;color:{T['chalk2']};letter-spacing:.04em">TOTAL</span>
              <span></span><span></span>
              <span style="font-size:14px;font-weight:500;color:{color}">{total_contrib:.0f}</span>
            </div></div>"""
            st.markdown(html, unsafe_allow_html=True)

    # ── Protective Measures
    if score > 30:
        sep()
        st.markdown(f'<div class="pl-section">', unsafe_allow_html=True)
        card_section("🛡️","Protective Measures","Tools to reduce your exposure on this site")
        tips = []; tc = st.columns(3)
        if safe_get(row,"script")>0.5:
            tips.append(("uBlock Origin","Blocks tracking scripts before they execute. The single most effective free privacy tool.",
                         "https://ublockorigin.com",T["lime"]))
        if safe_get(row,"cookie_samesite_none")>0.2:
            tips.append(("Firefox + TCP","Total Cookie Protection isolates cookies per site — stops cross-site tracking completely.",
                         "https://www.mozilla.org/firefox",T["sky"]))
        if safe_get(row,"iframe")>0.3:
            tips.append(("Privacy Badger","Learns and blocks invisible trackers automatically as you browse.",
                         "https://privacybadger.org",T["amber"]))
        if safe_get(row,"referer_leaked")>0.2:
            tips.append(("Brave Browser","Strips referrer headers and blocks fingerprinting by default.",
                         "https://brave.com",T["gold"]))
        if safe_get(row,"beacon")>0.1:
            tips.append(("uBlock Strict Mode","Intercepts beacon and ping requests at the network level.",
                         "https://ublockorigin.com",T["red"]))
        if not tips:
            tips.append(("Privacy Browser","Start with Brave or Firefox Enhanced Tracking Protection.",
                         "https://brave.com",T["sky"]))
        for i,(tool,desc,url,tcol) in enumerate(tips[:3]):
            with tc[i%3]:
                st.markdown(f"""<a href="{url}" target="_blank" style="text-decoration:none;display:block">
                <div style="padding:16px;background:{T['ink3']};border:1px solid {T['line']};
                     border-top:2px solid {tcol};border-radius:6px">
                  <div style="font-size:14px;font-weight:600;color:{T['chalk']};
                       font-family:'DM Sans',sans-serif;margin-bottom:6px">{tool}</div>
                  <div style="font-size:12px;color:{T['chalk2']};font-family:'DM Sans',sans-serif;
                       line-height:1.6;margin-bottom:12px">{desc}</div>
                  <div style="font-family:'DM Mono',monospace;font-size:9px;color:{tcol};
                       letter-spacing:.12em;text-transform:uppercase">Visit →</div>
                </div></a>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Raw data
    sep()
    st.markdown(f'<div class="pl-section">', unsafe_allow_html=True)
    card_section("🔬","Raw Signal Values","Underlying data powering this analysis")
    with st.expander("Show raw values"):
        raw_cols = ["script","xhr","sgeo","iframe","cookie_samesite_none","referer_leaked",
                    "beacon","image","tracked","it1","it2","it3","privacy_score",
                    "trackers","companies","requests","requests_tracking"]
        raw = {c:[round(safe_get(row,c),4)] for c in raw_cols if c in row.index}
        if raw: st.dataframe(pd.DataFrame(raw), use_container_width=True)
        else:   st.caption("No raw data available.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── AI Privacy Assistant
    sep()
    st.markdown(f'<div class="pl-section">', unsafe_allow_html=True)
    card_section("🤖","AI Privacy Assistant",f"Ask anything about {sel_site} or how this app works")

    lang_col, _ = st.columns([1,3])
    with lang_col:
        eyebrow("Response Language")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        chosen_lang = st.selectbox("lang", list(LANGUAGES.keys()),
                                   index=list(LANGUAGES.keys()).index(st.session_state.chat_lang),
                                   label_visibility="collapsed")
        st.session_state.chat_lang = chosen_lang

    cat_for_prompt = safe_get(row,"category","—") if has_col(row,"category") else "—"
    system_prompt = f"""You are PrivacyLens AI — expert privacy analyst.
Analysing: {sel_site}
Score: {score:.1f}/100 — {label} | Category: {cat_for_prompt}
Scripts:{safe_get(row,'script'):.1%} XHR:{safe_get(row,'xhr'):.1%} CoreSig:{safe_get(row,'sgeo'):.1%}
CrossCook:{safe_get(row,'cookie_samesite_none'):.1%} Iframes:{safe_get(row,'iframe'):.1%}
Referrer:{safe_get(row,'referer_leaked'):.1%} Beacons:{safe_get(row,'beacon'):.1%}
Pixels:{safe_get(row,'image'):.1%} Trackers:{safe_get(row,'trackers',0.0):.1f} Companies:{safe_get(row,'companies',0.0):.1f}

You also answer general questions about: the PrivacyLens app, how scores are calculated,
what each signal means (XHR, beacons, cookies, iframes, referrer, fingerprinting),
the WhoTracks.me dataset, the Analytics Dashboard charts (histograms, scatter plots,
heatmaps, radar charts, box plots, rankings), and how to protect privacy online.

Reply in {chosen_lang}. Be concise. Use bullets for lists. Plain language only."""

    if not api_key:
        st.markdown(f"""<div style="padding:20px 24px;background:{T['ink3']};
          border:1px solid {T['line2']};border-radius:6px;text-align:center">
          <div style="font-family:'DM Mono',monospace;font-size:11px;color:{T['chalk3']};line-height:2">
            Add <code style="color:{T['sky']};background:{T['ink4']};padding:2px 8px;border-radius:3px">GROQ_API_KEY=gsk_...</code>
            to your <code style="color:{T['sky']};background:{T['ink4']};padding:2px 8px;border-radius:3px">.env</code>
            to enable the AI assistant.
          </div></div>""", unsafe_allow_html=True)
    else:
        # FIX 2: quick prompts only shown when no chat yet — hidden once conversation starts
        if not st.session_state.chat_msgs:
            eyebrow("Quick Prompts")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            qc = st.columns(3)
            quick = [f"What is the biggest risk on {sel_site}?",
                     f"Is {sel_site} safe to use?",
                     f"How do I protect myself on {sel_site}?"]
            for i,(col,prompt) in enumerate(zip(qc,quick)):
                with col:
                    if st.button(prompt, key=f"qp_{sel_site}_{i}", use_container_width=True):
                        st.session_state.chat_msgs.append({"role":"user","content":prompt})
                        with st.spinner("Analysing…"):
                            reply = call_groq(st.session_state.chat_msgs, system_prompt, api_key)
                        st.session_state.chat_msgs.append({"role":"assistant","content":reply})
                        st.rerun()

        for msg in st.session_state.chat_msgs:
            with st.chat_message(msg["role"], avatar="🧑" if msg["role"]=="user" else "🔍"):
                st.markdown(msg["content"])

        # FIX 3: counter-based key forces Streamlit to remount the text_input
        # clean after every sent message — no manual clearing needed
        if "chat_input_counter" not in st.session_state:
            st.session_state.chat_input_counter = 0

        # FIX 1: align Send button with input using CSS flex on a wrapper div
        st.markdown(f"""
        <style>
        div[data-testid="stHorizontalBlock"]:has(> div > div[data-testid="stTextInput"]) {{
            align-items: flex-end !important;
        }}
        </style>""", unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        input_col, btn_col = st.columns([5,1])
        with input_col:
            user_input = st.text_input(
                "chat_inline",
                placeholder=f"Ask about {sel_site}, tracking methods, charts, dataset…",
                label_visibility="collapsed",
                key=f"chat_text_{sel_site}_{st.session_state.chat_input_counter}",
            )
        with btn_col:
            send_clicked = st.button("Send →", key=f"chat_send_{sel_site}_{st.session_state.chat_input_counter}", use_container_width=True)

        if send_clicked and user_input and user_input.strip():
            msg_text = user_input.strip()
            st.session_state.chat_msgs.append({"role":"user","content":msg_text})
            with st.spinner("Analysing…"):
                reply = call_groq(st.session_state.chat_msgs, system_prompt, api_key)
            st.session_state.chat_msgs.append({"role":"assistant","content":reply})
            # increment counter → new key → input widget remounts empty
            st.session_state.chat_input_counter += 1
            st.rerun()

        if st.session_state.chat_msgs:
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            if st.button("Clear conversation", key=f"clear_{sel_site}"):
                st.session_state.chat_msgs = []
                st.session_state.chat_input_counter = 0
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── FAQ
    sep()
    st.markdown(f'<div class="pl-section">', unsafe_allow_html=True)
    card_section("❓","Privacy FAQ","Everything you need to know about web tracking")
    faqs = [
        ("🔐  Why is online privacy needed?", T["sky"],
         "Every website you visit builds a profile — your interests, income bracket, health concerns, political views, and daily routines. This data is bought and sold without your direct consent. Privacy isn't about hiding something; it's about controlling your own narrative."),
        ("⚠️  Why should you be aware of tracking?", T["amber"],
         "Most tracking is invisible. A single webpage can fire 50+ hidden requests to third-party companies before you read the first paragraph. These aren't just ad companies — they include data brokers who sell your profile to insurers, employers, and governments."),
        ("📱  How does tracking impact your daily life?", T["red"],
         "Tracking shapes what you pay (dynamic pricing), what you see (filter bubbles), what you buy (dark patterns), and your access to services (insurance risk scoring). Studies show tracked users pay higher prices for flights, hotels, and loans."),
        ("🛡️  How to protect yourself from tracking?", T["lime"],
         "Use Firefox or Brave with uBlock Origin. Enable DNS-over-HTTPS. Use container tabs. Search with DuckDuckGo. On mobile, disable ad tracking in OS settings. Review app permissions. Use PrivacyLens to audit websites before trusting them with your data."),
    ]
    for title,accent,body in faqs:
        with st.expander(title):
            st.markdown(f"""<div style="padding:4px 0 4px 14px;border-left:2px solid {accent};
                 font-family:'DM Sans',sans-serif;font-size:13px;color:{T['chalk2']};line-height:1.8">{body}</div>""",
                 unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — ANALYTICS DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
else:
    dfw   = add_tier_col(df)
    n_cat = dfw["category"].nunique() if "category" in dfw.columns else "—"

    st.markdown(f"""
    <div style="padding-bottom:20px;border-bottom:1px solid {T['line']};margin-bottom:24px">
      <div class="eyebrow" style="margin-bottom:8px">📊 Analytics Dashboard</div>
      <h1 style="font-family:'Fraunces',serif !important;font-size:34px;font-weight:300;
           color:{T['chalk']} !important;letter-spacing:-.04em;margin:0 0 6px">Analytics Dashboard</h1>
      <p style="color:{T['chalk4']};font-size:13px;font-family:'DM Sans',sans-serif;margin:0">
        {len(dfw):,} websites · {n_cat} categories · full visual intelligence</p>
    </div>""", unsafe_allow_html=True)

    k1,k2,k3,k4,k5,k6 = st.columns(6)
    k1.metric("Total Sites",    f"{len(dfw):,}")
    k2.metric("Avg Risk Score", f"{dfw['privacy_score'].mean():.1f}")
    k3.metric("High Risk",      f"{(dfw['privacy_score']>60).sum():,}")
    k4.metric("Private",        f"{(dfw['privacy_score']<20).sum():,}")
    k5.metric("Avg Trackers",   f"{dfw['trackers'].mean():.1f}" if "trackers" in dfw.columns else "—")
    k6.metric("Avg Companies",  f"{dfw['companies'].mean():.1f}" if "companies" in dfw.columns else "—")

    sep()

    cat_avg = pd.Series(dtype=float)
    if "category" in dfw.columns:
        cat_avg = dfw.groupby("category")["privacy_score"].mean().sort_values(ascending=False)

    def sec(text, sub=""):
        s2 = f'<div style="font-size:12px;color:{T["chalk5"]};margin-top:3px;font-family:\'DM Sans\',sans-serif">{sub}</div>' if sub else ""
        st.markdown(f"""<div style="margin:1.8rem 0 1.2rem;display:flex;align-items:baseline;gap:10px">
          <span style="font-family:'DM Mono',monospace;font-size:9px;color:{T['chalk5']};letter-spacing:.2em">◈</span>
          <div><span style="font-family:'Fraunces',serif;font-size:18px;font-weight:300;
               color:{T['chalk2']};letter-spacing:-.02em">{text}</span>{s2}</div>
          <div style="flex:1;height:1px;background:{T['line']};margin-left:8px;margin-bottom:2px"></div>
        </div>""", unsafe_allow_html=True)

    def view_data_expander(label, data_df, key):
        with st.expander(f"📋  View Data — {label}"):
            st.dataframe(data_df.reset_index(drop=True), use_container_width=True)

    def tier_clr(v):
        if v<20: return T["lime"]
        if v<40: return T["sky"]
        if v<60: return T["amber"]
        if v<80: return T["red"]
        return T["rose"]

    sec("Score Overview")
    ra1,ra2,ra3 = st.columns(3)
    with ra1:
        fig = px.histogram(dfw, x="privacy_score", nbins=30, title="Score Distribution",
                           color_discrete_sequence=[T["sky"]])
        fig.update_layout(**PLOTLY_BASE, height=260)
        fig.update_traces(marker_line_color=T["ink0"], marker_line_width=0.3, marker_opacity=0.8)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        hd = dfw["privacy_score"].describe().reset_index(); hd.columns=["Statistic","Value"]
        view_data_expander("Score Distribution", hd, "score_dist")
    with ra2:
        tc = dfw["tier"].value_counts().reindex(TIER_ORDER).fillna(0)
        fig = go.Figure(go.Pie(
            labels=tc.index.tolist(), values=tc.values.tolist(),
            marker_colors=[TIER_COLORS[t] for t in tc.index],
            hole=0.65, textinfo="label+percent",
            textfont_size=9, textfont_color=T["chalk3"]))
        fig.update_layout(**{**PLOTLY_BASE,"title":{"text":"Risk Tiers","font":{"size":11}},"height":260,"showlegend":False,
            "annotations":[dict(text=f"{len(dfw):,}",font_size=14,showarrow=False,
                               font_color=T["chalk3"],font_family="DM Mono")]})
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        td = tc.reset_index(); td.columns=["Tier","Count"]
        view_data_expander("Risk Tiers", td, "risk_tiers")
    with ra3:
        fig = go.Figure()
        for t in TIER_ORDER:
            sub = dfw[dfw["tier"]==t]["privacy_score"]
            if len(sub):
                fig.add_trace(go.Box(y=sub, name=t, marker_color=TIER_COLORS[t],
                    line_color=TIER_COLORS[t], fillcolor=hex_rgba(TIER_COLORS[t], 0.08), line_width=1.2))
        fig.update_layout(**{**PLOTLY_BASE,"title":{"text":"Score by Tier","font":{"size":11}},"height":260,"showlegend":False,
            "xaxis":dict(gridcolor=T["line"],tickfont_size=9),"yaxis":dict(gridcolor=T["line"])})
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        view_data_expander("Score by Tier", dfw.groupby("tier")["privacy_score"].describe().round(2), "score_by_tier")

    if "category" in dfw.columns and len(cat_avg):
        sec("Category Analysis")
        rb1,rb2 = st.columns(2)
        with rb1:
            cc = [TIER_COLORS.get(
                "Private" if v<20 else "Low Risk" if v<40 else "Moderate" if v<60 else "High Risk" if v<80 else "Critical",
                T["red"]) for v in cat_avg.values]
            fig = go.Figure(go.Bar(x=cat_avg.values, y=cat_avg.index, orientation="h",
                marker_color=cc, marker_line_color=T["ink0"], marker_line_width=0.3, marker_opacity=0.85,
                text=[f"{v:.1f}" for v in cat_avg.values], textposition="outside",
                textfont=dict(color=T["chalk4"],size=9,family="DM Mono")))
            fig.update_layout(**{**PLOTLY_BASE,"title":{"text":"Avg Risk by Category","font":{"size":11}},"height":320,
                "xaxis":dict(gridcolor=T["line"]),"yaxis":dict(autorange="reversed",gridcolor=RGBA0)})
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            cad = cat_avg.reset_index(); cad.columns=["Category","Avg Risk Score"]
            view_data_expander("Avg Risk by Category", cad, "avg_risk_cat")
        with rb2:
            fig = px.box(dfw, x="category", y="privacy_score", title="Score Distribution by Category",
                color="category",
                color_discrete_sequence=[T["sky"],T["lime"],T["gold"],T["amber"],T["red"],T["rose"],T["chalk4"],"#34d399","#fb7185","#38bdf8"])
            fig.update_layout(**{**PLOTLY_BASE,"height":320,"showlegend":False,
                "xaxis":dict(tickangle=-30,gridcolor=T["line"],tickfont_size=9),"yaxis":dict(gridcolor=T["line"])})
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            view_data_expander("Score by Category", dfw.groupby("category")["privacy_score"].describe().round(2), "score_dist_cat")

        rb3,rb4 = st.columns(2)
        with rb3:
            ccnt = dfw["category"].value_counts()
            pal  = [T["sky"],T["lime"],T["gold"],T["amber"],T["red"],T["rose"],T["chalk4"],"#34d399","#fb7185","#38bdf8"]
            fig  = go.Figure(go.Bar(x=ccnt.index.tolist(), y=ccnt.values.tolist(),
                marker_color=pal[:len(ccnt)], marker_opacity=0.85,
                text=ccnt.values.tolist(), textposition="outside",
                textfont=dict(color=T["chalk4"],size=9)))
            fig.update_layout(**{**PLOTLY_BASE,"title":{"text":"Sites per Category","font":{"size":11}},"height":270,
                "xaxis":dict(tickangle=-30,gridcolor=RGBA0,tickfont_size=9),"yaxis":dict(gridcolor=T["line"])})
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            ccd = ccnt.reset_index(); ccd.columns=["Category","Site Count"]
            view_data_expander("Sites per Category", ccd, "sites_per_cat")
        with rb4:
            top_cats = cat_avg.head(5).index.tolist()
            radsig   = [s for s in ["script","xhr","cookie_samesite_none","beacon","iframe","referer_leaked"] if s in dfw.columns]
            fig      = go.Figure()
            cr       = [T["red"],T["amber"],T["gold"],T["lime"],T["sky"]]
            rrows    = []
            for cat,c in zip(top_cats,cr):
                sub  = dfw[dfw["category"]==cat]
                vals = [sub[s].mean() for s in radsig]
                fig.add_trace(go.Scatterpolar(r=vals+[vals[0]], theta=radsig+[radsig[0]],
                    fill="toself", name=cat,
                    fillcolor=hex_rgba(c,0.08), line=dict(color=c,width=1.5)))
                rrows.append({"Category":cat,**{s:round(v,3) for s,v in zip(radsig,vals)}})
            fig.update_layout(**{**PLOTLY_BASE,
                "title":{"text":"Signal Radar — Top 5 Riskiest Categories","font":{"size":11}},"height":270,
                "polar":dict(bgcolor=RGBA0,
                    radialaxis=dict(visible=True,range=[0,1],gridcolor=T["line"],tickfont=dict(size=7,color=T["chalk5"])),
                    angularaxis=dict(gridcolor=T["line"],tickfont=dict(size=9,color=T["chalk4"])))})
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            view_data_expander("Signal Radar Data", pd.DataFrame(rrows), "radar_data")

    sec("Signal Deep-Dives")
    corr_cols = [c for c in ["script","xhr","sgeo","iframe","cookie_samesite_none","referer_leaked",
                              "beacon","image","tracked","cookies","bad_qs","privacy_score"] if c in dfw.columns]
    if len(corr_cols) > 1:
        cm   = dfw[corr_cols].corr().round(2)
        labs = [SIGNAL_LABELS.get(c,c) for c in corr_cols]
        fig  = go.Figure(go.Heatmap(z=cm.values, x=labs, y=labs,
            colorscale=[[0,hex_rgba(T["lime"],0.6)],[0.5,hex_rgba(T["amber"],0.5)],[1,hex_rgba(T["red"],0.7)]],
            zmin=-1, zmax=1, text=cm.values.round(2), texttemplate="%{text}", textfont_size=9))
        fig.update_layout(**{**PLOTLY_BASE,"title":{"text":"Signal Correlation Matrix","font":{"size":11}},"height":420,
            "xaxis":dict(tickangle=-40,tickfont_size=8),"yaxis":dict(tickfont_size=8,autorange="reversed"),
            "margin":dict(l=100,r=10,t=38,b=90)})
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        cd = cm.copy(); cd.index=labs; cd.columns=labs
        view_data_expander("Correlation Matrix", cd.reset_index(), "corr_matrix")

    rc_cols = st.columns(3)
    for i,(ck,title,clr) in enumerate([
            ("script","JS Script Intensity",T["sky"]),
            ("xhr","XHR Background Calls",T["lime"]),
            ("beacon","Beacon Pings",T["red"]),
            ("cookie_samesite_none","Cross-Site Cookies",T["amber"]),
            ("iframe","Hidden Iframes",T["gold"]),
            ("referer_leaked","Referrer Leaking",T["rose"])]):
        if ck in dfw.columns:
            fig = px.histogram(dfw, x=ck, nbins=25, title=title, color_discrete_sequence=[clr])
            fig.update_layout(**{**PLOTLY_BASE,"height":230,
                "xaxis":dict(gridcolor=T["line"]),"yaxis":dict(gridcolor=T["line"])})
            fig.update_traces(marker_opacity=0.8)
            with rc_cols[i%3]:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
                cd2 = dfw[ck].describe().reset_index(); cd2.columns=["Statistic","Value"]
                view_data_expander(title, cd2, f"hist_{ck}")

    sec("Signal Relationships")
    rd1,rd2 = st.columns(2)
    with rd1:
        if "script" in dfw.columns and "xhr" in dfw.columns:
            sc   = ["script","xhr","privacy_score","site"] + (["category"] if "category" in dfw.columns else [])
            samp = safe_sample(dfw[sc].dropna(subset=["script","xhr"]))
            fig  = px.scatter(samp, x="script", y="xhr", color="privacy_score",
                color_continuous_scale=[[0,T["lime"]],[0.4,T["sky"]],[0.7,T["amber"]],[1,T["red"]]],
                title="Script vs XHR (coloured by risk)", opacity=0.5,
                hover_data={"site":True,"privacy_score":True})
            fig.update_layout(**{**PLOTLY_BASE,"height":290,
                "xaxis":dict(gridcolor=T["line"]),"yaxis":dict(gridcolor=T["line"]),
                "coloraxis_colorbar":dict(title="Score",tickfont_color=T["chalk4"])})
            fig.update_traces(marker_size=3.5)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            view_data_expander("Script vs XHR", samp[["site","script","xhr","privacy_score"]].round(3), "script_xhr")
    with rd2:
        if "trackers" in dfw.columns and "companies" in dfw.columns:
            tc2  = ["trackers","companies","site"] + (["category"] if "category" in dfw.columns else [])
            samp = safe_sample(dfw[tc2].dropna(subset=["trackers","companies"]))
            fig  = px.scatter(samp, x="trackers", y="companies",
                color="category" if "category" in samp.columns else None,
                title="Trackers vs Companies", opacity=0.5, hover_data={"site":True})
            fig.update_layout(**{**PLOTLY_BASE,"height":290,
                "xaxis":dict(gridcolor=T["line"]),"yaxis":dict(gridcolor=T["line"])})
            fig.update_traces(marker_size=3.5)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            view_data_expander("Trackers vs Companies", samp[["site","trackers","companies"]].round(2), "track_comp")

    rd3,rd4 = st.columns(2)
    with rd3:
        if "popularity" in dfw.columns:
            pd2 = dfw[dfw["popularity"]>0].copy()
            if len(pd2):
                pc   = ["popularity","privacy_score","site"] + (["category"] if "category" in pd2.columns else [])
                samp = safe_sample(pd2[pc])
                fig  = px.scatter(samp, x="popularity", y="privacy_score",
                    color="category" if "category" in samp.columns else None,
                    log_x=True, title="Popularity vs Privacy Score", opacity=0.55,
                    hover_data={"site":True})
                fig.update_layout(**{**PLOTLY_BASE,"height":270,
                    "xaxis":dict(gridcolor=T["line"],title="Popularity (log)"),
                    "yaxis":dict(gridcolor=T["line"],title="Risk Score")})
                fig.update_traces(marker_size=3.5)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
                view_data_expander("Popularity vs Risk", samp[["site","popularity","privacy_score"]].round(4), "pop_risk")
    with rd4:
        if "requests" in dfw.columns and "requests_tracking" in dfw.columns:
            rdf  = dfw[dfw["requests"]<500].copy()
            if len(rdf):
                samp = safe_sample(rdf[["requests","requests_tracking","privacy_score","site"]])
                fig  = px.scatter(samp, x="requests", y="requests_tracking", color="privacy_score",
                    color_continuous_scale=[[0,T["lime"]],[0.5,T["amber"]],[1,T["red"]]],
                    title="Total vs Tracking Requests", opacity=0.5, hover_data={"site":True})
                fig.update_layout(**{**PLOTLY_BASE,"height":270,
                    "xaxis":dict(gridcolor=T["line"]),"yaxis":dict(gridcolor=T["line"])})
                fig.update_traces(marker_size=3.5)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
                view_data_expander("Total vs Tracking Requests",
                    samp[["site","requests","requests_tracking","privacy_score"]].round(2), "req_track")

    sec("Tracker & Company Analysis")
    re1,re2,re3 = st.columns(3)
    with re1:
        if "trackers" in dfw.columns:
            fig = px.histogram(dfw, x="trackers", nbins=30, title="Trackers per Site",
                               color_discrete_sequence=[T["sky"]])
            fig.update_layout(**{**PLOTLY_BASE,"height":230,
                "xaxis":dict(gridcolor=T["line"]),"yaxis":dict(gridcolor=T["line"])})
            fig.update_traces(marker_opacity=0.8)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            view_data_expander("Trackers per Site",
                dfw["trackers"].describe().reset_index().rename(columns={"index":"Stat","trackers":"Value"}),
                "trackers_hist")
    with re2:
        if "companies" in dfw.columns:
            fig = px.histogram(dfw, x="companies", nbins=30, title="Companies per Site",
                               color_discrete_sequence=[T["lime"]])
            fig.update_layout(**{**PLOTLY_BASE,"height":230,
                "xaxis":dict(gridcolor=T["line"]),"yaxis":dict(gridcolor=T["line"])})
            fig.update_traces(marker_opacity=0.8)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            view_data_expander("Companies per Site",
                dfw["companies"].describe().reset_index().rename(columns={"index":"Stat","companies":"Value"}),
                "companies_hist")
    with re3:
        if "category" in dfw.columns and "trackers" in dfw.columns:
            ct  = dfw.groupby("category")["trackers"].mean().sort_values(ascending=False)
            fig = go.Figure(go.Bar(x=ct.index.tolist(), y=ct.values.tolist(),
                marker_color=T["sky"], marker_opacity=0.85,
                text=ct.values.round(1).tolist(), textposition="outside",
                textfont=dict(color=T["chalk4"],size=9)))
            fig.update_layout(**{**PLOTLY_BASE,"title":{"text":"Avg Trackers by Category","font":{"size":11}},"height":230,
                "xaxis":dict(tickangle=-30,gridcolor=RGBA0,tickfont_size=9),"yaxis":dict(gridcolor=T["line"])})
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            ctd = ct.reset_index(); ctd.columns=["Category","Avg Trackers"]
            view_data_expander("Avg Trackers by Category", ctd, "avg_trackers_cat")

    if "category" in dfw.columns:
        sec("Category × Signal Heatmap")
        sch = [c for c in ["script","xhr","cookie_samesite_none","beacon","iframe","referer_leaked",
                            "image","tracked","cookies","bad_qs"] if c in dfw.columns]
        if sch:
            hdf = dfw.groupby("category")[sch].mean().round(3)
            fig = go.Figure(go.Heatmap(z=hdf.values,
                x=[SIGNAL_LABELS.get(c,c) for c in sch], y=hdf.index.tolist(),
                colorscale=[[0,hex_rgba(T["lime"],0.7)],[0.4,hex_rgba(T["amber"],0.6)],
                            [0.7,hex_rgba(T["red"],0.7)],[1,hex_rgba(T["rose"],0.8)]],
                text=hdf.values.round(2), texttemplate="%{text}", textfont_size=9,
                colorbar=dict(title="Avg",tickfont_color=T["chalk4"])))
            fig.update_layout(**{**PLOTLY_BASE,
                "title":{"text":"Avg Signal Intensity — Category × Technique","font":{"size":11}},"height":340,
                "xaxis":dict(tickangle=-30,tickfont_size=9),"yaxis":dict(tickfont_size=9),
                "margin":dict(l=110,r=70,t=38,b=90)})
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            view_data_expander("Category × Signal Data", hdf.reset_index(), "cat_signal_heat")

    sec("Rankings & Extremes")
    rg1,rg2 = st.columns(2)
    with rg1:
        rcols = ["site","privacy_score"] + (["category"] if "category" in dfw.columns else [])
        top20 = dfw.nlargest(20,"privacy_score")[rcols]
        fig   = go.Figure(go.Bar(
            x=top20["privacy_score"].tolist(), y=top20["site"].tolist(), orientation="h",
            marker_color=[tier_clr(v) for v in top20["privacy_score"]], marker_opacity=0.85,
            text=top20["privacy_score"].round(1).tolist(), textposition="outside",
            textfont=dict(color=T["chalk4"],size=9,family="DM Mono"),
            hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>"))
        fig.update_layout(**{**PLOTLY_BASE,"title":{"text":"Top 20 Highest Risk Sites","font":{"size":11}},"height":490,
            "xaxis":dict(range=[0,108],gridcolor=T["line"]),
            "yaxis":dict(autorange="reversed",tickfont_size=9,gridcolor=RGBA0)})
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        view_data_expander("Top 20 Highest Risk", top20.round(2), "top20_risk")
    with rg2:
        bot20 = dfw.nsmallest(20,"privacy_score")[["site","privacy_score"]]
        fig   = go.Figure(go.Bar(
            x=bot20["privacy_score"].tolist(), y=bot20["site"].tolist(), orientation="h",
            marker_color=T["lime"], marker_opacity=0.85,
            text=bot20["privacy_score"].round(1).tolist(), textposition="outside",
            textfont=dict(color=T["chalk4"],size=9,family="DM Mono")))
        fig.update_layout(**{**PLOTLY_BASE,"title":{"text":"Top 20 Most Private Sites","font":{"size":11}},"height":490,
            "xaxis":dict(range=[0,30],gridcolor=T["line"]),
            "yaxis":dict(autorange="reversed",tickfont_size=9,gridcolor=RGBA0)})
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        view_data_expander("Top 20 Most Private", bot20.round(2), "top20_private")

    sec("Network Request Analysis")
    rh1,rh2,rh3 = st.columns(3)
    with rh1:
        if "track_ratio" in dfw.columns:
            pd3 = dfw[dfw["requests"]>0]
            if len(pd3):
                fig = px.histogram(pd3, x="track_ratio", nbins=30, title="Tracking Request Ratio",
                                   color_discrete_sequence=[T["amber"]])
                fig.update_layout(**{**PLOTLY_BASE,"height":240,
                    "xaxis":dict(tickformat=".0%",gridcolor=T["line"]),"yaxis":dict(gridcolor=T["line"])})
                fig.update_traces(marker_opacity=0.8)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
                view_data_expander("Tracking Request Ratio", pd3["track_ratio"].describe().reset_index(), "track_ratio")
    with rh2:
        if "hosts" in dfw.columns:
            pd4 = dfw[dfw["hosts"]<40]
            if len(pd4):
                fig = px.histogram(pd4, x="hosts", nbins=30, title="Distinct Hosts per Page",
                                   color_discrete_sequence=[T["sky"]])
                fig.update_layout(**{**PLOTLY_BASE,"height":240,
                    "xaxis":dict(gridcolor=T["line"]),"yaxis":dict(gridcolor=T["line"])})
                fig.update_traces(marker_opacity=0.8)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
                view_data_expander("Distinct Hosts", pd4["hosts"].describe().reset_index(), "hosts_hist")
    with rh3:
        if "category" in dfw.columns and "requests_tracking" in dfw.columns:
            cr2 = dfw.groupby("category")["requests_tracking"].mean().sort_values(ascending=False)
            fig = go.Figure(go.Bar(x=cr2.values.tolist(), y=cr2.index.tolist(), orientation="h",
                marker_color=T["red"], marker_opacity=0.85,
                text=cr2.values.round(1).tolist(), textposition="outside",
                textfont=dict(color=T["chalk4"],size=9)))
            fig.update_layout(**{**PLOTLY_BASE,"title":{"text":"Avg Tracking Requests by Category","font":{"size":11}},"height":240,
                "xaxis":dict(gridcolor=T["line"]),"yaxis":dict(autorange="reversed",gridcolor=RGBA0)})
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            crd = cr2.reset_index(); crd.columns=["Category","Avg Tracking Requests"]
            view_data_expander("Avg Tracking Requests", crd, "avg_req_cat")

    sec("Advanced Tracking Methods")
    ri1,ri2,ri3 = st.columns(3)
    with ri1:
        if "image" in dfw.columns:
            fig = px.histogram(dfw, x="image", nbins=25, title="Tracking Pixels",
                               color_discrete_sequence=[T["rose"]])
            fig.update_layout(**{**PLOTLY_BASE,"height":230,
                "xaxis":dict(gridcolor=T["line"]),"yaxis":dict(gridcolor=T["line"])})
            fig.update_traces(marker_opacity=0.8)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            view_data_expander("Tracking Pixels", dfw["image"].describe().reset_index(), "pixels_data")
    with ri2:
        if "bad_qs" in dfw.columns:
            fig = px.histogram(dfw, x="bad_qs", nbins=25, title="URL Fingerprinting",
                               color_discrete_sequence=[T["gold"]])
            fig.update_layout(**{**PLOTLY_BASE,"height":230,
                "xaxis":dict(gridcolor=T["line"]),"yaxis":dict(gridcolor=T["line"])})
            fig.update_traces(marker_opacity=0.8)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            view_data_expander("URL Fingerprinting", dfw["bad_qs"].describe().reset_index(), "url_fp_data")
    with ri3:
        if "it2" in dfw.columns:
            fig = px.histogram(dfw, x="it2", nbins=25, title="Core Combo: Script × XHR",
                               color_discrete_sequence=[T["amber"]])
            fig.update_layout(**{**PLOTLY_BASE,"height":230,
                "xaxis":dict(gridcolor=T["line"]),"yaxis":dict(gridcolor=T["line"])})
            fig.update_traces(marker_opacity=0.8)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            view_data_expander("Script × XHR Combo", dfw["it2"].describe().reset_index(), "it2_data")

    sep()
    eyebrow("Full Dataset")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    ts1,ts2,ts3 = st.columns([1,1,2])
    with ts1:
        sopts    = [c for c in ["privacy_score","trackers","companies","popularity"] if c in dfw.columns]
        sort_col = st.selectbox("Sort by", sopts)
    with ts2:
        sort_asc = st.selectbox("Order", ["Highest first","Lowest first"]) == "Lowest first"
    with ts3:
        tier_filter = st.multiselect("Filter by tier", TIER_ORDER, default=TIER_ORDER)
    tcols = [c for c in ["site","category","privacy_score","tier","script","xhr","sgeo",
                          "cookie_samesite_none","iframe","referer_leaked","beacon","image",
                          "tracked","trackers","companies","popularity"] if c in dfw.columns]
    ft = dfw[dfw["tier"].isin(tier_filter)] if tier_filter else dfw
    st.dataframe(ft[tcols].sort_values(sort_col, ascending=sort_asc).head(200),
                 use_container_width=True, height=400)
    st.caption(f"Showing 200 of {len(ft):,} matching records")

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
sep()
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
     padding:8px 0 16px;flex-wrap:wrap;gap:10px">
  <span style="font-family:'Fraunces',serif;font-size:15px;font-weight:300;color:{T['chalk2']}">
    Privacy<span style="color:{T['gold']}">Lens</span></span>
  <span style="font-family:'DM Mono',monospace;font-size:10px;color:{T['chalk4']};letter-spacing:.04em">
    WhoTracks.me · HTTP-level analysis · Does not include fingerprinting or app-level tracking</span>
</div>""", unsafe_allow_html=True)