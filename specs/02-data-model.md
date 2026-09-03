# 02 - Data Model

**Status:** Normative for M1 fields; implementation anchored in `schema.py`

## SubjectRecord

Each input row becomes one `SubjectRecord` with:

| Field | Meaning |
| --- | --- |
| `image_id` | Source image identifier |
| `race` | One of the seven locked FairFace race labels |
| `gender` | `Male` or `Female` |
| `age` | One of the nine locked FairFace age bins |
| `true_label` | Ground-truth value for the selected audit task |
| `predicted_label` | Model prediction for that task |

The demographic fields are fixed vocabularies. Task labels remain caller-defined strings.

## MetricResult

Each metric row contains `metric_name`, `subgroup`, `subgroup_sample_size`, `metric_value`, `ci_lower`, `ci_upper`, `p_value`, and `insufficient_sample`.

The permitted metric names are:

- `demographic_parity_difference`
- `equalized_odds_difference`
- `equal_opportunity_difference`
- `disparate_impact_ratio`

## Invariants

- `MIN_SUBGROUP_SAMPLE_SIZE = 30`.
- A subgroup with `n < 30` must set `insufficient_sample=True` and must not carry a computed metric value.
- `ALPHA = 0.05`.
- `MIN_BOOTSTRAP_RESAMPLES = 1000`.
- Intersectional subgroup strings are supported; their exact composite-key format is an implementation contract, not part of the original M1 lock.

The authoritative field definitions are in [schema-lock-m1.md](../docs/schema-lock-m1.md) and [`schema.py`](../src/bias_aperture/schema.py). Do not create a competing schema here.
