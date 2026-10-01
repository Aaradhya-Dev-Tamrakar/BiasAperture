# Verified audit repairs — first implementation batch

Prepared October 1, 2026 (Asia/Katmandu). Phases 0–3 are implemented locally;
phases 4–6 are not complete. This is an implementation record, not a benchmark
reproduction or a statistical calibration claim.

## Workspace and revision

- Repository: `BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models`
  inside `C:\Users\user\Documents\ChatGPT\Aaradhya`.
- Initial checkout: clean `main` at `e918441c59cdf08325ecf62de36e55490fae510a`.
- Repair base: `f842acc591a80c0230551aad66a8b4fd173ec065`, verified modularization
  branch; local repair branch: `codex/verified-audit-repairs`.
- Implementation revision: the repair commit containing this ledger on
  `codex/verified-audit-repairs`, against the base above. The initial batch was
  local and uncommitted; the user subsequently authorized pushing a separate
  branch. No unrelated edits existed at start. The locked schema and
  subgroup-versus-overall estimand are unchanged.
- Instructions: repository-root `AGENTS.md`; no nested instruction files found.
- Evidence: the external `evaluation-verification/verification-report.md` and
  `probe.py`, plus the archived transcript at the base. The transcript's scores
  were not treated as measurements or instructions.

## Environment

No project `uv` environment was available. Tests used the existing verification
runtime with the same versions as the recorded baseline:

| Component | Version |
|---|---|
| OS | Windows |
| Python | 3.12.14 |
| NumPy | 2.5.3 |
| pandas | 3.0.6 |
| SciPy | 1.18.1 |
| scikit-learn | 1.9.1 |
| Fairlearn | 0.14.0 |
| AIF360 | 0.6.1 |
| pytest | 9.1.1 |
| Jinja2 | 3.1.6 |
| Ruff (separately installed for checks) | 0.16.9 |

