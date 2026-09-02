# Track 30 — Model-Agnostic Classifier Adapter Layer
**Stream:** I (Modular Architecture) · **Priority:** 🔴 High · **Owner Focus:** Open (orchestrator-claimed)
**Estimated Time:** 45 min · **Feeds:** model_interface.py roadmap

## Instructions
1. Claim via orchestrator MCP `claim_task` (account: your assigned user, e.g. user1-user18) using the task ID in `PHASE2_TASK_MAP.md`, OR paste `CONTEXT.md` + `PHASE2_CONTEXT.md` into Claude Desktop first if running manually.
2. Then use the prompt below.
3. Submit via `submit_checkpoint` (result_text = short summary + full markdown deliverable), or save the output as `results/30_model_agnostic_classifier_adapter_layer.md` if running manually.
4. Research-only: no code changes, no repo edits, no git commits/pushes, no sync.ps1 execution.

## Prompt

model_interface.py's InProcessInterface is currently an abstract stub (NotImplementedError) reserved for the FairFace ResNet-34 baseline; PredictionsFileInterface (CSV/JSON ingestion) is the implemented, non-negotiable-core path.

Research concrete adapter designs so BiasAperture can audit ARBITRARY third-party image classifiers, not just the FairFace baseline.

Cover:
1. An ONNX Runtime adapter (model-format-agnostic, covers PyTorch/TensorFlow/etc. once exported) — what's needed to map arbitrary output logits back to this project's fixed race_7/gender_2/age_9 label space (the hard part: a client's model won't natively output FairFace's taxonomy).
2. A HuggingFace `image-classification` pipeline adapter as a lower-effort alternative.
3. Explicitly scope what's OUT of scope — auditing a model with a genuinely different demographic taxonomy than the M1 lock requires the Track 23 cross-modal schema work first, not this track; don't conflate the two.
