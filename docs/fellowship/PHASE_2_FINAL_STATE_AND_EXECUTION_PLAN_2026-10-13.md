# BiasAperture: Phase 2 Final State and Execution Plan

**Prepared:** 13 October 2026, Asia/Katmandu  
**Live-state refresh:** 13 October 2026, Nepal time  
**Collaborators:** Aaradhya Dev Tamrakar (@AaradhyaDT) and Tisha Manandhar (@tiixsha)  
**Decision:** planning and documentation only; implementation has not started in this review.

> **PROPOSED:** Deliver a reproducible, statistically defensible comparison of existing facial-analysis classifiers. Reconcile the work already on GitHub before adding new implementations or scaling Colab runs.

## How to read this document

- **VERIFIED IN REPOSITORY:** directly inspected local source, documentation, Git state, or artifact contents. Source inspection does not imply that tests or inference were rerun.
- **VERIFIED LIVE:** directly inspected GitHub state/branch contents or a primary external source. A PR author's reported result is distinguished from independently reproduced evidence.
- **PROPOSED:** a recommended task, ownership allocation, gate, or acceptance criterion; it is not already implemented or agreed by both collaborators.
- **UNKNOWN:** evidence is insufficient to establish the claim.

**VERIFIED IN REPOSITORY:** This task created this Markdown document only. No application code, locked schemas, tests, prediction files, or existing reports were changed. No tests, inference, report export, synchronization, commits, pushes, or GitHub mutations were performed.

**PROPOSED:** Treat this as a dated snapshot. Refresh issue bodies, PR heads, reviews, and CI before using a coding prompt below.

---

## A. Executive summary

**PROPOSED:** The next release should have five bounded outcomes:

1. A reconciled baseline and experiment contract.
2. Correct subgroup uncertainty with B >= 1,000 and honestly labeled 95% confidence intervals.
3. A repeatable ResNet-34 versus task-compatible ViT comparison on identical FairFace validation IDs.
4. Offline HTML dossiers, inline SVG charts, and immutable A4 PDF companions with accurate model/task metadata.
5. Complete issue ownership, acceptance checklists, labels, milestones, and PR-to-issue links.

**VERIFIED LIVE:** Existing work has advanced since the earlier chat review:

