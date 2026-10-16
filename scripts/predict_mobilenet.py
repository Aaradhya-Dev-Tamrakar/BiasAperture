#!/usr/bin/env python3
"""
MobileNetV2 Gender Classification Inference Pipeline — Model 4 Integration.

Runs inference using the HuggingFace MobileNetV2 gender classification checkpoint
(`rizvandwiki/gender-classification`, fine-tuned MobileNetV2 on diverse face images)
on FairFace validation images to generate a schema-aligned predictions CSV.

This completes the 4-model architectural comparison suite:
  1. FairFace ResNet-34 (Shallow CNN Baseline)
  2. Vision Transformer ViT-B/16 (Non-convolutional Self-Attention)
  3. ResNet-50 (Deeper Residual Bottleneck CNN)
  4. MobileNetV2 (Ultra-Lightweight Edge / Mobile CNN — this script)

Model: rizvandwiki/gender-classification
  - Architecture : MobileNetV2 (google/mobilenet_v2_1.0_224 backbone)
  - Fine-tuned on: gender classification dataset (diverse face images)
  - Input        : 224x224, preprocessed by AutoImageProcessor
  - Output labels: {"female": 0, "male": 1} (resolved via model.config.id2label)

Output CSV Columns (Milestone M1 Schema Invariant):
  face_name_align, race, gender, age, true_label, predicted_label

Usage:
  # Standard inference on FairFace validation split
  python scripts/predict_mobilenet.py \\
    --data-root data/raw/fairface \\
    --split val \\
    --output data/processed/fairface_predictions_mobilenet_val.csv \\
    --batch-size 32

  # Test run on first 10 images
  python scripts/predict_mobilenet.py --max-samples 10
"""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# ============================================================================
# Model & Taxonomy Constants
# ============================================================================

DEFAULT_MODEL_ID = "rizvandwiki/gender-classification"

RAW_AGE_MAPPING = {
    "more than 70": "70+",
}

# ============================================================================
# FairFace Dataset Helper
# ============================================================================


class FairFaceDataset(Dataset):
    """Lightweight FairFace image dataset for batch inference."""

    def __init__(
        self,
        df: pd.DataFrame,
        images_dir: Path,
        processor,
    ):
        self.df = df.reset_index(drop=True)
        self.images_dir = images_dir
        self.processor = processor
        self._skipped: list[int] = []

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]
        image_name = str(row.get("file") or row.get("face_name_align", ""))
        if "/" in image_name or "\\" in image_name:
            image_name = Path(image_name).name

        img_path = self.images_dir / image_name
        try:
            pil_img = Image.open(img_path).convert("RGB")
        except Exception as exc:
            raise RuntimeError(
                f"Audit-cohort integrity violation: failed to read image '{image_name}' "
                f"at '{img_path}': {exc}. Synthetic image substitution is strictly prohibited "
                "to prevent demographic distortion and maintain audit validity."
            ) from exc

        # AutoImageProcessor handles resize, normalisation, tensor conversion
        pixel_values = self.processor(images=pil_img, return_tensors="pt")["pixel_values"][0]

        meta = {
            "image_name": image_name,
            "race": str(row.get("race", "")),
            "gender": str(row.get("gender", "")),
            "age": str(row.get("age", "")),
        }
        return pixel_values, meta


def collate_fn(batch):
    pixels = torch.stack([item[0] for item in batch])
    metas = [item[1] for item in batch]
    return pixels, metas


# ============================================================================
# Main Inference Pipeline
# ============================================================================


