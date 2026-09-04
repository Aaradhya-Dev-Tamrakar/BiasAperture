# Research Report: SHAP Explainability Principles & Feature Weighting

**Project:** BiasAperture — A Diagnostic Framework for Demographic Bias Auditing in Facial Analysis Models  
**Workstream:** WP4 (Explainability / FR-005) · Stream D (Tracks 15 & 16)  
**Authors:** Aaradhya Dev Tamrakar (`@AaradhyaDT`), Tisha Manandhar (`@tiixsha`)  
**Supervised by:** Shreejan Kisee (Teaching Assistant, Fusemachines AI Fellowship)  
**Date:** September 2026  
**Implementation Anchor:** [`src/bias_aperture/explainability.py`](../../src/bias_aperture/explainability.py)

---

## 1. Executive Summary

This research document addresses the formal explainability foundations of SHAP (SHapley Additive exPlanations) and answers the core theoretical question: **how do we decide what values receive what weight in feature attribution?**

In summary:

1. **The Game-Theoretic Principle:** Model inference is framed as a cooperative game where features act as players collaborating to produce a payout (the difference between the model prediction and baseline expectation). Shapley values (Lloyd Shapley, 1953; Lundberg & Lee, 2017) are the **unique** attribution configuration satisfying four foundational fairness axioms: _Efficiency (Local Accuracy)_, _Symmetry (Equal Treatment)_, _Dummy (Null Player)_, and _Additivity (Linearity)_.
2. **The Weighting Mechanism:**
   - **Combinatorial Weights (Exact Shapley):** Coalitions are weighted by the probability of player arrival in a uniformly random permutation:
     $$W(|S|) = \frac{|S|!(|N| - |S| - 1)!}{|N|!} = \frac{1}{|N| \binom{|N|-1}{|S|}}$$
     This ensures every coalition size $k \in \{0, \dots, |N|-1\}$ receives an equal $1/|N|$ overall probability mass, preventing middle-sized subsets from dominating simply because they are combinatorially abundant.
   - **Kernel Weights (KernelSHAP):** Approximating attributions via weighted linear regression requires the **Shapley Kernel**:
     $$\pi_x(z') = \frac{M - 1}{\binom{M}{|z'|} \cdot |z'| \cdot (M - |z'|)}$$
     This forms a **U-shaped weighting curve** that heavily prioritizes single-feature main effects ($|z'|=1$) and total interactive effects ($|z'|=M-1$), while down-weighting intermediate coalitions.
3. **What "Values" Mean:** Feature values are quantified through their marginal contribution to the prediction relative to a background baseline expectation $\mathbb{E}[f(X)]$. In linear surrogate models, this reduces to $\phi_i = w_i \cdot (x_i - \mathbb{E}[x_i])$, directly matching BiasAperture's surrogate explainer implementation.
4. **Diagnostic Application to BiasAperture:** For facial analysis models (ResNet-34 on FairFace), pixel-level SHAP is computationally intractable ($50,176$ features). BiasAperture structures explainability by partitioning faces into semantic anatomical regions (skin tone, hair, facial geometry, background) to detect **proxy variable entanglement** (Kurian et al. 2024; EU AI Act Article 13/15) when demographic disparities are statistically flagged ($p < 0.05, n \ge 30$).

---

## 2. Theoretical Foundations of SHAP

### 2.1 The Cooperative Game Theory Formulation

Cooperative game theory analyzes scenarios where a set of players form coalitions to generate a collective gain.

In machine learning feature attribution:

- **The Grand Coalition ($N$):** The set of all $M$ input features, $N = \{1, 2, \dots, M\}$.
- **A Coalition ($S \subseteq N$):** A subset of active features.
- **Characteristic Payout Function ($v(S)$):** The expected model output when only features in $S$ are observed, with missing features marginalized over a background distribution:
  $$v(S) = \mathbb{E}_{X_{\bar{S}}}\left[f(x_S, X_{\bar{S}})\right]$$
- **The Total Gain:** The difference between the instance prediction $f(x)$ and the baseline expected prediction $\mathbb{E}[f(X)]$:
  $$\Delta = f(x) - \mathbb{E}[f(X)]$$
- **Shapley Attribution ($\phi_i$):** The fair credit assigned to feature $i$.

