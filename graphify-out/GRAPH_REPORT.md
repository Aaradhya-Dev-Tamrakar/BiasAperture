# Graph Report - BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models  (2026-09-01)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1095 nodes · 1377 edges · 129 communities (90 shown, 34 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 94 edges (avg confidence: 0.91)
- Token cost: 7,523 input · 1,503 output

## Graph Freshness
- Built from commit: `a3c591de`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- System Module Design
- CLI and Report Generation
- Proposal Defense Strategy
- Parallel Research Guide
- Sprint Roadmap and Criteria
- Fairness First Principles
- Fairness Backend Orchestration
- Core Fairness Metrics
- Statistical Implementation Details
- Verification and Scrutiny Guide
- Base Fairness Classes
- Task Assignment and Feasibility
- Defense Presentation Slides
- Research Runner Setup
- Project Audit and Tasks
- Literature Review Matrix
- Executive Project Synthesis
- Backend Harmonization Tests
- Mock Testing Data
- Dataset Profiling Scripts
- Data Ingestion Pipeline
- Technical Sprint Specifications
- Novelty and Integration Defense
- Integration Innovation Memo
- Statistical Rigor Engine
- Metric Definition Resolutions
- Research Claim Ledger
- Dataset Exploration Reports
- Model Interface Layer
- Explainability Engine
- Compliance and Standards
- Assistant Coding Standards
- Project Architecture Guidelines
- Repository Documentation
- Fairness Engine Synthesis
- Weekly Progress Report WK3
- Architectural Design Specs
- Weekly Progress Report WK4
- Weekly Progress Report WK1
- Weekly Progress Report WK2
- Technical Accomplishments Summary
- System Context Overview
- Pre-Defense Reading Guide
- Project Management Assets
- Research Stream Context
- Project Scope Invariants
- Schema Lock Specifications
- Data Governance Policy
- Internal Schema Contracts
- Git Sync Utilities
- Report Generation Synthesis
- Explainability Module Synthesis
- Developer Agent Guidelines
- AI Agent Instructions
- Coding Operating Invariants
- Pull Request Template
- Cross-Track Conflict Log
- Architecture Testing Synthesis
- Monthly Progress Index
- Report Generation
- Project Report Index
- Backend Consensus Verifier
- FairFace Dataset Research
- Data Pipeline Synthesis
- Regulatory Mapping Synthesis
- Tisha Manandhar
- Data Directory Structure
- Literature Review Templates
- Dataset and Schema Benchmarks
- Fairness Theory and Constants
- UTKFace Comparison Research
- Data Validation Patterns
- Inference Source Analysis
- Jinja2 Report Templates
- Model Card Specifications
- Dataset Datasheet Drafts
- EU AI Act Mapping
- Fairlearn API Integration
- AIF360 API Integration
- Bootstrap CI Implementation
- Chi-Squared Significance Testing
- Disparate Impact Analysis
- Equalized Odds Theory
- SHAP Integration Research
- Proxy Variable Detection
- Strategy Design Pattern
- Pytest Metric Patterns
- NIST RMF Mapping
- Competitor Tool Analysis
- Development Tooling
- System Specification Levels
- Regulatory Defense Synthesis
- Model Inference Scripts
- Platform and Package Scope
- Literature Review Matrix
- Project Changelog
- Research Documentation
- Reporting Standards
- Copilot Instructions
- Advanced Statistical Methods
- System Context Guides
- Fairness Engine Logs
- Aaradhya Dev Tamrakar
- AIF360 Toolkit
- FairFace Data Analysis
- UTKFace Data Analysis
- EU AI Act Compliance
- Computer Vision Fairness Survey
- Medical Imaging Bias Research
- Fairlearn Library
- Cross-Validation Management
- Bias Aperture Project
- Pre-commit Hooks
- Fusemachines Branding
- Metric Result Data
- Pandas Data Validation
- FairFace Prediction Analysis
- Disparate Impact Metrics
- Fairness Equality Metrics
- FairFace Setup Guide
- Session Summary
- Dependency Management
- UTKFace Comparison
- Scrutiny Framework

## God Nodes (most connected - your core abstractions)
1. `DataIngestionPipeline` - 29 edges
2. `SubjectRecord` - 24 edges
3. `IngestionConfig` - 21 edges
4. `MetricResult` - 21 edges
5. `2. Slide Deck Outline (15–20 slides)` - 21 edges
6. `SubjectRecord` - 20 edges
7. `BiasAperture-AT (v10)` - 20 edges
8. `MetricResult` - 19 edges
9. `BiasAperture-AT (v6)` - 17 edges
10. `ValidationMode` - 14 edges

## Surprising Connections (you probably didn't know these)
- `High-Level Architecture Diagram` --references--> `BiasAperture-AT Project Log`  [INFERRED]
  report/src/images/architecture_highlevel.jpg → research/context feed/BiasAperture-AT.md
