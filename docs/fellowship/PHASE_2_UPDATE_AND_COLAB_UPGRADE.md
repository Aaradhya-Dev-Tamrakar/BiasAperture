# BiasAperture — Phase 2 Update & Colab Pro Upgrade Briefing

---

## 1. Proposal Defense Debrief Summary (Sept 7)

### Panel Verdict
- **Overall Assessment:** Positive — project evaluated as *"very impressive"* and *"a very good project"*. Zero blocking technical objections.
- **Primary Panel Concern:** Workload and scope feasibility for a 2-person team.

### Q&A Key Points & Resolutions
1. **Dataset Selection (`00:13:25`)**:
   - FairFace justified via manual human annotation (~100K images, 7 races × 9 age groups × 2 genders).
   - UTKFace exclusion confirmed (DEX synthetic label noise, misaligned racial taxonomy).
2. **Hardware & VRAM Skepticism (`00:14:54`)**:
   - Panel expressed skepticism over whether 6–8 GB VRAM is sufficient.
   - **Resolution:** Added mathematical sizing to Master Dossier §1.11. Peak inference footprint is **$\sim 602\text{ MB}$** (model weights $83\text{ MB}$ + batch activations $500\text{ MB}$ under `torch.no_grad()`). Statistical testing ($\chi^2$, bootstrap) and surrogate attribution are CPU-only. Bottleneck is disk I/O, not GPU memory.
3. **Evaluating Pre-Existing Models (`00:15:42`)**:
   - Clarified that BiasAperture operates as independent diagnostic metrology (evaluating model inferences), not a training or debiasing pipeline.
4. **Multi-Model Recommendation (`00:16:57`)**:
   - Panel explicitly advised evaluating more than just ResNet-34: *"It's better to evaluate different models, not just ResNet. Try some other models [like ViT, different ResNets] and compare the scores."*
   - **Resolution:** Opened **GitHub Issue #46** to track multi-model evaluation.
5. **Deployment Context Scoping (`00:24:24`)**:
   - Panel recommended grounding the audit narrative into a specific deployment task (e.g., biometric access control or e-KYC).

---

## 2. Google Colab Pro Hardware Elevation

### Available Compute Specifications
- **GPU:** NVIDIA L4 (24 GB VRAM, Ada Lovelace, 4th Gen Tensor Cores + FP8) / A100 (40/80 GB)
- **System Memory:** 53+ GB High-RAM
- **Storage:** 193+ GB Cloud NVMe Scratch Space
- **Network:** 1+ Gbps Backbone (FairFace download completes in ~90s)

### Scope Boundary Invariant
- **Rule 1 & M1 Schema Lock:** Compute is strictly dedicated to **inference, statistical resampling, and spatial explainability**. Zero model retraining, fine-tuning, or weights debiasing.

---

## 3. Phase 2 Upgrades Enabled by Colab Pro

### Upgrade 1: Multi-Model Comparative Evaluation (GitHub Issue #46)
- Evaluates 3 distinct model paradigms side-by-side against the full FairFace dataset (97,698 images):
  1. **FairFace ResNet-34** (Baseline)
  2. **ResNet-50** (Deeper CNN)
  3. **Vision Transformer (ViT-B/16)** (`google/vit-base-patch16-224`)
- Ingestion operates through the existing `PredictionsFileInterface` via CSV output — zero core architectural rework.
- Outputs comparative fairness tables measuring whether self-attention mechanisms reduce or amplify demographic disparity metrics ($\Delta_{\text{DIR}}, \Delta_{\text{EOD}}$) relative to convolutional backbones.

### Upgrade 2: True Spatial Pixel-Level SHAP (GitHub Issue #17)
- Previously deferred to Phase 2 due to local 6–8 GB GPU memory limits.
- Runs **`shap.PartitionExplainer` on GPU image tensors** for the top 5 most severely disparate demographic cohorts (e.g., darker females vs. lighter males).
- Produces actual pixel-level attribution heatmaps testing whether models anchor on facial morphology vs. visual proxies (lighting, background, hair).
- Embeds side-by-side image/heatmap evidence cards into the HTML report and companion A4 PDF.

### Upgrade 3: 10x Full-Dataset Ingestion Speedup
- Scales batch size from 32 to **128 / 256** using mixed precision (`torch.amp.autocast(dtype=torch.float16)`).
- High-RAM mode supports multi-process DataLoader prefetching (`num_workers=8`).
- Full FairFace 97,698-image inference drops from **~4 hours to ~18–25 minutes per model**.

### Upgrade 4: 10,000-Resample Intersectional Matrix (GitHub Issue #25 & #23)
- Scales BCa bootstrap resampling to **$B = 10{,}000$ iterations** across all **126 intersectional cohorts** ($7 \text{ race} \times 9 \text{ age} \times 2 \text{ gender}$).
- Produces tight 95% confidence intervals and exact permutation tests.

---

## 4. Current Repository Status & Synced Files

All changes are verified (`.\make.bat lint` clean, **106/106 pytest suite passed 100%**) and synced across all remotes (`duo`, `origin`, `org` at commit `75900e0`):

| File / Resource | Location / Link | Description |
|---|---|---|
| **Defense Transcript** | `docs/fellowship/PROPOSAL_DEFENSE_TRANSCRIPT_2026-09-07.md` | Full 26-min verbatim audio transcription |
| **Defense Debrief** | `docs/fellowship/PROPOSAL_DEFENSE_DEBRIEF.md` | Structured 6-point Q&A analysis & action matrix |
| **VRAM Sizing Math** | `docs/PROPOSAL_DEFENSE_MASTER_DOSSIER.md` (§1.11) | Memory table proving ~600 MB inference footprint |
| **Colab Pro Roadmap** | `docs/fellowship/COLAB_PRO_UPGRADE_ROADMAP.md` | Comprehensive architectural upgrade report |
| **Multi-Model Issue** | GitHub Issue #46 | Tracked Phase 2 issue for ResNet-50 / ViT evaluation |

---

## 5. Next Immediate Steps

1. Review candidate Vision Transformer selection: `google/vit-base-patch16-224` vs. facial-specific backbone.
2. Establish `notebooks/colab_bias_aperture_benchmark.ipynb` for the remote batch inference run.
3. Export prediction CSVs into `outputs/` and feed directly into the existing fairness engine.
