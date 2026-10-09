# BiasAperture — Proposal Defense Debrief

**Date:** 2026-09-07, 18:00 GMT+05:45  
**Duration:** ~26 minutes (13 min presentation + 13 min Q&A)  
**Presenters:** Aaradhya Dev Tamrakar (Slides 1–10: Introduction through Literature), Tisha Manandhar (Architecture through Conclusion)  
**Program:** Fusemachines AI Fellowship (AIF) 2026  
**Supervisor:** Shreejan Kisee (TA)  
**Transcript:** [`PROPOSAL_DEFENSE_TRANSCRIPT_2026-09-07.md`](./PROPOSAL_DEFENSE_TRANSCRIPT_2026-09-07.md)

---

## Panel Verdict

**Overall Assessment:** Positive — project described as "very impressive" and "a very good project" by multiple panelists. Primary concern was scope feasibility for a 2-person team. No blocking objections raised.

---

## Q&A Record

| # | Timestamp | Questioner | Question | Answer Given | Panel Reaction |
|---|-----------|------------|----------|--------------|----------------|
| 1 | 00:13:25 | Panelist A | "Where are you getting the datasets from?" | FairFace dataset — manually annotated, ~100K images, 9 age groups, 7 racial groups, 2 genders. UTKFace initially planned but cut due to label mapping issues and non-human annotation. | Follow-up: confirmed annotations are pre-existing. Satisfied. |
| 2 | 00:14:54 | Panelist A | "Have you researched resources? GPU is a major concern." | 6–8 GB GPU RAM sufficient on our devices. | "I'm still a little bit skeptical" — wanted evidence of estimation, not just anecdotal confirmation. |
| 3 | 00:15:30 | Panelist A | (Comment, not question) | — | "This project you are undertaking is very impressive, and I wish you guys the best of luck. You will learn a lot if you complete this project." |
| 4 | 00:15:42 | Panelist B | "Are you leveraging already existing models and trying to check their own fairness, or generating your own separate model?" | Leveraging existing models — evaluating, not creating. Starting with FairFace ResNet-34, plan to try other models. | Understood and accepted. |
| 5 | 00:16:57 | Panelist B | "Which kind of model? Any idea — ViT, U-Net, ResNet?" | FairFace ResNet-34 initially, then explore others. | "It's better to evaluate different models, not just ResNet. Try some other models and compare the scores." |
| 6 | 00:24:24 | Panelist C | (Scope discussion) | General facial analysis model auditing scope. | Suggested narrowing to a specific task context (e.g., attendance system, e-KYC). "Pick a specific scope." |

---

## Actionable Feedback Matrix

| # | Panel Feedback | Category | Existing Coverage | Action Required | Tracking |
|---|----------------|----------|-------------------|-----------------|----------|
| 1 | Dataset: FairFace, manually annotated | Dataset justification | ✅ Master Dossier §1.9, BiasAperture-AT §8, Discrepancy Notes #2 | None — fully documented | — |
| 2 | GPU resource estimation skepticism | Resource sizing | ⚠️ Partial — §1.11 says "≥ 8 GB VRAM" but no engineering breakdown | Add VRAM sizing justification with model weight / tensor / overhead math | Dossier §1.11 amendment |
| 3 | "Very impressive" / positive assessment | Validation | ✅ N/A | Record for morale | — |
| 4 | Leveraging existing models, not creating | Architecture clarity | ✅ Master Dossier §1.10, `model_interface.py`, Novelty Defense memo | None — model-agnostic architecture already documented | — |
| 5 | Multi-model comparison recommended | Evaluation scope | ❌ Not tracked — no issue exists for evaluating ViT, ResNet-50, etc. | Create GitHub issue for multi-model comparative evaluation | **New Issue #46+** |
| 6 | Narrow scope to specific deployment context | Report framing | ⚠️ Scope is "facial analysis models" generally | Consider adding a primary evaluation context in report framing (Phase 2) | Issue #22 (ongoing reconciliation) |
| 7 | Team size concern (2 people) | Feasibility | ✅ 5-Tier Descoping Cut-List (Dossier §5.6, BiasAperture-AT §8) | None — descoping strategy already addresses this | — |

---

## Key Takeaways

1. **Dataset choice is solid.** FairFace's manual annotation (Amazon Mechanical Turk consensus) was the right call. UTKFace cut was validated by the panel's follow-up — they accepted the reasoning.
2. **Resource estimation needs formalization.** The verbal "6–8 GB" was accepted but met with skepticism. A documented VRAM sizing breakdown (model weights + tensor batches + overhead) should be added to the master dossier.
3. **Multi-model evaluation is expected.** The panel explicitly recommended comparing architectures beyond ResNet-34. This is achievable via the existing `PredictionsFileInterface` without code changes — only prediction generation from additional models.
4. **Scope framing is adequate but could be sharper.** The diagnostic scope is well-defined technically. For the final report, consider naming a primary deployment context (e.g., "biometric access control" or "e-KYC onboarding") to ground the evaluation.
5. **Team size concern is mitigated.** The 5-tier descoping cut-list directly addresses this. No further action needed.

---

## Cross-References

- Pre-defense preparation: [`PROPOSAL_DEFENSE_GUIDE.md`](../PROPOSAL_DEFENSE_GUIDE.md)
- Master specification: [`PROPOSAL_DEFENSE_MASTER_DOSSIER.md`](../PROPOSAL_DEFENSE_MASTER_DOSSIER.md)
- Novelty reframe: [`BiasAperture_NOVELTY_INTEGRATION_DEFENSE.md`](../BiasAperture_NOVELTY_INTEGRATION_DEFENSE.md)
- Slide discrepancies: [`PRESENTATION_DISCREPANCY_NOTES.md`](../PRESENTATION_DISCREPANCY_NOTES.md)
- Project specification: [`BiasAperture-AT.md`](../BiasAperture-AT.md)
