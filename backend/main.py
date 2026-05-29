from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import io
import base64
import tempfile
import shutil
import numpy as np
import librosa
import librosa.display
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Import the model inferencer
from backend.inference import VoiceCloningDetector

app = FastAPI(title="VoiceGuard API")

allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]

# Setup CORS to allow Next.js frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "cnn_model.keras")
try:
    detector = VoiceCloningDetector(MODEL_PATH)
    print("[SUCCESS] Model CNN loaded successfully.")
except Exception as e:
    detector = None
    print(f"[ERROR] Error loading model: {e}")

# ══════════════════════════════════════════════════════════════
# VISUALIZATION HELPERS (Same as Streamlit version)
# ══════════════════════════════════════════════════════════════

def _ax_clean(ax):
    ax.set_facecolor("#f8fafc")
    for sp in ax.spines.values():
        sp.set_edgecolor("#e2e8f0")
        sp.set_linewidth(0.8)
    ax.tick_params(colors="#94a3b8", labelsize=7)
    ax.grid(True, color="#f1f5f9", linewidth=0.8)

def fig_to_base64(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def generate_vad_compare(raw: np.ndarray, vad: np.ndarray, sr: int) -> str:
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
    return fig_to_base64(fig)

def generate_mfcc_heatmap(signal: np.ndarray, sr: int) -> str:
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
    return fig_to_base64(fig)

def generate_mfcc_variance(signal: np.ndarray, sr: int) -> str:
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
    return fig_to_base64(fig)

# ══════════════════════════════════════════════════════════════
# API ROUTES
# ══════════════════════════════════════════════════════════════

@app.get("/")
def read_root():
    return {"status": "ok", "message": "VoiceGuard Backend API is running."}

@app.post("/api/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    if detector is None:
        raise HTTPException(status_code=500, detail="Model gagal dimuat. Periksa file cnn_model.keras.")

    # Save uploaded file to temp
    tmp_path = f"temp_{file.filename}"
    with open(tmp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Load audio for raw comparison (no VAD)
        raw_sig, sr = librosa.load(tmp_path, sr=16000)
        
        # Run inference (applies VAD internally)
        result = detector.predict_from_file(tmp_path)
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=400, detail=f"Gagal membaca file audio. Pastikan file valid (.wav/.mp3) atau coba file lain. Detail: {str(e)}")

    try:
        # To get VAD signal for plotting, we recreate it here
        intervals = librosa.effects.split(raw_sig, top_db=20)
        if len(intervals) > 0:
            vad_sig = np.concatenate([raw_sig[s:e] for s, e in intervals])
            if len(vad_sig) < sr * 0.5:
                vad_sig = raw_sig
        else:
            vad_sig = raw_sig

        # Generate Plot Images in Base64
        b64_vad = generate_vad_compare(raw_sig, vad_sig, sr)
        b64_heatmap = generate_mfcc_heatmap(vad_sig, sr)
        b64_variance = generate_mfcc_variance(vad_sig, sr)

        return {
            "status": "success",
            "filename": file.filename,
            "prediction": {
                "is_fake": bool(result.is_fake),
                "confidence": float(result.confidence),
                "total_chunks": int(result.total_chunks),
                "fake_votes": int(result.fake_votes),
                "real_votes": int(result.real_votes),
            },
            "plots": {
                "vad": b64_vad,
                "mfcc_heatmap": b64_heatmap,
                "mfcc_variance": b64_variance
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(tmp_path)
