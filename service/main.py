"""FastAPI inference service for the knee X-ray POC.

Isolated on purpose: the only thing the React app knows about is
POST /api/knee/analyze and this response schema. Swapping the underlying
model later means changing model.py/preprocessing.py, not the frontend.
"""
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from model import load_model
from preprocessing import preprocess_image
from schema import KLProbabilities, KneeAnalysisResponse, ModelInfo, OsteoarthritisAssessment, TkrRisk

WEIGHTS_PATH = Path(__file__).parent / "weights" / "best_weights.pth"
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
TKR_THRESHOLD = 0.3802338

_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    _state["model"] = load_model(WEIGHTS_PATH, DEVICE)
    yield
    _state.clear()


app = FastAPI(title="Knee X-ray Inference Service", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    # Vite's default dev port is 3016 but it auto-increments if taken, so allow any localhost port.
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "device": str(DEVICE)}


@app.post("/api/knee/analyze", response_model=KneeAnalysisResponse)
async def analyze(file: UploadFile = File(...)):
    if file.content_type not in ("image/png", "image/jpeg"):
        raise HTTPException(400, f"Unsupported content type: {file.content_type}")

    image_bytes = await file.read()
    try:
        tensor = preprocess_image(image_bytes).to(DEVICE)
    except Exception as exc:
        raise HTTPException(400, f"Could not read image: {exc}") from exc

    model = _state["model"]
    with torch.no_grad():
        tkr_logits, kl_logits = model(tensor)
        tkr_probs = torch.softmax(tkr_logits, dim=1)[0].cpu().tolist()
        kl_probs = torch.softmax(kl_logits, dim=1)[0].cpu().tolist()

    grade = max(range(len(kl_probs)), key=lambda i: kl_probs[i])
    tkr_positive = tkr_probs[1]

    return KneeAnalysisResponse(
        imageId=str(uuid.uuid4()),
        assessment=OsteoarthritisAssessment(grade=grade, confidence=kl_probs[grade]),
        probabilities=KLProbabilities(
            grade0=kl_probs[0], grade1=kl_probs[1], grade2=kl_probs[2],
            grade3=kl_probs[3], grade4=kl_probs[4],
        ),
        additionalFindings={
            "totalKneeReplacementRisk": TkrRisk(
                probability=tkr_positive,
                aboveThreshold=tkr_positive >= TKR_THRESHOLD,
            )
        },
        modelInfo=ModelInfo(),
    )
