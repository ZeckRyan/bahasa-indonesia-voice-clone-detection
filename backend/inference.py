"""
inference.py — Engine Inferensi LCNN Voice Cloning Detector
============================================================
Modul ini mengenkapsulasi seluruh pipeline:
  1. Load model dengan custom MaxFeatureMap layer
  2. Preprocessing audio (VAD → Pre-emphasis → 39 MFCC)
  3. Sliding window + Hard voting untuk audio durasi variabel

Cara Penggunaan:
  from inference import VoiceCloningDetector
  detector = VoiceCloningDetector("model/lcnn_model.keras")
  result = detector.predict_from_file("audio.wav")
"""

import os
import numpy as np
import librosa
import tensorflow as tf
from dataclasses import dataclass
from typing import Optional


# ============================================================
# KONFIGURASI PIPELINE (HARUS IDENTIK DENGAN SAAT TRAINING)
# ============================================================

SAMPLE_RATE     = 16000       # Hz — Sample rate standar wicara
N_MFCC          = 13          # Jumlah koefisien MFCC dasar
N_FFT           = 512         # Ukuran FFT window
HOP_LENGTH      = int(SAMPLE_RATE * 0.01)  # 160 sampel = 10ms
MAX_FRAMES      = 100         # Panjang matriks MFCC (dimensi waktu)
PRE_EMPHASIS    = 0.97        # Koefisien pre-emphasis filter
VAD_TOP_DB      = 20          # Threshold VAD (dalam desibel)
MIN_SIGNAL_DUR  = 0.5         # Durasi minimum sinyal aktif (detik)
FAKE_THRESHOLD  = 0.8         # Threshold klasifikasi sigmoid
WINDOW_OVERLAP  = 0.5         # Overlap antar chunk (50%)


# ============================================================
# CUSTOM LAYER — MAX FEATURE MAP (MFM)
# Menggunakan custom Layer class (bukan Lambda) agar dapat
# disimpan dan dimuat kembali tanpa safe_mode=False.
# Sesuai dengan model yang disimpan oleh save_model_colab.py.
# ============================================================