- `Project Gantt Chart` --references--> `BiasAperture-AT Project Log`  [INFERRED]
  report/src/images/gantt.png → research/context feed/BiasAperture-AT.md
- `System Workflow Flowchart` --references--> `BiasAperture-AT Project Log`  [INFERRED]
  report/src/images/workflow_flowchart.jpg → research/context feed/BiasAperture-AT.md
- `BiasAperture-AT Project Log` --references--> `BiasAperture Proposal Report`  [EXTRACTED]
  research/context feed/BiasAperture-AT.md → report/main.pdf
- `ReportContext` --uses--> `MetricResult`  [INFERRED]
  src/bias_aperture/report/generator.py → research/context feed/schema.py

## Import Cycles
- None detected.

## Communities (129 total, 34 thin omitted)

### Community 0 - "System Module Design"
Cohesion: 0.22
Nodes (9): 2.1. Module 1: Ingestion & Invariant Validation (`data_ingestion.py`, `model_interface.py`), 2.2. Module 2: Fairness Strategy Engine (`bias_aperture/fairness/`), 2.3. Module 3: Statistical Rigor Engine (`fairness/statistics.py`), 2.4. Module 4: Targeted Explainability & Proxy Detection (`explainability.py`), 2.5. Module 5: Compliance Report Generation (`report/`), 2. Component Design & Interfacing, Ingestion Contracts & Patterns, Shared Base Architecture (`fairness/base.py`) (+1 more)

### Community 1 - "CLI and Report Generation"
Cohesion: 0.08
Nodes (30): ArgumentParser, build_parser(), main(), Construct CLI argument parser., HTMLReportGenerator, Any, Path, Compliance report generator engine (WP3 / Stream B). Compiles demographic… (+22 more)

### Community 2 - "Proposal Defense Strategy"
Cohesion: 0.05
Nodes (38): 1. Defense Format & Strategy, 3. Slide-by-Slide Script & Talking Points, 4. The Novelty Question — Your Most Important Defense, 5. Anticipated Hard Questions & Scripted Answers (32 Questions), 6. Traps to Avoid, 7. Numbers You Must Know Cold, 8. Mock Grilling Checklist, Architecture (Slide 9) — The Pipeline (+30 more)

### Community 3 - "Parallel Research Guide"
Cohesion: 0.06
Nodes (34): After All 20 Complete, Checklist, Implementation Order, 🚀 Parallel Research Runner Guide — 20 Claude Desktop Instances, 🔴 Phase 1 — Critical (read these first), 🟡 Phase 2 — Medium (read these second), 🟢 Phase 3 — Low (read last), Priority Order (if reviewing as they finish) (+26 more)

### Community 4 - "Sprint Roadmap and Criteria"
Cohesion: 0.06
Nodes (34): §16. Coming-Week Task Assignment — Trait-Based Split (August 20, 2026), §17. Research Verification & Feature Branch Allocation (August 23, 2026), §18. Master Task Division & 4-Week Sprint Roadmap (Implementation Phase, August 2026), §19. Proposal Defense & Final Deadline Check (August 26, 2026), 1. Dual-backend validation (AIF360 + Fairlearn in parallel), 1. Work Package & Stream Allocation, 2. Four-Week Sprint Timeline, 2. Per-subgroup-cell statistical completeness (n ≥ 30 minimum reporting threshold) (+26 more)

### Community 5 - "Fairness First Principles"
Cohesion: 0.15
Nodes (13): 10. Passing Audit Semantics, 11. Regulatory Alignment, 12. Scope Boundary, 1. Problem & Intersectional Masking, 2. Fairness Metrics Hierarchy, 3. Multi-Class One-vs-Rest (OvR) Policy, 3. The 12 Master First-Principles Questions, 4. Effect-Size Interpretation (+5 more)

### Community 6 - "Fairness Backend Orchestration"
Cohesion: 0.14
Nodes (17): AIF360Backend, CrossValidationOrchestrator, FairlearnBackend, Fairness backends and dual-backend cross-validation orchestrator (WP4).…, AIF360 backend harmonized to compute max-of-gaps EOD and unsigned EOP. Directly…, Fairness backend utilizing Fairlearn-aligned metric definitions., Orchestrates multi-backend execution and detects algorithmic divergence., FairnessBackend (+9 more)

### Community 7 - "Core Fairness Metrics"
Cohesion: 0.14
Nodes (21): ndarray, Compute Core Four metrics using native AIF360 dataset & metrics., Compute Core Four metrics with statistical confidence bounds., compute_group_rates(), demographic_parity_difference(), equal_opportunity_difference(), equalized_odds_difference(), ndarray (+13 more)

