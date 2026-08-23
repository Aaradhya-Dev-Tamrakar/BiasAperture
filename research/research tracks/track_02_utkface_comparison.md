# Track 02 — UTKFace Comparison & Risk Assessment
**Stream:** A (Data Pipeline) · **Priority:** 🟡 Medium · **Owner Focus:** Aaradhya (WP2)
**Estimated Time:** 30 min · **Feeds:** UTKFace cut decision

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/02_utkface_comparison.md`

## Prompt

Research the UTKFace dataset for a bias auditing platform. Compare it against FairFace (108,501 images, 7-race taxonomy). Cover:
1. UTKFace label format: how race/gender/age are encoded in filenames vs. CSV
2. DEX-based age labeling methodology and its known noise characteristics
3. Race taxonomy differences vs. FairFace's 7-group taxonomy — what mapping is needed?
4. Sample size per demographic subgroup — which subgroups fall below n=30?
5. Missing bib entry: find the canonical citation for UTKFace (original paper)
6. Recommendation: is UTKFace worth the engineering effort, or should it be cut?

The project's cut-list says: "UTKFace's DEX label-noise is already the doc's own flagged risk." Evaluate whether this risk is real.
