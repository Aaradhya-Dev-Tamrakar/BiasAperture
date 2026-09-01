#!/usr/bin/env python
"""
BiasAperture P1: FairFace Validation Inference Pipeline

This script runs ResNet-34 inference on FairFace validation images and generates
a schema-aligned predictions CSV for the bias audit engine.

Usage:
    uv run python scripts/run_fairface_inference.py
    uv run python scripts/run_fairface_inference.py --fairface-root ../FairFace --batch-size 32 --device cuda

Requirements:
    - FairFace repo cloned (../FairFace)
    - FairFace validation images in: ../FairFace/faces/val/
    - Label CSV in: ../FairFace/data/fairface_label_val.csv
    - predict.py in: ../FairFace/
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import warnings

warnings.filterwarnings("ignore")

def main():
    parser = argparse.ArgumentParser(
        description="FairFace Validation Inference for BiasAperture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Standard inference (CUDA if available)
  uv run python scripts/run_fairface_inference.py

  # Custom FairFace path
  uv run python scripts/run_fairface_inference.py --fairface-root /path/to/fairface

  # CPU-only mode
  uv run python scripts/run_fairface_inference.py --device cpu

  # Custom batch size
  uv run python scripts/run_fairface_inference.py --batch-size 16

OUTPUT:
  - data/processed/fairface_predictions_val.csv
    Columns: image_id, predicted_race, predicted_gender, predicted_age,
             true_race, true_gender, true_age, subgroup_race, subgroup_gender, subgroup_age
"""
    )

    parser.add_argument(
        "--fairface-root",
        type=Path,
        default=Path(__file__).parent.parent / "FairFace",
        help="Path to FairFace repository root (default: ../FairFace)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for inference (default: 32)"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "cuda", "cpu"],
        help="Compute device: auto (GPU if available), cuda (force GPU), cpu (force CPU)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "processed",
        help="Output directory for predictions CSV"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate setup without running inference"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip schema validation after inference"
    )

    args = parser.parse_args()

    # ========================================================================
    # SETUP & VALIDATION
    # ========================================================================
    print("=" * 70)
    print("BiasAperture P1: FairFace Validation Inference Pipeline")
    print("=" * 70)
    print()

    # Resolve paths
    fairface_root = args.fairface_root.resolve()
    label_csv = fairface_root / "data" / "fairface_label_val.csv"
    val_images_dir = fairface_root / "val"
    output_dir = args.output_dir.resolve()

    print("[1/5] Validating setup...")
    print()

    # Check FairFace root
    if not fairface_root.exists():
        print(f"  ✗ FairFace root not found: {fairface_root}")
        print(f"    Expected directory structure:")
        print(f"      {fairface_root}/")
        print(f"        ├── data/")
        print(f"        │   └── fairface_label_val.csv")
        print(f"        └── val/")
        print(f"              └── *.jpg")
        sys.exit(1)
    print(f"  ✓ FairFace root: {fairface_root}")

    # Check label CSV
    if not label_csv.exists():
        print(f"  ✗ Label CSV not found: {label_csv}")
        print(f"    Expected: {label_csv}")
        print(f"    Download from FairFace repository: data/fairface_label_val.csv")
        sys.exit(1)
    with open(label_csv) as f:
        label_count = sum(1 for _ in f) - 1  # Exclude header
    print(f"  ✓ Label CSV: {label_csv} ({label_count} validation images)")

    # Check validation images
    if not val_images_dir.exists():
        print(f"  ✗ Validation images directory not found: {val_images_dir}")
        print(f"    Expected: {val_images_dir}/")
        print(f"    Download from FairFace: fairface_val_padding0.25.zip")
        sys.exit(1)
    val_image_count = len(list(val_images_dir.glob("*.jpg")))
    if val_image_count == 0:
        print(f"  ⚠ No JPEG images found in: {val_images_dir}")
        print(f"    Checking other formats...")
        val_image_count = len(list(val_images_dir.glob("*.*")))
    print(f"  ✓ Validation images: {val_images_dir} ({val_image_count} images)")

    # Check checkpoint candidates in priority order.
    # The repository's locked baseline is the official 7-race FairFace checkpoint,
    # with the 4-race file treated as an optional compatibility fallback.
    checkpoint_candidates = [
        Path(__file__).parent.parent / "data" / "fairface_alldata_20191111.pt",
        Path(__file__).parent.parent / "data" / "res34_fair_align_multi_7_20190809.pt",
        Path(__file__).parent.parent / "data" / "fairface_alldata_4race_20191111.pt",
    ]
    checkpoint_path = next((p for p in checkpoint_candidates if p.exists()), checkpoint_candidates[0])
    if not checkpoint_path.exists():
        print(f"  ⚠ Checkpoint not found (will verify later): {checkpoint_path}")
    else:
        print(f"  ✓ Checkpoint: {checkpoint_path} ({checkpoint_path.stat().st_size / 1e6:.1f} MB)")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    output_csv = output_dir / "fairface_predictions_val.csv"
    print(f"  ✓ Output directory: {output_dir}")
    print()

    if args.dry_run:
        print("[✓] DRY RUN COMPLETE — All prerequisites validated")
        print()
        print("Next: uv run python scripts/run_fairface_inference.py (without --dry-run)")
        sys.exit(0)

    # ========================================================================
    # IMPORT DEPENDENCIES
    # ========================================================================
    print("[2/5] Importing dependencies...")
    print()

    try:
        import torch
        import torch.nn as nn
        import torchvision.transforms as transforms
        from PIL import Image
        import numpy as np
        print(f"  ✓ PyTorch {torch.__version__}")
        print(f"  ✓ torchvision")
        print(f"  ✓ PIL")
        print(f"  ✓ NumPy")
    except ImportError as e:
        print(f"  ✗ Missing dependency: {e}")
        print(f"    Run: uv sync --extra dev")
        sys.exit(1)

    # Detect device
    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device
    print(f"  ✓ Device: {device.upper()}")
    if device == "cuda":
        print(f"    GPU: {torch.cuda.get_device_name(0)}")
    print()

    # ========================================================================
    # DEFINE FAIRFACE-ALIGNED LABELS FOR THE DETECTED CHECKPOINT TYPE
    # ========================================================================
    print("[3/5] Loading label taxonomies (auto-detecting checkpoint head)...")
    print()

    RACE_LABELS_7 = (
        "White",
        "Black",
        "Latino_Hispanic",
        "East Asian",
        "Southeast Asian",
        "Indian",
        "Middle Eastern",
    )
    RACE_LABELS_4 = ("White", "Black", "Asian", "Indian")
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

    # ========================================================================
    # LOAD MODEL & CHECKPOINT
    # ========================================================================
    print("[4/5] Loading ResNet-34 checkpoint...")
    print()

    if not checkpoint_path.exists():
        print(f"  ✗ Checkpoint not found: {checkpoint_path}")
        print(f"    Expected one of: {', '.join(str(p.name) for p in checkpoint_candidates)}")
        sys.exit(1)

    try:
        checkpoint = torch.load(checkpoint_path, map_location=device)
        print(f"  ✓ Checkpoint loaded: {checkpoint_path}")
        print(f"    File size: {checkpoint_path.stat().st_size / 1e6:.1f} MB")

        fc_output_size = None
        for key, tensor in checkpoint.items():
            if 'fc' in key and 'weight' in key:
                fc_output_size = tensor.shape[0]
                print(f"  ✓ FC layer: {key} → {tensor.shape}")
                break

        if fc_output_size == 13:
            race_labels = RACE_LABELS_4
            print(f"  ✓ Confirmed: 4-race variant (13 outputs)")
        elif fc_output_size == 18:
            race_labels = RACE_LABELS_7
            print(f"  ✓ Confirmed: 7-race variant (18 outputs)")
        else:
            print(f"  ✗ Unexpected FC output size: {fc_output_size} (expected 13 or 18)")
            sys.exit(1)

        print(f"  ✓ Race taxonomy: {race_labels}")
        print(f"  ✓ Gender taxonomy: {GENDER_LABELS}")
        print(f"  ✓ Age taxonomy ({len(AGE_LABELS)} groups): {AGE_LABELS}")

    except Exception as e:
        print(f"  ✗ Failed to load checkpoint: {e}")
        sys.exit(1)

    # Build ResNet-34 model (matching FairFace architecture)
    try:
        model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet34', pretrained=False)

        num_outputs = fc_output_size if fc_output_size else 13
        model.fc = nn.Linear(model.fc.in_features, num_outputs)
        
        # Load checkpoint weights
        model.load_state_dict(checkpoint, strict=False)
        model.to(device)
        model.eval()
        
        print(f"  ✓ ResNet-34 model initialized ({num_outputs} outputs)")
    except Exception as e:
        print(f"  ✗ Failed to build model: {e}")
        sys.exit(1)
    
    # Image preprocessing (FairFace standard)
    image_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    
    print(f"  ✓ Image preprocessing pipeline ready")
    print()

    # Read label CSV to get ground truth
    label_map = {}
    race_taxonomy = set()
    gender_taxonomy = set()
    age_taxonomy = set()

    with open(label_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            image_id = row.get("file")
            label_map[image_id] = {
                "race": row.get("race"),
                "gender": row.get("gender"),
                "age": row.get("age"),
            }
            race_taxonomy.add(row.get("race"))
            gender_taxonomy.add(row.get("gender"))
            age_taxonomy.add(row.get("age"))

    print(f"  ✓ Loaded {len(label_map)} ground truth labels")
    print(f"  ✓ Race categories: {sorted(race_taxonomy)}")
    print(f"  ✓ Gender categories: {sorted(gender_taxonomy)}")
    print(f"  ✓ Age categories: {sorted(age_taxonomy)}")
    print()

    # ========================================================================
    # RUN INFERENCE & GENERATE CSV
    # ========================================================================
    print("[5/5] Running inference & generating predictions CSV...")
    print()

    predictions = []
    failed_images = []
    
    with torch.no_grad():
        for idx, (image_id, labels) in enumerate(label_map.items(), 1):
            # Build image path
            # Note: image_id already includes "val/" prefix, so use fairface_root directly
            image_path = fairface_root / image_id
            
            if not image_path.exists():
                # Try alternative extensions
                found = False
                for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
                    alt_path = val_images_dir / (image_id.replace('.jpg', '') + ext)
                    if alt_path.exists():
                        image_path = alt_path
                        found = True
                        break
                
                if not found:
                    failed_images.append(image_id)
                    if idx % 1000 == 0:
                        print(f"    [{idx}/{len(label_map)}] ⚠ Image not found: {image_id}")
                    continue
            
            # Load and preprocess image
            try:
                image = Image.open(image_path).convert('RGB')
                image_tensor = image_transform(image).unsqueeze(0).to(device)
            except Exception as e:
                failed_images.append(image_id)
                if idx % 1000 == 0:
                    print(f"    [{idx}/{len(label_map)}] ⚠ Failed to load: {image_id} ({e})")
                continue
            
            # Model inference
            try:
                outputs = model(image_tensor)
                outputs = outputs.cpu().numpy()[0]
                
                # Parse outputs based on checkpoint type
                if len(outputs) == 13:  # 4-race variant
                    race_logits = outputs[:4]
                    gender_logits = outputs[4:6]
                    age_logits = outputs[6:13]
                elif len(outputs) == 18:  # 7-race variant
                    race_logits = outputs[:7]
                    gender_logits = outputs[7:9]
                    age_logits = outputs[9:18]
                else:
                    failed_images.append(image_id)
                    if idx % 1000 == 0:
                        print(f"    [{idx}/{len(label_map)}] ⚠ Unexpected output size: {len(outputs)}")
                    continue
                
                # Convert logits to predicted labels via argmax
                pred_race_idx = np.argmax(race_logits)
                pred_gender_idx = np.argmax(gender_logits)
                pred_age_idx = np.argmax(age_logits)
                
                pred_race = race_labels[pred_race_idx]
                pred_gender = GENDER_LABELS[pred_gender_idx]
                pred_age = AGE_LABELS[pred_age_idx]
                
                predictions.append({
                    "image_id": image_id,
                    "predicted_race": pred_race,
                    "predicted_gender": pred_gender,
                    "predicted_age": pred_age,
                    "true_race": labels["race"],
                    "true_gender": labels["gender"],
                    "true_age": labels["age"],
                    "subgroup_race": labels["race"],  # For now, use true race as subgroup
                    "subgroup_gender": labels["gender"],
                    "subgroup_age": labels["age"]
                })
                
                # Progress report
                if idx % 1000 == 0:
                    print(f"    [{idx}/{len(label_map)}] ✓ Inferred {idx} images...")
                    
            except Exception as e:
                failed_images.append(image_id)
                if idx % 1000 == 0:
                    print(f"    [{idx}/{len(label_map)}] ✗ Inference error: {image_id} ({e})")
                continue
    
    print(f"  ✓ Inference complete: {len(predictions)}/{len(label_map)} images processed")
    if failed_images:
        print(f"  ⚠ Failed to process: {len(failed_images)} images")
    print()
    
    # Write predictions to CSV
    print(f"  ℹ Writing predictions CSV...")
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "image_id",
            "predicted_race", "predicted_gender", "predicted_age",
            "true_race", "true_gender", "true_age",
            "subgroup_race", "subgroup_gender", "subgroup_age"
        ])
        writer.writeheader()
        writer.writerows(predictions)

    print(f"  ✓ CSV written: {output_csv}")
    print(f"    Records: {len(label_map)}")
    print()

    # ========================================================================
    # VALIDATION & SUMMARY
    # ========================================================================
    if not args.skip_validation:
        print("[✓] Post-inference validation...")
        csv_record_count = sum(1 for _ in open(output_csv)) - 1
        print(f"  ✓ CSV records: {csv_record_count}")
        print(f"  ✓ Expected records: {len(label_map)}")
        if csv_record_count == len(label_map):
            print(f"  ✓ SCHEMA VALID")
        else:
            print(f"  ✗ Record count mismatch!")
            sys.exit(1)
    print()

    # ========================================================================
    # NEXT STEPS
    # ========================================================================
    print("=" * 70)
    print("✓ INFERENCE COMPLETE")
    print("=" * 70)
    print()
    print("Next: Run BiasAperture audit on predictions CSV")
    print()
    print(f"  uv run python -m bias_aperture.cli audit \\")
    print(f"    --predictions {output_csv} \\")
    print(f"    --output report/audit_report.html \\")
    print(f"    --explain")
    print()


if __name__ == "__main__":
    main()
