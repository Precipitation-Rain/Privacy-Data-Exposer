# 🔍 PrivacyLens — Privacy Data Exposer

> **Discover which websites track you, what data they collect, how they collect it, and how safe your data really is.**

PrivacyLens is a Streamlit web app that turns raw web-tracking data (from [WhoTracks.me](https://whotracks.me)) into actionable privacy intelligence. Search any website, get a 0–100 Privacy Risk Score, and let an AI chatbot explain what it means — in plain English or your preferred language.

---

## Features

**Score Analyzer**
- Search any website by name or category
- Instant 0–100 Privacy Risk Score with a gauge chart
- See *what* data is collected (identity, cross-site cookies, browsing history, etc.)
- See *how* it's collected (JS scripts, XHR calls, tracking pixels, beacons, iframes)
- See *why* — behavioural profiling, real-time bidding auctions, data broker sales
- Full score breakdown with weighted signal bars
- Compare against the category average
- Per-site AI chatbot (Groq / LLaMA-3-70B) — supports 20+ languages including Hindi, Bengali, Tamil, and more

**Analytics Dashboard**
- Fleet-level risk distribution across all sites
- Tier breakdown: Private → Low Risk → Moderate → High Risk → Critical
- Signal correlation heatmap
- Top trackers by category
- Radar chart comparing tracking signals per site

---

## Tech Stack

| Layer | Technology |
|---|---|
| App framework | Streamlit ≥ 1.32 |
| Data processing | Pandas ≥ 2.0, NumPy ≥ 1.24 |
| Visualisation | Plotly ≥ 5.18 |
| AI chatbot | Groq API (llama3-70b-8192) |
| Data source | WhoTracks.me April 2026 — `sites.csv` |
| Config | python-dotenv |

---

## Scoring Engine

The Privacy Risk Score (0–100) is a **rule-based, no-ML** weighted formula computed from real tracker signals in the dataset:

```
privacy_score = weighted_sum(signals) / total_weight × 100
```

| Signal | Weight | Description |
|---|---|---|
| `sgeo` (√script × xhr) | 0.50 | Core composite — active JS + background requests |
| `it2` (script × xhr) | 0.30 | Interaction term for simultaneous script + XHR |
| `referer_leaked` | 0.10 | Navigation history sent to third parties |
| `it3` (iframe × sgeo) | 0.10 | Iframe-amplified tracking |
| `it1` (cookie_samesite_none × sgeo) | 0.05 | Cross-site cookie + script combo |
| `cookie_samesite_none` | 0.03 | Standalone cross-site cookie signal |
| `iframe` | 0.03 | Embedded hidden frames |
| `beacon` | 0.02 | Post-unload tracking pings |

**Risk tiers:**

| Score | Tier |
|---|---|
| 0 – 19 | 🟢 PRIVATE |
| 20 – 39 | 🔵 LOW RISK |
| 40 – 59 | 🟡 MODERATE |
| 60 – 79 | 🔴 HIGH RISK |
| 80 – 100 | 🟣 CRITICAL |

---

## Project Structure

```
Privacy-Data-Exposer/
├── app.py                     # Main Streamlit application (1659 lines)
├── sites.csv                  # WhoTracks.me global sites dataset
├── whotracks_2026/
│   └── sites.csv              # Alternative dataset path (auto-detected)
├── PrivacyRiskScorer_EDA.ipynb # Exploratory data analysis notebook
├── requirements.txt
├── .gitignore
└── .env                       # (not committed) — store GROQ_API_KEY here
```

---

## Setup & Run

**1. Clone the repo**
```bash
git clone https://github.com/Precipitation-Rain/Privacy-Data-Exposer.git
cd Privacy-Data-Exposer
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your Groq API key** (optional — needed for AI chatbot)

Create a `.env` file:
```
GROQ_API_KEY=gsk_your_key_here
```
Get a free key at [console.groq.com](https://console.groq.com).

**4. Run the app**
```bash
streamlit run app.py
```

The app auto-detects `sites.csv` from the project root or `whotracks_2026/sites.csv`. If neither exists, you can upload a CSV directly from the sidebar.

---

## Data

The app uses the **WhoTracks.me April 2026** dataset (`sites.csv`, ~260K rows), filtered to `country == 'global'`.

Columns used for scoring: `script`, `xhr`, `iframe`, `cookie_samesite_none`, `referer_leaked`, `beacon`, `image`, `tracked`, `cookies`, `bad_qs`, `media`.

Columns excluded due to data quality issues: `has_blocking` (all zeros), `t_active` (corrupted negatives), `plugin`.

You can also bring your own WhoTracks.me-compatible CSV — just drop it in the sidebar uploader (max 50 MB).

---

## AI Chatbot

The per-site AI assistant is powered by **Groq's LLaMA-3-70B** and knows the full scoring context for the selected site. It supports 20+ languages (English, Hindi, Bengali, Tamil, Marathi, and more) and maintains per-site conversation history — switching sites resets the chat.

Rate limiting: 3-second cooldown between requests per session. Chat history is capped at 20 messages per API call to stay within token limits.

---

## License

This project is open-source. Data is sourced from [WhoTracks.me](https://whotracks.me) under their respective terms.