def run_mobilenet_predictions(
    data_root: Path,
    split: Literal["train", "val"] = "val",
    output_path: Path | None = None,
    model_id: str = DEFAULT_MODEL_ID,
    batch_size: int = 32,
    device_str: str = "auto",
    max_samples: int | None = None,
    start_index: int = 0,
    end_index: int | None = None,
) -> int:
    """Run MobileNetV2 gender classification on FairFace images and write CSV."""
    from transformers import AutoImageProcessor, AutoModelForImageClassification

    # ── 1. Resolve device ────────────────────────────────────────────────────
    if device_str == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device_str)
    print(f"[*] Device: {device}")

    # ── 2. Resolve paths ─────────────────────────────────────────────────────
    labels_csv = data_root / f"fairface_label_{split}.csv"
    if not labels_csv.exists():
        labels_csv = data_root / "data" / f"fairface_label_{split}.csv"
    if not labels_csv.exists():
        print(f"[ERROR] Labels CSV not found: {labels_csv}", file=sys.stderr)
        return 1

    candidate_img_dirs = [
        data_root / "detected_faces" / split,
        data_root / split,
        data_root / "detected_faces",
    ]
    images_dir = next((d for d in candidate_img_dirs if d.exists()), candidate_img_dirs[0])
    if not images_dir.exists():
        print(f"[ERROR] Images directory not found in: {candidate_img_dirs}", file=sys.stderr)
        return 1

    print(f"[*] Labels CSV : {labels_csv}")
    print(f"[*] Images dir : {images_dir}")

    # ── 3. Read labels ───────────────────────────────────────────────────────
    df_labels = pd.read_csv(labels_csv)
    print(f"[*] Total records in split: {len(df_labels)}")

    if start_index or end_index is not None:
        end = end_index if end_index is not None else len(df_labels)
        df_labels = df_labels.iloc[start_index:end]
        print(f"[*] Sharded range: [{start_index}:{end}] ({len(df_labels)} rows)")

    if max_samples:
        df_labels = df_labels.head(max_samples)
        print(f"[*] Sample limit: {max_samples}")

    # ── 4. Load model & processor ────────────────────────────────────────────
    print(f"[*] Loading model & processor: {model_id}")
    processor = AutoImageProcessor.from_pretrained(model_id)
    model = AutoModelForImageClassification.from_pretrained(model_id)
    model.to(device)
    model.eval()

    # Resolve label mapping from model config (robust to any id2label ordering)
    id2label_raw: dict = model.config.id2label  # e.g. {0: "female", 1: "male"}
    # Normalise to Title-case ("Female", "Male") to match FairFace schema
    id2label = {k: v.strip().title() for k, v in id2label_raw.items()}
    print(f"[*] Model id2label: {id2label}")

    # ── 5. Build DataLoader ──────────────────────────────────────────────────
    dataset = FairFaceDataset(df_labels, images_dir, processor)
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,  # 0 avoids Windows multiprocessing issues
        collate_fn=collate_fn,
    )

    # ── 6. Inference loop ────────────────────────────────────────────────────
    records: list[dict] = []
    print(
        f"[*] Running MobileNetV2 inference across {len(dataset)} items "
        f"(batch_size={batch_size}, device={device})..."
    )

    with torch.no_grad():
        for pixel_values, metas in tqdm(loader, desc="Predicting (MobileNetV2)"):
            pixel_values = pixel_values.to(device)
            outputs = model(pixel_values=pixel_values)
            pred_indices = torch.argmax(outputs.logits, dim=-1).cpu().tolist()

            for meta, pred_idx in zip(metas, pred_indices):
                pred_label = id2label.get(int(pred_idx), "Male")
                raw_age = meta["age"]
                norm_age = RAW_AGE_MAPPING.get(raw_age, raw_age)

                records.append(
                    {
                        "face_name_align": meta["image_name"],
                        "race": meta["race"],
                        "gender": meta["gender"],
                        "age": norm_age,
                        "true_label": meta["gender"],
                        "predicted_label": pred_label,
                    }
                )

    if not records:
        print("[ERROR] No successful predictions generated.", file=sys.stderr)
        return 1

    df_out = pd.DataFrame(records)

    # ── 7. Save CSV ──────────────────────────────────────────────────────────
    if output_path is None:
        output_path = Path("data/processed/fairface_predictions_mobilenet_val.csv")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(output_path, index=False)

    acc = (df_out["true_label"] == df_out["predicted_label"]).mean() * 100
    print(f"\n[✓] Predictions saved: {output_path}")
    print(f"    Rows    : {len(df_out)}")
    print(f"    Columns : {list(df_out.columns)}")
    print(f"    Overall Gender Accuracy: {acc:.2f}%")

    male_pred  = (df_out["predicted_label"] == "Male").sum()
    female_pred = (df_out["predicted_label"] == "Female").sum()
    print(f"    Pred dist: Male={male_pred}, Female={female_pred}")

    return 0


# ============================================================================
# CLI Entrypoint
# ============================================================================


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="MobileNetV2 Gender Classification Batch Prediction Runner for BiasAperture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path("data/raw/fairface"),
        help="Path to FairFace root dataset directory (default: data/raw/fairface)",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="val",
        choices=["train", "val"],
        help="Dataset split to evaluate (default: val)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("data/processed/fairface_predictions_mobilenet_val.csv"),
        help="Destination predictions CSV file path",
    )
    parser.add_argument(
        "--model-id",
        type=str,
        default=DEFAULT_MODEL_ID,
        help=f"HuggingFace model ID (default: {DEFAULT_MODEL_ID})",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for model inference (default: 32)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="Compute device (default: auto)",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Optional maximum number of samples to evaluate (for testing)",
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=0,
        help="Start index for sharded processing (default: 0)",
    )
    parser.add_argument(
        "--end-index",
        type=int,
        default=None,
        help="End index for sharded processing (default: None)",
    )

    args = parser.parse_args(argv)

    return run_mobilenet_predictions(
        data_root=args.data_root,
        split=args.split,
        output_path=args.output,
        model_id=args.model_id,
        batch_size=args.batch_size,
        device_str=args.device,
        max_samples=args.max_samples,
        start_index=args.start_index,
        end_index=args.end_index,
    )


if __name__ == "__main__":
    sys.exit(main())
