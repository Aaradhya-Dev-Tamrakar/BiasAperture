#!/usr/bin/env python3
"""
Diagnostic script: inspect SSCMA MobileNetV2 ONNX model output under
different normalization/channel-order schemes to find the correct preprocessing.

Run:
    uv run python scripts/diagnose_mobilenet.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import onnxruntime as ort
import pandas as pd
from PIL import Image

ONNX_PATH = Path("models/mobilenetv2_gender/mbv2_0.35_rep_gender.onnx")
DATA_ROOT = Path("data/raw/fairface")
LABELS_CSV = DATA_ROOT / "fairface_label_val.csv"
IMAGES_DIR = DATA_ROOT / "detected_faces" / "val"
N_SAMPLES = 30

# -- Load model ----------------------------------------------------------------
session = ort.InferenceSession(str(ONNX_PATH), providers=["CPUExecutionProvider"])
in_name  = session.get_inputs()[0].name
out_name = session.get_outputs()[0].name
print(f"Input  : {in_name}  shape={session.get_inputs()[0].shape}")
print(f"Output : {out_name} shape={session.get_outputs()[0].shape}\n")

# -- Load sample images --------------------------------------------------------
df = pd.read_csv(LABELS_CSV).head(N_SAMPLES)
images, true_labels = [], []
for _, row in df.iterrows():
    fname = Path(str(row.get("file") or row.get("face_name_align"))).name
    img = Image.open(IMAGES_DIR / fname).convert("RGB").resize((64, 64), Image.Resampling.BILINEAR)
    images.append(np.array(img, dtype=np.float32))   # HWC, RGB, [0,255]
    true_labels.append(str(row["gender"]))

ID2LABEL = {0: "Female", 1: "Male"}

def run_scheme(name: str, arrays: list) -> None:
    preds, raw_logits = [], []
    for arr in arrays:
        chw = np.transpose(arr, (2, 0, 1))[np.newaxis]          # (1,3,64,64)
        logits = session.run([out_name], {in_name: chw})[0][0]  # (2,)
        raw_logits.append(logits)
        preds.append(ID2LABEL[int(np.argmax(logits))])

    correct = sum(p == t for p, t in zip(preds, true_labels))
    avg_logits = np.mean(raw_logits, axis=0)
    male_count = preds.count("Male")
    print(f"[{name}]")
    print(f"  Accuracy   : {correct}/{N_SAMPLES} = {100*correct/N_SAMPLES:.1f}%")
    print(f"  Pred dist  : Male={male_count}, Female={N_SAMPLES - male_count}")
    print(f"  Mean logits: Female={avg_logits[0]:.3f}, Male={avg_logits[1]:.3f}")
    print()

# -- Scheme 1: RGB [0,255] original -------------------------------------------
MEAN_RGB = np.array([123.675, 116.28, 103.53], dtype=np.float32)
STD_RGB  = np.array([58.395,  57.12,  57.375], dtype=np.float32)
s1 = [(img - MEAN_RGB) / STD_RGB for img in images]
run_scheme("S1 RGB [0,255] std ImageNet means", s1)

# -- Scheme 2: BGR [0,255] current fix ----------------------------------------
MEAN_BGR = np.array([103.53, 116.28, 123.675], dtype=np.float32)
STD_BGR  = np.array([57.375, 57.12,  58.395],  dtype=np.float32)
s2 = [((img[:,:,::-1].copy()) - MEAN_BGR) / STD_BGR for img in images]
run_scheme("S2 BGR [0,255] std ImageNet means", s2)

# -- Scheme 3: RGB [0,1] standard PyTorch ImageNet ----------------------------
MEAN_01 = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD_01  = np.array([0.229, 0.224, 0.225], dtype=np.float32)
s3 = [((img / 255.0) - MEAN_01) / STD_01 for img in images]
run_scheme("S3 RGB [0,1] PyTorch ImageNet means", s3)

# -- Scheme 4: BGR [0,1] -------------------------------------------------------
MEAN_BGR_01 = np.array([0.406, 0.456, 0.485], dtype=np.float32)
STD_BGR_01  = np.array([0.225, 0.224, 0.229], dtype=np.float32)
s4 = [((img[:,:,::-1].copy() / 255.0) - MEAN_BGR_01) / STD_BGR_01 for img in images]
run_scheme("S4 BGR [0,1] PyTorch ImageNet means", s4)

# -- Scheme 5: Raw [0,255] no normalization ------------------------------------
s5 = [img.copy() for img in images]
run_scheme("S5 RGB [0,255] no normalization", s5)

# -- Scheme 6: Raw [0,1] no mean/std ------------------------------------------
s6 = [img / 255.0 for img in images]
run_scheme("S6 RGB [0,1] no mean/std", s6)

# -- Ground truth distribution -------------------------------------------------
male_gt = true_labels.count("Male")
print(f"Ground truth: Male={male_gt}, Female={N_SAMPLES - male_gt} out of {N_SAMPLES}")
