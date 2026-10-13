"""ViT Batch Prediction Runner — Multi-Model Auditing.

Runs inference on FairFace validation images using a Hugging Face
Vision Transformer (ViT-B/16) fine-tuned for gender classification.
Outputs schema-aligned predictions CSV for bias auditing.

Usage:
  uv run python scripts/predict_vit.py \\
    --data-root data/raw/fairface \\
    --split val \\
    --output data/processed/fairface_predictions_vit_val.csv \\
    --model-name rizvandwiki/gender-classification-2 \\
    --batch-size 64 \\
    --device cuda
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Literal

import pandas as pd
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm
from transformers import AutoImageProcessor, AutoModelForImageClassification


class FairFaceImageDataset(Dataset):
    """PyTorch Dataset loading pre-aligned FairFace images."""

    def __init__(
        self,
        image_dir: Path,
        df: pd.DataFrame,
    ) -> None:
        self.image_dir = image_dir
        self.df = df.reset_index(drop=True)

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> tuple[Image.Image, dict]:
        row = self.df.iloc[idx]
        img_filename = Path(row["file"]).name
        img_path = self.image_dir / img_filename

        try:
            img = Image.open(img_path).convert("RGB")
        except Exception as exc:
            raise RuntimeError(
                f"Audit-cohort integrity violation: failed to read image '{img_filename}' "
                f"at '{img_path}': {exc}. Synthetic image substitution is strictly prohibited "
                "to prevent demographic distortion and maintain audit validity."
            ) from exc

        metadata = {
            "face_name_align": img_filename,
            "race": str(row.get("race", "Unknown")),
            "gender": str(row.get("gender", "Unknown")),
            "age": str(row.get("age", "Unknown")),
        }
        return img, metadata


def normalize_gender_label(raw_label: str) -> str:
    """Normalize predicted class string to standard 'Male' or 'Female'."""
    lower = raw_label.strip().lower()
    if "female" in lower or "woman" in lower:
        return "Female"
    if "male" in lower or "man" in lower:
        return "Male"
    return raw_label.capitalize()


def run_vit_batch_prediction(
    data_root: Path,
    split: Literal["train", "val"] = "val",
    output_path: Path = Path("data/processed/fairface_predictions_vit_val.csv"),
    model_name: str = "rizvandwiki/gender-classification-2",
    batch_size: int = 64,
    device: str = "cuda",
    max_samples: int | None = None,
) -> int:
    """Run batch prediction using Hugging Face ViT."""
    label_csv = data_root / f"fairface_label_{split}.csv"
    if not label_csv.exists():
        raise FileNotFoundError(f"Label file not found: {label_csv}")

    img_dir = data_root / "detected_faces" / split
    if not img_dir.exists():
        img_dir = data_root / split
    if not img_dir.exists():
        raise FileNotFoundError(f"Image directory not found: {img_dir}")

    print(f"[*] Reading labels from {label_csv}...")
    df = pd.read_csv(label_csv)
    if max_samples:
        df = df.head(max_samples)
    print(f"[*] Total cohort samples: {len(df):,}")

    dev = torch.device(device if torch.cuda.is_available() and device == "cuda" else "cpu")
    print(f"[*] Loading model '{model_name}' onto {dev}...")

    processor = AutoImageProcessor.from_pretrained(model_name)
    model = AutoModelForImageClassification.from_pretrained(model_name)
    model.to(dev)
    model.eval()

    id2label = model.config.id2label

    dataset = FairFaceImageDataset(img_dir, df)

    def collate_fn(batch):
        images, metas = zip(*batch)
        inputs = processor(images=list(images), return_tensors="pt")
        return inputs, metas

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
        collate_fn=collate_fn,
    )

    records: list[dict] = []
    print(f"[*] Running ViT inference (batch size: {batch_size})...")

    with torch.no_grad():
        for inputs, metas in tqdm(loader, desc="ViT Inference"):
            inputs = {k: v.to(dev) for k, v in inputs.items()}
            outputs = model(**inputs)
            preds = torch.argmax(outputs.logits, dim=1).cpu().tolist()

            for pred_idx, meta in zip(preds, metas):
                raw_pred = id2label[pred_idx]
                norm_pred = normalize_gender_label(raw_pred)

                records.append(
                    {
                        "face_name_align": meta["face_name_align"],
                        "race": meta["race"],
                        "gender": meta["gender"],
                        "age": meta["age"],
                        "true_label": meta["gender"],  # Auditing perceived gender task
                        "predicted_label": norm_pred,
                    }
                )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame(records)
    out_df.to_csv(output_path, index=False)
    print(f"[+] Predictions saved to: {output_path} ({len(out_df):,} rows)")
    return len(out_df)


def main() -> None:
    parser = argparse.ArgumentParser(description="ViT Batch Inference on FairFace")
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path("data/raw/fairface"),
        help="Path to data/raw/fairface root",
    )
    parser.add_argument(
        "--split",
        choices=["train", "val"],
        default="val",
        help="Dataset split (train or val)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/fairface_predictions_vit_val.csv"),
        help="Output CSV path",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="rizvandwiki/gender-classification-2",
        help="Hugging Face model repository ID",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Inference batch size",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        help="Inference device (cuda or cpu)",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Cap sample count for dry runs",
    )

    args = parser.parse_args()
    run_vit_batch_prediction(
        data_root=args.data_root,
        split=args.split,
        output_path=args.output,
        model_name=args.model_name,
        batch_size=args.batch_size,
        device=args.device,
        max_samples=args.max_samples,
    )


if __name__ == "__main__":
    main()