```
┌─────────────────────────────────────────────────────────────┐
│ Prediction Instance x (Image / Demographic Vector)          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Total Payout: Δ = f(x) - E[f(X)]                            │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Cooperative Game Solver (Shapley Additive Attribution)      │
│  - Efficiency: Σ phi_i = f(x) - E[f(X)]                     │
│  - Symmetry: Equal marginal gain -> Equal phi               │
│  - Dummy: Zero marginal gain -> phi = 0                     │
│  - Additivity: phi(f1 + f2) = phi(f1) + phi(f2)             │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
     phi_1 (Eyes/Nose)   phi_2 (Skin ITA)   phi_M (Lighting)
```

---

### 2.2 The Four Axiomatic Pillars (Uniqueness Guarantee)

Shapley (1953) proved that there exists **exactly one** mapping $\phi(v)$ from the characteristic function to feature attributions that simultaneously satisfies four axioms:

#### 1. Efficiency (Local Accuracy)

$$\sum_{i=1}^M \phi_i = f(x) - \mathbb{E}[f(X)]$$
_The sum of all feature attributions must equal the difference between the local prediction and the baseline expected value. No prediction value is lost or unallocated._

#### 2. Symmetry (Equal Treatment)

$$\text{If } v(S \cup \{i\}) = v(S \cup \{j\}) \quad \forall S \subseteq N \setminus \{i, j\}, \quad \text{then } \phi_i = \phi_j$$
_If two features contribute identically across every possible coalition of remaining features, their attributions must be strictly equal._

#### 3. Dummy / Null Player

$$\text{If } v(S \cup \{i\}) = v(S) \quad \forall S \subseteq N \setminus \{i\}, \quad \text{then } \phi_i = 0$$
_If adding feature $i$ never changes the expected prediction in any coalition, its attribution is zero._

#### 4. Additivity (Linearity)

$$\text{If } f(x) = f_1(x) + f_2(x), \quad \text{then } \phi_i(f_1 + f_2) = \phi_i(f_1) + \phi_i(f_2)$$
_If the model output is an ensemble or linear combination of sub-models, the overall attribution is the sum of attributions from each sub-model._

