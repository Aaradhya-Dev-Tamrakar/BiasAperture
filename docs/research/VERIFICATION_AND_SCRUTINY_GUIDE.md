# BiasAperture — Research Verification & Scrutiny Guide

**Target Audience:** Aaradhya Dev Tamrakar & Tisha Manandhar (Principal Investigators & Authors)  
**Document Purpose:** Practical, step-by-step methodologies to audit, empirically stress-test, and defend every research claim before supervisors, examiners, and code reviews.  
**Philosophy:** *"Trust, but empirically verify."*  
**Date:** August 2026

---

## 1. The 4-Tier Scrutiny Framework

When evaluating any AI-assisted research finding or third-party claim, apply the **4-Tier Scrutiny Ladder**:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           THE 4-TIER SCRUTINY LADDER                      │
└──────────────────────────────────────────────────────────────────────────┘

  [ Tier 4: Boundary & Adversarial Stress-Testing ] ──► (Degenerate inputs, edge cases)
                     ▲
  [ Tier 3: Known-Answer Hand Calculations ]       ──► (Pen & paper validation on n=8)
                     ▲
  [ Tier 2: Live REPL / Minimal Probe Scripts ]    ──► (Isolated 10-line Python proofs)
                     ▲
  [ Tier 1: Primary Source Byte Inspection ]       ──► (Inspect raw tensors, CSVs, laws)
