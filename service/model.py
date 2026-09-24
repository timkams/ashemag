"""Model architecture and checkpoint loading for the denizlab oai-xray-tkr-klg
ResNet-34 (https://github.com/denizlab/oai-xray-tkr-klg, weights CC-BY-4.0,
code AGPLv3). Architecture reproduced from that repo's inference.py so a
released checkpoint loads without modification.
"""
from pathlib import Path

import torch
from torch import nn
from torchvision import models

KL_GRADES = 5
TKR_CLASSES = 2


class MultiOutputModel(nn.Module):
    def __init__(self, model_core: nn.Module, num_ftrs: int):
        super().__init__()
        self.resnet_model = model_core
        self.y1o = nn.Linear(num_ftrs, TKR_CLASSES)
        self.y2o = nn.Linear(num_ftrs, KL_GRADES)

    def forward(self, x: torch.Tensor):
        features = self.resnet_model(x)
        return self.y1o(features), self.y2o(features)


def build_model() -> MultiOutputModel:
    backbone = models.resnet34(weights=None)
    backbone.avgpool = nn.AvgPool2d(kernel_size=28, stride=1, padding=0)
    num_ftrs = backbone.fc.in_features
    backbone.fc = nn.Sequential()
    return MultiOutputModel(backbone, num_ftrs)


def load_model(weights_path: Path, device: torch.device) -> MultiOutputModel:
    if not weights_path.exists():
        raise FileNotFoundError(
            f"Model weights not found at {weights_path}. See service/README.md "
            "for how to download them from Zenodo record 11479344."
        )
    model = build_model()
    state_dict = torch.load(weights_path, map_location=device, weights_only=True)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model