> **Significance for Bias Auditing:** Alternative attribution approaches (e.g., LIME with heuristic exponential kernels, raw saliency gradients, or decision tree Gini impurity decrease) violate one or more of these axioms. In particular, non-Shapley methods frequently violate _Consistency_ (where a feature's true impact increases, yet its assigned score paradoxically decreases). SHAP prevents this failure mode.

---

## 3. The Weighting Mechanism: How Weights and Values Are Assigned

### 3.1 Combinatorial Weights in Exact Shapley Formulation

The classical Shapley attribution formula calculates feature $i$'s contribution as:

$$\phi_i(v) = \sum_{S \subseteq N \setminus \{i\}} W(|S|) \cdot \left[ v(S \cup \{i\}) - v(S) \right]$$

where the coalition weight is:
$$W(|S|) = \frac{|S|!(|N| - |S| - 1)!}{|N|!}$$

#### Derivation A: The Random Permutation Perspective

Consider all $|N|$ features arriving in a sequential room in a random permutation $\sigma \in \mathcal{S}_N$. There are $|N|!$ possible orderings, each equally likely with probability $1/|N|!$.

When feature $i$ enters, a coalition $S$ has already arrived. The marginal value feature $i$ creates upon entrance is $[v(S \cup \{i\}) - v(S)]$.

How many of the $|N|!$ permutations result in feature $i$ encountering **exactly** the subset $S$?

1. The $|S|$ features belonging to $S$ must arrive prior to $i$. There are $|S|!$ permutations for these features.
2. Feature $i$ occupies position $|S| + 1$.
3. The remaining $(|N| - |S| - 1)$ features arrive after $i$. There are $(|N| - |S| - 1)!$ permutations for these features.

The number of favorable permutations is $|S|! \times (|N| - |S| - 1)!$. Dividing by the total permutation count $|N|!$:
$$P(\text{preceding set} = S) = \frac{|S|!(|N| - |S| - 1)!}{|N|!}$$

Thus, $\phi_i$ is the mathematically exact **expected marginal contribution** across uniformly random arrival orderings.

#### Derivation B: Two-Stage Uniform Sampling

The weight can be factored as:
$$W(|S|) = \frac{1}{|N|} \cdot \frac{1}{\binom{|N|-1}{|S|}}$$

This reveals a two-stage fair draw:

1. **Stage 1 ($\frac{1}{|N|}$):** Select the coalition size $k = |S| \in \{0, 1, \dots, |N|-1\}$ uniformly at random. Each coalition size receives equal probability weight $1/|N|$.
2. **Stage 2 ($\frac{1}{\binom{|N|-1}{k}}$):** Given size $k$, select one specific subset $S$ uniformly among the $\binom{|N|-1}{k}$ possible subsets of that size.

```
Why Uniform Subset Weighting (1 / 2^(M-1)) Fails:
Combinatorial distribution of subset sizes:
   Subset Count
      ▲
      │                    ████████  (k ≈ M/2: Middle-sized subsets dominate)
      │                ████████████████
      │            ████████████████████████
      │        ████████████████████████████████
      │    ████████████████████████████████████████
      │ █                                        █ (k=0, k=M-1: Isolated effects vanish)
      └─────────────────────────────────────────────► Coalition Size k
Shapley's weight W(|S|) divides by (M * C(M-1, k)), perfectly flattening the size bias!
```

If every subset were assigned equal weight $1/2^{|N|-1}$, middle-sized coalitions ($k \approx |N|/2$) would completely drown out single-feature main effects and total interaction effects, directly violating the _Efficiency_ axiom.

---

### 3.2 Regression Weights in KernelSHAP

For complex models where evaluating $2^M$ coalitions is intractable, Lundberg & Lee (2017) demonstrated that Shapley values can be computed via weighted linear regression:

$$g(z') = \phi_0 + \sum_{i=1}^M \phi_i z_i', \quad z' \in \{0, 1\}^M$$

where $z_i' = 1$ indicates feature $i$ is present, and $z_i' = 0$ indicates it is masked.

The coefficients $\phi_i$ recover exact Shapley values when minimizing:
$$\arg\min_{\phi_0, \dots, \phi_M} \sum_{z' \in \mathcal{Z}} \left[ f(h_x(z')) - g(z') \right]^2 \cdot \pi_x(z')$$

The regression weights are governed by the **Shapley Kernel**:
$$\pi_x(z') = \frac{M - 1}{\binom{M}{|z'|} \cdot |z'| \cdot (M - |z'|)}$$

where:

- $M$ = total feature count.
- $|z'| = \sum_{j=1}^M z_j'$ = number of active features in binary mask $z'$.

```
Shapley Kernel Weight π(z') vs Coalition Size |z'|
  Weight π
    ▲
 ∞  │ █                                                 █
    │ █                                                 █
    │  █                                               █
    │   █                                             █
    │     █                                         █
    │       ▀█▄                                 ▄█▀
    │           ▀▀▀▄▄▄                   ▄▄▄▀▀▀
 0  └─────────────────────██████████──────────────────────►
    |z'| = 0   |z'| = 1        |z'| = M/2      |z'| = M-1   |z'| = M
             (Single Features)               (All-but-one)
```

#### Why the Kernel Is U-Shaped

1. **At $|z'| = 1$ and $|z'| = M - 1$:** The denominator is minimized, causing $\pi_x(z') \to \infty$ (enforced as extreme weights in regression).
   - Coalitions of size 1 isolate **direct, unconfounded main effects**.
   - Coalitions of size $M - 1$ isolate the **total interactive effect** of removing a single feature in the presence of all others.
2. **At $|z'| \approx M/2$:** The binomial coefficient $\binom{M}{|z'|}$ reaches its maximum. The kernel heavily **down-weights** these samples because intermediate coalitions entangle dozens of higher-order interactions, yielding noisy regression gradients.
3. **At $|z'| = 0$ and $|z'| = M$:** These boundary constraints enforce:
   - $\phi_0 = \mathbb{E}[f(X)]$ (the global baseline when no features are present).
   - $\sum_{i=1}^M \phi_i = f(x) - \mathbb{E}[f(X)]$ (local accuracy when all features are present).

---

### 3.3 What "Values" Mean: The Baseline Expectation $\mathbb{E}[f(X)]$

Neural networks cannot natively process "missing" inputs. To simulate feature absence, values are marginalized against a reference distribution $D_{\text{bg}}$:

