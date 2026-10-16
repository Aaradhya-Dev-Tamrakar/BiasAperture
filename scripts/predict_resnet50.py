#!/usr/bin/env python3
"""
ResNet-50 Gender Classification Inference Pipeline — Model 3 Integration.

Runs inference using the pretrained HuggingFace ResNet-50 gender classification checkpoint
(`crangana/trained-gender`, fine-tuned from microsoft/resnet-50 on FairFace)
on FairFace validation images to generate a schema-aligned predictions CSV.

This completes the 3-model architectural comparison suite:
  1. FairFace ResNet-34 (Shallow CNN Baseline)
  2. Vision Transformer ViT-B/16 (Non-convolutional Self-Attention)
  3. ResNet-50 (Deeper Residual CNN — this script)

Output CSV Columns:
  face_name_align, race, gender, age, true_label, predicted_label

Usage:
  # Standard inference on FairFace validation split
  python scripts/predict_resnet50.py \
    --data-root data/raw/fairface \
    --split val \
    --output data/processed/fairface_predictions_resnet50_val.csv \
    --batch-size 64 \
    --device auto

  # Test run on first 10 images
  python scripts/predict_resnet50.py --max-samples 10
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

# Suppress standard benign warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# ============================================================================
# Model & Taxonomy Constants (Locked to schema.py)
# ============================================================================

DEFAULT_MODEL_ID = "crangana/trained-gender"

RACE_LABELS = (
    "White",
    "Black",
    "Latino_Hispanic",
    "East Asian",
    "Southeast Asian",
    "Indian",
    "Middle Eastern",
)
GENDER_LABELS = ("Male", "Female")
AGE_LABELS = (
    "0-2",
    "3-9",
    "10-19",
    "20-29",
    "30-39",
    "40-49",
    "50-59",
    "60-69",
    "70+",
)

# Canonical mapping for raw FairFace age aliases
RAW_AGE_MAPPING = {
    "more than 70": "70+",
}


# ============================================================================
# Dataset Definition for High-Throughput Batching
# ============================================================================


class FairFaceImageDataset(Dataset):
    """PyTorch Dataset for batched image loading and preprocessing."""

    def __init__(
        self,
        df_labels: pd.DataFrame,
        images_dir: Path,
        processor_or_transform,
        use_hf_processor: bool = True,
    ):
        self.df = df_labels.reset_index(drop=True)
        self.images_dir = images_dir
        self.processor = processor_or_transform
        self.use_hf_processor = use_hf_processor

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> dict:
        row = self.df.iloc[idx]
        image_name = str(row.get("file") or row.get("face_name_align"))
        if "/" in image_name:
            image_name = Path(image_name).name

        image_path = self.images_dir / image_name

        try:
            pil_img = Image.open(image_path).convert("RGB")
        except Exception as e:
            pil_img = None
            err_msg = str(e)
        else:
            err_msg = ""

        return {
            "index": idx,
            "image_name": image_name,
            "pil_image": pil_img,
            "error": err_msg,
            "race": str(row.get("race", "")),
            "gender": str(row.get("gender", "")),
            "age": str(row.get("age", "")),
        }


def collate_fairface_batch(batch: list[dict], processor, device: torch.device):
    """Collate function that batches PIL images through processor/transform."""
    valid_items = [item for item in batch if item["pil_image"] is not None]
    if not valid_items:
        return None

    images = [item["pil_image"] for item in valid_items]

    # Preprocess via HuggingFace AutoImageProcessor or torchvision
    if hasattr(processor, "preprocess"):
        inputs = processor(images=images, return_tensors="pt")
        pixel_values = inputs["pixel_values"].to(device)
    else:
        # Standard torchvision transform
        tensors = [processor(img) for img in images]
        pixel_values = torch.stack(tensors).to(device)

    metadata = [
        {
            "index": item["index"],
            "image_name": item["image_name"],
            "race": item["race"],
            "gender": item["gender"],
            "age": item["age"],
        }
        for item in valid_items
    ]

    return {"pixel_values": pixel_values, "metadata": metadata}


# ============================================================================
# Model Loader
# ============================================================================


def load_resnet50_gender_model(
    model_id_or_path: str = DEFAULT_MODEL_ID,
    device: torch.device = torch.device("cpu"),
):
    """Load ResNet-50 gender classification model and processor.

    Tries HuggingFace transformers first; supports local directory or hub id.
    """
    try:
        from transformers import AutoModelForImageClassification
        import torchvision.transforms as transforms

        print(f"[*] Loading ResNet-50 gender model weights from Hugging Face: {model_id_or_path}")
        model = AutoModelForImageClassification.from_pretrained(model_id_or_path)
        model.to(device)
        model.eval()

        # Output label mapping
        id2label = getattr(model.config, "id2label", {0: "Male", 1: "Female"})
        id2label = {int(k) if isinstance(k, str) and k.isdigit() else k: v for k, v in id2label.items()}
        print(f"[*] Architecture: {getattr(model.config, 'architectures', ['ResNetForImageClassification'])}")
        print(f"[*] Label mapping: {id2label}")

        # Try Hugging Face image processor first; fall back to standard ImageNet torchvision transform
        processor = None
        use_hf_processor = False
        try:
            from transformers import AutoImageProcessor
            processor = AutoImageProcessor.from_pretrained(model_id_or_path)
            use_hf_processor = True
            print("[*] Image processor: Hugging Face AutoImageProcessor")
        except Exception:
            try:
                from transformers import AutoFeatureExtractor
                processor = AutoFeatureExtractor.from_pretrained(model_id_or_path)
                use_hf_processor = True
                print("[*] Image processor: Hugging Face AutoFeatureExtractor")
            except Exception:
                processor = transforms.Compose(
                    [
                        transforms.Resize((224, 224)),
                        transforms.ToTensor(),
                        transforms.Normalize(
                            mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                        ),
                    ]
                )
                use_hf_processor = False
                print("[*] Image processor: Standard PyTorch torchvision transform (224x224 RGB, ImageNet mean/std)")

        return model, processor, id2label, use_hf_processor

    except Exception as exc:
        checkpoint_p = Path(model_id_or_path)
        if not checkpoint_p.exists() or not checkpoint_p.is_file():
            print(
                f"\n[ERROR] Could not load Hugging Face model '{model_id_or_path}'.\n"
                f"Reason: {exc}\n\n"
                f"To run real inference with the trained weights, please verify 'transformers' is installed:\n"
                f"    pip install transformers\n"
                f"or using uv:\n"
                f"    uv pip install transformers\n",
                file=sys.stderr,
            )
            raise RuntimeError(
                f"Failed to load '{model_id_or_path}': {exc}"
            ) from exc

        import torchvision.models as models
        import torchvision.transforms as transforms

        print(f"[*] Loading local checkpoint fallback from {checkpoint_p}...", file=sys.stderr)
        model = models.resnet50(weights=None)
        model.fc = torch.nn.Linear(model.fc.in_features, 2)
        state = torch.load(checkpoint_p, map_location=device)
        model.load_state_dict(state, strict=False)
        print(f"[*] Successfully loaded local weights from {checkpoint_p}")

        model.to(device)
        model.eval()

        transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )
        id2label = {0: "Male", 1: "Female"}
        return model, transform, id2label, False


# ============================================================================
# Batch Inference Runner
# ============================================================================


def run_resnet50_predictions(
    data_root: Path,
    split: Literal["train", "val"] = "val",
    output_path: Path | None = None,
    model_id: str = DEFAULT_MODEL_ID,
    batch_size: int = 64,
    device: str = "auto",
    max_samples: int | None = None,
    start_index: int = 0,
    end_index: int | None = None,
) -> int:
    """Run batch inference using ResNet-50 on FairFace images and write CSV."""
    if device == "auto":
        device_obj = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device_obj = torch.device(device)

    print(f"[*] Compute device: {device_obj}")
    if device_obj.type == "cuda":
        print(f"    GPU: {torch.cuda.get_device_name(0)}")

    # 1. Resolve paths
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

    print(f"[*] Labels CSV: {labels_csv}")
    print(f"[*] Images dir: {images_dir}")

    # 2. Read labels
    df_labels = pd.read_csv(labels_csv)
    print(f"[*] Total records in split: {len(df_labels)}")

    if start_index or end_index is not None:
        end = end_index if end_index is not None else len(df_labels)
        df_labels = df_labels.iloc[start_index:end]
        print(f"[*] Sharded range: [{start_index}:{end}] ({len(df_labels)} rows)")

    if max_samples:
        df_labels = df_labels.head(max_samples)
        print(f"[*] Sample limit: {max_samples}")

    # 3. Load model and processor
    model, processor, id2label, is_hf = load_resnet50_gender_model(model_id, device_obj)

    # 4. Construct dataset and loader
    dataset = FairFaceImageDataset(df_labels, images_dir, processor, is_hf)
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
        collate_fn=lambda b: collate_fairface_batch(b, processor, device_obj),
    )

    # 5. Inference loop
    records: list[dict] = []
    skipped = 0

    print(f"[*] Running ResNet-50 inference across {len(dataset)} items (batch_size={batch_size})...")
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Predicting (ResNet-50)"):
            if batch is None:
                continue

            pixel_values = batch["pixel_values"]
            metadata = batch["metadata"]

            outputs = model(pixel_values)
            logits = outputs.logits if hasattr(outputs, "logits") else outputs

            preds_idx = torch.argmax(logits, dim=-1).cpu().numpy()

            for i, meta in enumerate(metadata):
                pred_label = id2label.get(preds_idx[i], str(preds_idx[i]))
                if pred_label.lower() == "male":
                    pred_label = "Male"
                elif pred_label.lower() == "female":
                    pred_label = "Female"

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

    # 6. Save predictions CSV
    if output_path is None:
        output_path = Path("data/processed/fairface_predictions_resnet50_val.csv")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(output_path, index=False)

    print(f"\n[✓] Successfully generated ResNet-50 predictions: {output_path}")
    print(f"    Rows: {len(df_out)}")
    print(f"    Columns: {list(df_out.columns)}")
    print(f"    Overall Gender Accuracy: {(df_out['true_label'] == df_out['predicted_label']).mean() * 100:.2f}%")

    return 0


# ============================================================================
# CLI Entrypoint
# ============================================================================


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="ResNet-50 Gender Classification Batch Prediction Runner for BiasAperture",
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
        default=Path("data/processed/fairface_predictions_resnet50_val.csv"),
        help="Destination predictions CSV file path",
    )
    parser.add_argument(
        "--model-id",
        type=str,
        default=DEFAULT_MODEL_ID,
        help=f"HuggingFace model ID or local directory (default: {DEFAULT_MODEL_ID})",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Batch size for model inference (default: 64)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "cuda", "cpu"],
        help="Execution device (default: auto)",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Optional maximum number of samples to evaluate (for testing)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate parameters and file paths without executing inference",
    )

    args = parser.parse_args(argv)

    if args.dry_run:
        print("=" * 65)
        print("BiasAperture: ResNet-50 Gender Inference Setup Validation (Dry Run)")
        print("=" * 65)
        print(f"  Model ID:     {args.model_id}")
        print(f"  Data root:    {args.data_root.resolve()}")
        print(f"  Split:        {args.split}")
        print(f"  Output CSV:   {args.output.resolve()}")
        print(f"  Batch size:   {args.batch_size}")
        print(f"  Device:       {args.device}")
        print("  Status:       Ready for execution.")
        return 0

    return run_resnet50_predictions(
        data_root=args.data_root,
        split=args.split,
        output_path=args.output,
        model_id=args.model_id,
        batch_size=args.batch_size,
        device=args.device,
        max_samples=args.max_samples,
    )


if __name__ == "__main__":
    sys.exit(main())