class MaxFeatureMap(tf.keras.layers.Layer):
    """
    Layer aktivasi Max-Feature-Map (MFM).
    Membagi tensor menjadi dua bagian pada dimensi channel,
    lalu mengambil nilai maksimum elemen-per-elemen.

    Input:  tensor shape (..., C)
    Output: tensor shape (..., C//2)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call(self, x):
        n = tf.shape(x)[-1] // 2
        return tf.maximum(x[..., :n], x[..., n:])

    def compute_output_shape(self, input_shape):
        shape = list(input_shape)
        shape[-1] = shape[-1] // 2
        return tuple(shape)

    def get_config(self):
        return super().get_config()


# ============================================================
# DATA CLASS — HASIL PREDIKSI
# ============================================================

@dataclass
class PredictionResult:
    """Struktur data yang menyimpan hasil inferensi lengkap."""
    label: str                # "REAL" atau "FAKE"
    is_fake: bool             # True jika terdeteksi sebagai FAKE
    confidence: float         # Probabilitas rata-rata (0.0 - 1.0)
    fake_votes: int           # Jumlah chunk yang divoting FAKE
    real_votes: int           # Jumlah chunk yang divoting REAL
    total_chunks: int         # Total chunk yang dianalisis
    chunk_probabilities: list # List probabilitas tiap chunk
    error: Optional[str]      # Pesan error jika ada


# ============================================================
# KELAS UTAMA — VOICE CLONING DETECTOR
# ============================================================

class VoiceCloningDetector:
    """
    Kelas utama untuk deteksi kloning suara TTS.
    Menggabungkan pipeline DSP dan inferensi model LCNN.
    """

    def __init__(self, model_path: str):
        """
        Inisialisasi detektor dan muat model dari file.

        Args:
            model_path: Path ke file model (.keras)
        """
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        """Memuat model LCNN dengan custom_objects untuk MFM layer."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"File model tidak ditemukan: {self.model_path}\n"
                f"Pastikan Anda sudah menjalankan save_model_colab.py di Google Colab "
                f"dan meletakkan file lcnn_model.keras di folder 'model/'."
            )

        print(f"[INFO] Memuat model dari: {self.model_path}")
        self.model = tf.keras.models.load_model(
            self.model_path,
            custom_objects={"MaxFeatureMap": MaxFeatureMap}
        )
        print(f"[INFO] Model berhasil dimuat. Input shape: {self.model.input_shape}")

    # ----------------------------------------------------------
    # STEP 1: VOICE ACTIVITY DETECTION (VAD)
    # ----------------------------------------------------------
    def _apply_vad(self, signal: np.ndarray) -> np.ndarray:
        """
        Menghapus jeda kosong dari sinyal menggunakan energy-based VAD.
        Mencegah model belajar dari karakteristik noise floor.

        Args:
            signal: Array sinyal audio 1D

        Returns:
            Sinyal yang hanya berisi segmen aktif (suara)
        """
        intervals = librosa.effects.split(signal, top_db=VAD_TOP_DB)
        if len(intervals) == 0:
            return signal

        active_segments = [signal[start:end] for start, end in intervals]
        concatenated = np.concatenate(active_segments)

        # Gunakan hasil VAD hanya jika cukup panjang
        if len(concatenated) > SAMPLE_RATE * MIN_SIGNAL_DUR:
            return concatenated
        return signal

    # ----------------------------------------------------------
    # STEP 2: PRE-EMPHASIS FILTER
    # ----------------------------------------------------------
    def _apply_pre_emphasis(self, signal: np.ndarray) -> np.ndarray:
        """
        Menerapkan filter high-pass pre-emphasis untuk memperkuat
        frekuensi tinggi yang mengandung artefak deepfake.

        Formula: y[n] = x[n] - α * x[n-1]  (α = 0.97)
        """
        return np.append(signal[0], signal[1:] - PRE_EMPHASIS * signal[:-1])

    # ----------------------------------------------------------
    # STEP 3: EKSTRAKSI 39 MFCC
    # ----------------------------------------------------------
    def _extract_mfcc(self, signal: np.ndarray) -> Optional[np.ndarray]:
        """
        Mengekstrak matriks 39 MFCC dari sinyal audio.

        Pipeline:
          - 13 MFCC Statis  → bentuk dasar saluran vokal
          - 13 MFCC Delta   → kecepatan perubahan (turunan pertama)
          - 13 MFCC Delta²  → percepatan perubahan (turunan kedua)

        Returns:
            Array shape (39, T) atau None jika gagal
        """
        mfcc_static = librosa.feature.mfcc(
            y=signal,
            sr=SAMPLE_RATE,
            n_mfcc=N_MFCC,
            n_fft=N_FFT,
            hop_length=HOP_LENGTH
        )

        # Minimal 9 frame diperlukan agar delta dapat dihitung
        if mfcc_static.shape[1] < 9:
            return None

        mfcc_delta  = librosa.feature.delta(mfcc_static)
        mfcc_delta2 = librosa.feature.delta(mfcc_static, order=2)

        return np.vstack([mfcc_static, mfcc_delta, mfcc_delta2])  # shape: (39, T)

    # ----------------------------------------------------------
    # STEP 4: SLIDING WINDOW CHUNKING
    # ----------------------------------------------------------
    def _create_chunks(self, mfcc_matrix: np.ndarray) -> list:
        """
        Memotong matriks MFCC menjadi chunk-chunk berukuran (39, 100)
        dengan overlap 50% untuk menangani audio berdurasi variabel.

        Jika total frame < MAX_FRAMES, dilakukan zero-padding.

        Args:
            mfcc_matrix: Array shape (39, T)

        Returns:
            List of arrays, masing-masing shape (39, MAX_FRAMES, 1)
        """
        n_frames = mfcc_matrix.shape[1]
        chunks = []

        if n_frames <= MAX_FRAMES:
            # Audio pendek: lakukan zero-padding
            pad_width = MAX_FRAMES - n_frames
            padded = np.pad(mfcc_matrix, ((0, 0), (0, pad_width)), mode='constant')
            chunks.append(padded[..., np.newaxis])
        else:
            # Audio panjang: sliding window dengan overlap 50%
            step = int(MAX_FRAMES * (1 - WINDOW_OVERLAP))  # = 50 frame
            for start in range(0, n_frames - MAX_FRAMES + 1, step):
                chunk = mfcc_matrix[:, start:start + MAX_FRAMES]
                chunks.append(chunk[..., np.newaxis])

            # Tambahkan chunk terakhir jika ada sisa frame
            last_start = n_frames - MAX_FRAMES
            if last_start % step != 0:
                chunk = mfcc_matrix[:, last_start:]
                if chunk.shape[1] < MAX_FRAMES:
                    pad_w = MAX_FRAMES - chunk.shape[1]
                    chunk = np.pad(chunk, ((0, 0), (0, pad_w)), mode='constant')
                chunks.append(chunk[..., np.newaxis])

        return chunks

    # ----------------------------------------------------------
    # PIPELINE UTAMA — PREPROCESSING
    # ----------------------------------------------------------
    def preprocess(self, audio_path: str) -> Optional[list]:
        """
        Menjalankan pipeline preprocessing lengkap pada satu file audio.

        Args:
            audio_path: Path ke file audio (.wav, .mp3, .ogg, dll)

        Returns:
            List chunk siap inferensi, atau None jika gagal
        """
        # Load audio dengan sample rate yang sesuai
        signal, _ = librosa.load(audio_path, sr=SAMPLE_RATE)

        # Step 1: VAD
        signal = self._apply_vad(signal)

        # Step 2: Pre-emphasis
        signal = self._apply_pre_emphasis(signal)

        # Step 3: Ekstraksi 39 MFCC
        mfcc_matrix = self._extract_mfcc(signal)
        if mfcc_matrix is None:
            return None

        # Step 4: Chunking dengan sliding window
        chunks = self._create_chunks(mfcc_matrix)
        return chunks

    # ----------------------------------------------------------
    # INFERENSI UTAMA — HARD VOTING
    # ----------------------------------------------------------
    def predict_from_file(self, audio_path: str) -> PredictionResult:
        """
        Melakukan deteksi kloning suara pada file audio.

        Pipeline:
          1. Preprocessing → chunks
          2. Prediksi setiap chunk dengan model LCNN
          3. Majority hard voting → keputusan akhir

        Args:
            audio_path: Path ke file audio

        Returns:
            PredictionResult dengan detail lengkap
        """
        if self.model is None:
            return PredictionResult(
                label="ERROR", is_fake=False, confidence=0.0,
                fake_votes=0, real_votes=0, total_chunks=0,
                chunk_probabilities=[], error="Model belum dimuat."
            )

        # --- Preprocessing ---
        try:
            chunks = self.preprocess(audio_path)
        except Exception as e:
            return PredictionResult(
                label="ERROR", is_fake=False, confidence=0.0,
                fake_votes=0, real_votes=0, total_chunks=0,
                chunk_probabilities=[], error=f"Preprocessing gagal: {str(e)}"
            )

        if chunks is None or len(chunks) == 0:
            return PredictionResult(
                label="ERROR", is_fake=False, confidence=0.0,
                fake_votes=0, real_votes=0, total_chunks=0,
                chunk_probabilities=[], error="Sinyal terlalu pendek atau tidak ada suara yang terdeteksi."
            )

        # --- Batch Prediction ---
        batch = np.array(chunks)  # shape: (N_chunks, 39, 100, 1)
        probabilities = self.model.predict(batch, verbose=0).ravel()  # shape: (N_chunks,)

        # --- Hard Voting ---
        fake_votes = int(np.sum(probabilities > FAKE_THRESHOLD))
        real_votes = len(probabilities) - fake_votes
        is_fake = fake_votes > real_votes

        # Confidence: rata-rata probabilitas (ke arah label pemenang)
        avg_prob = float(np.mean(probabilities))

        return PredictionResult(
            label="FAKE" if is_fake else "REAL",
            is_fake=is_fake,
            confidence=avg_prob,
            fake_votes=fake_votes,
            real_votes=real_votes,
            total_chunks=len(chunks),
            chunk_probabilities=probabilities.tolist(),
            error=None
        )