$$v(S) = \frac{1}{|D_{\text{bg}}|} \sum_{x' \in D_{\text{bg}}} f(x_S, x'_{\bar{S}})$$

#### How Baseline Selection Dictates Attribution

- **Neutral/Zero Baseline (e.g., all-black pixels $[0,0,0]$):** Features are credited simply for having luminance or color, biasing explanations toward bright regions regardless of semantic importance.
- **Demographic Cohort Baseline (e.g., 20–100 balanced FairFace exemplars):** Features are credited strictly for **how the subject deviates from the population mean**, highlighting features unique to the audited individual.

---

### 3.4 Exact Shapley Weights in Linear Surrogate Models (BiasAperture Implementation)

In [`src/bias_aperture/explainability.py`](../../src/bias_aperture/explainability.py), BiasAperture implements an exact additive Shapley surrogate over demographic dummy variables:

```python
# Extracted from src/bias_aperture/explainability.py (lines 146-148)
shapley_values = (X - baseline) * weights
mean_importance = np.abs(shapley_values).mean(axis=0)
```

#### Formal Proof

Let a linear surrogate model be defined as:
$$f(x) = w_0 + \sum_{j=1}^M w_j x_j$$

Under feature independence, the expected prediction for coalition $S$ is:
$$v(S) = w_0 + \sum_{j \in S} w_j x_j + \sum_{j \notin S} w_j \mathbb{E}[X_j]$$

The marginal contribution of adding feature $i$ is:
$$v(S \cup \{i\}) - v(S) = w_i x_i - w_i \mathbb{E}[X_i] = w_i (x_i - \mathbb{E}[X_i])$$

Because this marginal contribution is constant across all subsets $S$, the Shapley formula collapses:
$$\phi_i = \sum_{S \subseteq N \setminus \{i\}} W(|S|) \cdot \left[ w_i (x_i - \mathbb{E}[X_i]) \right] = w_i (x_i - \mathbb{E}[X_i]) \sum_{S} W(|S|) = w_i (x_i - \mathbb{E}[X_i])$$

**Summary of "What Values" vs. "What Weight":**

- **The Weight ($w_i$):** The regression coefficient from the surrogate model (measuring sensitivity).
- **The Value ($x_i - \mathbb{E}[x_i]$):** The centered demographic attribute value (measuring deviation from the cohort baseline).

---

## 4. Application to Facial Analysis Models (BiasAperture & ResNet-34)

### 4.1 The Pixel Tractability Challenge & Semantic Partitioning

Evaluating individual pixels ($224 \times 224 = 50,176$) via KernelSHAP is computationally intractable ($2^{50176}$ combinations).

BiasAperture resolves this through a two-tiered strategy:

1. **Hierarchical Partitioning (`shap.PartitionExplainer`):** Evaluates image superpixels using hierarchical spatial trees, drastically reducing forward passes.
2. **Semantic Region Mapping (Face Parsing):** Groups pixels into anatomical face masks:
   - Skin tone / Cheeks ($R_{\text{skin}}$)
   - Hair texture ($R_{\text{hair}}$)
   - Primary facial geometry: Eyes, Nose, Mouth ($R_{\text{geo}}$)
   - Background / Lighting ($R_{\text{env}}$)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Flagged Disparity Trigger (p < 0.05, n ≥ 30)            │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Feature Coalition Strategy                               │
