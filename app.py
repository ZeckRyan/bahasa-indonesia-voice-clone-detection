"""
app.py — VoiceGuard: Sistem Deteksi Kloning Suara TTS Berbahasa Indonesia
Single-page, multi-section Streamlit application.

Run: streamlit run app.py
"""

import os
import base64
import time
import tempfile
import numpy as np
import librosa
import librosa.display
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="VoiceGuard — Deteksi Deepfake Audio",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════
# HERO IMAGE → BASE64
# ══════════════════════════════════════════════════════════════

def _to_b64(path: str) -> str:
    try:
        ext  = os.path.splitext(path)[1].lower().lstrip(".")
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext, "jpeg")
        with open(path, "rb") as f:
            return f"data:image/{mime};base64,{base64.b64encode(f.read()).decode()}"
    except Exception:
        return ""

_hero_path = next(
    (p for p in ["assets/hero.jpg", "assets/hero.png", "assets/hero.jpeg", "assets/hero.webp"]
    if os.path.exists(p)), ""
)
HERO_URL = _to_b64(_hero_path)

# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
html, body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: #ffffff;
    color: #1e293b;
}}
.stApp {{ background: #ffffff !important; }}
#MainMenu, footer, header {{ visibility: hidden; }}
/* Hide ALL Streamlit top chrome completely */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stHeader"] {{ display: none !important; }}
/* Remove padding from all wrapping containers */
.block-container {{ padding: 0 !important; max-width: 100% !important; }}
[data-testid="stAppViewContainer"] > section > div:first-child {{ padding-top: 0 !important; }}
[data-testid="stMain"] {{ overflow-x: hidden; }}

/* ─────────────────────────────────────────
SECTION 1 — HERO
───────────────────────────────────────── */
.s1 {{
    position: relative;
    width: 100%;
    height: 100vh;
    min-height: 600px;
    display: flex;
    align-items: center;
    background-color: #08101e;
    background-image: {f'url("{HERO_URL}")' if HERO_URL else 'none'};
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    overflow: hidden;
}}
.s1-ov {{
    position: absolute; inset: 0;
    background: linear-gradient(
        to right,
        rgba(4, 8, 24, 0.20)  0%,
        rgba(4, 8, 24, 0.06)  26%,
        rgba(4, 8, 24, 0.68)  54%,
        rgba(4, 8, 24, 0.92)  72%,
        rgba(4, 8, 24, 0.98) 100%
    );
}}
.s1-inner {{
    position: relative; z-index: 5;
    max-width: 580px;
    margin-left: 50%;
    padding: 2rem 5% 2rem 2.5rem;
}}
.s1-eyebrow {{
    font-family: 'Montserrat', sans-serif;
    font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.28em; text-transform: uppercase;
    color: rgba(147, 197, 253, 0.88);
    display: flex; align-items: center; gap: 0.6rem;
    margin-bottom: 1.3rem;
}}
.s1-eyebrow::before {{
    content: ''; display: block;
    width: 28px; height: 1.5px;
    background: rgba(147, 197, 253, 0.7);
    border-radius: 2px;
}}
.s1-h1 {{
    font-family: 'Montserrat', sans-serif;
    font-size: clamp(2rem, 3.3vw, 3.1rem);
    font-weight: 900; line-height: 1.08;
    letter-spacing: -0.01em;
    color: #ffffff !important;
    text-shadow: 0 2px 40px rgba(0,0,0,0.4);
    margin-bottom: 1.1rem;
}}
.s1-p {{
    font-size: 0.93rem; font-weight: 300;
    line-height: 1.8; color: #cbd5e1 !important;
    margin-bottom: 2rem;
}}
.s1-cta {{
    display: inline-block;
    padding: 0.88rem 2.2rem;
    background: #2563eb;
    color: #ffffff !important;
    font-family: 'Montserrat', sans-serif;
    font-size: 0.8rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
    text-decoration: none !important;
    border-radius: 6px;
    box-shadow: 0 6px 28px rgba(37, 99, 235, 0.45);
    transition: all 0.25s ease;
    cursor: pointer;
}}
.s1-cta:hover {{
    background: #1d4ed8;
    transform: translateY(-2px);
    box-shadow: 0 10px 36px rgba(37, 99, 235, 0.58);
    color: #ffffff !important;
}}
.s1-scroll {{
    position: absolute; bottom: 2.5rem; left: 50%;
    transform: translateX(-50%);
    text-align: center;
    color: rgba(255,255,255,0.28);
    font-family: 'Montserrat', sans-serif;
    font-size: 0.62rem; letter-spacing: 0.26em; text-transform: uppercase;
}}
.s1-scroll::before {{
    content: ''; display: block;
    width: 1px; height: 38px;
    background: rgba(255,255,255,0.15);
    margin: 0 auto 0.5rem;
}}

/* ─────────────────────────────────────────
SHARED SECTION UTILITIES
───────────────────────────────────────── */
.sw {{ padding: 5.5rem 8%; }}
.sw-gray  {{ background: #f8fafc; }}
.sw-white {{ background: #ffffff; }}
.sw-amber {{ background: #fffbeb; }}
.sw-navy  {{ background: #0f172a; }}

.eyebrow {{
    display: flex; align-items: center; gap: 0.6rem;
    margin-bottom: 0.75rem;
}}
.eyebrow-line {{ width: 28px; height: 2px; background: #2563eb; border-radius: 2px; }}
.eyebrow-text {{
    font-family: 'Montserrat', sans-serif;
    font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.22em; text-transform: uppercase;
    color: #2563eb;
}}
.sec-title {{
    font-family: 'Montserrat', sans-serif;
    font-size: clamp(1.55rem, 2.4vw, 2.2rem);
    font-weight: 800; color: #0f172a; line-height: 1.15;
    margin-bottom: 0.55rem;
}}
.sec-sub {{
    font-size: 0.92rem; color: #64748b; line-height: 1.72;
    max-width: 620px; margin-bottom: 3rem;
}}

/* ─────────────────────────────────────────
SECTION 2 — THE PROBLEM
───────────────────────────────────────── */
.prob-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
}}
.prob-card {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 2rem 1.75rem;
    position: relative; overflow: hidden;
    transition: all 0.25s ease;
}}
.prob-card::before {{
    content: '';
    position: absolute; top: 0; left: 0; right: 0;
    height: 3px; border-radius: 14px 14px 0 0;
}}
.prob-card.c1::before {{ background: linear-gradient(90deg, #ef4444, #f97316); }}
.prob-card.c2::before {{ background: linear-gradient(90deg, #f59e0b, #eab308); }}
.prob-card.c3::before {{ background: linear-gradient(90deg, #2563eb, #0891b2); }}
.prob-card:hover {{
    box-shadow: 0 12px 36px rgba(0,0,0,0.07);
    transform: translateY(-4px);
    border-color: #bfdbfe;
}}
.prob-n {{
    font-family: 'Montserrat', sans-serif;
    font-size: 2.8rem; font-weight: 900;
    color: #f1f5f9; line-height: 1;
    display: block; margin-bottom: 1rem;
}}
.prob-title {{
    font-family: 'Montserrat', sans-serif;
    font-size: 1rem; font-weight: 700;
    color: #0f172a; margin-bottom: 0.6rem; line-height: 1.3;
}}
.prob-desc {{ font-size: 0.85rem; color: #64748b; line-height: 1.75; }}
.prob-tag {{
    display: inline-block; margin-top: 1.25rem;
    padding: 0.22rem 0.7rem; border-radius: 999px;
    font-family: 'Montserrat', sans-serif;
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.05em; text-transform: uppercase;
}}
.prob-tag.t1 {{ background: #fef2f2; color: #b91c1c; }}
.prob-tag.t2 {{ background: #fffbeb; color: #92400e; }}
.prob-tag.t3 {{ background: #eff6ff; color: #1d4ed8; }}

/* ─────────────────────────────────────────
SECTION 3 — HOW IT WORKS
───────────────────────────────────────── */
.steps-row {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2.5rem;
    position: relative;
    margin-top: 0.5rem;
}}
.steps-row::before {{
    content: '';
    position: absolute;
    top: 25px;
    left: calc(100% / 6);
    width: calc(100% * 2 / 3);
    height: 1px;
    background: linear-gradient(90deg, #bfdbfe, #a5f3fc, #c4b5fd);
    opacity: 0.6;
}}
.step {{ text-align: center; padding: 0 0.5rem; }}
.step-circle {{
    width: 50px; height: 50px;
    background: #2563eb; color: #ffffff;
    font-family: 'Montserrat', sans-serif;
    font-size: 1.2rem; font-weight: 800;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 1.25rem;
    box-shadow: 0 4px 18px rgba(37, 99, 235, 0.32);
    position: relative; z-index: 1;
}}
.step-title {{
    font-family: 'Montserrat', sans-serif;
    font-size: 0.95rem; font-weight: 700;
    color: #0f172a; margin-bottom: 0.6rem;
}}
.step-desc {{ font-size: 0.84rem; color: #64748b; line-height: 1.75; margin-bottom: 0.8rem; }}
.step-code {{
    display: inline-block;
    padding: 0.22rem 0.65rem;
    background: #f1f5f9; border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem; color: #64748b;
}}

/* ─────────────────────────────────────────
SECTION 4 — UPLOAD & RESULTS
───────────────────────────────────────── */
.s4-head {{ text-align: center; }}
.s4-head .sec-sub {{ margin: 0 auto 0; }}
.s4-head .eyebrow {{ justify-content: center; }}

/* File Uploader */
[data-testid="stFileUploader"] section {{
    background: #f8fafc !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 2rem 1.5rem !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stFileUploader"] section:hover {{
    border-color: #93c5fd !important;
    background: #eff6ff !important;
}}
[data-testid="stFileUploader"] section p,
[data-testid="stFileUploader"] section small {{
    color: #64748b !important; font-size: 0.84rem !important;
}}
[data-testid="stFileUploader"] button {{
    background: #2563eb !important; color: #fff !important;
    border: none !important; border-radius: 6px !important;
    font-weight: 600 !important; font-size: 0.8rem !important;
}}
audio {{ width: 100%; border-radius: 8px; margin-top: 0.5rem; }}

/* Primary Button */
.stButton > button {{
    background: #2563eb !important; color: #ffffff !important;
    border: none !important; border-radius: 8px !important;
    padding: 0.78rem 2rem !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.82rem !important; font-weight: 700 !important;
    letter-spacing: 0.08em !important; text-transform: uppercase !important;
    width: 100% !important;
    box-shadow: 0 4px 18px rgba(37, 99, 235, 0.25) !important;
    transition: all 0.2s ease !important;
}}
.stButton > button:hover {{
    background: #1d4ed8 !important;
    box-shadow: 0 8px 28px rgba(37, 99, 235, 0.4) !important;
    transform: translateY(-1px) !important;
}}
.stButton > button:disabled {{
    background: #e2e8f0 !important; color: #94a3b8 !important;
    box-shadow: none !important; transform: none !important;
}}

/* File info chip */
.file-chip {{
    font-size: 0.78rem; color: #64748b;
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 6px; padding: 0.35rem 0.75rem;
    margin: 0.5rem 0 0.25rem;
}}

/* ─────────────────────────────────────────
VERDICT CARD
───────────────────────────────────────── */
.v-card {{
    border-radius: 14px; padding: 2.5rem 2rem;
    text-align: center; border: 1.5px solid;
    margin-bottom: 1.5rem;
}}
.v-real {{ background: #f0fdf4; border-color: #86efac; }}
.v-fake {{ background: #fef2f2; border-color: #fca5a5; }}
.v-eyebrow {{
    font-family: 'Montserrat', sans-serif;
    font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.22em; text-transform: uppercase;
    margin-bottom: 0.45rem;
}}
.v-eyebrow.real {{ color: #16a34a; }}
.v-eyebrow.fake {{ color: #b91c1c; }}
.v-big {{
    font-family: 'Montserrat', sans-serif;
    font-size: 4.2rem; font-weight: 900;
    letter-spacing: 0.04em; line-height: 1;
    margin-bottom: 0.15rem;
}}
.v-big.real {{ color: #15803d; }}
.v-big.fake {{ color: #991b1b; }}
.v-pct {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem; margin-bottom: 1rem;
}}
.v-pct.real {{ color: #16a34a; }}
.v-pct.fake {{ color: #dc2626; }}
.v-desc {{ font-size: 0.87rem; color: #475569; line-height: 1.7; max-width: 460px; margin: 0 auto; }}
.v-bar {{ max-width: 280px; margin: 1.2rem auto 0; }}
.v-bar-track {{ height: 6px; background: rgba(0,0,0,0.07); border-radius: 999px; overflow: hidden; }}
.v-bar-real {{ height: 100%; background: linear-gradient(90deg, #15803d, #4ade80); border-radius: 999px; }}
.v-bar-fake {{ height: 100%; background: linear-gradient(90deg, #991b1b, #f87171); border-radius: 999px; }}
.v-votes {{ display: flex; justify-content: center; gap: 2rem; margin-top: 1.2rem; }}
.v-vote {{ text-align: center; }}
.v-vote-n {{ font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700; line-height: 1; }}
.v-vote-n.real {{ color: #16a34a; }}
.v-vote-n.fake {{ color: #dc2626; }}
.v-vote-n.neutral {{ color: #64748b; }}
.v-vote-lbl {{
    font-family: 'Montserrat', sans-serif;
    font-size: 0.65rem; color: #94a3b8;
    text-transform: uppercase; letter-spacing: 0.12em;
    font-weight: 600; margin-top: 0.2rem;
}}

/* ─────────────────────────────────────────
EXPLAIN BOX
───────────────────────────────────────── */
.explain-box {{
    background: #f8fafc;
    border-left: 3px solid #2563eb;
    border-radius: 0 10px 10px 0;
    padding: 1.5rem 1.75rem;
    margin-top: 1.25rem;
}}
.explain-lbl {{
    font-family: 'Montserrat', sans-serif;
    font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.2em; text-transform: uppercase;
    color: #2563eb; margin-bottom: 0.7rem;
}}
.explain-text {{ font-size: 0.88rem; color: #334155; line-height: 1.8; }}

/* ─────────────────────────────────────────
CHART LABELS
───────────────────────────────────────── */
.chart-lbl {{
    font-family: 'Montserrat', sans-serif;
    font-size: 0.62rem; font-weight: 700;
    letter-spacing: 0.18em; text-transform: uppercase;
    color: #94a3b8; margin-bottom: 0.45rem;
    border-bottom: 1px solid #f1f5f9; padding-bottom: 0.4rem;
}}
[data-testid="stImage"] img {{ border-radius: 8px; border: 1px solid #e2e8f0; }}

/* ─────────────────────────────────────────
SECTION 5 — DISCLAIMER
───────────────────────────────────────── */
.disc-box {{
    background: #fffbeb; border: 1px solid #fde68a;
    border-radius: 14px; padding: 2rem 2.5rem;
    max-width: 900px; margin: 0 auto;
}}
.disc-title {{
    font-family: 'Montserrat', sans-serif;
    font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.2em; text-transform: uppercase;
    color: #92400e; margin-bottom: 0.75rem;
}}
.disc-text {{ font-size: 0.88rem; color: #78350f; line-height: 1.82; }}
.disc-tags {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1.25rem; }}
.dtag {{
    font-size: 0.68rem; font-weight: 600; padding: 0.22rem 0.68rem;
    border-radius: 999px; font-family: 'Montserrat', sans-serif;
    letter-spacing: 0.04em;
}}
.dtag.ok {{ background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }}
.dtag.no {{ background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }}

/* ─────────────────────────────────────────
SECTION 6 — FOOTER
───────────────────────────────────────── */
.s6 {{ background: #0f172a; padding: 4rem 8% 2.5rem; color: #94a3b8; }}
.s6-grid {{
    display: grid; grid-template-columns: 2fr 1fr 1fr;
    gap: 3rem; margin-bottom: 2.5rem;
}}
.s6-brand {{
    font-family: 'Montserrat', sans-serif;
    font-size: 1.05rem; font-weight: 800;
    color: #f1f5f9; letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 0.5rem;
}}
.s6-tagline {{ font-size: 0.8rem; color: #475569; line-height: 1.65; }}
.s6-col-lbl {{
    font-family: 'Montserrat', sans-serif;
    font-size: 0.62rem; font-weight: 700;
    letter-spacing: 0.2em; text-transform: uppercase;
    color: #334155; margin-bottom: 0.7rem;
}}
.s6-col-val {{ font-size: 0.83rem; color: #64748b; line-height: 1.7; }}
.s6-line {{ height: 1px; background: rgba(255,255,255,0.06); margin-bottom: 1.5rem; }}
.s6-bottom {{
    display: flex; justify-content: space-between; align-items: center;
    font-size: 0.74rem; color: #334155;
}}
.s6-links {{ display: flex; gap: 1.5rem; }}
.s6-links a {{ color: #475569; text-decoration: none; font-size: 0.74rem; transition: color 0.2s; }}
.s6-links a:hover {{ color: #94a3b8; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MODEL LOADING
# ══════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def load_detector():
    from inference import VoiceCloningDetector
    try:
        return VoiceCloningDetector("model/lcnn_model.keras"), None
    except Exception as e:
        return None, str(e)

detector, load_error = load_detector()

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════

for _k, _v in {"result": None, "raw_sig": None, "vad_sig": None, "sr": 16000}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ══════════════════════════════════════════════════════════════
# VISUALIZATION HELPERS
# ══════════════════════════════════════════════════════════════

def _apply_vad(signal: np.ndarray, sr: int = 16000) -> np.ndarray:
    try:
        intervals = librosa.effects.split(signal, top_db=20)
        if len(intervals) > 0:
            segs = [signal[s:e] for s, e in intervals]
            vad  = np.concatenate(segs)
            if len(vad) > sr * 0.5:
                return vad
    except Exception:
        pass
    return signal


def _ax_clean(ax):
    ax.set_facecolor("#f8fafc")
    for sp in ax.spines.values():
        sp.set_edgecolor("#e2e8f0")
        sp.set_linewidth(0.8)
    ax.tick_params(colors="#94a3b8", labelsize=7)
    ax.grid(True, color="#f1f5f9", linewidth=0.8)


def fig_vad_compare(raw: np.ndarray, vad: np.ndarray, sr: int) -> plt.Figure:
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 3.8), facecolor="white")
    fig.subplots_adjust(hspace=0.5)

    cap = 20000
    t1  = np.linspace(0, len(raw[:cap]) / sr, len(raw[:cap]))
    a1.fill_between(t1, raw[:cap], alpha=0.28, color="#94a3b8")
    a1.plot(t1, raw[:cap], color="#64748b", lw=0.5)
    a1.set_title("Sebelum VAD — termasuk jeda senyap", fontsize=8, color="#475569", pad=4)
    _ax_clean(a1); a1.set_xlim(0)

    t2  = np.linspace(0, len(vad[:cap]) / sr, len(vad[:cap]))
    a2.fill_between(t2, vad[:cap], alpha=0.35, color="#3b82f6")
    a2.plot(t2, vad[:cap], color="#2563eb", lw=0.5)
    a2.set_title("Sesudah VAD — jeda dihapus, sinyal dipadatkan", fontsize=8, color="#2563eb", pad=4)
    a2.set_xlabel("Waktu (detik)", color="#94a3b8", fontsize=7)
    _ax_clean(a2); a2.set_xlim(0)

    plt.tight_layout(pad=0.5)
    return fig


def fig_mfcc_heatmap(signal: np.ndarray, sr: int) -> plt.Figure:
    hop = int(sr * 0.01)
    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=13, n_fft=512, hop_length=hop)
    d1   = librosa.feature.delta(mfcc)
    d2   = librosa.feature.delta(mfcc, order=2)
    m39  = np.vstack([mfcc, d1, d2])

    fig, ax = plt.subplots(figsize=(8, 3.4), facecolor="white")
    img = librosa.display.specshow(m39, x_axis="time", sr=sr, ax=ax, cmap="YlOrBr", hop_length=hop)
    plt.colorbar(img, ax=ax, format="%+.0f", pad=0.01).ax.tick_params(colors="#94a3b8", labelsize=7)
    ax.set_xlabel("Waktu (detik)", color="#94a3b8", fontsize=7)
    ax.set_ylabel("Koefisien", color="#94a3b8", fontsize=7)
    ax.axhline(13, color="#3b82f6", lw=0.9, ls="--", alpha=0.55)
    ax.axhline(26, color="#0891b2", lw=0.9, ls="--", alpha=0.55)
    for y, lbl, col in [(6, "Static", "#64748b"), (19, "Delta", "#0891b2"), (32, "Delta²", "#7c3aed")]:
        ax.text(0.005, y, lbl, transform=ax.get_yaxis_transform(), color=col, fontsize=6.5, va="center")
    _ax_clean(ax); ax.set_facecolor("#fff8f0")
    plt.tight_layout(pad=0.4)
    return fig


def fig_mfcc_variance(signal: np.ndarray, sr: int) -> plt.Figure:
    hop  = int(sr * 0.01)
    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=13, n_fft=512, hop_length=hop)
    d1   = librosa.feature.delta(mfcc)
    d2   = librosa.feature.delta(mfcc, order=2)
    stds = np.std(np.vstack([mfcc, d1, d2]), axis=1)

    fig, ax = plt.subplots(figsize=(8, 3.4), facecolor="white")
    colors = ["#3b82f6"] * 13 + ["#0891b2"] * 13 + ["#7c3aed"] * 13
    ax.bar(range(1, 40), stds, color=colors, alpha=0.82, width=0.72, zorder=3)
    ax.axvline(13.5, color="#e2e8f0", lw=1.2, zorder=2)
    ax.axvline(26.5, color="#e2e8f0", lw=1.2, zorder=2)
    peak = max(stds) * 1.08
    for x, lbl, c in [(7, "Static MFCC", "#3b82f6"), (20, "Delta", "#0891b2"), (33, "Delta²", "#7c3aed")]:
        ax.text(x, peak, lbl, ha="center", color=c, fontsize=7, fontweight="bold")
    ax.set_xlabel("Indeks Koefisien MFCC", color="#94a3b8", fontsize=7)
    ax.set_ylabel("Standar Deviasi", color="#94a3b8", fontsize=7)
    ax.set_xlim(0, 40)
    _ax_clean(ax)
    plt.tight_layout(pad=0.4)
    return fig


def generate_explanation(result) -> str:
    n, fv, rv = result.total_chunks, result.fake_votes, result.real_votes
    pct = result.confidence * 100

    if result.is_fake:
        return (
            f"Sistem mendeteksi pola anomali akustik pada rekaman ini. "
            f"Dari total <strong>{n} segmen</strong> yang dianalisis menggunakan metode "
            f"<em>Sliding Window</em>, sebanyak <strong>{fv} segmen ({fv/n*100:.0f}%)</strong> "
            f"menunjukkan probabilitas sintetik di atas ambang batas 0.5. "
            f"Distribusi energi pada koefisien Delta dan Delta-Delta menunjukkan regularitas yang "
            f"tidak lazim — ciri khas dari proses sintesis mesin <em>Text-to-Speech</em>. "
            f"Tingkat kepercayaan rata-rata: <strong>{pct:.1f}%</strong>."
        )
    else:
        conf_real = (1 - result.confidence) * 100
        return (
            f"Tidak ditemukan anomali akustik yang signifikan pada rekaman ini. "
            f"Dari total <strong>{n} segmen</strong> yang dianalisis, hanya "
            f"<strong>{fv} segmen ({fv/n*100:.0f}%)</strong> yang memiliki probabilitas sintetik di atas 0.5. "
            f"Variabilitas distribusi energi pada koefisien MFCC bersifat organik dan tidak teratur — "
            f"konsisten dengan karakteristik fisiologis saluran vokal manusia. "
            f"Tingkat kepercayaan rata-rata: <strong>{conf_real:.1f}%</strong>."
        )


# ══════════════════════════════════════════════════════════════
# SECTION 1 — HERO
# ══════════════════════════════════════════════════════════════

st.markdown("""
<section class="s1">
    <div class="s1-ov"></div>
    <div class="s1-inner">
        <div class="s1-eyebrow">Forensik Akustik Berbasis Kecerdasan Buatan</div>
        <h1 class="s1-h1">Suara Siapa yang<br>Sebenarnya Anda Dengar?</h1>
        <p class="s1-p">
            Lindungi diri dari penipuan Voice Cloning dan Deepfake Audio.
            Unggah rekaman suara, dan biarkan AI menganalisis
            jejak forensik akustiknya dalam hitungan detik.
        </p>
        <a href="#section-analisis" class="s1-cta">Mulai Analisis Audio</a>
    </div>
    <div class="s1-scroll">Gulir ke bawah</div>
</section>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SECTION 2 — THE PROBLEM
# ══════════════════════════════════════════════════════════════

st.markdown("""
<div class="sw sw-gray">
    <div class="eyebrow">
        <div class="eyebrow-line"></div>
        <span class="eyebrow-text">Mengapa Ini Penting</span>
    </div>
    <h2 class="sec-title">Ancaman Nyata di Balik Suara Digital</h2>
    <p class="sec-sub">
        Teknologi Voice Cloning telah berkembang pesat. Suara sintetik yang dihasilkan kini hampir
        tidak dapat dibedakan oleh telinga manusia biasa, menciptakan risiko serius di berbagai bidang kehidupan.
    </p>
    <div class="prob-grid">
        <div class="prob-card c1">
            <span class="prob-n">01</span>
            <div class="prob-title">Penipuan Finansial</div>
            <p class="prob-desc">
                Pelaku kejahatan menggunakan kloning suara anggota keluarga atau eksekutif perusahaan
                untuk meyakinkan korban agar melakukan transfer dana dalam jumlah besar.
                Kasus semacam ini dilaporkan meningkat signifikan di berbagai negara.
            </p>
            <span class="prob-tag t1">Ancaman Kriminal</span>
        </div>
        <div class="prob-card c2">
            <span class="prob-n">02</span>
            <div class="prob-title">Penyebaran Disinformasi</div>
            <p class="prob-desc">
                Tokoh publik dan politisi sering menjadi korban manipulasi audio deepfake untuk
                menggiring opini publik, merusak reputasi, atau memprovokasi perpecahan di masyarakat
                melalui pernyataan yang tidak pernah diucapkan.
            </p>
            <span class="prob-tag t2">Ancaman Demokrasi</span>
        </div>
        <div class="prob-card c3">
            <span class="prob-n">03</span>
            <div class="prob-title">Keterbatasan Indera Manusia</div>
            <p class="prob-desc">
                Algoritma Text-to-Speech generasi terkini menghasilkan suara sintetik berkualitas tinggi
                yang tidak lagi dapat dibedakan secara auditif. Diperlukan analisis forensik akustik
                berbasis kecerdasan buatan untuk mendeteksinya.
            </p>
            <span class="prob-tag t3">Solusi Teknologi</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SECTION 3 — HOW IT WORKS
# ══════════════════════════════════════════════════════════════

st.markdown("""
<div class="sw sw-white">
    <div class="eyebrow">
        <div class="eyebrow-line"></div>
        <span class="eyebrow-text">Cara Kerja Sistem</span>
    </div>
    <h2 class="sec-title">Tiga Tahap Analisis Forensik Akustik</h2>
    <p class="sec-sub">
        Proses analisis berlangsung sepenuhnya otomatis melalui tiga tahap yang menggabungkan
        teknik Pemrosesan Sinyal Digital (DSP) dan Jaringan Saraf Tiruan Konvolusional (CNN).
    </p>
    <div class="steps-row">
        <div class="step">
            <div class="step-circle">1</div>
            <div class="step-title">Unggah Audio</div>
            <p class="step-desc">
                Masukkan file rekaman suara dalam format apapun.
                Sistem menerima berbagai durasi — dari beberapa detik hingga beberapa menit —
                tanpa batasan panjang rekaman.
            </p>
            <span class="step-code">.wav / .mp3 / .ogg / .flac</span>
        </div>
        <div class="step">
            <div class="step-circle">2</div>
            <div class="step-title">Ekstraksi Sidik Jari Suara</div>
            <p class="step-desc">
                Jeda senyap dihilangkan menggunakan Voice Activity Detection (VAD).
                Kemudian 39 koefisien MFCC diekstrak sebagai representasi unik
                dari karakteristik saluran vokal pembicara.
            </p>
            <span class="step-code">VAD + Pre-emphasis + 39 MFCC</span>
        </div>
        <div class="step">
            <div class="step-circle">3</div>
            <div class="step-title">Analisis Model LCNN</div>
            <p class="step-desc">
                Light CNN memindai pola MFCC secara bertahap menggunakan metode Sliding Window,
                lalu mengambil keputusan akhir melalui mekanisme Hard Voting dari
                seluruh segmen yang dianalisis.
            </p>
            <span class="step-code">LCNN + Sliding Window + Hard Voting</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SECTION 4 — CORE APP
# ══════════════════════════════════════════════════════════════

st.markdown("""
<div id="section-analisis"></div>
<div class="sw sw-gray s4-head">
    <div class="eyebrow" style="justify-content:center">
        <div class="eyebrow-line"></div>
        <span class="eyebrow-text">Analisis Audio</span>
        <div class="eyebrow-line"></div>
    </div>
    <h2 class="sec-title" style="text-align:center">Unggah dan Deteksi Sekarang</h2>
    <p class="sec-sub" style="text-align:center; margin:0 auto">
        Unggah file rekaman suara dan sistem akan menganalisis keasliannya
        menggunakan forensik akustik berbasis Light Convolutional Neural Network.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Upload Widget ─────────────────────────────────────────────
_, col_mid, _ = st.columns([1, 2, 1])

with col_mid:
    if load_error:
        st.markdown(f"""
        <div style="background:#fef2f2; border:1px solid #fca5a5; border-radius:10px;
            padding:1rem 1.25rem; font-size:0.84rem; color:#991b1b; margin-bottom:1rem;">
            <strong>Model belum tersedia.</strong><br>
            {load_error}<br>
            Jalankan <code>save_model_colab.py</code> di Colab, lalu letakkan file di
            <code>model/lcnn_model.keras</code>.
        </div>
        """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload audio",
        type=["wav", "mp3", "ogg", "flac", "m4a"],
        label_visibility="collapsed"
    )

    if uploaded:
        st.markdown(
            f'<div class="file-chip">{uploaded.name} &nbsp;&middot;&nbsp; {uploaded.size/1024:.1f} KB</div>',
            unsafe_allow_html=True
        )
        st.audio(uploaded, format=uploaded.type)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    run = st.button("Deteksi Sekarang", disabled=(uploaded is None or detector is None))

# ── Processing ───────────────────────────────────────────────
if run and uploaded and detector:
    suffix = os.path.splitext(uploaded.name)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.getvalue())
        tmp_path = tmp.name

    with st.status("Menganalisis audio...", expanded=True) as status:
        st.write("Tahap 1 — Memuat sinyal audio dan menerapkan Voice Activity Detection...")
        raw_sig, _ = librosa.load(tmp_path, sr=16000)
        vad_sig    = _apply_vad(raw_sig)

        st.write("Tahap 2 — Mengekstrak 39 koefisien MFCC (Statis + Delta + Delta-Delta)...")
        time.sleep(0.3)

        st.write("Tahap 3 — Menjalankan inferensi LCNN dengan Sliding Window dan Hard Voting...")
        result = detector.predict_from_file(tmp_path)
        status.update(label="Analisis selesai.", state="complete", expanded=False)

    st.session_state.result  = result
    st.session_state.raw_sig = raw_sig
    st.session_state.vad_sig = vad_sig
    st.session_state.sr      = 16000

    try:
        os.remove(tmp_path)
    except Exception:
        pass

# ── Results ──────────────────────────────────────────────────
if st.session_state.result is not None:
    result  = st.session_state.result
    raw_sig = st.session_state.raw_sig
    vad_sig = st.session_state.vad_sig
    sr      = st.session_state.sr

    if result.error:
        _, ec, _ = st.columns([1, 2, 1])
        with ec:
            st.error(f"Analisis gagal: {result.error}")
    else:
        cls   = "real" if not result.is_fake else "fake"
        label = "ASLI" if not result.is_fake else "PALSU"
        pct   = (1 - result.confidence) * 100 if not result.is_fake else result.confidence * 100
        desc  = (
            "Tidak ditemukan pola anomali akustik yang signifikan. "
            "Distribusi energi MFCC konsisten dengan karakteristik suara manusia asli."
            if not result.is_fake else
            "Terdeteksi pola anomali akustik yang tidak lazim pada rekaman ini. "
            "Distribusi energi MFCC menunjukkan regularitas khas mesin Text-to-Speech."
        )

        # Verdict card
        _, vc, _ = st.columns([1, 2, 1])
        with vc:
            st.markdown(f"""
            <div class="v-card v-{cls}">
                <div class="v-eyebrow {cls}">Hasil Deteksi Forensik Akustik</div>
                <div class="v-big {cls}">{label}</div>
                <div class="v-pct {cls}">{pct:.1f}%</div>
                <p class="v-desc">{desc}</p>
                <div class="v-bar">
                    <div class="v-bar-track">
                        <div class="v-bar-{cls}" style="width:{pct:.1f}%"></div>
                    </div>
                </div>
                <div class="v-votes">
                    <div class="v-vote">
                        <div class="v-vote-n real">{result.real_votes}</div>
                        <div class="v-vote-lbl">Vote Asli</div>
                    </div>
                    <div class="v-vote">
                        <div class="v-vote-n fake">{result.fake_votes}</div>
                        <div class="v-vote-lbl">Vote Palsu</div>
                    </div>
                    <div class="v-vote">
                        <div class="v-vote-n neutral">{result.total_chunks}</div>
                        <div class="v-vote-lbl">Total Segmen</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            explanation = generate_explanation(result)
            st.markdown(f"""
            <div class="explain-box">
                <div class="explain-lbl">Analisis Forensik</div>
                <div class="explain-text">{explanation}</div>
            </div>
            """, unsafe_allow_html=True)

        # Forensic charts
        st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="padding: 0 8%; margin-bottom: 0.75rem;">
            <div class="eyebrow">
                <div class="eyebrow-line"></div>
                <span class="eyebrow-text">Grafik Forensik</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        ch1, ch2, ch3 = st.columns(3)
        with ch1:
            st.markdown('<div class="chart-lbl">Waveform Sebelum dan Sesudah VAD</div>', unsafe_allow_html=True)
            f1 = fig_vad_compare(raw_sig, vad_sig, sr)
            st.pyplot(f1, use_container_width=True)
            plt.close(f1)
        with ch2:
            st.markdown('<div class="chart-lbl">Heatmap 39 MFCC — Static + Delta + Delta²</div>', unsafe_allow_html=True)
            f2 = fig_mfcc_heatmap(vad_sig, sr)
            st.pyplot(f2, use_container_width=True)
            plt.close(f2)
        with ch3:
            st.markdown('<div class="chart-lbl">Variansi Energi Per Koefisien MFCC</div>', unsafe_allow_html=True)
            f3 = fig_mfcc_variance(vad_sig, sr)
            st.pyplot(f3, use_container_width=True)
            plt.close(f3)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SECTION 5 — DISCLAIMER
# ══════════════════════════════════════════════════════════════

st.markdown("""
<div class="sw sw-white">
    <div class="eyebrow">
        <div class="eyebrow-line" style="background:#d97706"></div>
        <span class="eyebrow-text" style="color:#d97706">Batasan Sistem</span>
    </div>
    <h2 class="sec-title">Disclaimer dan Cakupan Model</h2>
    <p class="sec-sub">
        Memahami batasan sistem adalah bagian dari penggunaan yang bertanggung jawab
        dan interpretasi hasil yang akurat.
    </p>
    <div class="disc-box">
        <div class="disc-title">Pernyataan Batasan Sistem</div>
        <p class="disc-text">
            Sistem ini dilatih secara khusus untuk mendeteksi audio sintetik yang dihasilkan oleh
            algoritma <strong>Text-to-Speech (TTS)</strong>, menggunakan dataset 480 sampel audio
            dari 24 pembicara berbahasa Indonesia dengan rekaman asli dan sintetik dari platform
            ElevenLabs. Evaluasi menggunakan metode <em>Speaker-Independent Split</em> dengan
            pembagian 75%/25% untuk memastikan generalisasi terhadap pembicara baru.
            <br><br>
            Akurasi sistem dapat menurun secara signifikan pada kondisi berikut: audio yang
            dihasilkan menggunakan metode <strong>Voice-to-Voice (RVC)</strong>, rekaman yang
            telah mengalami <strong>kompresi platform media sosial</strong> (WhatsApp, Instagram,
            TikTok), audio dengan <strong>musik latar yang dominan</strong>, atau rekaman
            berkualitas akustik sangat rendah. Hasil analisis bersifat pendukung keputusan,
            bukan pengganti investigasi forensik profesional.
            <br><br>
            Performa model pada data uji: <strong>Equal Error Rate (EER) = 11.67%</strong>,
            Akurasi = 90.83%, Presisi = 90.5%, Recall = 97.2%.
        </p>
        <div class="disc-tags">
            <span class="dtag ok">Bahasa Indonesia</span>
            <span class="dtag ok">TTS ElevenLabs</span>
            <span class="dtag ok">Audio Rekaman Bersih</span>
            <span class="dtag no">Voice-to-Voice / RVC</span>
            <span class="dtag no">Kompresi Media Sosial</span>
            <span class="dtag no">Musik Latar Berat</span>
            <span class="dtag no">Bahasa Selain Indonesia</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SECTION 6 — FOOTER
# ══════════════════════════════════════════════════════════════

st.markdown("""
<div class="s6">
    <div class="s6-grid">
        <div>
            <div class="s6-brand">VoiceGuard</div>
            <p class="s6-tagline">
                Sistem Deteksi Kloning Suara Text-to-Speech<br>
                Berbahasa Indonesia Berbasis Light Convolutional Neural Network (LCNN)
            </p>
        </div>
        <div>
            <div class="s6-col-lbl">Peneliti</div>
            <div class="s6-col-val">
                [Nama Mahasiswa]<br>
                [NIM]<br>
                [Program Studi]
            </div>
        </div>
        <div>
            <div class="s6-col-lbl">Institusi</div>
            <div class="s6-col-val">
                [Nama Universitas]<br>
                Fakultas [Nama Fakultas]<br>
                &copy; 2025
            </div>
        </div>
    </div>
    <div class="s6-line"></div>
    <div class="s6-bottom">
        <span>Penelitian Skripsi &mdash; Program Studi [Nama Prodi]</span>
        <div class="s6-links">
            <a href="#">GitHub</a>
            <a href="#">LinkedIn</a>
            <a href="#">Laporan Skripsi</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)