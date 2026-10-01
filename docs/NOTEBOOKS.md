# NotebookLM & Gemini Knowledge Bases

This document catalogues the Google NotebookLM and Gemini workspaces maintained for the **BiasAperture** research and development lifecycle. These knowledge bases provide grounded literature synthesis, specification cross-referencing, and oral defense preparation.

---

## Workspace Directory

| Workspace | Notebook ID | Direct Link | Grounding Scope & Purpose |
| :--- | :--- | :--- | :--- |
| **BiasAperture — Strategy & Foundations** | `99bee3c6-07ed-4ff0-8ac8-0027b18ad06a` | [Open Notebook](https://notebook.google.com/notebook/99bee3c6-07ed-4ff0-8ac8-0027b18ad06a) | **Master Conceptual Workspace**: Primary research corpus, fellowship requirements, architectural decisions, research sprint tracks (Tracks 01–20), and system design notes. |
| **BiasAperture — References** | `bbac9235-404b-4c39-a2a4-1f30069af30b` | [Open Notebook](https://notebook.google.com/notebook/bbac9235-404b-4c39-a2a4-1f30069af30b) | **Academic Foundations & Literature Review**: Full-text peer-reviewed papers and legal frameworks corresponding to `report/references.bib` and `docs/literature-review-matrix.md` (e.g., *Gender Shades*, *FairFace*, *Model Cards*, *Datasheets*, Equal Opportunity, Four-Fifths Rule, SHAP surrogate foundations, and the EU AI Act). |
| **BiasAperture — Source & Specs** | `928b5ed7-1353-4cb3-a1ce-b215e80b7db4` | [Open Notebook](https://notebook.google.com/notebook/928b5ed7-1353-4cb3-a1ce-b215e80b7db4) | **Ground-Truth Implementation Layer**: Technical specifications (`specs/00`–`11`), core production source code (`src/bias_aperture/`), verification test suites, and empirical findings (`research/results/`). |
| **BiasAperture — Repo State** | `6e9505f0-2d5c-4655-8bc7-9f97cf9620b9` | [Open Notebook](https://notebook.google.com/notebook/6e9505f0-2d5c-4655-8bc7-9f97cf9620b9) | **Synthesis & Defense Layer**: Developer logs (`dev-logs/`), weekly milestone reports (WK1–WK5), proposal defense master dossiers, discrepancy ledgers, and repository verification logs. |

---

## Related & Personal Workspaces

| Workspace | Notebook ID | Direct Link | Scope |
| :--- | :--- | :--- | :--- |
| **Personal Workspace** | `95a79d26-2f87-42cd-8cb9-8361a1e56059` | [Open Notebook](https://notebook.google.com/notebook/95a79d26-2f87-42cd-8cb9-8361a1e56059) | Lead engineer workspace and research journal. |
| **SPARK** | `2c00f5a4-98dc-4783-96d1-3682fa3cb516` | [Open Notebook](https://notebook.google.com/notebook/2c00f5a4-98dc-4783-96d1-3682fa3cb516) | Shared cross-project knowledge repository. |

---

## MCP & Tooling Integration

When interacting with MCP tools (`super-nlm` or `notebooklm`), use the corresponding Notebook ID to query or ground outputs:

```json
{
  "notebook_id": "99bee3c6-07ed-4ff0-8ac8-0027b18ad06a",
  "query": "Explain the rationale for why UTKFace was cut from runtime evaluation."
}
```
