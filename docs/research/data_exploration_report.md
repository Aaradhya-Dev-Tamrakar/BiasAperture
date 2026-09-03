# Data Exploration Report — FairFace & UTKFace

**Phase:** WP1 — Data ingestion & exploration
**Datasets:** FairFace (primary), UTKFace (secondary)
**Scripts:** `scripts/explore_fairface.py`, `scripts/explore_utkface.py`

---

## 1. FairFace

**Source:** `data/raw/fairface/` — `fairface_label_train.csv`,
`fairface_label_val.csv`, images under `detected_faces/{train,val}/`

**Validation performed:** every row's `age`, `gender`, `race` checked
against the locked vocabularies in `schema.py`; every row's image file
confirmed to exist on disk.

### Result — clean, after one fix

| Split | Total rows | Valid rows | Malformed | Missing images |
|-------|-----------:|-----------:|----------:|----------------:|
| train | 86,744     | 86,744     | 0         | 0                |
| val   | 10,954     | 10,954     | 0         | 0                |

**Issue found & fixed:** the raw CSVs use the age label `'more than 70'`,
while `schema.py`'s locked `AGE_LABELS` uses `'70+'`. Normalized in
`scripts/explore_fairface.py` (not in `schema.py`, which is locked).
Affected 842 train rows and 118 val rows before the fix; 0 after.

### Distributions (combined view, valid rows)

**Age** (train, representative of both splits):
20-29 29.5% · 30-39 22.2% · 40-49 12.4% · 3-9 12.0% · 10-19 10.5% ·
50-59 7.2% · 60-69 3.2% · 0-2 2.1% · 70+ 1.0%

**Gender:** Male 53.0% · Female 47.0%

**Race** (7 categories, FairFace race_7):
White 19.1% · Latino_Hispanic 15.4% · Indian 14.2% · East Asian 14.2% ·
Black 14.1% · Southeast Asian 12.4% · Middle Eastern 10.6%

**Note:** race distribution is comparatively balanced across all 7
categories (range 10.6%–19.1%) — FairFace was explicitly constructed
this way.

---

## 2. UTKFace

**Source:** `data/raw/utkface/detected_faces/` — no label CSV; labels
are encoded in each filename as `[age]_[gender]_[race]_[date&time].jpg`
(age 0–116 integer, gender 0/1, race 0–4).

**Validation performed:** every filename parsed and checked for the
expected 4-field structure and in-range values (age 0–116, gender
code ∈ {0,1}, race code ∈ {0,1,2,3,4}).

### Result — clean, after exclusion

| Total files | Valid (parsed) | Malformed |
|------------:|----------------:|----------:|
| 23,708      | 23,705           | 3 → excluded |

Age range observed: 1–116.

### Distributions (valid files)

**Age** (readable buckets, not FairFace's schema bins):
20-29 31.0% · 30-39 19.1% · 50-59 9.7% · 40-49 9.5% · 10-19 6.5% ·
0-2 6.8% · 70+ 5.8% · 60-69 5.6% · 3-9 6.1%

**Gender:** Male 52.3% · Female 47.7%

**Race** (UTKFace's own 5 categories — see Section 4, not yet mapped
to `schema.RACE_LABELS`):
White 42.5% · Black 19.1% · Indian 16.8% · Asian 14.5% · Others 7.1%

**Note:** race distribution is considerably less balanced than
FairFace's — White is more than double its FairFace share (42.5% vs.
19.1%), and the `Others` catch-all category is comparatively small
(7.1%). Relevant for later subgroup sample-size considerations
(`MIN_SUBGROUP_SAMPLE_SIZE = 30` in `schema.py`).

---

## 3. Data Integrity Decision — RESOLVED

### UTKFace: 3 malformed filenames excluded

Three files are missing the race field entirely (only 3 of the
expected 4 underscore-separated components):

```
39_1_20170116174525125.jpg.chip.jpg
61_1_20170109142408075.jpg.chip.jpg
61_1_20170109150557335.jpg.chip.jpg
```

This is a known quirk in the UTKFace dataset itself, not an artifact of
our download or parsing.

**Decision:** excluded from the working dataset. No race value is
guessed or imputed.

**Rationale:**

- 3 / 23,708 = 0.013% of the dataset — statistically negligible;
  excluding them does not materially shift any distribution or
  downstream fairness metric.
- Fabricating a race label would violate the project's data-integrity
  stance (schema.py / NFR-003: flag missing/insufficient data rather
  than fabricate values).
- Fully reproducible: re-running `scripts/explore_utkface.py` against
  the same raw download always flags the same 3 files.

**Status:** Resolved. No further action needed.

---

## 4. Historical Decision — UTKFace Excluded

### UTKFace race categories → schema.py's locked RACE_LABELS

`schema.py` locks `RACE_LABELS` to FairFace's 7-category race_7 scheme:
`White, Black, Latino_Hispanic, East Asian, Southeast Asian, Indian,
Middle Eastern`.

UTKFace only has 5 categories: `White, Black, Asian, Indian, Others`.

This is **not** a mechanical mapping:

- UTKFace's `Asian` (14.5% of the data) does not indicate whether a
  subject is East Asian or Southeast Asian — FairFace splits these
  into two distinct categories.
- UTKFace's `Others` (7.1%) is an explicit catch-all covering
  Hispanic/Latino, Middle Eastern, and other groups not captured
  elsewhere — it does not cleanly separate into FairFace's
  `Latino_Hispanic` vs. `Middle Eastern`.

**Status:** Resolved. UTKFace is excluded from the working benchmark; FairFace
remains the sole implementation dataset. No project-level remapping is required.
resolve inside an exploration or ingestion script), since `schema.py`'s
label vocabularies are locked at M1 and any interpretation choice here
affects every downstream fairness metric computed on UTKFace data.

**Blocks:** UTKFace → `SubjectRecord` ingestion (i.e., UTKFace cannot
be run through `model_interface.py` / `data_ingestion.py` for actual
bias auditing until this is resolved).

**Does not block:** further raw data exploration, documentation, or
any FairFace-only work.
