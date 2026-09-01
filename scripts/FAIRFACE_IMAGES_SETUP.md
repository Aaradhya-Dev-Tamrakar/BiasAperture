# FairFace Validation Images Setup Guide

## Status: ✅ INFERENCE COMPLETE

The validation inference was executed successfully and produced the verified predictions file at `data/processed/fairface_predictions_val.csv`.

**Verified evidence**:

- `10954/10954 images processed`
- `✓ CSV written: .../fairface_predictions_val.csv`
- `✓ SCHEMA VALID`
- `✓ INFERENCE COMPLETE`

## Option 1: Manual Download (Recommended - Simplest)

### Step 1: Download the ZIP from Google Drive

- **URL**: https://drive.google.com/file/d/1Z1RqRo0_JiavaZw2yzZG6WETdZQ8qX86/view
- **File**: `fairface_val_padding0.25.zip` (contains face_images/val/ with 10,954 JPEGs)
- **Size**: ~2 GB
- **Time**: Depends on connection (typically 5-15 minutes on broadband)

### Step 2: Extract to FairFace Directory

```powershell
# After download completes:
cd "path\to\FairFace"
Expand-Archive -Path "fairface_val_padding0.25.zip" -DestinationPath "."
# This creates: FairFace/face_images/val/ (or FairFace/faces/val/ depending on structure)
```

### Step 3: Verify Structure

```powershell
# Count images
(Get-ChildItem 'FairFace/faces/val' -Recurse -Filter "*.jpg" | Measure-Object).Count
# Should return: 10954
```

---

## Option 2: Direct Download with PowerShell (If Manual Download Fails)

```powershell
# CD to FairFace directory
cd "C:\Users\Aaradhya\Downloads\_Organized\Fuse AI Fellowship\Capstone Project\fuseai-fellowship\FairFace"

# Download ZIP
$GoogleDriveFileId = "1Z1RqRo0_JiavaZw2yzZG6WETdZQ8qX86"
$OutputZip = "fairface_val_padding0.25.zip"

# This is complex because Google Drive blocks direct downloads
# Recommended: Use browser to download instead (Option 1)
```

---

## Option 3: Alternative Images Source (Padding=1.25)

If padding=0.25 is unavailable, you can use the alternative with more margin:

- **URL**: https://drive.google.com/file/d/1g7qNOZz9wC7OfOhcPqH1EZ5bk1UFGmlL/view
- **File**: `fairface_val_padding1.25.zip`
- **Size**: ~2.5 GB (slightly larger, more border around faces)
- **Same structure**: Contains 10,954 validation JPEGs

---

## Expected Directory Structure After Setup

```
FairFace/
├── data/
│   ├── fairface_label_val.csv       ✅ Downloaded
│   ├── fairface_label_train.csv     ✅ Downloaded
│   └── test_*.csv (test samples)
├── faces/                           (or face_images/)
│   └── val/                         ⏳ TO BE DOWNLOADED
│       ├── 0001.jpg
│       ├── 0002.jpg
│       └── ... (10,954 total)
├── predict.py                       ✅ Present
├── predict_bbox.py
├── README.md
└── ...other files...
```

---

## Next Steps (After Images Downloaded)

### 1. Verify Image Count

```powershell
cd "C:\Users\Aaradhya\Downloads\_Organized\Fuse AI Fellowship\Capstone Project\fuseai-fellowship"
cd FairFace
(Get-ChildItem 'faces/val' -Recurse -Filter "*.jpg" | Measure-Object).Count
# Should return: 10954
```

### 2. Run Inference Pipeline

```powershell
cd "..\BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models"
uv run python scripts/run_fairface_inference.py --fairface-root ../FairFace
```

### 3. Verify Output

```powershell
ls data/processed/fairface_predictions_val.csv
# Should contain: 10,954 rows + header
```

---

## Troubleshooting

### Issue: "Cannot find folder 'faces/val'"

**Solution**: After extraction, verify the exact path:

```powershell
Get-ChildItem 'FairFace' -Recurse -Directory -Filter "val" | Format-Table FullName
# Copy the full path and use it in inference script
```

### Issue: "File structure doesn't match"

**Solution**: The extract may create intermediate folders. Ensure your directory structure matches:

- `FairFace/faces/val/*.jpg` (10,954 files)
  OR
- `FairFace/face_images/val/*.jpg` (10,954 files)

If it's the second, update the inference script path accordingly.

### Issue: Google Drive says "too many downloads"

**Solution**:

- Wait a few minutes and retry
- Use Option 3 (alternative padding source)
- Contact Aaradhya for alternate download link

---

## References

- **FairFace Data**: https://github.com/dchen236/FairFace#data
- **BiasAperture P1.1 Task**: Validation inference run (10,954 images → fairface_predictions_val.csv)
- **Schema Validation**: `src/bias_aperture/schema.py` (n ≥ 30 sample minimum per subgroup)
- **Inference Script**: `scripts/run_fairface_inference.py`

---

## Status Summary

| Step | Status | File/Output |
|------|--------|------------|
| 1. Download label CSV | ✅ Done | `FairFace/data/fairface_label_val.csv` (10,954 records) |
| 2. Prepare local FairFace data | ✅ Done | local validation split available in `data/fairface-img-margin025-trainval` |
| 3. Run inference | ✅ Done | `data/processed/fairface_predictions_val.csv` (10,954 rows) |
| 4. Validate schema | ✅ Done | `✓ SCHEMA VALID` |
| 5. Generate audit/report | 🔄 Next | fairness audit over the predictions CSV |

---

**Current state**: The inference baseline is complete and ready for the audit stage.

**Next action**: Run the fairness/audit workflow against `data/processed/fairface_predictions_val.csv`.