### Community 8 - "Statistical Implementation Details"
Cohesion: 0.22
Nodes (9): 3.1. Vectorized Stratified BCa Bootstrap Confidence Intervals, 3.2. Chi-Squared Contingency & Holm-Bonferroni Adjustment, 3.3.1. Screening Invariant ($n \ge 30$) vs. Conservative Support Rules, 3.3.2. DIR Zero-Denominator Reporting Invariant, 3.3. Statistical Adequacy & Estimand Mapping, 3. Statistical Engine Implementation Details, Bootstrap Population Model & Stratified Resampling Rationale, Mathematical Steps for BCa (+1 more)

### Community 9 - "Verification and Scrutiny Guide"
Cohesion: 0.08
Nodes (23): 1. The 4-Tier Scrutiny Framework, 2. Investigator Ownership & Stream Allocation, 3. Stream-by-Stream Verification Protocols, 4. Top 10 Viva / Defense Interrogation Questions (Self-Test), 5. Verification Checklist Before Any Milestone Merge, BiasAperture — Research Verification & Scrutiny Guide, Claim 1: EU AI Act Article 10 mandates statistical adequacy and bias detection, Claim 1: FairFace ResNet-34 uses an 18-unit linear head (not 3 separate heads) (+15 more)

### Community 10 - "Base Fairness Classes"
Cohesion: 0.17
Nodes (15): EligibilityReport, eligible_groups(), MetricResult, ndarray, SubjectRecord, Abstract fairness backend and shared sample-guard infrastructure (WP4). Defines…, Screen numeric arrays for per-metric eligibility. This is the authoritative…, Return labels of groups eligible for a given metric. Parameters ----------… (+7 more)

### Community 11 - "Task Assignment and Feasibility"
Cohesion: 0.09
Nodes (21): §16. Coming-Week Task Assignment — Trait-Based Split (August 20, 2026), Acceptance Criteria, BiasAperture-AT (v6), Cut-List (if behind schedule — drop in this order), Defense Framing (Updated August 20, 2026), Engineering Decisions That Differ from Industry Optimization (August 20, 2026 Reflation), Feasibility Study — Reviewed, Naming History Note (+13 more)

### Community 12 - "Defense Presentation Slides"
Cohesion: 0.10
Nodes (21): 2. Slide Deck Outline (15–20 slides), Slide 10: The Core Four Disparity Metrics, Slide 11: Heterogeneous Backend Harmonization, Slide 12: Statistical Safeguards — Three-Tier Inferential Defense, Slide 13: Explainability — Targeted Proxy Evidence Analysis, Slide 14: Regulatory Traceability Mapping, Slide 15: Report Output — Self-Contained Offline HTML, Slide 16: Work Breakdown & Schedule (+13 more)

### Community 13 - "Research Runner Setup"
Cohesion: 0.14
Nodes (13): After All 20 Complete, Checklist, Implementation Order, 🚀 Parallel Research Runner Guide — 20 Claude Desktop Instances, 🔴 Phase 1 — Critical (read these first), 🟡 Phase 2 — Medium (read these second), 🟢 Phase 3 — Low (read last), Priority Order (if reviewing as they finish) (+5 more)

### Community 14 - "Project Audit and Tasks"
Cohesion: 0.04
Nodes (43): Master Task Division (BiasAperture-AT.md), Fairness Backends, 1. Executive Summary & Objectives, 2. Audit Findings & Resolution Matrix, 3.1 Native AIF360 Backend (`src/bias_aperture/fairness/backends.py`), 3.2 Additive Shapley Surrogate Explainability (`src/bias_aperture/explainability.py`), 3.3 CLI Integration (`src/bias_aperture/cli.py`), 3.4 Package & Dependency Alignment (`pyproject.toml`, `uv.lock`) (+35 more)

### Community 15 - "Literature Review Matrix"
Cohesion: 0.15
Nodes (13): 1. Buolamwini & Gebru (2018) — *Gender Shades: Intersectional Accuracy Disparities in Commercial Gender Classification*, 2. Kärkkäinen & Joo (2021) — *FairFace: Face Attribute Dataset for Balanced Race, Gender, and Age*, 2. The 4-Layer Conceptual Reading Matrix, 3. Hardt, Price, & Srebro (2016) — *Equality of Opportunity in Supervised Learning*, 4. Watkins, McKenna, & Chen (2022) — *The Four-Fifths Rule is Not Disparate Impact*, 5. Efron (1987) — *Better Bootstrap Confidence Intervals (BCa)*, 6. Bilodeau et al. (2022) — *Impossibility Theorems for Feature Attribution*, 7. Dehdashtian, Wang, & Boddeti (2024) — *Fairness and Bias Mitigation in Computer Vision: A Survey* (+5 more)

