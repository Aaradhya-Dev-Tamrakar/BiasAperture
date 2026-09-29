# BiasAperture — 126-Cohort Intersectional Audit Matrix

**Project:** BiasAperture (Demographic Bias Auditing Platform for Computer Vision)  
**Work Package:** WP2 (Stream A: Data Ingestion & Governance) & WP3 (Reporting)  
**Author:** Tisha Manandhar (`tiixsha`)  
**Dataset:** FairFace Benchmark Validation Cohort (`data/processed/fairface_predictions_val.csv`)  
**Sample Size Threshold:** $n \ge 30$ (NFR-003, EU AI Act Article 10(5))  
**Taxonomy Lock:** Milestone M1 (7 Races × 9 Age Bins × 2 Genders = 126 Cells)  

---

## 1. Executive Summary

Under **EU AI Act Article 10(5)** and **NFR-003**, demographic auditing cannot rely exclusively on 1D marginal distributions (e.g. race alone or gender alone). Deeply marginalized intersectional subgroups may experience compounding error rates that remain obscured in aggregate performance figures.

However, intersectional partitioning rapidly dilutes sample sizes. Measuring performance disparities on undersized subgroups ($n < 30$) introduces statistical noise and invalidates asymptotic assumptions (Claim **R-008**, **R-009**). BiasAperture strictly enforces reportability suppression: cells with $n < 30$ are flagged as `insufficient_sample=True` with metric suppression.

### Key Audit Metrics:
- **Evaluated Cohort Size:** 10,389 subjects
- **Total Intersectional Slices:** 126 (7 Races × 9 Age Bins × 2 Genders)
- **Statistically Reportable Cells ($n \ge 30$):** **85 / 126** (67.5%)
- **Sparse / Suppressed Cells ($n < 30$):** **41 / 126** (32.5%)

---

## 2. Marginal Subgroup Distributions & Coverage Rates

### A. By Protected Racial Category (18 Intersectional Slices per Race)

| Racial Category | Total Sample ($n$) | Eligible Slices ($n \ge 30$) | Sparse Slices ($n < 30$) | Intersectional Coverage |
|:---|:---:|:---:|:---:|:---:|
| **White** | 1,963 | 13 / 18 | 5 / 18 | 72.2% |
| **Black** | 1,463 | 12 / 18 | 6 / 18 | 66.7% |
| **Latino_Hispanic** | 1,545 | 12 / 18 | 6 / 18 | 66.7% |
| **East Asian** | 1,474 | 12 / 18 | 6 / 18 | 66.7% |
| **Southeast Asian** | 1,359 | 12 / 18 | 6 / 18 | 66.7% |
| **Indian** | 1,447 | 12 / 18 | 6 / 18 | 66.7% |
| **Middle Eastern** | 1,138 | 12 / 18 | 6 / 18 | 66.7% |

### B. By Age Group (14 Intersectional Slices per Age Bin)

| Age Bracket | Total Sample ($n$) | Eligible Slices ($n \ge 30$) | Sparse Slices ($n < 30$) | Intersectional Coverage |
|:---|:---:|:---:|:---:|:---:|
| **0-2** | 198 | 1 / 14 | 13 / 14 | 7.1% |
| **3-9** | 1,308 | 14 / 14 | 0 / 14 | 100.0% |
| **10-19** | 1,121 | 14 / 14 | 0 / 14 | 100.0% |
| **20-29** | 3,105 | 14 / 14 | 0 / 14 | 100.0% |
| **30-39** | 2,188 | 14 / 14 | 0 / 14 | 100.0% |
| **40-49** | 1,287 | 14 / 14 | 0 / 14 | 100.0% |
| **50-59** | 764 | 12 / 14 | 2 / 14 | 85.7% |
| **60-69** | 303 | 2 / 14 | 12 / 14 | 14.3% |
| **70+** | 115 | 0 / 14 | 14 / 14 | 0.0% |

---

## 3. Comprehensive 126-Cell Contingency Matrix

The table below details all 126 demographic intersections. Cells tagged with `🚨 Sparse (n < 30)` 
are systematically screened from downstream disparity computations and marked `insufficient_sample=True`.

