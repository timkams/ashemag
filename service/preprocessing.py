"""Adapts an uploaded PNG/JPEG knee X-ray into the tensor shape the
denizlab oai-xray-tkr-klg model expects, reproducing the published steps
from ExtractKnee/utils.py and XrayDataLoader.py in that repo.

KNOWN FIDELITY GAP: the original pipeline crops a 1024x1024 knee-centered
patch using a separate, unreleased knee-localizer model. That localizer is
not available here, so this adapter resizes the *whole* input image instead
of a knee-centered crop. Predictions on images that are not already tightly
framed on a single knee joint should be treated with additional caution.
"""
import io

import numpy as np
import torch
from PIL import Image

RESIZE_TO = 1024
CENTER_CROP_TO = 896
PERCENTILE_LOW = 5
PERCENTILE_HIGH = 99


def _global_contrast_normalize(img: np.ndarray, multiplier: float = 255.0) -> np.ndarray:
    lo, hi = np.percentile(img, [PERCENTILE_LOW, PERCENTILE_HIGH])
    img = np.clip(img, lo, hi)
    img = img - img.min()
    max_val = img.max()
    if max_val > 0:
        img = img / max_val
    return img * multiplier


def _resize(img: np.ndarray, size: int) -> np.ndarray:
    return np.array(Image.fromarray(img.astype(np.float32)).resize((size, size), Image.BICUBIC))


def _center_crop(img: np.ndarray, size: int) -> np.ndarray:
    h, w = img.shape[:2]
    top = (h - size) // 2
    left = (w - size) // 2
    return img[top:top + size, left:left + size]


def preprocess_image(image_bytes: bytes) -> torch.Tensor:
    """Returns a (1, 3, 896, 896) float tensor, unbatched values in [0, 255]."""
    pil_image = Image.open(io.BytesIO(image_bytes)).convert("L")
    img = np.array(pil_image, dtype=np.float64)

    img = _global_contrast_normalize(img)
    img = _resize(img, RESIZE_TO)
    img = _center_crop(img, CENTER_CROP_TO)

    img = np.tile(img[..., np.newaxis], 3)  # grayscale -> 3-channel
    img = np.transpose(img, (2, 0, 1))  # HWC -> CHW, matches XrayDataLoader.ToTensor
    tensor = torch.from_numpy(img).float()
    return tensor.unsqueeze(0)
