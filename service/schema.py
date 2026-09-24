"""Response schema for POST /api/knee/analyze.

The underlying model (denizlab/oai-xray-tkr-klg) predicts KL grade AND a
total-knee-replacement (TKR) risk probability — two heads, not one. Rather
than dropping the TKR head to force-fit a narrower schema, it's preserved
under `additionalFindings` alongside the requested `assessment`/
`probabilities` shape.
"""
from pydantic import BaseModel

LIMITATIONS = [
    "Research prototype only — not a diagnostic device and not validated for clinical use.",
    "The original model pipeline crops a knee-centered region using a separate, unreleased "
    "localizer model. This service resizes the full uploaded image instead, which may reduce "
    "accuracy on images that are not already tightly framed on a single knee joint.",
    "Uses one nested-cross-validation fold (Fold_1/CV1) of the released weights, not the full "
    "fold ensemble the source paper's reported metrics are based on.",
]


class OsteoarthritisAssessment(BaseModel):
    task: str = "osteoarthritis"
    grade: int
    confidence: float


class KLProbabilities(BaseModel):
    grade0: float
    grade1: float
    grade2: float
    grade3: float
    grade4: float


class TkrRisk(BaseModel):
    probability: float
    threshold: float = 0.3802338
    aboveThreshold: bool


class ModelInfo(BaseModel):
    name: str = "denizlab/oai-xray-tkr-klg"
    checkpoint: str = "Fold_1/CV1"
    weightsSource: str = "https://zenodo.org/records/11479344"
    license: str = "Weights: CC-BY-4.0. Inference code (adapted): AGPL-3.0."


class KneeAnalysisResponse(BaseModel):
    imageId: str
    modality: str = "knee-xray"
    assessment: OsteoarthritisAssessment
    probabilities: KLProbabilities
    additionalFindings: dict[str, TkrRisk]
    modelInfo: ModelInfo
    limitations: list[str] = LIMITATIONS