| # | Race | Age Bracket | Gender | Sample Size ($n$) | NFR-003 Eligibility Status |
|:---:|:---|:---:|:---:|:---:|:---:|
| 1 | White | 0-2 | Male | 27 | 🚨 Sparse (n < 30) |
| 2 | White | 0-2 | Female | 16 | 🚨 Sparse (n < 30) |
| 3 | White | 3-9 | Male | 90 | ✅ Eligible (n ≥ 30) |
| 4 | White | 3-9 | Female | 97 | ✅ Eligible (n ≥ 30) |
| 5 | White | 10-19 | Male | 71 | ✅ Eligible (n ≥ 30) |
| 6 | White | 10-19 | Female | 84 | ✅ Eligible (n ≥ 30) |
| 7 | White | 20-29 | Male | 259 | ✅ Eligible (n ≥ 30) |
| 8 | White | 20-29 | Female | 340 | ✅ Eligible (n ≥ 30) |
| 9 | White | 30-39 | Male | 249 | ✅ Eligible (n ≥ 30) |
| 10 | White | 30-39 | Female | 199 | ✅ Eligible (n ≥ 30) |
| 11 | White | 40-49 | Male | 157 | ✅ Eligible (n ≥ 30) |
| 12 | White | 40-49 | Female | 84 | ✅ Eligible (n ≥ 30) |
| 13 | White | 50-59 | Male | 135 | ✅ Eligible (n ≥ 30) |
| 14 | White | 50-59 | Female | 64 | ✅ Eligible (n ≥ 30) |
| 15 | White | 60-69 | Male | 51 | ✅ Eligible (n ≥ 30) |
| 16 | White | 60-69 | Female | 19 | 🚨 Sparse (n < 30) |
| 17 | White | 70+ | Male | 14 | 🚨 Sparse (n < 30) |
| 18 | White | 70+ | Female | 7 | 🚨 Sparse (n < 30) |
| 19 | Black | 0-2 | Male | 19 | 🚨 Sparse (n < 30) |
| 20 | Black | 0-2 | Female | 6 | 🚨 Sparse (n < 30) |
| 21 | Black | 3-9 | Male | 146 | ✅ Eligible (n ≥ 30) |
| 22 | Black | 3-9 | Female | 100 | ✅ Eligible (n ≥ 30) |
| 23 | Black | 10-19 | Male | 89 | ✅ Eligible (n ≥ 30) |
| 24 | Black | 10-19 | Female | 107 | ✅ Eligible (n ≥ 30) |
| 25 | Black | 20-29 | Male | 167 | ✅ Eligible (n ≥ 30) |
| 26 | Black | 20-29 | Female | 203 | ✅ Eligible (n ≥ 30) |
| 27 | Black | 30-39 | Male | 160 | ✅ Eligible (n ≥ 30) |
| 28 | Black | 30-39 | Female | 150 | ✅ Eligible (n ≥ 30) |
| 29 | Black | 40-49 | Male | 109 | ✅ Eligible (n ≥ 30) |
| 30 | Black | 40-49 | Female | 73 | ✅ Eligible (n ≥ 30) |
| 31 | Black | 50-59 | Male | 47 | ✅ Eligible (n ≥ 30) |
| 32 | Black | 50-59 | Female | 39 | ✅ Eligible (n ≥ 30) |
| 33 | Black | 60-69 | Male | 9 | 🚨 Sparse (n < 30) |
| 34 | Black | 60-69 | Female | 19 | 🚨 Sparse (n < 30) |
| 35 | Black | 70+ | Male | 7 | 🚨 Sparse (n < 30) |
| 36 | Black | 70+ | Female | 13 | 🚨 Sparse (n < 30) |
| 37 | Latino_Hispanic | 0-2 | Male | 10 | 🚨 Sparse (n < 30) |
| 38 | Latino_Hispanic | 0-2 | Female | 9 | 🚨 Sparse (n < 30) |
| 39 | Latino_Hispanic | 3-9 | Male | 74 | ✅ Eligible (n ≥ 30) |
| 40 | Latino_Hispanic | 3-9 | Female | 95 | ✅ Eligible (n ≥ 30) |
| 41 | Latino_Hispanic | 10-19 | Male | 88 | ✅ Eligible (n ≥ 30) |
| 42 | Latino_Hispanic | 10-19 | Female | 113 | ✅ Eligible (n ≥ 30) |
| 43 | Latino_Hispanic | 20-29 | Male | 172 | ✅ Eligible (n ≥ 30) |
| 44 | Latino_Hispanic | 20-29 | Female | 236 | ✅ Eligible (n ≥ 30) |
| 45 | Latino_Hispanic | 30-39 | Male | 161 | ✅ Eligible (n ≥ 30) |
| 46 | Latino_Hispanic | 30-39 | Female | 162 | ✅ Eligible (n ≥ 30) |
| 47 | Latino_Hispanic | 40-49 | Male | 140 | ✅ Eligible (n ≥ 30) |
| 48 | Latino_Hispanic | 40-49 | Female | 109 | ✅ Eligible (n ≥ 30) |
| 49 | Latino_Hispanic | 50-59 | Male | 75 | ✅ Eligible (n ≥ 30) |
| 50 | Latino_Hispanic | 50-59 | Female | 52 | ✅ Eligible (n ≥ 30) |
| 51 | Latino_Hispanic | 60-69 | Male | 28 | 🚨 Sparse (n < 30) |
| 52 | Latino_Hispanic | 60-69 | Female | 17 | 🚨 Sparse (n < 30) |
| 53 | Latino_Hispanic | 70+ | Male | 1 | 🚨 Sparse (n < 30) |
| 54 | Latino_Hispanic | 70+ | Female | 3 | 🚨 Sparse (n < 30) |
| 55 | East Asian | 0-2 | Male | 31 | ✅ Eligible (n ≥ 30) |
| 56 | East Asian | 0-2 | Female | 18 | 🚨 Sparse (n < 30) |
| 57 | East Asian | 3-9 | Male | 135 | ✅ Eligible (n ≥ 30) |
| 58 | East Asian | 3-9 | Female | 81 | ✅ Eligible (n ≥ 30) |
| 59 | East Asian | 10-19 | Male | 61 | ✅ Eligible (n ≥ 30) |
| 60 | East Asian | 10-19 | Female | 76 | ✅ Eligible (n ≥ 30) |
| 61 | East Asian | 20-29 | Male | 249 | ✅ Eligible (n ≥ 30) |
| 62 | East Asian | 20-29 | Female | 364 | ✅ Eligible (n ≥ 30) |
| 63 | East Asian | 30-39 | Male | 128 | ✅ Eligible (n ≥ 30) |
| 64 | East Asian | 30-39 | Female | 112 | ✅ Eligible (n ≥ 30) |
| 65 | East Asian | 40-49 | Male | 77 | ✅ Eligible (n ≥ 30) |
| 66 | East Asian | 40-49 | Female | 45 | ✅ Eligible (n ≥ 30) |
| 67 | East Asian | 50-59 | Male | 36 | ✅ Eligible (n ≥ 30) |
| 68 | East Asian | 50-59 | Female | 20 | 🚨 Sparse (n < 30) |
| 69 | East Asian | 60-69 | Male | 17 | 🚨 Sparse (n < 30) |
| 70 | East Asian | 60-69 | Female | 10 | 🚨 Sparse (n < 30) |
| 71 | East Asian | 70+ | Male | 7 | 🚨 Sparse (n < 30) |
| 72 | East Asian | 70+ | Female | 7 | 🚨 Sparse (n < 30) |
| 73 | Southeast Asian | 0-2 | Male | 19 | 🚨 Sparse (n < 30) |
| 74 | Southeast Asian | 0-2 | Female | 15 | 🚨 Sparse (n < 30) |
| 75 | Southeast Asian | 3-9 | Male | 108 | ✅ Eligible (n ≥ 30) |
| 76 | Southeast Asian | 3-9 | Female | 93 | ✅ Eligible (n ≥ 30) |
| 77 | Southeast Asian | 10-19 | Male | 87 | ✅ Eligible (n ≥ 30) |
| 78 | Southeast Asian | 10-19 | Female | 83 | ✅ Eligible (n ≥ 30) |
| 79 | Southeast Asian | 20-29 | Male | 203 | ✅ Eligible (n ≥ 30) |
| 80 | Southeast Asian | 20-29 | Female | 243 | ✅ Eligible (n ≥ 30) |
| 81 | Southeast Asian | 30-39 | Male | 141 | ✅ Eligible (n ≥ 30) |
| 82 | Southeast Asian | 30-39 | Female | 117 | ✅ Eligible (n ≥ 30) |
| 83 | Southeast Asian | 40-49 | Male | 65 | ✅ Eligible (n ≥ 30) |
| 84 | Southeast Asian | 40-49 | Female | 58 | ✅ Eligible (n ≥ 30) |
| 85 | Southeast Asian | 50-59 | Male | 42 | ✅ Eligible (n ≥ 30) |
| 86 | Southeast Asian | 50-59 | Female | 32 | ✅ Eligible (n ≥ 30) |
| 87 | Southeast Asian | 60-69 | Male | 23 | 🚨 Sparse (n < 30) |
| 88 | Southeast Asian | 60-69 | Female | 16 | 🚨 Sparse (n < 30) |
| 89 | Southeast Asian | 70+ | Male | 6 | 🚨 Sparse (n < 30) |
| 90 | Southeast Asian | 70+ | Female | 8 | 🚨 Sparse (n < 30) |
| 91 | Indian | 0-2 | Male | 9 | 🚨 Sparse (n < 30) |
| 92 | Indian | 0-2 | Female | 9 | 🚨 Sparse (n < 30) |
| 93 | Indian | 3-9 | Male | 90 | ✅ Eligible (n ≥ 30) |
| 94 | Indian | 3-9 | Female | 86 | ✅ Eligible (n ≥ 30) |
| 95 | Indian | 10-19 | Male | 71 | ✅ Eligible (n ≥ 30) |
| 96 | Indian | 10-19 | Female | 110 | ✅ Eligible (n ≥ 30) |
| 97 | Indian | 20-29 | Male | 157 | ✅ Eligible (n ≥ 30) |
| 98 | Indian | 20-29 | Female | 212 | ✅ Eligible (n ≥ 30) |
| 99 | Indian | 30-39 | Male | 175 | ✅ Eligible (n ≥ 30) |
| 100 | Indian | 30-39 | Female | 153 | ✅ Eligible (n ≥ 30) |
| 101 | Indian | 40-49 | Male | 104 | ✅ Eligible (n ≥ 30) |
| 102 | Indian | 40-49 | Female | 81 | ✅ Eligible (n ≥ 30) |
| 103 | Indian | 50-59 | Male | 69 | ✅ Eligible (n ≥ 30) |
| 104 | Indian | 50-59 | Female | 56 | ✅ Eligible (n ≥ 30) |
| 105 | Indian | 60-69 | Male | 21 | 🚨 Sparse (n < 30) |
| 106 | Indian | 60-69 | Female | 20 | 🚨 Sparse (n < 30) |
| 107 | Indian | 70+ | Male | 13 | 🚨 Sparse (n < 30) |
| 108 | Indian | 70+ | Female | 11 | 🚨 Sparse (n < 30) |
| 109 | Middle Eastern | 0-2 | Male | 8 | 🚨 Sparse (n < 30) |
| 110 | Middle Eastern | 0-2 | Female | 2 | 🚨 Sparse (n < 30) |
| 111 | Middle Eastern | 3-9 | Male | 67 | ✅ Eligible (n ≥ 30) |
| 112 | Middle Eastern | 3-9 | Female | 46 | ✅ Eligible (n ≥ 30) |
| 113 | Middle Eastern | 10-19 | Male | 44 | ✅ Eligible (n ≥ 30) |
| 114 | Middle Eastern | 10-19 | Female | 37 | ✅ Eligible (n ≥ 30) |
| 115 | Middle Eastern | 20-29 | Male | 155 | ✅ Eligible (n ≥ 30) |
| 116 | Middle Eastern | 20-29 | Female | 145 | ✅ Eligible (n ≥ 30) |
| 117 | Middle Eastern | 30-39 | Male | 217 | ✅ Eligible (n ≥ 30) |
| 118 | Middle Eastern | 30-39 | Female | 64 | ✅ Eligible (n ≥ 30) |
| 119 | Middle Eastern | 40-49 | Male | 143 | ✅ Eligible (n ≥ 30) |
| 120 | Middle Eastern | 40-49 | Female | 42 | ✅ Eligible (n ≥ 30) |
| 121 | Middle Eastern | 50-59 | Male | 74 | ✅ Eligible (n ≥ 30) |
| 122 | Middle Eastern | 50-59 | Female | 23 | 🚨 Sparse (n < 30) |
| 123 | Middle Eastern | 60-69 | Male | 46 | ✅ Eligible (n ≥ 30) |
| 124 | Middle Eastern | 60-69 | Female | 7 | 🚨 Sparse (n < 30) |
| 125 | Middle Eastern | 70+ | Male | 10 | 🚨 Sparse (n < 30) |
| 126 | Middle Eastern | 70+ | Female | 8 | 🚨 Sparse (n < 30) |

---

## 4. Viva Defense & Regulatory Audit Notes

1. **Infant & Geriatric Sparsity:** Across all racial cohorts, the extreme age brackets (`0-2`, `60-69`, `70+`) consistently yield the lowest representation, demonstrating empirical risk of undersized cohort bias in real-world CV deployments.
2. **Harmonized Disparity Safeguard:** In accordance with Milestone M1 and Claim R-008, BiasAperture's dual backends (Fairlearn & AIF360) evaluate disparities across eligible strata while generating transparent regulatory disclosures for unmeasurable sparse cohorts per NIST AI RMF Measure 1.1.