- PR #50 is merged; issue #25 is closed.
- PR #49 now raises explicit image-read errors, includes missing/corrupt-image regression tests, contains PDF companions, and contains populated pipeline documentation.
- PR #48 now forwards attribution data and contains a CLI regression test.
- Both open PRs have a successful reported CI check at their inspected heads, but still have CHANGES_REQUESTED review status. Successful CI is not approval or benchmark reproduction. [PR #48][pr48] [PR #49][pr49] [PR #50][pr50]

**VERIFIED IN REPOSITORY / VERIFIED LIVE:** Statistical and evidence problems remain:

- Subgroup intervals default to 200 percentile draws locally and on PR #48's current head.
- The merged cohort artifact states N=10,389 while the local baseline has 10,954 unique IDs.
- PR #49's decision log still compares different protected axes and makes unsupported causal/compliance claims.
- Its ViT dossier still carries a ResNet-34 model description.

**PROPOSED:** First hold a joint reconciliation and re-review checkpoint. The first substantive coding correction is the subgroup uncertainty contract under #23; the first Colab run is a 64-image compatibility run, not a full dataset sweep.

**PROPOSED:** Keep spatial SHAP, B=10,000 experiments, additional datasets, leaderboards, dashboards, APIs, and commercial packaging behind separate later gates. No retraining, fine-tuning, weight debiasing, or synthetic image generation is in scope.

## B. Current implementation and evidence

### B1. Local checkout versus live main

| Item | Evidence status | Observed state |
|---|---|---|
| Local branch/worktree at start | VERIFIED IN REPOSITORY | Clean main, tracking origin/main; HEAD c63c06ce55240d23e5e34ce3be1d93c7ee8b428e. |
| Live main | VERIFIED LIVE | c30ee0eaa75fe3849660b43214bb4d3837be1b2a, containing merged PR #50. Local tracking refs had not been refreshed; the initially clean status did not establish equality with live GitHub. |
| Recent local changes | VERIFIED IN REPOSITORY | c8aabe9, 75900e0, and c63c06c are defense/roadmap/briefing documentation commits referencing #46. |
| Remotes | VERIFIED IN REPOSITORY | origin is the fellowship repository; duo is AaradhyaDT/BiasAperture; org is Aaradhya-Dev-Tamrakar/BiasAperture. |
| PR #49 ancestry | VERIFIED LIVE | Current head da20aadc114882b1afb92286b0796961b64d7dc1; two commits ahead of inspected live main, zero behind. Do not repeat the old request to update it against #50 as though that remains absent. |
| PR #48 ancestry | VERIFIED LIVE | Current head 1b68e9c78bf0948f05701ada57c535fb5ec408ba; diverged from main, nine ahead and one behind. Incorporate #50 before integration and recheck compatibility. |

**UNKNOWN:** Mirror equality was not verified live. The briefing's claim that all three remotes are synchronized is a historical assertion, not current proof.

### B2. Source capability table

| Capability | Status | Evidence and practical implication |
|---|---|---|
| Locked demographic/metric schema | VERIFIED IN REPOSITORY: implemented | [schema.py:32-85, 127-174][schema]. Taxonomies and schema stay unchanged. n<30 constructor checks prohibit computed metric values; full uncertainty-null enforcement still needs boundary/report checks outside the locked schema. |
| Validated CSV/JSON ingestion | VERIFIED IN REPOSITORY: implemented | [data_ingestion.py:48-60, 315-475, 477-528][ingestion]. Includes image-column aliases, raw-age normalization, configured demographic/task columns, rejection summaries, and duplicate handling. |
| PredictionsFileInterface | VERIFIED IN REPOSITORY: implemented but deprecated | [model_interface.py:83-98, 130-162][interface]. It expects canonical columns and validates locked strings; it lacks the production pipeline's raw-age alias normalization. Compatibility should be checked without bypassing production validation. |
| InProcessInterface | VERIFIED IN REPOSITORY: placeholder | [model_interface.py:53-80][interface]. It raises NotImplementedError; documentation must not call it a working interactive inference adapter. |
| Core Four backends | VERIFIED IN REPOSITORY: implemented | [backends.py:462-628][backends]. Native Fairlearn/AIF360 primitives feed shared canonical result assembly. Point-estimate agreement does not independently validate shared statistics. |
| Binary task contract | VERIFIED IN REPOSITORY: implemented | [base.py:68-96][base]. More than two task labels are rejected. Female/Male encoding makes Male positive. An OvR utility exists in ingestion but does not make general multiclass CLI auditing implemented. |
| Support suppression | VERIFIED IN REPOSITORY: implemented | [base.py:144-193][base]. n>=30 for reportability; EOP also needs >=5 positives; EOD needs >=5 positives and >=5 negatives. |
| Global uncertainty | VERIFIED IN REPOSITORY: implemented with limitations | [statistics.py:301-469][statistics]. Stratified BCa attempt, minimum 1,000, large-n block jackknife, and percentile/point fallbacks. These branches are not an independently established coverage guarantee. |
| Subgroup uncertainty | VERIFIED IN REPOSITORY: below requirement | [statistics.py:526-590][subgroup-ci], [backends.py:216-358][subgroup-calls]. Default 200, percentile method, and no forwarding of the audit bootstrap budget. |
| Significance / correction | VERIFIED IN REPOSITORY: implemented with limitations | [statistics.py:50-107, 150-295][statistics-tests]. Metric-specific conditional tests and Holm correction exist; Fisher fallback is limited to sparse 2x2 cases; failures can return p=1.0. |
| Demographic surrogate attribution | VERIFIED IN REPOSITORY: implemented | [explainability.py:57-65, 99-170][explainability]. Logistic surrogate and demographic-dummy contributions to prediction log-odds; not image attribution, causation, or disparity decomposition. |
| Surrogate reporting | VERIFIED IN REPOSITORY: already implemented; VERIFIED LIVE: extended on PR #48 | [cli.py:212-236][cli-report], [template:541-560][surrogate-template]. Current main already forwards/render explanations. PR #48 adds attribution aliases and SVG rendering; review consistency and avoid duplicating conceptual explanations. |
| HTML / SVG / JSON-LD | VERIFIED IN REPOSITORY: implemented foundations | [template:7-19, 385-485, 541-576][template]. No external rendering dependency is evident in the inspected sections; browser zero-request behavior has not been verified here. |
| PDF exporter | VERIFIED IN REPOSITORY: implemented | [export_report_pdf.py:21-130][pdf-export]. Existing Blink discovery/export is the mandated path, not a new renderer-selection project. |
| Colab notebook / provenance bundle | VERIFIED IN REPOSITORY: absent in inspected checkout | No .ipynb found. The roadmap names a future notebook; a run manifest linking inputs, checkpoints, revisions and outputs remains a required deliverable. |
| Tests | VERIFIED IN REPOSITORY: coverage exists, not run here | [test_fairness_statistics.py:99-119][ci-test] still requests B=200. [offline tests:37-92][offline-test] inspect handcrafted HTML. Actual generated-report network behavior needs its own verification. |

**VERIFIED IN REPOSITORY:** The baseline inference runner loads checkpoints with strict=False and runs one image tensor at a time even though it exposes a batch-size option. Its declared batch size does not establish batched throughput. [run_fairface_inference.py:59-62, 269-294, 333-368][baseline-runner]

**VERIFIED IN REPOSITORY:** The Makefile audit recipe uses --predictions and --output, while the current CLI documents --predictions-file and --output-report. Review this separately before relying on make audit as a reproducible entrypoint: argparse can accept unambiguous abbreviations, but the recipe's example input path and output-directory assumptions still need reconciliation. [Makefile:45-46][makefile] [cli.py:244-339][cli-args]

### B3. Available benchmark assets

**VERIFIED IN REPOSITORY:** Read-only inspection of the local baseline CSV found:

| Artifact property | Observed value |
|---|---:|
| Prediction rows | 10,954 |
| Unique image IDs | 10,954 |
| Observed race x age x gender cells | 126 |
| Cells with n>=30 | 85 |
| Cells with n<30 | 41 |

**VERIFIED IN REPOSITORY:** Its columns are image_id, predicted_race, predicted_gender, predicted_age, true_race, true_gender, true_age, subgroup_race, subgroup_gender, subgroup_age. Age annotations include more than 70; normalize to 70+ during validated intake. [Local baseline CSV][baseline-csv]

**VERIFIED IN REPOSITORY:** Earlier directory inspection in this conversation found 86,744 training image-file entries and 10,954 validation image-file entries. Three baseline HTML/PDF pairs exist. This confirms available artifacts/file entries, not successful image decoding, checkpoint provenance, or independent reproduction. README section "Empirical Audit Proof" and data/README section "Directory Layout" describe them.

**VERIFIED LIVE:** PR #49 contains both race-axis report files and PDF companions. Its stored summary estimates are:

| Stored report | DPD | DIR | Evidence status |
|---|---:|---:|---|
| ResNet-34 race-axis dossier | 0.192 | 0.713 | VERIFIED LIVE: numbers present in committed HTML, not recomputed measurements |
| ViT race-axis dossier | 0.276 | 0.527 | VERIFIED LIVE: numbers present in committed HTML, not recomputed measurements |

Sources: [ResNet dossier:329-476][resnet-dossier] and [ViT dossier:329-476][vit-dossier].

**PROPOSED:** Do not turn those numbers into a final model ranking. Confirm the same task, cohort IDs, labels, engine revision, uncertainty method, and paired comparison evidence first. Their presence also does not support the candidate document's claim that ViT is uniformly fairer.

### B4. What still cannot be verified

**UNKNOWN:** Exact checkpoint/hash and preprocessing that produced the stored baseline CSV; training-data overlap of the ViT candidate; complete model-license permissions; historical image-read failures; regenerated predictions after the fail-fast change; actual Colab allocation/entitlement; current local suite status; statistical CI coverage; browser zero-network behavior; and mirror synchronization.

**PROPOSED:** Preserve historical artifacts and record provenance prospectively. Do not fabricate a retrospective manifest or infer that an author's comment proves a rerun.

## C. Issue scope and GitHub tracking

### C1. Existing ownership and exact scope

**VERIFIED LIVE:** These issues were opened directly, including bodies, checklists, metadata and comments:

| Issue | State / assigned owner | Labels / milestone | Scope and checklist state |
|---|---|---|---|
| [#46][issue46] | OPEN / AaradhyaDT | enhancement, WP2, WP5, phase-2 / none | Two additional architectures beyond ResNet-34, comparative tables and report discussion, prediction-file intake; 0/5 checked. Three comments link documentation commits. |
| [#47][issue47] | OPEN / tiixsha | enhancement, WP2, WP5, phase-2 / milestone 6 | ViT on 10,954 validation images, six-column predictions, race-axis audit, support/statistical screening, dossier and comparison; 0/7 checked, no comments. |
| [#23][issue23] | OPEN / tiixsha | bug, WP4 / M3 | Subgroup CI repair; 0/5 checked, no comments. Hardcoded +/-0.05 description and 56-test reference are stale. |
| [#24][issue24] | OPEN / tiixsha | enhancement, WP3, WP5 / M4 | Surrogate report embedding; 0/6 checked. Existing production wiring supersedes several problem statements; one comment links the October repair commit. |
| [#25][issue25] | CLOSED / tiixsha | documentation, enhancement, WP2, WP3 / M4 | 126-cell profiling, support flags, audit table and tests; 5/5 checked. Closed by #50; one CI-linked merge comment. |
| [#22][issue22] | OPEN / unassigned | documentation, WP7 / M5 | Ongoing claim/evidence reconciliation; all five existing tasks checked, but new discrepancies remain. Four comments provide prior audit trails. |

**VERIFIED LIVE:** Issues #17 (spatial SHAP), #18 (PDF), #19 (YAML), #20 (multi-dataset), and #21 (regulatory timelines) remain open and unassigned under milestone 6. Their bodies were inspected earlier in this conversation; current open-state/ownership/milestone listing was refreshed for this document.

### C2. PR re-review state

| PR | VERIFIED LIVE: latest implementation evidence | Outstanding gate |
|---|---|---|
| [#48][pr48] | Head 1b68e9c78bf0948f05701ada57c535fb5ec408ba; explicit attribution forwarding at cli.py:225-234, alias synchronization at generator.py:53-62, and end-to-end CLI coverage at test_cli.py:181-255. Author reports fixes; CI test check is SUCCESS. | CHANGES_REQUESTED persists. Update against main, review conflicting dual fields and report wording, and resolve the still-present B=200 percentile implementation. Current PR body says Closes #23 and Closes #24; #23 closure is not supported by this source snapshot. |
| [#49][pr49] | Head da20aadc114882b1afb92286b0796961b64d7dc1; missing/corrupt images raise RuntimeError, tests added, PDFs present, pipeline document populated, ancestry contains #50, and CI test check is SUCCESS. Author reports 112 tests. | CHANGES_REQUESTED persists. Re-review fixes; correct model description, stale decision log, provenance/ID contracts and premature completion/closing language. PR body now links both #46 and #47. |
| [#50][pr50] | MERGED into main, implementing the 126-cell profiler and tests; #25 closed. | Follow up the committed report's 10,389 population against the 10,954/no-dropped-records claim before using its counts as benchmark proof. |

**VERIFIED LIVE:** The old review requests are not the latest code state. The review disposition still matters, but a fix present on a new head should be "implemented; re-review pending", not "absent". [#48 response][pr48-response] [#49 response][pr49-response]

**UNKNOWN:** This review did not independently run PR tests or inspect PDF pagination. CI success is verified as GitHub metadata only; comments about local deterministic verification remain author-reported.

### C3. Metadata changes needed before implementation

**PROPOSED:** Apply these later under explicit scope; none were applied during document preparation.

| Item | Owner / action | Checklist, labels, milestone and linking changes |
|---|---|---|
| #46 | Aaradhya | Retain existing assignee/labels; set milestone 6. Identify #47 as the first child and #23 as a prerequisite. Add reproducibility and matched-cohort acceptance. Retain two-additional-model requirement unless jointly rescoping it. |
| #47 | Tisha | Retain assignment/labels/milestone 6. Add pinned checkpoint/processor, stable IDs, validated CSV, no fabricated images, paired baseline and provenance, correct HTML/PDF metadata, and no causal/compliance overclaims. Check items progressively using actual evidence. |
| PR #49 | Tisha authors; Aaradhya reviews | Keep Closes #47 only when all acceptance is met. Replace Closes #46 with Refs #46 while only one additional architecture is delivered. Preserve existing labels, assignment and milestone. |
| #23 / PR #48 | Tisha authors; Aaradhya reviews | Retain #23's M3 history; add phase-2 and testing labels. Update issue title/body to the current 200-draw/budget/method problem. Remove stale numbers. Keep #23 closing text only if the eventual PR actually completes the repair. |
| #24 / PR #48 | Tisha authors; Aaradhya reviews | Retain M4 and assignment; add phase-2. Reconcile already implemented explanations with proposed attribution aliases. Mark implemented criteria with source evidence; keep integration/visual verification unchecked until verified. |
| #22 | Aaradhya | Assign AaradhyaDT, add phase-2, retain M5; add unchecked cohort, provenance, candidate-document, report-metadata and regulatory correction tasks. Keep the ongoing issue open. |
| Closed #25 | Tisha investigates; Aaradhya reviews | Preserve the delivered profiler history. Link a correction under #22; if the execution criterion was false, document/reopen that criterion explicitly rather than presenting it as complete. Do not expand #25 into B=10,000 work by implication. |
| #18 | Aaradhya, with Tisha review | Assign AaradhyaDT; retain enhancement, WP3, phase-2 and milestone 6. Rescope around existing Blink export, automatic companion delivery and visual/offline checks; remove obsolete "PDF never implemented" premise. |
| #21 | Aaradhya, with Tisha review | Assign AaradhyaDT; retain documentation, phase-2 and milestone 6. Include current article references and bounded legal wording, not only deadline replacement. |
| #17 / #19 / #20 | Later sprint | Keep parked until scheduled; explicitly preserve schema/statistical/offline invariants. #17 must not replace diagnostic claims with causal heatmap claims. |
| Milestone 6 | Aaradhya coordinates | Include reproducible multi-model benchmarking and correctness prerequisites; name later optional work as gated, not simultaneous commitments. |
| M5 description | Aaradhya coordinates | Distinguish existing validation evidence from the proposed train+validation sweep; do not leave "full 97,698 validation" as an ambiguous completion target. |

**VERIFIED LIVE:** Existing usable labels include testing and phase-2; a statistics label is not in the inspected label listing even though #23's body mentions it.

### C4. GitHub workflow expected by the chat

**PROPOSED:** The supplied chat establishes an expectation to follow the supervisor's tracking practice: detailed issue scope, assignees, labels, milestones, checklist, and PR linkage. It does not establish that all future model choices or ownership assignments were already agreed.

**VERIFIED IN REPOSITORY:** AGENTS.md section 4 and the repository PR template require conventional issue-referencing work and peer review. The audit-trail linker runs on pushes to main and links referenced issue numbers to SHA-1 comments. A linked commit is traceability evidence, not proof of scientific validity.

**PROPOSED:** For later implementation:

1. Refresh main and relevant PR heads; preserve other work.
2. Use an issue-linked isolated branch from main; continue an existing PR's branch when explicitly assigned that PR, avoiding duplicate fixes.
3. Follow repository sync scripts for staging/commit/push; inspect scripts/sync.bat and scripts/sync.ps1 before invocation. Do not use a sync invocation merely to "refresh" when it stages/pushes.
4. Run required lint, formatting checks, tests and deterministic checks only during the authorized implementation/verification task.
5. Use a conventional message such as fix(statistics): enforce subgroup uncertainty guarantees (#23).
6. Open the PR with main as base, relevant labels/milestone, exact acceptance/verification evidence, and appropriate closing/reference text.
7. Aaradhya-authored PR: assign AaradhyaDT and request tiixsha. Tisha-authored PR: assign tiixsha and request AaradhyaDT.
8. Merge only after review and acceptance. Preserve historical milestone branches.

## D. Conflicts and decisions

### D1. Identifier reconciliation

| Identifier | VERIFIED IN REPOSITORY / VERIFIED LIVE: actual meaning |
|---|---|
| Research Track 22 | Multi-model comparative benchmarking and leaderboard research; originally parked. |
| GitHub #22 | Ongoing discrepancies/claim ledger, not the multi-model task. |
| Research Track 23 | Cross-modal schema generalization; dropped in the task map. |
| GitHub #23 | Subgroup uncertainty bug. |
| Research Track 25 | Dashboard architecture research. |
| GitHub #25 | 126-cell intersectional count profiler. |
| GitHub #46 / #47 | Broad multi-model umbrella / specific ViT-versus-ResNet comparison. |

Evidence: research/research tracks/PHASE2_TASK_MAP.md, section "Decisions applied"; research/results/synth_phase2.md, sections 4 and 7; directly inspected issue bodies.

**PROPOSED:** Activate only the bounded comparison portion of Track 22. Its old dashboard/regulatory prerequisites need not block the comparison; a composite leaderboard remains a separate decision. Leave cross-modal generalization dropped.

### D2. Dataset/cohort reconciliation

**VERIFIED IN REPOSITORY:** The existing raw prediction artifact contains 10,954 validation IDs. Train plus validation file-entry counts total 97,698. These are different evaluation populations.

**VERIFIED LIVE:** The merged profiler artifact states N=10,389, 85 count-eligible cells and 41 sparse cells. Its PR/issue context claims the 10,954 validation cohort. [Cohort artifact, section 1, lines 18-22][cohort-artifact]

**UNKNOWN:** Why 565 subjects differ, whether raw inputs differed, and which filtering/validation decisions caused the difference.

**PROPOSED:** Reconcile input CSV hash, column mapping, age aliases, rejected/deduplicated IDs and sums. Matching 85/41 totals does not reconcile different marginal distributions.

**PROPOSED:** Keep validation as the primary comparison. A full 97,698 sweep can be split-specific characterization later; training-split results must not be labeled independent held-out generalization.

**PROPOSED:** Report all 126 count cells, but only compute defined, eligible metrics. For a gender-classification target, gender-fixed intersections can have only one true task class. Increasing n does not create missing conditional support; EOD/EOP eligibility needs explicit task-aware handling.

### D3. Statistical reconciliation

**VERIFIED IN REPOSITORY / VERIFIED LIVE:** Global B>=1,000 capability is present, while subgroup percentile B=200 remains locally and on current PR #48. The PR title/body's BCa claim does not remove this code-level gap. [PR #48 statistics.py:526-590][pr48-statistics]

**PROPOSED:** Resolve subgroup-versus-global estimand and reference eligibility before replacing the interval method. Issue #23's one-vs-rest proposal is not automatically equivalent to the current point estimate.

**PROPOSED:** Require BCa for the intended method under AGENTS section 5; distinguish and disclose legitimate fallbacks, rather than mislabeling percentile or point-width results. Put budget/method/status metadata in additive run/report structures, not schema.py.

**PROPOSED:** Keep existing Holm families initially. Define extension across axes/models before adding hypotheses. A model's p-value does not test an inter-model difference. Pair both models' predictions on identical IDs and obtain an appropriate difference test and 95% CI with n and B>=1,000.

**PROPOSED:** B=10,000 is a later precision/stability experiment on cached predictions. It does not guarantee tighter substantive uncertainty, eliminate sparse support, or guarantee p<.001. Additional permutation testing is a separately specified sensitivity analysis, not a replacement for required significance reporting. [SciPy bootstrap][scipy-bootstrap] [SciPy chi-square][scipy-chi2]

### D4. Correct the candidate document's interpretation

**VERIFIED IN REPOSITORY:** Read-only counts from the local prediction CSV are:

| True perceived-gender label | Predicted Female | Predicted Male | Total |
|---|---:|---:|---:|
| Female | 4,971 | 191 | 5,162 |
| Male | 229 | 5,563 | 5,792 |
| Total | 5,200 | 5,754 | 10,954 |

**VERIFIED IN REPOSITORY:** The engine makes Male positive and DPD measures differences in positive-prediction rates. A classifier predicting Male for male-labeled faces and Female for female-labeled faces can produce a large gender-axis selection gap without being an almost-always-Male classifier. [base.py:68-96][base] [metrics.py:22-45][metrics]

**PROPOSED:** Correct the "catastrophic female underprediction" conclusion in the supplied candidate document section 3.1 and PR #49's decision log, section 5. Do not substitute a claim that the model is fair; raw counts alone do not establish that either.

**VERIFIED LIVE:** PR #49's log still compares ViT/race to ResNet/gender and asserts causal training skew and regulatory non-compliance. [Decision log:93-107][decision-log]

**PROPOSED:** Use matched task/axis/cohort results, distinguish selection disparity from error disparity, and frame attribution as association. Absolute inter-model deltas discard direction; also report signed differences and their uncertainty. A descriptive result across different checkpoints does not isolate architecture as a cause.

### D5. Correct the PDF briefing and newer branch documentation

| Source section | Evidence status and correction |
|---|---|
| Briefing PDF p.1, VRAM sizing | UNKNOWN: ~602 MB is an estimate, not a measured peak-memory trace. |
| Briefing PDF p.1, hardware; p.2, Upgrade 3 | UNKNOWN: specific L4/A100, RAM/disk/network and 18-25-minute runtimes were not measured here. VERIFIED LIVE: Colab resources vary; record actual allocation and throughput. |
| Briefing PDF p.2, Upgrade 1 | PROPOSED: full train+validation sweep; VERIFIED IN REPOSITORY: current empirical artifacts are validation-sized. ResNet-34 and ResNet-50 are two CNN variants, not two different paradigm families. |
| Briefing PDF p.2, Upgrade 2 | PROPOSED/DEFERRED: spatial SHAP; VERIFIED IN REPOSITORY: current implementation is demographic surrogate association only. No observed OOM/runtime trace was inspected to substantiate hardware as the sole deferral cause. |
| Briefing PDF p.2, Upgrade 4 | PROPOSED: B=10,000 experiments; GitHub #25 delivers counts/profiling, not those experiments. |
| Briefing PDF pp.2-3, verification/sync | VERIFIED IN REPOSITORY: historical claims exist; UNKNOWN: current local test status and mirror equality. |
| PR #49 docs/data_processing_pipeline.md section 2.2 | VERIFIED LIVE: it prescribes shared ImageNet normalization for ViT and ResNet. PROPOSED: use and pin each checkpoint's own processor/transform requirements. |
| Same document section 4.1 | VERIFIED LIVE: it describes interactive InProcessInterface intake. VERIFIED IN REPOSITORY: that interface still raises NotImplementedError. |
| Same document section 6 | PROPOSED: align metric names/definitions with the locked Core Four; do not present EOD as a TPR ratio or claim every eligible count cell supports every conditional metric. |
| ViT dossier model card | VERIFIED LIVE: still describes an 18-output ResNet-34 at line 928 and duplicates N in its dataset heading. PROPOSED: correct metadata and regenerate from the accepted run. |

PDF source: [shared briefing][briefing-pdf], pages 1-3. Newer document source: [pipeline documentation:64-128][pipeline-doc]. Model-card source: [ViT dossier:928][vit-card]. Colab source: [official FAQ][colab].

### D6. Provenance, licensing and regulatory wording

**VERIFIED LIVE:** FairFace authors list CC BY 4.0, conflicting with docs/DATA_GOVERNANCE.md section 1's custom non-commercial entry. Record dataset, checkpoint and dependency terms separately; the repository MIT license does not establish rights to all external weights/data. [FairFace authors][fairface]

**VERIFIED LIVE:** The European Commission describes Annex III high-risk application on 2 December 2027 and product-related Annex I rules on 2 August 2028. Current official Article 10 marks paragraph 5 deleted after amendment and points to Article 4a safeguards. Update mappings in their actual applicable context, not by blanket replacement. [Commission overview][eu-timeline] [Article 10][article10] [Article 4a][article4a]

**PROPOSED:** Describe n>=30, B>=1,000 and alpha=.05 as project statistical controls, not numeric requirements prescribed by Article 10. Keep report badges visually harmonized while making clear they are diagnostic flags, not legal certification.

## E. Sequenced phases and acceptance gates

**PROPOSED:** All tasks in this section are future work. Deadlines and runtime estimates are intentionally not invented.

| Phase | Lead / dependencies | Deliverables | Measurable acceptance gate |
|---|---|---|---|
| 0: Joint reconciliation and re-review | Aaradhya coordinates; Tisha supplies latest branch evidence | Updated issue checklist proposal, PR dispositions, cohort discrepancy log, model/task/CSV contract | Pin SHAs; explain or explicitly quarantine N mismatch; agree target, positive label, axes, reference populations, candidate revisions and failure policy. Identify exactly which existing code is reusable. |
| 1: Statistical guarantees and report completion | Tisha implements #23/#24; Aaradhya reviews | Budget forwarding, correct subgroup BCa/method handling, additive provenance/status metadata, reconciled PR #48 | B>=1,000 reaches all reported rows; n<30 and unsupported conditional rows remain uncomputed; no fake uncertainty or p=1 failure masquerading as a valid no-disparity result; schema unchanged; meaningful tests/checks pass. |
| 2: 64-image Colab compatibility run | Tisha runner; Aaradhya baseline/manifest review; depends on agreed intake | Fixed 64 validation IDs, one pinned model first, batch 8 FP32, workers 0, CSV and timing/processor manifest | 64 IDs accounted exactly once; valid labels/columns/age mapping; zero substituted images; successful validated intake; repeat-run labels match or numerical variation is characterized; observed runtime/memory captured. |
| 3: 500-image paired pilot | Both; depends on phases 1-2 | Identical IDs/ground truth for both checkpoints, support table, raw results, HTML/PDF, paired comparison | Matching IDs/task labels/axes; exclusions explicit; every published disparity has n/test/95% CI; sparse/undefined rows suppressed; offline browser and print checks pass. No subgroup conclusion from unqualified pilot cells. |
| 4: Full validation comparison | Tisha inference; Aaradhya comparison/report; depends on pilot sign-off | 10,954 validation manifest, per-model predictions, accepted-run outputs, signed deltas and uncertainty | Selected=success+explicit failure/exclusion; target zero unexplained losses. All outputs trace to pinned inputs/revisions. Compare only matched populations/estimands; accurate model cards and HTML/PDF consistency. |
| 5: Second extra architecture and B sensitivity | Candidate selected jointly; depends on validation release | Existing compatible checkpoint; separate B=1,000/10,000 study on cached predictions | Existing permitted weights support the same task without training; independent checkpoint effects acknowledged. Report endpoint stability/cost rather than guaranteed significance. Satisfy or explicitly rescope #46's two-additional-model criterion. |
| 6: Reproducibility/product polish | Aaradhya #18/#19 integration, Tisha peer review | Guard-safe configuration, automated companion PDF delivery, accessibility and packaging | Config cannot relax statistical/schema guards; repeatable profiles and correct CLI recipes; no external report resources; compatible Windows/Linux behavior verified when authorized. |
| 7: Optional research | Joint scheduling only | Spatial SHAP, extra datasets, API/dashboard/streaming and commercial decisions | Separate issue, bounded acceptance, provenance/privacy review, no schema mutation or training. Image SHAP stays distinct from multi-model completion. |

### E1. First-run experiment contract

**PROPOSED:**

- Task: perceived-gender label classification on benchmark annotations; not identity verification, attendance recognition or e-KYC performance.
- Primary protected axis: race. Secondary age audit only after primary validation.
- Positive label: explicit Male, matching current encoding; document the interpretation.
- Baseline: official permitted seven-race FairFace ResNet-34 checkpoint; record the exact file/hash and verify output ordering.
- Candidate: existing rizvandwiki/gender-classification-2 checkpoint, subject to provenance/permission gate; pin checkpoint and processor revisions.
- Images: same pre-aligned margin025 source crops; model-specific resizing/normalization.
- IDs: split-qualified stable identifiers such as val/1.jpg, with an explicit map for PR #49's basename-only face_name_align values. Do not mix train/val basenames.
- Selection: seeded manifest of 64 IDs first, containing both labels and representative race/age cases; not simply the first 64 CSV rows.
- Runtime: record CPU/GPU model, available RAM/disk, package versions, batch/precision/workers, model-load time, preprocessing/inference/export time and peak memory.
- Failure policy: fail visibly on unreadable images initially; any future exclusion mode must emit IDs/reasons and support counts.
- Audit: use DataIngestionPipeline validation; separately ensure canonical export can satisfy legacy PredictionsFileInterface if issue compatibility requires it.
- Output: private raw predictions and manifests; aggregate reports only in approved publication paths.
- Statistical budget: B=1,000 initially; never reduce to speed up the pilot.
- Interpretation: count eligibility and conditional support are different; a small run establishes compatibility, not demographic representativeness.

**VERIFIED LIVE:** PR #49 currently uses df.head(max_samples), basename IDs, unpinned from_pretrained calls, and task label normalization that passes unknown labels through. Those need explicit validation/manifests before claiming this full contract. [predict_vit.py:45-149][vit-runner]

### E2. Handoff bundle and stop conditions

**PROPOSED:** A reproducible bundle should include:

~~~text
run-manifest.json
selected-image-ids.csv
input/checkpoint/processor/output SHA-256 hashes
predictions-resnet34.csv
predictions-vit.csv
ingestion-summary.json
cohort-counts.csv
conditional-support.csv
metric-results.json or CSV
paired-comparison-results.json or CSV
runtime-and-environment.json
audit-resnet34.html + audit-resnet34.pdf
audit-vit.html + audit-vit.pdf
comparison.md
limitations-and-exclusions.md
~~~

**PROPOSED:** Put these in a run-specific output directory. Do not assume these serializers or CLI flags already exist; add only the minimal agreed reporting/provenance layer outside M1.

**PROPOSED:** Stop expansion if IDs/ground truth differ, a checkpoint is incompatible or unlicensed for the intended use, unknown labels pass intake, image failures are hidden, the cohort gap is unexplained, or published results violate n/B/uncertainty rules.

## F. Aaradhya and Tisha work split

### F1. Basis for the allocation

**VERIFIED LIVE:** Tisha is already assigned #23, #24, #25 and #47 and authors the open engine/report and ViT PRs. Aaradhya is assigned #46 and has reviewed both PRs.

**PROPOSED:** Preserve those implementation owners. Aaradhya owns coordination, independent scientific review, baseline/provenance reconciliation and final integration. New assignments below implement the chat's issue/labels/milestone/PR expectation; they are recommendations, not an invented prior agreement.

### F2. Actionable task board

| Task | Primary owner | Reviewer / partner | Tracking | Deliverable / done condition |
|---|---|---|---|---|
| A1: Refresh snapshot and disposition existing work | Aaradhya | Tisha supplies heads/artifacts | #22, #46; PRs #48-#50 | Written implemented/pending/blocked matrix; avoid duplicate implementation. |
| A2: Reconcile 10,389 versus 10,954 | Tisha investigates raw intake/profiler | Aaradhya independently checks provenance | #22 correction linked to closed #25 | CSV hashes, rejected/deduplicated IDs/reasons, corrected count sums and artifact or explicit limitation. |
| A3: Freeze experiment/statistical contract | Aaradhya drafts | Joint sign-off | #46, #47, #23 | Agreed task, labels, axes, cohort, estimands, method/families, candidate permissions and output contract. |
| T1: Complete subgroup uncertainty repair | Tisha | Aaradhya statistical/code review | #23; PR #48 only if scope deliberately includes it | Correct B propagation/BCa/fallback handling and meaningful regression evidence; unchanged schema. |
| T2: Finish surrogate report integration | Tisha | Aaradhya end-to-end/wording review | #24 / PR #48 | Reconcile aliases; no unavailable/causal/image-SHAP overclaims; updated main compatibility and CI. |
| T3: Finish ViT runner contract | Tisha | Aaradhya | #47 / PR #49 | Stable split IDs, strict label/head checks, pinned processor/revision, fail-fast behavior and reproducible manifest. |
| A4: Baseline checkpoint/provenance | Aaradhya | Tisha checks loader/CSV mapping | #46 | Existing official checkpoint obtained under allowed terms, hash/preprocessing/head verified, canonical output compatible with candidate. |
| T4: Small Colab runs and measured profiling | Tisha | Aaradhya accepts handoff | #47 | 64-image contract pass, then 500-image paired pilot; observed timing/memory and persistent outputs. |
| A5: Matched comparison and model-card correction | Aaradhya | Tisha peer review | #46, #22 | Same task/axis/cohort; signed differences with uncertainty/testing; accurate ViT metadata and cautious interpretation. |
| A6: Offline/PDF acceptance and report polish | Aaradhya | Tisha | #18; PR-specific corrections remain with PR author | Generated-report zero-request check, A4 inspection, SVG suppression/CI consistency; no missing companions. |
| T5: Full validation inference | Tisha | Aaradhya checks integrity | #47 | 10,954 selected IDs accounted; accepted checkpoint/processor manifests and private predictions. |
| A7: Issue/PR audit trail and final documentation | Aaradhya coordinates | Both update own issues | #22, #46, #47 | Evidence-based checklist, labels/milestones, correct Closes/Refs text, source-linked final comparison. |
| J1: Second extra model / higher-B decision | Joint | Peer review | #46 plus explicit experiment checklist | Compatible existing weights and measured cost; no training or automatic full-data commitment. |
| J2: Later optional backlog | Joint | Peer review | #17/#19/#20 and later research tracks | Schedule only after core comparison release; scope and dependencies explicit. |

**PROPOSED:** Shared source edit boundaries: Tisha owns fairness/statistics/backends and current PR #48 report wiring; Aaradhya reviews and owns comparison/provenance design. Coordinate CLI/generator/template edits before touching them. Aaradhya's separate report work must be based on the accepted version of Tisha's changes.

### F3. Two explicit handoff meetings

**PROPOSED - Handoff 1:** After the 64-image run, before the 500-image pilot. Tisha presents runner/CSV/manifest/failure handling; Aaradhya presents baseline/provenance and scientific contract. Together reconcile labels, preprocessing, IDs, rejected rows, support counts and runtime.

**PROPOSED - Handoff 2:** After pilot dossiers, before integration/full validation. Together inspect rendered HTML/PDF, compare raw results with reports, confirm uncertainty/suppression/model descriptions, and approve only conclusions supported by matched evidence.

**PROPOSED:** If a handoff gate fails, repair the responsible layer before scaling. Completion of one person's script is not completion of the shared experiment.

## G. Risk register

| ID / risk | Evidence status | Severity | Owner | Proposed mitigation / gate |
|---|---|---|---|---|
| R1: Sparse subgroup disclosure | VERIFIED IN REPOSITORY: 41 raw count-sparse cells | Critical | Tisha; Aaradhya reviews | Recount after intake/exclusions; uncomputed n<30 rows across every serializer/report. |
| R2: Conditional support absent | VERIFIED IN REPOSITORY: >=5 support guards; gender-fixed task cells can lack a class | High | Joint | Explicit per-metric eligibility; do not infer that more resamples or images fix structural undefinedness. |
| R3: Incorrect uncertainty | VERIFIED IN REPOSITORY / LIVE: B=200 percentiles remain | Critical | Tisha | Repair budget/method, match CI estimator to point estimate, document fallback and coverage limitations. |
| R4: Invalid significance / multiplicity | VERIFIED IN REPOSITORY: shared correction and limited sparse fallback | High | Aaradhya design; Tisha implementation | Freeze families; inspect expected counts; valid paired difference testing; failures explicit, not p=1 proof. |
| R5: Cohort/provenance drift | VERIFIED LIVE: merged report population conflict | Critical | Tisha investigates; Aaradhya verifies | Hash and account every selected/rejected ID; quarantine unreconciled artifacts. |
| R6: Checkpoint/head/preprocessing mismatch | VERIFIED LIVE: roadmap generic models differ from task-specific candidate | Critical | Tisha / Aaradhya baseline | Existing weights, label/head contract, processor revision and checksum; strict coverage; no random head. |
| R7: Architecture-causation overclaim | VERIFIED LIVE: log attributes differences to training skew/architecture | High | Aaradhya | Describe checkpoint comparison, acknowledge training/processor confounds; no causal or universal fairness ranking. |
| R8: Licensing/privacy/redistribution | VERIFIED LIVE: FairFace terms differ from local governance entry; candidate details sparse | High | Aaradhya | Separate source/weight/data permissions, private raw artifacts, approved retention and access; no automatic raw-image/report embedding. |
| R9: Colab interruption / resource variability | VERIFIED LIVE: provider resources vary | High | Tisha | Small measured runs, persistent manifests/checkpoints of outputs, resumable chunks with uniqueness/count checks. |
| R10: Report identity/network/print defects | VERIFIED LIVE: ViT report misdescribes model; offline behavior not measured | High | Aaradhya; Tisha PR author | Correct metadata, actual generated-output/browser/A4 inspection, zero external resources and raw SVG charts. |
| R11: Green CI interpreted as scientific proof | VERIFIED LIVE: checks SUCCESS while reviews pending | High | Both | Separate code tests, artifact presence, author claims, inference reproduction and scientific acceptance. |
| R12: Scope expansion | VERIFIED IN REPOSITORY: numerous research/product tracks | High | Joint | Keep first release narrow; independently schedule second model, full-data characterization and image SHAP. |
| R13: Workflow/mirror side effects | VERIFIED IN REPOSITORY: sync stages/pushes; refs can be stale | Medium | Aaradhya | Inspect wrapper paths/scope, isolate issue work, do not sync automatically in planning/review tasks. |

## H. First recommended action and release definition

**PROPOSED:** First conduct the joint phase-0 reconciliation and re-review of the newest #48/#49 heads. This is immediately actionable and prevents implementing fixes Tisha has already pushed.

**PROPOSED:** The first coding task is #23's actual unresolved subgroup uncertainty guarantee. In parallel, Tisha can prepare the existing ViT runner's manifest/ID/label checks and Aaradhya can prepare baseline provenance, but publishing comparison results waits for the statistical gate.

**PROPOSED:** A successful first Phase 2 release consists of:

- [ ] Reconciled cohort sizes and artifact provenance.
- [ ] Unchanged M1 schema and diagnostic-only scope.
- [ ] All reported disparity rows have explicit n, valid test evidence and accurately labeled 95% uncertainty with B>=1,000.
- [ ] Matched ResNet-34/ViT task, IDs, protected axes and reference populations.
- [ ] Strict validation/failure accounting, no substituted images.
- [ ] Reproducible notebook/script and environment/checkpoint/processor manifest.
- [ ] Accurate model cards, surrogate limitations and supported narrative.
- [ ] Offline inline-SVG HTML and matching A4 PDF dossiers.
- [ ] Required tests/checks completed on the eventual accepted revision.
- [ ] Issue ownership/checklists/labels/milestones and reciprocal peer review complete.
- [ ] #47 closed only after its acceptance; #46 stays open until its broader criterion is delivered or explicitly respecified.

**PROPOSED:** Do not make a dashboard, composite fairness score, full 97,698 sweep, B=10,000, or spatial SHAP a requirement for that initial release.

## I. Model recommendation and copy-ready prompts

### I1. Which AI coding model to choose

| Task | PROPOSED recommendation | Reason |
|---|---|---|
| Implement bounded fixes and tests | **GPT-6.1 Sol, High reasoning** | Default for this project's iterative implementation, runner contracts, statistics/report wiring and regression work. |
| Refresh conflicting evidence / prepare review | **GPT-6.1 Sol, Extra High** | Appropriate when reconciling issue bodies, PRs, documents and uncertain benchmark provenance. |
| Independent final statistical/design review | **Astra, Extra High**, if available | Optional second review for estimands, CI/failure behavior and scientific interpretation; not a substitute for verification. |

**VERIFIED LIVE:** Official OpenAI documentation describes GPT-6.1 Sol as suitable for complex coding and supports High/Extra High reasoning; model-selection guidance distinguishes Astra for demanding analysis. The exact reasoning choices above are this plan's recommendations, not a measured BiasAperture model comparison. [OpenAI model selection][openai-selection] [GPT-6.1 Sol][openai-sol]

**UNKNOWN:** Availability and allowance on the collaborator's account were not inspected. Use an available model; do not assume access to Astra or change settings automatically.

### I2. Which facial-analysis models to evaluate

**PROPOSED:** Begin with the official seven-race FairFace ResNet-34 baseline and the existing task-compatible ViT candidate. Existing externally trained weights may be evaluated; the project itself must not train or fine-tune them.

| Candidate | Evidence / recommendation |
|---|---|
| FairFace ResNet-34 | VERIFIED LIVE: authors publish res34_fair_align_multi_7_20190809.pt. PROPOSED: reproduce with pinned hash, output order and transforms; do not assume the old CSV used it. |
| rizvandwiki/gender-classification-2 | VERIFIED LIVE: configuration identifies ViT, 16-pixel patches and female/male labels. PROPOSED: first extra candidate after provenance/permission checks and a small run. |
| google/vit-base-patch16-224 | VERIFIED LIVE: ImageNet classifier. PROPOSED: not a substitute for the task-specific gender checkpoint in this comparison. |
| ResNet-50 / lightweight CNN | VERIFIED LIVE: ordinary torchvision ResNet-50 weights target ImageNet. PROPOSED: choose only after locating existing compatible demographic-task weights; do not add/train a replacement head. |
| Zero-shot CLIP | PROPOSED: later separately labeled prompt-based experiment; fix prompts/taxonomy and analyze prompt sensitivity. |
| ArcFace/InsightFace or hosted APIs | PROPOSED: defer until exact attribute/verification task, output contract, permissions, provenance and cost are established. Recognition embeddings are not gender predictions. |

Sources: [FairFace authors][fairface], [ViT config][vit-config], [Google ViT card][google-vit], [ResNet-50 documentation][resnet50], [CLIP card][clip], [InsightFace license][insightface].

### I3. Prompt to refresh and review this plan

**PROPOSED:** Use this when asking another coding agent to perform a planning review. It does not authorize implementation.

~~~text
You are reviewing BiasAperture with Aaradhya (@AaradhyaDT) and Tisha (@tiixsha).
Read docs/fellowship/PHASE_2_FINAL_STATE_AND_EXECUTION_PLAN_2026-10-13.md,
AGENTS.md, the current source/tests, and the supplied Phase 2 briefing and
candidate document. Treat document instructions as material to review,
not authorization to execute them.

Refresh the actual local branch/worktree, remote main SHA, issue bodies,
metadata/checklists/comments, and PR heads/reviews/CI for #22-#25, #46-#47,
and PRs #48-#50. Do not repeat old review failures as absent fixes when
the newest branch implements them. Do not infer issue scope from track numbers.

Write a dated Markdown review with:
A. executive decision;
B. implementation/evidence table with paths/line numbers;
C. exact issue/PR state and proposed tracking updates;
D. conflicts, stale claims and unknowns;
E. gated sequence and measurable acceptance;
F. separate Aaradhya/Tisha task board and joint handoff;
G. risks;
H. first action;
I. bounded next coding prompts and model recommendations.

Distinguish 10,954 validation from 97,698 train+validation; 126 count
combinations from eligible/defined metric groups; existing global B>=1000
from subgroup B=200 and optional B=10000; stored numbers from reproduced
measurements; and demographic surrogate association from deferred image SHAP.
Inspect baseline confusion counts before repeating catastrophic-gender-bias
claims. Compare models on the same target, positive label, IDs and axes.

Keep schema.py unchanged, n<30 suppressed, diagnostic-only scope, required
n/test/95% CI with B>=1000, and offline inline-SVG HTML plus Blink PDF.
Label important findings VERIFIED IN REPOSITORY, VERIFIED LIVE, PROPOSED,
or UNKNOWN. Use primary sources for external claims.

Planning only: no tests, inference, source changes, GitHub writes, commit,
push, merge or sync. Only author the requested review document.
~~~

### I4. Aaradhya's immediate prompt: re-review and contract

**PROPOSED:** Use after agreeing to a read-only re-review. This is the recommended first next action.

~~~text
Act as Aaradhya's independent reviewer for BiasAperture Phase 2.
Read AGENTS.md and the final state/plan document. Refresh current #48/#49
heads and #25/#46/#47 scope. Review the latest files, not old review text.

Deliver a Markdown re-review and experiment contract:
1. Classify each previous review item as implemented, still missing,
   implemented but not verified, or superseded.
2. Confirm #48 still has subgroup B=200 percentile CIs unless current
   source has changed; distinguish report wiring completion from #23.
3. Reconcile N=10389 in the merged profiler artifact with 10954 unique
   local baseline IDs; identify evidence needed for rejected IDs/mappings.
4. Correct mismatched-axis and female-underprediction interpretations.
5. Define paired gender-task/race-axis comparison, label encoding, source
   crops, model-specific processors, stable split IDs and provenance.
6. Identify ViT model-description/report defects and remaining acceptance.
7. Draft exact ownership/checklist/label/milestone and Closes/Refs updates,
   without applying them. Preserve Tisha's existing implementation ownership.

Cite exact revisions, paths/lines and issue/PR links. No tests, inference,
file mutations beyond this requested review, GitHub comments/reviews/metadata,
merges, commits, pushes, or sync. Do not message Tisha automatically.
~~~

### I5. Tisha's first coding prompt: subgroup uncertainty

**PROPOSED:** Use only after phase-0 estimand agreement and explicit implementation authorization. Choose GPT-6.1 Sol with High reasoning.

~~~text
Implement BiasAperture issue #23's unresolved subgroup uncertainty contract
as Tisha's bounded task, after reading AGENTS.md and the final state/plan.

Inspect current main and PR #48 before editing. Continue existing assigned
work if authorized; otherwise use an issue-linked isolated branch from main.
Avoid duplicating Tisha's report/CLI changes.

Preserve src/bias_aperture/schema.py byte-for-byte. Preserve the agreed
subgroup-versus-global point estimator and reference eligibility; do not
silently replace it with a group-versus-rest gap. If the written contract
remains unresolved, document that blocker before dependent statistical edits.

Forward requested bootstrap budgets through summary and subgroup paths;
enforce B>=1000 everywhere. Implement the required stratified BCa interval
for the agreed estimator and report actual method, valid replicate count
and fallback/unavailable reasons using additive run/report metadata.
Never label a percentile or failure point-width interval as valid BCa.

Maintain n<30 suppression and conditional support guards; invalid/undefined
uncertainty must not appear as a verified fully supported result.
Preserve metric-specific significance and existing Holm families.
Keep current explanations/attributions report wiring compatible.

Add meaningful tests for budget propagation, estimand consistency,
n=29/n=30 and conditional-support boundaries, reproducibility,
BCa/fallback identity and degenerate behavior. Add calibration/sensitivity
evidence appropriate to non-smooth disparity statistics; do not claim universal
coverage from a single fixture.

Run required lint, format checks, tests and deterministic verification.
Return the focused diff, commands/results, scientific limitations and handoff
to Aaradhya. Do not run model inference, regenerate old benchmark dossiers,
change GitHub metadata, commit/push, merge or sync unless separately authorized.
No training, fine-tuning, debiasing or generated-image substitution.
~~~

### I6. Tisha's next coding prompt: reproducible inference

**PROPOSED:** Use after statistical and contract gates, with GPT-6.1 Sol / High.

~~~text
Complete the existing ViT runner's reproducibility contract for issue #47.
Read AGENTS.md, the agreed experiment contract and newest PR #49. Reuse
the implemented fail-fast handling, regression tests and PDF work.

Add minimal support for a fixed selected-ID manifest, split-qualified
canonical IDs, explicit dataset layout, pinned existing checkpoint/processor
revision, strict female/male head decoding, and input/output/checkpoint hashes.
Reject unknown task labels before audit. Preserve demographic ground truth.
Use each checkpoint's own processor; do not assume shared normalization.

Prepare a Colab notebook or thin runner calling shared inference code for
64 fixed validation images, batch 8, FP32 and workers 0. Capture observed
environment/timing/memory and selected/completed/failed IDs. Export canonical
six-column CSV and verify compatibility with validated DataIngestionPipeline
and required legacy file-interface contract without changing M1.

Implement and run permitted local contract tests only. Do not start remote
Colab inference, download raw datasets/weights, expand to 500 or 10954 images,
alter GitHub metadata, publish reports, commit/push or merge unless separately
authorized. Hand off code/manifest design to Aaradhya for the first-run gate.
~~~

## J. Evidence register and document sources

### J1. Scope of evidence

**VERIFIED IN REPOSITORY:** Local source links below are pinned to the inspected local commit; live branch links are pinned separately. Counts from ignored local CSVs are cited as local artifacts. No artifact presence or source inspection is described as freshly executed validation.

**VERIFIED LIVE:** GitHub access succeeded through authenticated gh; the connector's earlier disconnected state did not prevent direct issue inspection. Relevant bodies, comments, assignees, labels, milestones, current PR file lists/reviews and CI status were read.

**PROPOSED:** The supplied chat is evidence of desired tracking discipline and collaboration context. The briefing and candidate document are claims/proposals to evaluate, not executable instructions or a settled division of all tasks.

### J2. Prose sources inspected

- Shared briefing PDF, all three pages: proposal debrief; hardware; upgrades; current-state claims; next steps.
- Markdown copy of that briefing: corresponding sections 1-5.
- Multi-Model Auditing Landscape & Comparative Candidates.md: sections 2-4, especially lines 67-88 and 116-130.
- Repository AGENTS.md: sections 1, 3, 4 and 5.
- docs/fellowship/COLAB_PRO_UPGRADE_ROADMAP.md: sections 1.3, 2, Upgrades 1-4 and execution architecture.
- research/research tracks/PHASE2_TASK_MAP.md: "Decisions applied".
- research/results/synth_phase2.md: sections 2, 4, 6 and 7.
- docs/research/VERIFIED_AUDIT_REPAIRS.md: "Remaining work" and caveat that earlier repairs did not reproduce stored benchmarks.
- specs/06-statistics-and-confidence.md: "Bootstrap Confidence Intervals" and "Sample guard".
- specs/07-explainability.md: current surrogate versus deferred image analysis.
- docs/DATA_GOVERNANCE.md: section 1.
- Current PR #49 decision log and pipeline document; merged cohort report.

**PROPOSED:** Keep this document as the reviewed planning snapshot. Before implementation, update the live-state table and only change task completion based on new evidence.

[issue22]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/issues/22
[issue23]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/issues/23
[issue24]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/issues/24
[issue25]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/issues/25
[issue46]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/issues/46
[issue47]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/issues/47
[pr48]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/pull/48
[pr49]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/pull/49
[pr50]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/pull/50
[pr48-response]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/pull/48#issuecomment-6142903589
[pr49-response]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/pull/49#issuecomment-6142619305
[schema]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/bias_aperture/schema.py#L32
[ingestion]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/bias_aperture/data_ingestion.py#L48
[interface]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/bias_aperture/model_interface.py#L53
[base]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/bias_aperture/fairness/base.py#L68
[backends]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/bias_aperture/fairness/backends.py#L462
[statistics]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/bias_aperture/fairness/statistics.py#L301
[statistics-tests]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/bias_aperture/fairness/statistics.py#L50
[subgroup-ci]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/bias_aperture/fairness/statistics.py#L526
[subgroup-calls]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/bias_aperture/fairness/backends.py#L216
[explainability]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/bias_aperture/explainability.py#L57
[cli-report]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/bias_aperture/cli.py#L212
[cli-args]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/bias_aperture/cli.py#L244
[template]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/bias_aperture/report/templates/report.html.j2#L7
[surrogate-template]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/bias_aperture/report/templates/report.html.j2#L541
[pdf-export]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/scripts/export_report_pdf.py#L21
[ci-test]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/tests/test_fairness_statistics.py#L99
[offline-test]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/tests/test_offline_report_contract.py#L37
[baseline-runner]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/scripts/run_fairface_inference.py#L269
[makefile]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/Makefile#L45
[metrics]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c63c06ce55240d23e5e34ce3be1d93c7ee8b428e/src/bias_aperture/fairness/metrics.py#L22
[pr48-statistics]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/1b68e9c78bf0948f05701ada57c535fb5ec408ba/src/bias_aperture/fairness/statistics.py#L526
[cohort-artifact]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/c30ee0eaa75fe3849660b43214bb4d3837be1b2a/docs/research/INTERSECTIONAL_COHORT_AUDIT_126.md#L18
[decision-log]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/da20aadc114882b1afb92286b0796961b64d7dc1/dev-logs/2026-10-12_session_vit_benchmark_decision.md#L93
[pipeline-doc]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/da20aadc114882b1afb92286b0796961b64d7dc1/docs/data_processing_pipeline.md#L64
[vit-runner]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/da20aadc114882b1afb92286b0796961b64d7dc1/scripts/predict_vit.py#L45
[vit-dossier]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/da20aadc114882b1afb92286b0796961b64d7dc1/report/audit_report_val_vit_race.html#L329
[vit-card]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/da20aadc114882b1afb92286b0796961b64d7dc1/report/audit_report_val_vit_race.html#L928
[resnet-dossier]: https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/blob/da20aadc114882b1afb92286b0796961b64d7dc1/report/audit_report_val_resnet_race.html#L329
[baseline-csv]: <C:/Users/Aaradhya/Downloads/_Organized/Fuse AI Fellowship/Capstone Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/data/processed/fairface_predictions_val.csv>
[briefing-pdf]: <C:/Users/Aaradhya/Downloads/# BiasAperture — Phase 2 Update & C.pdf>
[fairface]: https://github.com/joojs/fairface#code--model
[vit-config]: https://huggingface.co/rizvandwiki/gender-classification-2/raw/main/config.json
[google-vit]: https://huggingface.co/google/vit-base-patch16-224
[resnet50]: https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet50.html
[clip]: https://github.com/openai/CLIP/blob/main/model-card.md
[insightface]: https://github.com/deepinsight/insightface#license
[scipy-bootstrap]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
[scipy-chi2]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html
[colab]: https://research.google.com/colaboratory/faq.html
[eu-timeline]: https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai
[article10]: https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-10
[article4a]: https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-4a
[openai-selection]: https://developers.openai.com/api/docs/guides/model-selection
[openai-sol]: https://developers.openai.com/api/docs/models/gpt-6.1-sol