```

1. **Tier 1: Primary Source Byte Inspection**: Verify against official raw files, git repos, or legal gazettes rather than summary prose.
2. **Tier 2: Live REPL Probes**: Write self-contained, 10-line Python scripts verifying library behavior directly in a terminal.
3. **Tier 3: Known-Answer Hand Calculations**: Calculate expected values manually on minimal synthetic matrices ($n=4 \text{ or } 8$) before checking code output.
4. **Tier 4: Boundary Stress-Testing**: Probe degenerate edge cases ($n=0$, $n=29$, single-class subgroups, zero positive predictions).

---

## 2. Stream-by-Stream Verification Protocols

---

### Stream A: Data Pipeline & Model Ingestion (Tracks 01–04)

#### Claim 1: FairFace ResNet-34 uses an 18-unit linear head (not 3 separate heads).
- **How to Scrutinize**:
  Open a Python REPL in your environment and inspect the PyTorch checkpoint keys:
  ```python
  import torch
  state = torch.load("data/raw/fairface_alldata_20191111.pt", map_location="cpu")
  # Inspect the final classification layer weight shape
  fc_weight = state.get("fc.weight", state.get("module.fc.weight", None))
  print("FC Layer Shape:", fc_weight.shape)
  # Expected Output: torch.Size([18, 512]) -> Confirms 18 linear units!
  ```

#### Claim 2: Dataset released on disk has 97,698 images (not 108,501).
- **How to Scrutinize**:
  Count the actual rows in the released label CSV files using PowerShell or bash:
  ```powershell
  # Exclude header line (-1)
  $trainCount = (Get-Content data/raw/fairface_label_train.csv | Measure-Object -Line).Lines - 1
  $valCount = (Get-Content data/raw/fairface_label_val.csv | Measure-Object -Line).Lines - 1
  Write-Host "Train: $trainCount, Val: $valCount, Total: $($trainCount + $valCount)"
  # Expected: Train: 86744, Val: 10954, Total: 97698
  ```

#### Claim 3: Preprocessing uses `dlib` 5-point alignment, not MTCNN.
- **How to Scrutinize**:
  Search for `dlib` vs `mtcnn` in the official `predict.py` source code:
  ```python
  with open("predict.py") as f:
      content = f.read()
  print("dlib used:", "dlib" in content)
  print("get_face_chips used:", "get_face_chips" in content)
  print("mtcnn used:", "mtcnn" in content.lower())
  ```

---

### Stream B: Regulatory & Reporting (Tracks 05–08)

#### Claim 1: EU AI Act Article 10 mandates statistical adequacy and bias detection.
- **How to Scrutinize**:
  Check the official EUR-Lex text for Regulation (EU) 2024/1689:
  - Open EUR-Lex: [https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)
  - Verify **Article 10(2)(f)** (examination of possible biases), **Article 10(2)(g)** (detection, prevention, mitigation), and **Article 10(3)** (appropriate statistical properties).

#### Claim 2: The HTML report is 100% self-contained with zero external requests.
- **How to Scrutinize**:
  1. Generate `compliance_report.html`.
  2. Disconnect your machine from Wi-Fi/Internet completely.
  3. Open `compliance_report.html` in Chrome/Firefox.
  4. Press `F12` $\to$ Network tab $\to$ Reload. Verify that **0 failed network requests** occur, styles render perfectly, and all SHAP images display.

---

### Stream C: Fairness Engine & Statistical Math (Tracks 09–14)

#### Claim 1: Fairlearn and AIF360 calculate Equalized Odds differently (max vs. mean).
- **How to Scrutinize**:
  Run this exact 15-line test script in Python:
  ```python
  import numpy as np
  from fairlearn.metrics import equalized_odds_difference

  # 2 groups: Group A (TPR=0.8, FPR=0.1), Group B (TPR=0.7, FPR=0.4)
  # TPR gap = |0.8 - 0.7| = 0.10
  # FPR gap = |0.1 - 0.4| = 0.30

  # Fairlearn calculates max(TPR_gap, FPR_gap) = max(0.10, 0.30) = 0.30
  # AIF360 native calculates mean(TPR_gap, FPR_gap) = (0.10 + 0.30) / 2 = 0.20

  # Prove Fairlearn output:
  y_true = np.array([1]*10 + [0]*10 + [1]*10 + [0]*10)
  y_pred = np.array([1]*8 + [0]*2 + [1]*1 + [0]*9 +   # Group A: TPR=8/10, FPR=1/10
                    [1]*7 + [0]*3 + [1]*4 + [0]*6)   # Group B: TPR=7/10, FPR=4/10
  groups = np.array(["A"]*20 + ["B"]*20)

  fl_eod = equalized_odds_difference(y_true, y_pred, sensitive_features=groups)
  print(f"Fairlearn EOD: {fl_eod:.4f}")  # Outputs 0.3000
  print(f"AIF360 Mean EOD would be: {(0.10 + 0.30)/2:.4f}")  # Outputs 0.2000
  # Demonstrates why AIF360 must be harmonized to max-of-gaps!
  ```

#### Claim 2: AIF360 Equal Opportunity Difference is signed, Fairlearn is unsigned.
- **How to Scrutinize**:
  Swap Group A and Group B in AIF360’s `unprivileged_groups` definition. Notice that AIF360 returns $-0.10$ instead of $+0.10$. This proves why calling `abs()` on AIF360 output is mandatory before comparing.

#### Claim 3: $n < 30$ pre-filtering vs. post-filtering produces a $3\times$ disparity skew.
- **How to Scrutinize**:
  Construct a dataset where a small group with $n=5$ has $100\%$ error rate by chance:
  ```python
  # Group 1 (n=100, TPR=0.90), Group 2 (n=100, TPR=0.88), Group 3 (n=4, TPR=0.00)
  # If Group 3 is included in Fairlearn metric: gap = 0.90 - 0.00 = 0.90 (Huge disparity!)
  # If Group 3 is pre-filtered (n < 30): gap = 0.90 - 0.88 = 0.02 (True population disparity!)
  # 0.90 vs 0.02 is a massive 45x distortion caused by a 4-sample outlier!
  ```

#### Claim 4: `scipy.stats.bootstrap` fails on multi-group fairness metrics.
- **How to Scrutinize**:
  Pass a 2D multi-group array or multi-argument function to `scipy.stats.bootstrap(..., method='BCa')`.
  Observe that scipy raises `ValueError: multi-sample statistics are not supported with method='BCa'`. This proves why BiasAperture’s custom BCa engine is required.

---

### Stream D: Explainability & Proxy Detection (Tracks 15–16)

#### Claim 1: Individual Typology Angle (ITA) objectively measures skin tone.
- **How to Scrutinize**:
  Verify the standard CIELAB colorimetry formula:
  $$\text{ITA} = \frac{\arctan\left(\frac{L^* - 50}{b^*}\right) \times 180}{\pi}$$
  - Light skin ($L^*=80, b^*=10$): $\text{ITA} = \arctan(30/10) \times 180/\pi \approx 71.5^\circ$ (Very Light).
  - Dark skin ($L^*=30, b^*=10$): $\text{ITA} = \arctan(-20/10) \times 180/\pi \approx -63.4^\circ$ (Dark).
  - Matches the established dermatological Del Bino et al. / Fitzpatrick skin typology standard.

---

### Stream E: Architecture & Known-Answer Testing (Tracks 17–18)

#### Hand-Calculation of the 8-Record Known-Answer Baseline:
Verify this 8-record matrix by hand:

| ID | Race | Gender | True Label ($Y$) | Predicted ($\hat{Y}$) | Outcome |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | White | Female | Positive (1) | Positive (1) | TP |
| 2 | White | Female | Positive (1) | Positive (1) | TP |
| 3 | White | Female | Negative (0) | Positive (1) | FP |
| 4 | White | Female | Negative (0) | Negative (0) | TN |
| 5 | Black | Female | Positive (1) | Negative (0) | FN |
| 6 | Black | Female | Positive (1) | Positive (1) | TP |
| 7 | Black | Female | Negative (0) | Negative (0) | TN |
| 8 | Black | Female | Negative (0) | Negative (0) | TN |

**Step-by-step hand calculation:**
1. **Selection Rates $P(\hat{Y}=1)$**:
   - White: 3 positive predictions out of 4 = $0.750$
   - Black: 1 positive prediction out of 4 = $0.250$
   - $\text{DPD} = 0.750 - 0.250 = \mathbf{0.500}$
   - $\text{DIR} = 0.250 / 0.750 = \mathbf{0.333}$ ($1/3$)
2. **True Positive Rates (TPR)**:
   - White ($Y=1$ on IDs 1, 2): 2/2 = $1.000$
   - Black ($Y=1$ on IDs 5, 6): 1/2 = $0.500$
   - $\text{TPR Gap} = 1.000 - 0.500 = 0.500$
   - $\text{EOP} = \mathbf{0.500}$
3. **False Positive Rates (FPR)**:
   - White ($Y=0$ on IDs 3, 4): 1/2 = $0.500$
   - Black ($Y=0$ on IDs 7, 8): 0/2 = $0.000$
   - $\text{FPR Gap} = 0.500 - 0.000 = 0.500$
4. **Equalized Odds Difference (EOD)**:
   - $\text{EOD} = \max(\text{TPR Gap}, \text{FPR Gap}) = \max(0.500, 0.500) = \mathbf{0.500}$

*When your unit test runs on this exact block, you can personally guarantee the output down to the last decimal place.*

---

## 3. Top 10 Viva / Defense Interrogation Questions (Self-Test)

Before defending the capstone, test yourself with these 10 questions:

1. **Q: Why didn't you just use Aequitas or Google What-If Tool?**
   - *Defense*: Aequitas and WIT are designed for tabular data, do not handle computer vision multi-task logits, lack dual-backend cross-validation, and lack EU AI Act Article 10 sub-clause tracing.
2. **Q: Why is your sample size guard set to $n \ge 30$? Why not $n \ge 50$ or $10$?**
   - *Defense*: $n=30$ is the standard Central Limit Theorem threshold where sampling distributions of proportions approximate normality and $\chi^2$ asymptotic tests become stable. Below $n=30$, small random errors distort difference metrics by $3\times$ to $40\times$.
3. **Q: How can you claim dual-backend cross-validation when Fairlearn and AIF360 use different definitions for Equalized Odds?**
   - *Defense*: We explicitly uncovered this mathematical discrepancy in our research sprint. We harmonized the engine by having our AIF360 backend calculate the max-of-gaps directly from raw TPR/FPR primitives rather than its native average, ensuring both backends evaluate the exact same Hardt et al. statistic.
4. **Q: Why didn't you implement model debiasing or retraining?**
   - *Defense*: BiasAperture is strictly scoped as a neutral, third-party diagnostic and auditing platform. Conflating auditing with mitigation introduces conflicts of interest and invalidates compliance reporting under EU AI Act Article 10.
5. **Q: Why did you drop UTKFace from the benchmark evaluation?**
   - *Defense*: UTKFace collapses 7 race categories into 5 (combining East/Southeast Asian), uses noisy DEX model-predicted ages instead of human annotations, and lacks official splits. FairFace provides 97,698 cleanly annotated, 7-race balanced images.
6. **Q: Why use BCa Bootstrap over standard percentile bootstrap?**
   - *Defense*: Fairness metrics near boundary values ($0.0$ or $1.0$) exhibit skewed, non-normal sampling distributions. BCa corrects for both median bias ($z_0$) and skewness ($a$) using jackknife acceleration.
7. **Q: How do you prevent multiple hypothesis testing inflation across your 126 demographic cells?**
   - *Defense*: We apply the Holm-Bonferroni step-down FWER adjustment across hypothesis families, which controls false discovery without the excessive conservatism of standard Bonferroni.
8. **Q: Why use PartitionExplainer instead of DeepExplainer for SHAP?**
   - *Defense*: DeepExplainer has known PyTorch hook incompatibilities with in-place ReLU layers in ResNet-34. PartitionExplainer is model-agnostic, black-box friendly, and works seamlessly with predictions-file ingestion.
9. **Q: What happens when Disparate Impact Ratio has a zero denominator?**
   - *Defense*: If no group receives positive selection ($\max=0$), DIR evaluates to $1.0$ (no relative disparity). If the unprivileged group has $0$ selection while privileged is $>0$, DIR evaluates to $0.0$.
10. **Q: How does BiasAperture satisfy the NIST AI RMF?**
    - *Defense*: BiasAperture instruments the **Measure** core function (Measure 2.11 for bias documentation, Measure 1.1 for documenting unquantifiable sub-30 risks, and Measure 2.9 for explainability).

---

## 4. Verification Checklist Before Any Milestone Merge

- [ ] **Data Check**: Are all counts verified against disk files using byte/line measures?
- [ ] **Math Check**: Do all metrics match hand-calculated known-answer values on $n=8$?
- [ ] **Guard Check**: Does passing $n=29$ raise `ValueError` on `MetricResult` and skip execution in `base.py`?
- [ ] **Visual Check**: Does the HTML report render offline with 0 network calls?
- [ ] **Test Check**: Are all tests passing with `uv run --extra dev pytest` and formatted with `ruff`?
- [ ] **Sync Check**: Are all changes synchronized with conventional commits via `sync.ps1`?
