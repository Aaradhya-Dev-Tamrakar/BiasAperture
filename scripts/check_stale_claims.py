#!/usr/bin/env python3
"""
check_stale_claims.py — pre-commit guard against stale/overstated claims
in BiasAperture's .md/.tex documentation.

Guards three specific undersell/oversell drift patterns catalogued in
research/results/DISCREPANCY_LEDGER.md:

  1. Bare FairFace image counts (108,501 / 108501, including LaTeX
     `108{,}501` spacing groups) cited without a "released" /
     "pre-discard" / "pre-annotation" qualifier nearby. 108,501 is the
     pre-discard/pre-annotation total; 97,698 is the actual released
     count on disk (ledger §A).
  2. UTKFace mentioned without a nearby "cut"/"removed"/"dropped"/
     "excluded" qualifier. "Secondary" alone is NOT an acceptable
     substitute — the ledger explicitly names "secondary benchmark"
     framing itself as the undersell pattern, since it implies UTKFace
     is still an active dataset rather than cut per Cut-List #2
     (ledger §A). "Removed"/"dropped"/"excluded" are accepted synonyms
     for "cut" itself (same disposition, different verb) — this is not
     a loosening of the guard's intent, since all four words assert the
     same formally-cut status "secondary" fails to assert.
  3. SHAP mentioned without a nearby "surrogate" / "deferred" /
     "fallback" qualifier. Current implementation attempts SHAP and
     falls back to demographic-dummy surrogate attribution on failure
     (ledger §B) — SHAP must not be described as the unqualified,
     operative mechanism.

Word-proximity ("~15 words") is measured within the same paragraph
(blank-line-delimited block), not the whole file, so an unrelated
qualifier many paragraphs away cannot silently clear a violation.

Exit status: 1 if any violation is found (blocks the commit), 0 if
clean. Intended to run as a `repo: local` pre-commit hook against
staged `.md`/`.tex` files (see .pre-commit-config.yaml).
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass

# "~15 words" per spec; 16 covers the tightest real known-clean case
# (specs/07-explainability.md:9, SHAP..."are deferred" spans a 16-token
# gap once list/adjective clauses are counted) without materially
# loosening the guard elsewhere.
WINDOW = 16

WORD_RE = re.compile(r"[\w'-]+")
PARA_SPLIT_RE = re.compile(r"\n[ \t]*\n")


@dataclass(frozen=True)
class Rule:
    name: str
    target: re.Pattern[str]
    qualifiers: tuple[re.Pattern[str], ...]
    message: str


RULES: tuple[Rule, ...] = (
    Rule(
        name="bare-108501",
        # matches 108,501 / 108501 / LaTeX 108{,}501 spacing groups
        target=re.compile(r"\b108[\s{},]*501\b"),
        qualifiers=(
            re.compile(r"\breleased\b", re.IGNORECASE),
            re.compile(r"\bpre-discard\b", re.IGNORECASE),
            re.compile(r"\bpre-annotation\b", re.IGNORECASE),
        ),
        message=(
            "bare 108,501/108501 without 'released'/'pre-discard'/"
            "'pre-annotation' within ~15 words — distinguish the "
            "pre-discard total from the 97,698 released/on-disk count "
            "(DISCREPANCY_LEDGER.md §A)"
        ),
    ),
    Rule(
        name="utkface-not-cut",
        target=re.compile(r"\bUTKFace\b", re.IGNORECASE),
        qualifiers=(
            re.compile(r"\bcut\b", re.IGNORECASE),
            re.compile(r"\bremoved?\b", re.IGNORECASE),
            re.compile(r"\bdrop(?:s|ped|ping)?\b", re.IGNORECASE),
            re.compile(r"\bexcluded\b", re.IGNORECASE),
        ),
        message=(
            "UTKFace without 'cut'/'removed'/'dropped'/'excluded' within "
            "~15 words — 'secondary' alone does not satisfy this guard, "
            "it IS the undersell pattern being caught (UTKFace was cut "
            "per Cut-List #2, DISCREPANCY_LEDGER.md §A)"
        ),
    ),
    Rule(
        name="shap-not-qualified",
        target=re.compile(r"\bSHAP\b"),
        qualifiers=(
            re.compile(r"\bsurrogate\b", re.IGNORECASE),
            re.compile(r"\bdeferred\b", re.IGNORECASE),
            re.compile(r"\bfallback\b", re.IGNORECASE),
        ),
        message=(
            "SHAP without 'surrogate'/'deferred'/'fallback' within "
            "~15 words — current implementation falls back to "
            "demographic-dummy surrogate attribution, not real SHAP "
            "(DISCREPANCY_LEDGER.md §B)"
        ),
    ),
)


def _paragraphs_with_offset(text: str) -> list[tuple[int, str]]:
    """Split text into (start_offset, paragraph_text) pairs on blank lines."""
    paras: list[tuple[int, str]] = []
    pos = 0
    for para in PARA_SPLIT_RE.split(text):
        idx = text.index(para, pos)
        paras.append((idx, para))
        pos = idx + len(para)
    return paras


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def check_text(text: str) -> list[tuple[int, str, str]]:
    """Return (line_number, rule_name, message) for each violation."""
    violations: list[tuple[int, str, str]] = []
    for para_start, para in _paragraphs_with_offset(text):
        tokens = list(WORD_RE.finditer(para))
        for rule in RULES:
            for m in rule.target.finditer(para):
                tok_idx = next(
                    (i for i, t in enumerate(tokens) if t.start() >= m.start()),
                    len(tokens) - 1,
                )
                lo = max(0, tok_idx - WINDOW)
                hi = min(len(tokens), tok_idx + WINDOW + 1)
                if hi <= lo:
                    window_text = para[m.start() : m.end()]
                else:
                    window_text = para[tokens[lo].start() : tokens[hi - 1].end()]
                if not any(q.search(window_text) for q in rule.qualifiers):
                    abs_offset = para_start + m.start()
                    violations.append(
                        (_line_number(text, abs_offset), rule.name, rule.message)
                    )
    return violations


def main(argv: list[str]) -> int:
    paths = [p for p in argv if p.endswith((".md", ".tex"))]
    exit_code = 0
    for path in paths:
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"check_stale_claims: cannot read {path}: {e}", file=sys.stderr)
            exit_code = 1
            continue
        for line_no, rule_name, message in check_text(text):
            print(f"{path}:{line_no}: [{rule_name}] {message}")
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
