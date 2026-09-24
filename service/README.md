# Knee X-ray inference service

FastAPI wrapper around the pretrained [denizlab/oai-xray-tkr-klg](https://github.com/denizlab/oai-xray-tkr-klg)
ResNet-34 model (Kellgren-Lawrence grade + total-knee-replacement risk).
This service and its dependencies are licensed **AGPL-3.0** (see `LICENSE`
in this directory) — separate from the rest of this repository, which is
MIT. The model weights themselves are CC-BY-4.0.

This is a research prototype, not a diagnostic tool. See `schema.py` for
the caveats returned with every response.

## 1. Download the model weights

Weights are not committed to this repo (3.3 GB). Download them from
[Zenodo record 11479344](https://zenodo.org/records/11479344)
(`2020_03_DLTLMT_ModelWeights.zip`), then:

```sh
cd service
mkdir -p weights
unzip ~/Downloads/2020_03_DLTLMT_ModelWeights.zip -d weights/_extracted
cp weights/_extracted/Fold_1/CV1/best_weights.pth weights/best_weights.pth
```

This uses one nested-cross-validation fold (`Fold_1/CV1`). The archive
contains other folds under `weights/_extracted/Fold_N/CVn/` if you want to
try a different one — just point `weights/best_weights.pth` at whichever
checkpoint you use.

## 2. Set up the environment

```sh
cd service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Run the server

```sh
uvicorn main:app --reload --port 8000
```

On Apple Silicon, PyTorch will use MPS automatically if available,
otherwise it falls back to CPU — both work fine at this model's size.

## 4. Test it

```sh
curl -s http://localhost:8000/health

curl -s -X POST http://localhost:8000/api/knee/analyze \
  -F "file=@/path/to/knee.png" | python3 -m json.tool
```

The frontend (`app/knee-xray.ts`) calls this service at the URL in
`VITE_KNEE_API_URL` (defaults to `http://localhost:8000`).
