"""
FairFace Batch Prediction Runner — WP2 (Stream A).

Loads FairFace labeled dataset, runs inference using dchen236/FairFace ResNet-34,
and outputs schema-aligned predictions CSV for data_ingestion.py.

Requirements:
  - dlib (face detection & 5-point alignment)
  - torch (ResNet-34 inference)
  - torchvision (preprocessing)
  - pandas (CSV output)
  - Pillow (image I/O)

Usage:
  python scripts/predict.py \\
    --data-root data/raw/fairface \\
    --split val \\
    --output data/processed/fairface_predictions_val.csv \\
    --batch-size 64 \\
    --device cuda

Output CSV columns:
  face_name_align, race, gender, age, true_label, predicted_label
"""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path
from typing import Literal

import dlib
import numpy as np
import pandas as pd
import torch
import torchvision.transforms as transforms
from PIL import Image
from torch import nn
from tqdm import tqdm

# Suppress FutureWarning from torchvision transforms
warnings.filterwarnings("ignore", category=FutureWarning)

# ============================================================================
# ResNet-34 Model Definition (Compatible with FairFace Weights)
# ============================================================================


class ResNet34MultiTask(nn.Module):
    """
    ResNet-34 with three independent task heads for age, gender, race.
    Matches the architecture of dchen236/FairFace pretrained weights.
    """

    def __init__(self, num_classes_age: int = 9, num_classes_gender: int = 2, num_classes_race: int = 7):
        super().__init__()
        self.backbone = torch.hub.load("pytorch/vision:v0.10.0", "resnet34", pretrained=False)
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Identity()

        self.age_head = nn.Linear(in_features, num_classes_age)
        self.gender_head = nn.Linear(in_features, num_classes_gender)
        self.race_head = nn.Linear(in_features, num_classes_race)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Forward pass returns logits for each task."""
        features = self.backbone(x)
        age_logits = self.age_head(features)
        gender_logits = self.gender_head(features)
        race_logits = self.race_head(features)
        return age_logits, gender_logits, race_logits


# ============================================================================
# Label Vocabularies (Must Match schema.py)
# ============================================================================

AGE_LABELS = ("0-2", "3-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70+")
GENDER_LABELS = ("Male", "Female")
RACE_LABELS = ("White", "Black", "Latino_Hispanic", "East Asian", "Southeast Asian", "Indian", "Middle Eastern")


# ============================================================================
# Utilities
# ============================================================================


def load_model(checkpoint_path: Path, device: torch.device) -> ResNet34MultiTask:
    """Load FairFace ResNet-34 checkpoint."""
    model = ResNet34MultiTask()
    try:
        state_dict = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(state_dict, strict=False)
        print(f"[*] Loaded checkpoint: {checkpoint_path}")
    except Exception as e:
        print(f"[ERROR] Failed to load checkpoint {checkpoint_path}: {e}", file=sys.stderr)
        raise
    model.to(device)
    model.eval()
    return model


def detect_and_align_face(
    image_path: Path,
    detector: dlib.cnn_face_detection_model_v1,
    sp: dlib.shape_predictor,
    output_size: int = 224,
    padding: float = 0.25,
) -> np.ndarray | None:
    """
    Detect face using dlib CNN detector and align using 5-point landmark.
    Returns aligned face crop or None if no face detected.
    """
    try:
        img = dlib.load_rgb_image(str(image_path))
    except Exception as e:
        print(f"[WARN] Failed to load image {image_path}: {e}", file=sys.stderr)
        return None

    try:
        dets = detector(img, upsample_num_times=1)
        if len(dets) == 0:
            print(f"[WARN] No face detected in {image_path.name}", file=sys.stderr)
            return None

        det = dets[0].rect
        sp5 = sp(img, det)
        face_chip = dlib.get_face_chip(img, sp5, size=output_size, padding=padding)
        return np.array(face_chip)
    except Exception as e:
        print(f"[WARN] Face alignment failed for {image_path}: {e}", file=sys.stderr)
        return None


def predict_single_image(
    image_path: Path,
    model: ResNet34MultiTask,
    detector: dlib.cnn_face_detection_model_v1,
    sp: dlib.shape_predictor,
    device: torch.device,
    transform: transforms.Compose,
    true_age: str | None = None,
    true_gender: str | None = None,
    true_race: str | None = None,
) -> dict | None:
    """
    Run single-image prediction pipeline: detect → align → infer → decode labels.
    Returns a row dict or None on failure.
    """
    # Detect & align
    face_chip = detect_and_align_face(image_path, detector, sp)
    if face_chip is None:
        return None

    # Preprocess & infer
    try:
        pil_img = Image.fromarray(face_chip)
        tensor = transform(pil_img).unsqueeze(0).to(device)

        with torch.no_grad():
            age_logits, gender_logits, race_logits = model(tensor)
            age_pred = AGE_LABELS[age_logits.argmax(dim=1).item()]
            gender_pred = GENDER_LABELS[gender_logits.argmax(dim=1).item()]
            race_pred = RACE_LABELS[race_logits.argmax(dim=1).item()]
    except Exception as e:
        print(f"[WARN] Inference failed for {image_path}: {e}", file=sys.stderr)
        return None

    # Build output row
    return {
        "face_name_align": image_path.name,
        "race": true_race or race_pred,  # Use ground truth if available
        "gender": true_gender or gender_pred,
        "age": true_age or age_pred,
        "true_label": true_race or race_pred,  # Placeholder: set to predicted if no ground truth
        "predicted_label": race_pred,  # Primary prediction task (race)
    }


def run_batch_prediction(
    data_root: Path,
    split: Literal["train", "val"],
    output_path: Path,
    checkpoint_path: Path | None = None,
    batch_size: int = 64,
    device: str = "cuda",
    max_samples: int | None = None,
    start_index: int = 0,
    end_index: int | None = None,
) -> int:
    """
    Run batch predictions on FairFace split.

    Args:
        data_root: Root of FairFace dataset (should contain detected_faces/ and fairface_label_*.csv)
        split: "train" or "val"
        output_path: Output CSV path
        checkpoint_path: Path to pretrained ResNet-34 checkpoint
        batch_size: Batch size (not used for single-image inference, but kept for API compatibility)
        device: "cuda" or "cpu"
        max_samples: Limit number of samples (for dev/testing)
        start_index: Start row index into the labels CSV (for sharding across parallel runs)
        end_index: End row index (exclusive) into the labels CSV (for sharding across parallel runs)

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    device_obj = torch.device(device if torch.cuda.is_available() else "cpu")
    print(f"[*] Using device: {device_obj}")

    # ========================================================================
    # Load model
    # ========================================================================
    if checkpoint_path is None:
        checkpoint_path = Path("fairface_alldata_20191111.pt")
        if not checkpoint_path.exists():
            print(
                f"[ERROR] No checkpoint found at {checkpoint_path}. "
                "Download from: https://github.com/dchen236/FairFace/tree/master/detected_faces",
                file=sys.stderr,
            )
            return 1

    model = load_model(checkpoint_path, device_obj)

    # ========================================================================
    # Load FairFace labels CSV
    # ========================================================================
    labels_csv = data_root / f"fairface_label_{split}.csv"
    if not labels_csv.exists():
        print(f"[ERROR] Labels CSV not found: {labels_csv}", file=sys.stderr)
        return 1

    try:
        df_labels = pd.read_csv(labels_csv)
        print(f"[*] Loaded {len(df_labels)} labels from {labels_csv.name}")
    except Exception as e:
        print(f"[ERROR] Failed to read labels CSV: {e}", file=sys.stderr)
        return 1

    # ========================================================================
    # Slice for sharding (parallel runs across multiple processes)
    # ========================================================================
    if end_index is not None:
        df_labels = df_labels.iloc[start_index:end_index]
    elif start_index:
        df_labels = df_labels.iloc[start_index:]

    if start_index or end_index is not None:
        print(f"[*] Sharded to rows [{start_index}:{end_index if end_index is not None else 'end'}] "
              f"({len(df_labels)} rows)")

    if max_samples:
        df_labels = df_labels.head(max_samples)
        print(f"[*] Limited to {max_samples} samples for testing")

    # ========================================================================
    # Load dlib detectors
    # ========================================================================
    print("[*] Loading dlib face detector and shape predictor...")
    try:
        detector = dlib.cnn_face_detection_model_v1("mmod_human_face_detector.dat")
        sp = dlib.shape_predictor("shape_predictor_5_face_landmarks.dat")
    except Exception as e:
        print(
            f"[ERROR] Failed to load dlib models: {e}. "
            "Download: http://dlib.net/files/ and place in working directory",
            file=sys.stderr,
        )
        return 1

    # ========================================================================
    # Preprocessing transform
    # ========================================================================
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    # ========================================================================
    # Run predictions
    # ========================================================================
    images_root = data_root / "detected_faces"
    predictions = []
    skipped_count = 0

    print(f"[*] Running inference on {len(df_labels)} images...")
    for idx, row in tqdm(df_labels.iterrows(), total=len(df_labels), desc=f"Predicting ({split})"):
        image_id = row.get("file") or row.get("face_name_align")
        image_path = images_root / str(image_id)

        if not image_path.exists():
            print(f"[WARN] Image not found: {image_path}", file=sys.stderr)
            skipped_count += 1
            continue

        result = predict_single_image(
            image_path,
            model,
            detector,
            sp,
            device_obj,
            transform,
            true_age=row.get("age"),
            true_gender=row.get("gender"),
            true_race=row.get("race"),
        )

        if result:
            predictions.append(result)
        else:
            skipped_count += 1

    # ========================================================================
    # Write output
    # ========================================================================
    if not predictions:
        print("[ERROR] No successful predictions. Check image paths and detector models.", file=sys.stderr)
        return 1

    df_out = pd.DataFrame(predictions)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(output_path, index=False)

    print(f"\n[✓] Wrote {len(predictions)} predictions to {output_path}")
    print(f"[*] Skipped: {skipped_count}")
    print(f"[*] Success rate: {100 * len(predictions) / (len(predictions) + skipped_count):.1f}%")

    return 0