Interpreter:
`C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.
Dependencies: `C:\Users\user\Documents\ChatGPT\Aaradhya\evaluation-verification\deps`.
Ruff: `evaluation-verification\repair-tools\bin\ruff.exe` outside the repository.
These are not a frozen `uv.lock` reproduction. Sandbox permission errors required
approved unsandboxed access to the existing dependency directory and local Ruff.
The same revision/environment had an independently verified 85-test baseline,
so no additional unchanged-baseline run was needed.

## Changes and evidence anchors

| Finding | Changed executable behavior | Regression evidence |
|---|---|---|
| Numeric multiclass rates could exceed 1; categorical multiclass failed inconsistently | Shared encoder rejects more than two task labels before backend isolation. CLI exits 1 before report generation. Rate primitive rejects values outside encoded 0/1 without integer truncation. | `test_public_backend_rejects_multiclass`, `test_cli_rejects_multiclass_without_report`, `test_binary_rate_primitive_rejects_unencoded_values` |
| Named Fairlearn backend ran local formulas | Fairlearn `MetricFrame` invokes native selection-rate, TPR and FPR functions; shared canonical row assembly consumes those primitives. Missing Fairlearn is an explicit runtime error, never a substitute implementation. | `test_fairlearn_api_is_executed`, `test_missing_fairlearn_fails_clearly_in_backend_and_cli` |
| Backend failure could become an empty successful audit | Canonical failure aborts report production; secondary failures remain isolated, generate missing-value divergence alerts where applicable, and are labeled incomplete validation in HTML. | `test_unavailable_aif360_canonical_backend_prevents_report`, `test_secondary_backend_failure_is_visible_in_report`, existing `test_aif360_backend_failure_isolation_emits_divergence_alert` |
| Harmonization fixture only compared hand-written formulas and mislabeled average odds | Actual library APIs execute a TPR=.8/.7, FPR=.1/.4 fixture. Both EODs=.30; AIF360 signed average odds=-.10/+ .10 by orientation, absolute average=.20, unsigned EOP=.10. Adapter summaries agree. | `test_real_library_odds_definitions_and_adapter_consensus` |
| Zero/support/eligibility edge behavior needed real adapters | Both adapters retain DIR 0/0→1 and 0/nonzero→0; absent conditional support and n<30 rows remain suppressed. | `test_real_adapters_dir_zero_denominators`, `test_real_adapters_missing_conditional_support_and_small_groups` |
| Categorical predictions broke surrogate explanations | Explanations and fairness use the same truth-plus-prediction task vocabulary and sorted-positive default. Numeric and Female/Male fixtures produce equal metrics and associations. | `test_equivalent_binary_encodings_match_metrics_and_explanations` |
| CLI explanation could not be disabled | `--no-explain` prevents explainer invocation; default and `--explain` preserve enablement. | `test_cli_no_explain_prevents_invocation` |
| Computed attribution was dropped; unavailable paths claimed generation | Reports retain association values/statuses. No records or fitting failure is explicitly unavailable. Missing p-values do not trigger explanation; `explained_count` counts actual populated results. | `test_pipeline_retains_attributions_in_generated_report`, `test_surrogate_unavailable_is_not_reported_as_generated`, updated `test_shap_explainer_selective_triggering` |

The default positive label remains the sorted second label (1 for 0/1, Male for
Female/Male); a sole 1/True is positive and other sole labels are negative. No new
positive-label option or schema fields were added. General multiclass auditing
is still deferred. Protected demographic groups can have more than two labels.

The surrogate fits predictions across the full audit and summarizes demographic
contributions to logistic log-odds. It does not establish causes, explain images,
or decompose the disparity statistic. Repeated flagged rows refer to the same
full-audit fit. Image-native SHAP remains deferred.

Fairlearn's disaggregated metric API is documented in its
[official MetricFrame reference](https://fairlearn.org/main/api_reference/generated/fairlearn.metrics.MetricFrame.html).
Cross-library agreement here checks point estimates only. Bootstrap, hypothesis
tests and reporting remain shared code and are not independently validated by
that agreement. README usage now explicitly selects the `fairness` extra;
audit-engine and explainability specifications describe these executable limits.

## Commands and results

Executed from the nested repository. Equivalent PowerShell reproduction:

```powershell
$repairPython = 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $repairPython -B -c "import sys; sys.path[:0] = [r'C:\Users\user\Documents\ChatGPT\Aaradhya\evaluation-verification\deps', 'src']; import pytest; raise SystemExit(pytest.main(['src/tests', '-p', 'no:cacheprovider', '--basetemp', r'C:\Users\user\Documents\ChatGPT\Aaradhya\evaluation-verification\pytest-repair-full']))"
& 'C:\Users\user\Documents\ChatGPT\Aaradhya\evaluation-verification\repair-tools\bin\ruff.exe' check src/
& 'C:\Users\user\Documents\ChatGPT\Aaradhya\evaluation-verification\repair-tools\bin\ruff.exe' format --check src/
git diff --check
```

- Initial focused tests (repair regressions, harmonization, backend integrity,
  explainability): **28 passed**, 2 AIF360 division warnings, 8.98 seconds.
- Full integrated application suite after adding backend report-status coverage:
  **106 passed**, 4 AIF360 division warnings, 19.56 seconds. Warnings arise from
  absent conditional support in two fixtures; those paths assert suppression.
- Ruff check: **passed**. Ruff format check: **31 files already formatted**.
  Only the nine changed Python files were formatted; no unrelated mass formatting.
- `git diff --check`: **passed**.
- Follow-up repository workflow check: reviewed `CLAUDE.md`, `sync.ps1`, the
  PR template, Actions workflows and `.pre-commit-config.yaml`. The local
  stale-claim hook passed against `README.md`, `specs/05-audit-engine.md`,
  `specs/07-explainability.md` and this ledger via
  `python -B scripts/check_stale_claims.py <those four paths>`. No `SKILL.md`
  package was present in this checkout. `uv`, `gh` and `pre-commit` were not
  available on PATH. `sync.ps1` was inspected but not executed because its
  default path stages, commits and pushes, outside the local-only batch.

Tests replace two formula-only cases with actual library execution and add new
boundary regressions; the increase from 85 to 106 is not a benchmark performance
claim. Existing stored benchmark reports were not regenerated.

## GitHub Pilot tooling follow-up

The user subsequently added the sibling `github-pilot` repository and requested
its use. Read its `AGENTS.md` and created its isolated `.venv` with
`uv sync --locked --extra dev` using the bundled Python 3.12.14 interpreter.
The installed binaries are `gh` 2.102.0 under `C:\Program Files\GitHub CLI` and
`uv` 0.12.21 under the user's WinGet packages directory. This process has an older
PATH, so full executable paths were used. The GitHub CLI is not authenticated;
Pilot has a separate existing credential configuration (credentials were not
printed or copied).

Pilot's CLI status and `FleetAuditor` executed successfully. A TTL snapshot was
saved under `github-pilot/.cache/pilot/audit/`; the compact handoff is
`evaluation-verification/pilot-audit-result.json`. Of 84 repository metadata
records inspected, `Aaradhya-Dev-Tamrakar/BiasAperture` lacked a description and
topics; `AaradhyaDT/BiasAperture` had no anomalies under Pilot's metadata checks.
These are metadata checks, not application correctness or CI verification. The
configured targets did not include the primary `fuseai-fellowship` repository.
Pilot's current auditor never queries Actions runs, despite advertising CI
health, and its CLI `--limit` option is not forwarded to `audit_fleet`.

Ran Pilot's own `sync.ps1 -WhatIf -NoPush` within its repository. It normalized
the remote URL to the equivalent `.git` form but performed no commit or push.
Its sync script is specific to the Pilot repository and must not replace
BiasAperture's synchronization script. No tracked Pilot source was changed.

## Separate-branch publication

The user authorized a push to a separate branch on October 1, 2026. Publication
is scoped to `origin/codex/verified-audit-repairs` in the primary
`fuseai-fellowship` repository. The main branch and mirror branches are outside
this push. No PR creation or merge is part of this instruction.

The standard BiasAperture sync script ends by mirroring every origin branch,
which would exceed this publication scope. A scoped wrapper instead uses the
existing branch, explicit repair-file staging, GitHub Pilot's `Scan-Secrets`
function, conventional commit references to issues #22 and #24, and a single
non-force branch push. Author identity is the authenticated `AaradhyaDT` account
with GitHub's noreply email. Remote `main` was checked at the unchanged
`e918441c59cdf08325ecf62de36e55490fae510a`; the destination branch did not exist
before publication. Push verification compares the local commit with
`git ls-remote origin refs/heads/codex/verified-audit-repairs`.

## Remaining work

- Phase 4: consolidate inference architecture, strict checkpoint coverage,
  label order/preprocessing and prediction contract. No torch/weights/sample
  inference was executed in this batch.
- Phase 5: subgroup intervals still use the old 200-draw percentile default;
  global intervals still attempt BCa with fallbacks. Budget forwarding, interval
  labels, hypothesis-family contracts, schema uncertainty suppression and
  large-n jackknife calibration remain unresolved. The subgroup reference
  population was not changed.
- Phase 6: wider claim-ledger/traceability corrections, licensing acknowledgement,
  machine-checkable provenance/integrity bundles, CI portability and generated
  offline-report contract coverage remain. No browser zero-network verification
  occurred. Existing benchmark provenance must not be invented retrospectively.

The inherited README and wider research documents still contain statistical and
provenance overstatements outside this batch. Completing phases 0–3 does not make
those claims verified.