│    • Individual pixels intractable (50,176 pixels)          │
│    • Group into K Semantic Regions via Face Parsing         │
│      [Forehead, Eyes, Nose, Mouth, Cheeks, Hair, Background]│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. KernelSHAP / PartitionExplainer Attribution              │
│    • Mask regions with blur or cohort background mean       │
│    • Compute attribution mass per region R:                 │
│      Mass(R) = Σ |phi_(u,v)| / Σ |phi_total|                │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Proxy Variable Discrimination Test                       │
│    • Compare Subgroup Mass vs. Overall Population Mass      │
│    • Test difference with 95% Bootstrap CI (B ≥ 1,000)      │
│    • Corroborate with ITA (Individual Typology Angle)       │
└──────────────────────────────┘
```

---

### 4.2 Detecting Demographic Proxy Variables (Kurian et al. 2024 & FR-005)

Kurian et al. (2024) demonstrated that convolutional networks can inadvertently encode protected demographic attributes (e.g., race) through correlated visual proxies (e.g., lighting, background artifacts, skin reflectance), even when protected labels are omitted during training.

To detect this, BiasAperture defines **Attribution Mass Ratio**:
$$\text{Attribution Mass}(R) = \frac{\sum_{(u,v) \in R} |\phi_{(u,v)}|}{\sum_{(u,v) \in \text{Image}} |\phi_{(u,v)}|}$$

- **Legitimate Classification:** Attribution mass concentrates on task-relevant anatomy ($R_{\text{geo}}$: eyes, nose, mouth lines).
- **Proxy Entanglement:** Attribution mass shifts significantly to non-target regions ($R_{\text{skin}}$ or $R_{\text{env}}$) specifically in the flagged demographic subgroup.
- **Dual-Signal Cross-Validation:** Attribution shifts are cross-checked with the **Individual Typology Angle (ITA)** skin-tone colorimetry from [`src/bias_aperture/explainability.py`](../../src/bias_aperture/explainability.py):
  $$\text{ITA} = \arctan\left(\frac{L^* - 50}{b^*}\right) \times \frac{180}{\pi}$$
  Agreement between high skin SHAP mass and extreme ITA values validates a candidate proxy variable channel.

---

## 5. Structural Limitations & Defense Awareness

When presenting this work during project defense or review, cite these theoretical constraints:

1. **Bilodeau et al. (2022) Impossibility Theorem:**  
   Any attribution method that is both **complete** (Efficiency) and **linear** (Additivity) **cannot reliably distinguish true causal drivers from spurious correlations or random guessing** for non-trivial model classes. SHAP reveals what features the model attended to, not whether the relationship is causal.
2. **Credit-Splitting Across Collinear Features:**  
   If a model relies on both skin reflectance and hair texture as joint proxies for race, Shapley's equal-division property splits attribution between them. As a result, individual feature scores may fail to reach significance unless aggregated into region masks.
3. **Adversarial Scaffolding (Slack et al. 2020):**  
   Adversarial models can disguise discriminatory behavior by detecting when an input is being perturbed by an explainer's masking distribution, temporarily reverting to neutral predictions during audit runs.
4. **Statutory Reporting Standard (EU AI Act Art. 13/15):**  
   An absence of SHAP proxy signal must be documented as _"no proxy channel identified under this method"_, never as _"confirmed absence of proxy reliance"_.

---

## 6. Viva & Review Cheat Sheet

| Question                                                       | Core Technical Response                                                                                                                                                                                                                                                                                |
| :------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **What is the mathematical foundation of SHAP?**               | Adapts Lloyd Shapley's (1953) cooperative game theory. It models input features as players cooperating to produce the prediction payout $\Delta = f(x) - \mathbb{E}[f(X)]$. It is uniquely guaranteed to satisfy Efficiency, Symmetry, Dummy, and Additivity.                                          |
| **Why is the subset weight $\frac{\|S\|!(M-\|S\|-1)!}{M!}$?**  | It represents the exact probability of feature $i$ joining coalition $S$ when features arrive in a uniformly random permutation. Equivalently, it is a two-stage fair draw: choose a coalition size $k$ with probability $1/M$, then choose a subset of that size with probability $1/\binom{M-1}{k}$. |
| **How does KernelSHAP decide weights in practice?**            | KernelSHAP formulates attribution as a weighted linear regression. The Shapley Kernel $\pi_x(z')$ forms a U-shaped weighting curve that heavily weights size-1 coalitions (main effects) and size-(M-1) coalitions (total interactive effects), while suppressing noisy intermediate coalitions.       |
| **What does the baseline value $\mathbb{E}[f(X)]$ represent?** | Missing features are marginalized over a reference background dataset $D_{\text{bg}}$. The baseline defines the "neutral reference state," so attributions represent deviations from population expectation.                                                                                           |
| **How does BiasAperture use this in code?**                    | In `explainability.py`, when disparities are flagged ($p < 0.05, n \ge 30$), we compute exact additive Shapley values $\phi_i = w_i \cdot (x_i - \mathbb{E}[x_i])$ across demographic dummy axes via a surrogate linear model, and evaluate visual proxy attribution mass across face regions.         |