# ============================================================================
# CLI
# ============================================================================


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="FairFace batch prediction runner for BiasAperture WP2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run on validation split (GPU)
  python scripts/predict.py --data-root data/raw/fairface --split val \\
    --output data/processed/fairface_predictions_val.csv

  # Run on training split with CPU (slower)
  python scripts/predict.py --data-root data/raw/fairface --split train \\
    --output data/processed/fairface_predictions_train.csv --device cpu

  # Development subset (100 images for testing)
  python scripts/predict.py --data-root data/raw/fairface --split val \\
    --output data/processed/fairface_predictions_val_dev.csv --max-samples 100

  # Sharded run (e.g. worker 1 of 4, rows 0-2739) for parallel processing
  python scripts/predict.py --data-root data/raw/fairface --split val \\
    --output data/processed/fairface_predictions_val_part1.csv \\
    --start-index 0 --end-index 2739
        """,
    )

    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path("data/raw/fairface"),
        help="Root directory of FairFace dataset (default: data/raw/fairface)",
    )
    parser.add_argument(
        "--split",
        type=str,
        choices=["train", "val"],
        default="val",
        help="Dataset split to predict on (default: val)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/fairface_predictions.csv"),
        help="Output CSV path (default: data/processed/fairface_predictions.csv)",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        help="Path to pretrained ResNet-34 checkpoint (default: fairface_alldata_20191111.pt in current dir)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Batch size (default: 64, reserved for future batched implementation)",
    )
    parser.add_argument(
        "--device",
        type=str,
        choices=["cuda", "cpu"],
        default="cuda",
        help="Compute device (default: cuda)",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        help="Limit predictions to N samples (for testing/dev subsets)",
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=0,
        help="Start row index into the labels CSV, for sharding across parallel runs (default: 0)",
    )
    parser.add_argument(
        "--end-index",
        type=int,
        default=None,
        help="End row index (exclusive) into the labels CSV, for sharding across parallel runs (default: end)",
    )

    args = parser.parse_args(argv)

    return run_batch_prediction(
        data_root=args.data_root,
        split=args.split,
        output_path=args.output,
        checkpoint_path=args.checkpoint,
        batch_size=args.batch_size,
        device=args.device,
        max_samples=args.max_samples,
        start_index=args.start_index,
        end_index=args.end_index,
    )


if __name__ == "__main__":
    raise SystemExit(main())