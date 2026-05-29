# VoiceGuard: AI-Powered Voice Cloning & Deepfake Detection

## Overview

VoiceGuard is an advanced, automated acoustic forensics system designed to detect synthetic audio and voice cloning. Utilizing a deep learning architecture, specifically a Convolutional Neural Network (CNN), the system analyzes acoustic fingerprints to differentiate between authentic human voices and AI-generated speech (Text-to-Speech).

The architecture is fully decoupled, consisting of a high-performance Python FastAPI backend for model inference and a modern Next.js frontend for the user interface.

## System Architecture

- **Backend**: Built with FastAPI. It handles audio signal processing, Voice Activity Detection (VAD), Mel-Frequency Cepstral Coefficients (MFCC) feature extraction, and neural network inference.
- **Frontend**: Developed using Next.js and Tailwind CSS. It provides a highly responsive, professional user interface to upload audio files and visualize analysis results, including VAD plots, MFCC heatmaps, and spectral variance charts.
- **Model Training**: The deep learning model training pipeline is contained within a Jupyter Notebook, optimally designed for environments like Google Colab.

## Repository Structure

```text
.
├── backend/
│   ├── main.py                # FastAPI application entry point
│   ├── inference.py           # Core logic for DSP and model inference
│   ├── model/                 # Directory containing the pre-trained .keras model
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/                   # Next.js application source code
│   ├── public/                # Static assets (images, icons)
│   ├── package.json           # Node.js dependencies
│   └── tailwind.config.ts     # Tailwind CSS configuration
├── notebooks/                 # Directory for Jupyter Notebooks
│   └── training_colab.ipynb   # Google Colab notebook for training the model
└── README.md                  # Project documentation
```

## Setup and Installation

### 1. Backend Setup (FastAPI)

Ensure you have Python 3.9 or higher installed.

```bash
# Navigate to the project root
cd VoiceGuard

# Create a virtual environment
python -m venv venv

# Activate the virtual environment (Windows)
venv\Scripts\activate

# Install the required dependencies
pip install -r backend/requirements.txt
# Alternatively, if requirements are at root level: pip install -r requirements.txt

# Run the FastAPI server
uvicorn backend.main:app --reload --port 8000
```
The backend API will be available at `http://localhost:8000`.

### 2. Frontend Setup (Next.js)

Ensure you have Node.js (v18 or higher) installed.

```bash
# Open a new terminal and navigate to the frontend directory
cd VoiceGuard/frontend

# Install the Node.js dependencies
npm install

# Start the development server
npm run dev
```
The user interface will be accessible at `http://localhost:3000`.

## Model Training

The code used to train the acoustic forensic model is located in the `notebooks/` directory. You can upload the Jupyter Notebook (`.ipynb`) found inside this folder directly to Google Colab to train the model using GPU acceleration. After completing the training process, download the resulting `.keras` file and place it in the `backend/model/` directory.

## Deployment Notes

The `.kiro/` folder is local project metadata and planning data. It is not part of the app runtime, so you do not deploy it to Vercel.

For Vercel, deploy only the Next.js frontend from the `frontend/` folder. The Python FastAPI backend should be deployed separately, for example to Render, Railway, Fly.io, or another Python host. After that, set `NEXT_PUBLIC_API_BASE_URL` in Vercel to the backend URL.

For Render, deploy the repository root using the included `render.yaml`. Set `CORS_ORIGINS` in Render to your Vercel domain, for example `https://your-app.vercel.app`.

Example for local development:

```bash
# frontend/.env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

In Vercel, set the same variable to your production backend URL, for example `https://your-backend.onrender.com`.

## Limitations and Scope

- The model is optimized for detecting Text-to-Speech (TTS) cloning algorithms.
- Voice-to-Voice (RVC) conversion detection may have varying accuracy depending on the conversion quality.
- Audio inputs heavily corrupted by background noise may yield lower confidence scores.

## License

All rights reserved.