### Community 16 - "Executive Project Synthesis"
Cohesion: 0.17
Nodes (12): 1. Executive Summary & Vision, 2. The Five Operating Modules, 3. The 20-Track Research Sprint: Key Findings, 4.1. Reproducible Competitive Search Protocol, 4. Defensible Novelty & Competitor Positioning, 5. Regulatory Alignment: EU AI Act & NIST AI RMF, 7. Current Project State & Next Steps, BiasAperture — Research Sprint: High-Level Executive Synthesis (+4 more)

### Community 17 - "Backend Harmonization Tests"
Cohesion: 0.20
Nodes (9): Backend Harmonization & Edge-Case Mathematical Tests (R-005, R-006, R-008,…, R-005: Proves that worst-case max-gap (Hardt et al. / Fairlearn) and average-…, R-006: AIF360 returns signed difference (TPR_unprivileged - TPR_privileged),…, R-008: Verifies that evaluating metrics without pre-filtering small subgroups…, R-010: Tests the domain-specific policy conventions for zero denominators in…, test_disparate_impact_ratio_zero_denominator_contract(), test_equal_opportunity_signed_vs_unsigned_adapter(), test_equalized_odds_max_vs_mean_divergence() (+1 more)

### Community 18 - "Mock Testing Data"
Cohesion: 0.29
Nodes (7): mock_core_four_results(), fixture, MetricResult, SubjectRecord, Provide a diverse list of SubjectRecords across race and gender categories., Provide a valid mock dictionary of Core Four MetricResults., sample_subject_records()

### Community 19 - "Dataset Profiling Scripts"
Cohesion: 0.39
Nodes (7): explore_split(), main(), _parse_bool(), print_report(), Path, scripts/explore_fairface.py — exploration of the raw FairFace label CSVs…, SplitReport

### Community 20 - "Data Ingestion Pipeline"
Cohesion: 0.06
Nodes (61): Counter, DataFrame, Enum, BiasAperture Command-Line Interface (WP5 / System Orchestration). Wires…, DataIngestionPipeline, IngestionConfig, IngestionResult, OvRTransformer (+53 more)

### Community 21 - "Technical Sprint Specifications"
Cohesion: 0.25
Nodes (8): 1.0.1. Multi-Class One-vs-Rest (OvR) Evaluation Policy, 1.0. Audited Target Configurations, 1. Formal Semantics of Audited Targets & Demographic Attributes, 3.1. ResNet-34 Multi-Task Head & Tensor Slicing, 3.2. Preprocessing & Alignment Pipeline, 3. FairFace Architecture & Preprocessing Deep Dive, 4. Resolution Guide for the 21 Cross-Track Conflicts, BiasAperture — Research Sprint: Low-Level Technical Specification

### Community 22 - "Novelty and Integration Defense"
Cohesion: 0.14
Nodes (13): 1. **Schema Bridge**, 2. **Regulatory Mapping**, 3. **Explainability Envelope**, 4. **Repeated Auditability**, BiasAperture: Integration as Innovation, Defense Memo — Why Integrating Existing Tools is Novel Here, How to Defend This to an Examiner, Key Insight from Your Conversation (+5 more)

### Community 23 - "Integration Innovation Memo"
Cohesion: 0.14
Nodes (13): 1. **Schema Bridge**, 2. **Regulatory Mapping**, 3. **Explainability Envelope**, 4. **Repeated Auditability**, BiasAperture: Integration as Innovation, Defense Memo — Why Integrating Existing Tools is Novel Here, How to Defend This to an Examiner, Key Insight from Your Conversation (+5 more)

### Community 24 - "Statistical Rigor Engine"
Cohesion: 0.22
Nodes (12): compute_contingency_chi2(), compute_stratified_bootstrap_ci(), holm_bonferroni_correction(), ndarray, Statistical rigor engine (WP4 / Stream C). Implements statistical hypothesis…, Compute 95% stratified BCa bootstrap confidence interval (R-009). Resampling is…, Compute Pearson's chi-squared test of independence across demographic groups.…, Apply Holm-Bonferroni step-down procedure for FWER control (R-011). Given M… (+4 more)

### Community 25 - "Metric Definition Resolutions"
Cohesion: 0.29
Nodes (8): 1.1. Demographic Parity Difference (DPD), 1.2. Equalized Odds Difference (EOD) — Resolving Definitional Divergence, 1.3. Equal Opportunity Difference (EOP) — Resolving Sign Mismatch, 1.4. Disparate Impact Ratio (DIR) & Edge Cases, 2. Mathematical Fairness Formulations & Backend Harmonization, The Divergence Found in Research (Track 14), The Divergence Found in Research (Tracks 09, 10, 14), The Locked Resolution

### Community 26 - "Research Claim Ledger"
Cohesion: 0.29
Nodes (6): 1. Verification Lifecycle, 2. Master Research Claim Register, 3. Invalidated Claims (Research Failures & Refutations), 4. Claim Verification Status Summary, Academic Audit Statement, BiasAperture — Research Claim Ledger

### Community 27 - "Dataset Exploration Reports"
Cohesion: 0.17
Nodes (11): 1. FairFace, 2. UTKFace, 3. Data Integrity Decision — RESOLVED, 4. Open Decision — NOT YET RESOLVED, Data Exploration Report — FairFace & UTKFace, Distributions (combined view, valid rows), Distributions (valid files), Result — clean, after exclusion (+3 more)

### Community 28 - "Model Interface Layer"
Cohesion: 0.05
Nodes (48): InProcessInterface, ModelInterface, PredictionsFileInterface, ABC, Any, Path, SubjectRecord, ModelInterface — FR-002 (Dual-Mode Model Interface), WBS 1.2. "The system shall… (+40 more)

### Community 29 - "Explainability Engine"
Cohesion: 0.08
Nodes (35): MetricResult, One row of the detection engine's output (FR-003/FR-004), the shape Stream B's…, compute_ita(), ExplanationResult, MetricResult, Path, SubjectRecord, Explainability and visual proxy attribution module (WP4/WP5 / Stream D).… (+27 more)

### Community 30 - "Compliance and Standards"
Cohesion: 0.25
Nodes (9): HTML Report Generator, BiasAperture, EU AI Act, FairFace Benchmark, NFR-001 (Significance), NFR-002 (Uncertainty), NFR-003 (Sample Size Guard), NIST AI RMF (+1 more)

### Community 31 - "Assistant Coding Standards"
Cohesion: 0.18
Nodes (10): 1. Schema Invariants (M1 Lock — `src/bias_aperture/schema.py`), 2. Statistical & Safety Guards, Active Workstreams & Branch Mapping, Architecture & Locked Contracts, CLAUDE.md — Assistant Instructions for BiasAperture, Coding Standards, Commands & Workflows, Environment & Testing (+2 more)

### Community 32 - "Project Architecture Guidelines"
Cohesion: 0.18
Nodes (10): 1. Schema Invariants (M1 Lock — `src/bias_aperture/schema.py`), 2. Statistical & Safety Guards, Active Workstreams & Branch Mapping, Architecture & Locked Contracts, CLAUDE.md — Assistant Instructions for BiasAperture, Coding Standards, Commands & Workflows, Environment & Testing (+2 more)

### Community 33 - "Repository Documentation"
Cohesion: 0.18
Nodes (10): Abstract, BiasAperture, Branching & Workstreams, Building the Report, License, Local Git Workflow & Auto-Sync (`sync.ps1`), Project Progress & Roadmap, Python Development, Testing & Code Style (+2 more)

### Community 34 - "Fairness Engine Synthesis"
Cohesion: 0.18
Nodes (10): Bootstrap CI (Track 11) — locked implementation approach, Chi-squared testing (Track 12) — locked implementation approach, Cross-cutting architectural flag (Tracks 11, 13, 14 all raise the same underlying question independently), Disparate Impact Ratio (Track 13), Equalized Odds / Equal Opportunity (Track 14 — empirically cross-validated, not just theoretical), Multi-group handling — a real architecture asymmetry, not just an API-style difference, n≥30 guard — computed once, shared, enforced before any library call, Native library coverage — both backends need manual work for the same two metrics (+2 more)

### Community 35 - "Weekly Progress Report WK3"
Cohesion: 0.18
Nodes (10): 1. Executive Summary & Objectives, 2. Work Packages & Milestone Mapping, 3.1 Functional Requirements & Regulatory Mapping (`FR-001`–`FR-005`), 3.2 System Architecture & Flow Design, 3.3 Engineering Standards & Package Scaffolding, 3. Detailed Accomplishments & Technical Highlights, 4. Git Commit Provenance (Week 3), 5. Next Steps & Lookahead (Week 4) (+2 more)

### Community 36 - "Architectural Design Specs"
Cohesion: 0.33
Nodes (3): 1. System Topology & Component Overview, 3. Comprehensive Testing & Verification Architecture, BiasAperture — Research Sprint: Mid-Level Architectural Design

### Community 37 - "Weekly Progress Report WK4"
Cohesion: 0.33
Nodes (6): 1. Executive Summary & Objectives, 2. Work Packages & Milestone Mapping, 4. Git Commit Provenance (Week 4), 5. Master TO DOs & Remaining Roadmap, BiasAperture — Weekly Project Report (WK4), Key Objectives

### Community 38 - "Weekly Progress Report WK1"
Cohesion: 0.18
Nodes (10): 1. Executive Summary & Objectives, 2. Work Packages & Milestone Mapping, 3.1 Custom LaTeX Document Class & Optimization (`report/at_fuse_aif.cls`), 3.2 VS Code LaTeX Development Recipe, 3.3 Multi-Remote Git Synchronization Baseline (`sync.ps1`), 3. Detailed Accomplishments & Technical Highlights, 4. Git Commit Provenance (Week 1), 5. Next Steps & Lookahead (Week 2) (+2 more)

### Community 39 - "Weekly Progress Report WK2"
Cohesion: 0.20
Nodes (9): 1. Executive Summary & Objectives, 2. Work Packages & Milestone Mapping, 3.1 Milestone M1 Schema Contract Formulation (`docs/schema-lock-m1.md`), 3.2 Literature Review Matrix Scaffolding, 3. Detailed Accomplishments & Technical Highlights, 4. Git Commit Provenance (Week 2), 5. Next Steps & Lookahead (Week 3), BiasAperture — Weekly Project Report (WK2) (+1 more)

### Community 40 - "Technical Accomplishments Summary"
Cohesion: 0.33
Nodes (6): 3.1 20-Track Parallel Research Sprint & 3-Level Syntheses, 3.2 Dataset Profiling & Empirical Discoveries, 3.3 Native AIF360 Backend Harmonization (`src/bias_aperture/fairness/backends.py`), 3.4 Exact Additive Shapley Surrogate Explainability (`src/bias_aperture/explainability.py`), 3.5 Test Suite & Code Quality (55/55 Tests Passing), 3. Detailed Accomplishments & Technical Highlights

### Community 41 - "System Context Overview"
Cohesion: 0.22
Nodes (8): BiasAperture — System Context (paste this first), Core Four Disparity Metrics, Dual-Backend Architecture, Locked Schema (DO NOT modify), Output Schema (MetricResult dataclass), Project Scope, Statistical Requirements, Tech Stack

### Community 42 - "Pre-Defense Reading Guide"
Cohesion: 0.67
Nodes (3): 1. The Core Reasoning Chain, 4. Mental Hierarchy: Meaning $\to$ Justification $\to$ Limitation $\to$ Number, BiasAperture — Pre-Proposal Defense Reading Guide

### Community 43 - "Project Management Assets"
Cohesion: 0.22
Nodes (9): BiasAperture Proposal Report, High-Level Architecture Diagram, Project Gantt Chart, System Workflow Flowchart, BiasAperture-AT Project Log, BiasAperture Novelty Defense Memo, CLAUDE.md Assistant Instructions, Literature Review Matrix (+1 more)

### Community 44 - "Research Stream Context"
Cohesion: 0.22
Nodes (8): BiasAperture — System Context (paste this first), Core Four Disparity Metrics, Dual-Backend Architecture, Locked Schema (DO NOT modify), Output Schema (MetricResult dataclass), Project Scope, Statistical Requirements, Tech Stack

### Community 45 - "Project Scope Invariants"
Cohesion: 0.67
Nodes (3): 6. Scope Invariants & Descoping Strategy (Cut-List), Formal Cut-List (Ordered by Drop Priority), What BiasAperture Will NEVER Do

### Community 46 - "Schema Lock Specifications"
Cohesion: 0.25
Nodes (7): Change policy, Classifier baseline, Constants locked with the schema, Detection engine output schema (FR-003/FR-004), Internal schema (FR-001), Schema Lock — Milestone M1 (WP1), What this unblocks

### Community 48 - "Data Governance Policy"
Cohesion: 0.25
Nodes (7): 1.1. Ingestion Restrictions, 1. Dataset Provenance & Licensing, 2.1. Statutory Justification for Bias Auditing, 2. Special-Category Demographic Data & Regulatory Safeguards, 3. Storage, Retention & Security Policy, 4. Researcher Ethics & Responsibilities, BiasAperture — Data Governance & Privacy Protocol

### Community 49 - "Internal Schema Contracts"
Cohesion: 0.25
Nodes (7): Change policy, Classifier baseline, Constants locked with the schema, Detection engine output schema (FR-003/FR-004), Internal schema (FR-001), Schema Lock — Milestone M1 (WP1), What this unblocks

### Community 50 - "Git Sync Utilities"
Cohesion: 0.32
Nodes (3): Initialize-Remotes(), Push-AllRemotes(), Sync-AllOriginBranches()

### Community 51 - "Report Generation Synthesis"
Cohesion: 0.29
Nodes (6): Architecture (Track 05 — ready to implement), EU AI Act Article 10 mapping (Track 08 — sub-clause level, ready to consume), FairFace Datasheet (Track 07 — Gebru et al. 2018/2021 framework, drafted), Model Cards mapping (Track 06 — Mitchell et al. 2019, 9 sections), Open flags requiring owner decision, Stream B Synthesis — Report Generation (Tracks 05–08)

### Community 52 - "Explainability Module Synthesis"
Cohesion: 0.29
Nodes (6): Open flags requiring owner decision, Proxy variable detection methodology (Track 16 — builds on Track 15's SHAP primitives), Real limitations — must be in the report, not just the code (Track 16 §5), SHAP variant selection (Track 15), Stream D Synthesis — Explainability (Tracks 15–16), Trigger point and interface (Track 15)

### Community 53 - "Developer Agent Guidelines"
Cohesion: 0.33
Nodes (5): 1. Non-Negotiable Project Constraints, 2. Directory Layout & Module Ownership, 3. Build & Test Commands, 4. Git & Branching Strategy, AGENT.md — Developer & AI Agent Guidelines

### Community 54 - "AI Agent Instructions"
Cohesion: 0.33
Nodes (5): 1. Non-Negotiable Project Constraints, 2. Directory Layout & Module Ownership, 3. Build & Test Commands, 4. Git & Branching Strategy, AGENT.md — Developer & AI Agent Guidelines

### Community 55 - "Coding Operating Invariants"
Cohesion: 0.33
Nodes (5): ANTIGRAVITY.md — Google Antigravity & Gemini Coding Guidelines, Key Context & Metadata, Mission & Purpose, Operating Invariants for Antigravity, Role & Task Ownership Allocation

### Community 56 - "Pull Request Template"
Cohesion: 0.33
Nodes (5): 🛠️ Changes Made, 📋 Checklist, 📌 Purpose, 🔗 Related Issues, 🧪 Testing & Verification

### Community 57 - "Cross-Track Conflict Log"
Cohesion: 0.33
Nodes (5): Blocking — needed before WP4 implementation starts, Cross-Track Conflict & Discrepancy Log — BiasAperture 20-Track Research Sprint, Documentation/data corrections needed (not architectural, but currently wrong in project docs), Needs owner decision — not blocking implementation start, but unresolved, Process notes (not content conflicts — flagging for the record)

### Community 58 - "Architecture Testing Synthesis"
Cohesion: 0.33
Nodes (5): `fairness/base.py` design (Track 17 — code delivered, ready for review), Open flags requiring owner decision, Stream E Synthesis — Architecture & Testing (Tracks 17–18), Test suite architecture (Track 18 — grounded against live repo state), Track/field-name discrepancies Track 17 caught and worked around

### Community 59 - "Monthly Progress Index"
Cohesion: 0.29
Nodes (6): 1. Executive Summary, 2. Weekly Reports Breakdown, 3. High-Level Monthly Achievements, 4. Master TO DOs & Remaining Roadmap, 5. Related Master Documentation, BiasAperture — Monthly Progress & Weekly Reports Index

### Community 61 - "Project Report Index"
Cohesion: 0.24
Nodes (6): Weekly Report WK1 (2026-08-07), Weekly Report WK2 (2026-08-14), Weekly Report WK3 (2026-08-21), Monthly Progress & Weekly Reports Index (2026-08-31), Weekly Report WK4 (2026-08-31), Research Claim Ledger

### Community 62 - "Backend Consensus Verifier"
Cohesion: 0.40
Nodes (4): DivergenceAlert, MetricResult, Record of mathematical divergence between backends., Execute all backends, verify consensus, and return harmonized results.…

### Community 63 - "FairFace Dataset Research"
Cohesion: 0.40
Nodes (4): Track 01: FairFace Dataset Deep-Dive, Stream A Synthesis: Data Pipeline, Instructions, Prompt

### Community 64 - "Data Pipeline Synthesis"
Cohesion: 0.40
Nodes (4): Locked findings (verified against primary source, safe to build on), Open flags requiring owner decision (not resolved by any track), Stream A Synthesis — Data Pipeline (Tracks 01–04), Validation architecture (Track 03 — ready to implement against Track 01/04's confirmed column names)

### Community 65 - "Regulatory Mapping Synthesis"
Cohesion: 0.40
Nodes (4): Competitor analysis (Track 20 — 7 tools surveyed, live-verified), NIST AI RMF mapping (Track 19), Open flags requiring owner decision, Stream F Synthesis — Defense & Regulatory (Tracks 19–20)

### Community 68 - "Data Directory Structure"
Cohesion: 0.50
Nodes (3): Data Directory Layout, Directory Structure, Sourcing the FairFace Benchmark (FR-001)

### Community 69 - "Literature Review Templates"
Cohesion: 0.50
Nodes (4): AIF Literature Review Guidelines, AIF Project Requirement Templates, BiasAperture Literature Review, BiasAperture User Requirement Document

### Community 70 - "Dataset and Schema Benchmarks"
Cohesion: 0.67
Nodes (4): Gender Shades: Intersectional Accuracy Disparities in Commercial Gender Classification, FairFace: Face Attribute Dataset for Balanced Race, Gender, and Age for Bias Measurement and Mitigation, FairFace Pretrained ResNet-34, BiasAperture Internal Schema

### Community 71 - "Fairness Theory and Constants"
Cohesion: 0.50
Nodes (4): Equality of Opportunity in Supervised Learning, The Four-Fifths Rule is Not Disparate Impact: A Woeful Tale of Epistemic Trespassing in Algorithmic Fairness, Schema Constants, Detection Engine Output Schema

### Community 72 - "UTKFace Comparison Research"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 02 — UTKFace Comparison & Risk Assessment

### Community 73 - "Data Validation Patterns"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 03 — Pandas Data Validation Patterns

### Community 74 - "Inference Source Analysis"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 04 — FairFace predict.py Source Code Analysis

### Community 75 - "Jinja2 Report Templates"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 05 — Jinja2 HTML Report Template Patterns

### Community 76 - "Model Card Specifications"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 06 — Model Cards Specification Deep-Dive

### Community 77 - "Dataset Datasheet Drafts"
Cohesion: 0.83
Nodes (3): Instructions, Prompt, Track 07 — FairFace Datasheet Draft

### Community 78 - "EU AI Act Mapping"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 08 — EU AI Act Article 10 Regulatory Mapping

### Community 79 - "Fairlearn API Integration"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 09 — Fairlearn API — MetricFrame & Core Four

### Community 80 - "AIF360 API Integration"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 10 — AIF360 API — BinaryLabelDataset & Cross-Validation

### Community 81 - "Bootstrap CI Implementation"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 11 — Bootstrap Confidence Intervals

### Community 82 - "Chi-Squared Significance Testing"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 12 — Chi-Squared Significance Testing

### Community 83 - "Disparate Impact Analysis"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 13 — Disparate Impact Ratio — Implementation & Legal Context

### Community 84 - "Equalized Odds Theory"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 14 — Equalized Odds & Equal Opportunity — Theory to Code

### Community 85 - "SHAP Integration Research"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 15 — SHAP for Image Classifiers

### Community 86 - "Proxy Variable Detection"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 16 — Proxy Variable Detection via SHAP

### Community 87 - "Strategy Design Pattern"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 17 — Strategy Pattern for Dual Fairness Backends

### Community 88 - "Pytest Metric Patterns"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 18 — Pytest Testing Patterns for Fairness Metrics

### Community 89 - "NIST RMF Mapping"
Cohesion: 0.50
Nodes (3): Instructions, Prompt, Track 19 — NIST AI RMF Detailed Mapping

### Community 90 - "Competitor Tool Analysis"
Cohesion: 0.83
Nodes (3): Instructions, Prompt, Track 20 — Competitor Deep Analysis

### Community 91 - "Development Tooling"
Cohesion: 0.67
Nodes (3): Sync Script, UV Tool Execution, Ruff Pre-commit

### Community 92 - "System Specification Levels"
Cohesion: 0.67
Nodes (3): High Level Synthesis, Low Level Specification, Mid Level Architecture

### Community 93 - "Regulatory Defense Synthesis"
Cohesion: 0.67
Nodes (3): NIST AI RMF Detailed Mapping, Competitor Deep Analysis, Stream F Synthesis (Defense & Regulatory)

## Knowledge Gaps
- **482 isolated node(s):** `2.3. Module 3: Statistical Rigor Engine (`fairness/statistics.py`)`, `2.4. Module 4: Targeted Explainability & Proxy Detection (`explainability.py`)`, `2.5. Module 5: Compliance Report Generation (`report/`)`, `Ingestion Contracts & Patterns`, `Shared Base Architecture (`fairness/base.py`)` (+477 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 691 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SubjectRecord` connect `Model Interface Layer` to `Fairness Backend Orchestration`, `Base Fairness Classes`, `Mock Testing Data`, `Data Ingestion Pipeline`, `Explainability Engine`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `Monthly Progress & Weekly Reports Index (2026-08-31)` connect `Project Report Index` to `Project Audit and Tasks`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `ShapExplainerEngine` connect `Explainability Engine` to `CLI and Report Generation`, `Data Ingestion Pipeline`, `Model Interface Layer`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `DataIngestionPipeline` (e.g. with `SubjectRecord` and `test_cohort_profile_contingency_support()`) actually correct?**
  _`DataIngestionPipeline` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `SubjectRecord` (e.g. with `InProcessInterface` and `ModelInterface`) actually correct?**
  _`SubjectRecord` has 22 INFERRED edges - model-reasoned connections that need verification._
- **What connects `2.3. Module 3: Statistical Rigor Engine (`fairness/statistics.py`)`, `2.4. Module 4: Targeted Explainability & Proxy Detection (`explainability.py`)`, `2.5. Module 5: Compliance Report Generation (`report/`)` to the rest of the system?**
  _482 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `CLI and Report Generation` be split into smaller, more focused modules?**
  _Cohesion score 0.0796221322537112 - nodes in this community are weakly interconnected._