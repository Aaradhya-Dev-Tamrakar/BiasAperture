"""Declarative YAML configuration loader and validation for BiasAperture audits."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

__all__ = [
    "AuditConfig",
    "VALID_BACKENDS",
    "VALID_FORMATS",
    "VALID_PROTECTED_ATTRS",
    "load_audit_config",
]

VALID_PROTECTED_ATTRS: set[str] = {"race", "gender", "age", "race_gender"}
VALID_BACKENDS: set[str] = {"dual", "fairlearn", "aif360"}
VALID_FORMATS: set[str] = {"html", "pdf", "both"}


@dataclass(slots=True)
class AuditConfig:
    """Validated structured audit configuration."""

    predictions_file: Path | None = None
    true_label_col: str = "true_label"
    predicted_label_col: str = "predicted_label"
    race_col: str = "race"
    gender_col: str = "gender"
    age_col: str = "age"
    protected_attr: str = "race"
    backend: str = "dual"
    bca_resamples: int = 1000
    explain: bool = True
    output_report: Path = field(
        default_factory=lambda: Path("bias_aperture_report.html")
    )
    format: str | None = None
    model_name: str = "FairFace ResNet-34 Multi-Task Classifier"
    dataset_name: str = "FairFace Benchmark Dataset"
    model_description: str | None = None

    @classmethod
    def from_yaml(cls, path: Path | str) -> AuditConfig:
        """Instantiate an AuditConfig directly from a YAML configuration file."""
        cfg_dict = load_audit_config(path)
        return cls(**cfg_dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary suitable for parser defaults and pipeline execution."""
        data: dict[str, Any] = {}
        for k in self.__slots__:
            val = getattr(self, k)
            if val is not None:
                data[k] = val
        return data


def load_audit_config(config_path: Path | str) -> dict[str, Any]:
    """Load and validate an audit YAML configuration file.

    Supports both flat key-value configurations and structured nested sections
    ('audit' and 'report').

    Parameters
    ----------
    config_path : Path | str
        Path to YAML configuration file.

    Returns
    -------
    dict[str, Any]
        Flattened and validated dictionary of configuration parameters.

    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist.
    ValueError
        If the YAML content is malformed or violates schema invariants.
    """
    path = Path(config_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Audit configuration file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise ValueError(
            f"Malformed YAML in configuration file '{path}': {exc}"
        ) from exc

    if not isinstance(raw, dict):
        raise ValueError(
            f"Invalid configuration root in '{path}': expected mapping, "
            f"got {type(raw).__name__}"
        )

    # Flatten nested sections ('audit' and 'report') if present
    flattened: dict[str, Any] = {}
    for section_key in ("audit", "report"):
        sec = raw.get(section_key)
        if isinstance(sec, dict):
            flattened.update(sec)

    # Merge top-level keys (top-level overrides nested section collisions)
    for k, v in raw.items():
        if k not in ("audit", "report"):
            flattened[k] = v

    # Validate and normalize
    validated: dict[str, Any] = {}

    if "predictions_file" in flattened and flattened["predictions_file"]:
        pred_p = Path(flattened["predictions_file"])
        if not pred_p.is_absolute():
            # Check relative to config file directory first, then CWD
            cfg_dir = path.parent
            if (cfg_dir / pred_p).exists():
                pred_p = (cfg_dir / pred_p).resolve()
            else:
                pred_p = (Path.cwd() / pred_p).resolve()
        validated["predictions_file"] = pred_p

    if "output_report" in flattened and flattened["output_report"]:
        validated["output_report"] = Path(flattened["output_report"])

    if "format" in flattened and flattened["format"] is not None:
        fmt = str(flattened["format"]).strip().lower()
        if fmt not in VALID_FORMATS:
            raise ValueError(
                f"Invalid 'format' in configuration: '{fmt}'. "
                f"Must be one of {sorted(VALID_FORMATS)}."
            )
        validated["format"] = fmt

    if "protected_attr" in flattened:
        attr = str(flattened["protected_attr"]).strip()
        if attr not in VALID_PROTECTED_ATTRS:
            raise ValueError(
                f"Invalid 'protected_attr' in configuration: '{attr}'. "
                f"Must be one of {sorted(VALID_PROTECTED_ATTRS)}."
            )
        validated["protected_attr"] = attr

    if "backend" in flattened:
        bk = str(flattened["backend"]).strip().lower()
        if bk not in VALID_BACKENDS:
            raise ValueError(
                f"Invalid 'backend' in configuration: '{bk}'. "
                f"Must be one of {sorted(VALID_BACKENDS)}."
            )
        validated["backend"] = bk

    if "bca_resamples" in flattened:
        resamples = int(flattened["bca_resamples"])
        if resamples < 1000:
            raise ValueError(
                f"Invalid 'bca_resamples' in configuration: {resamples}. "
                "Must be >= 1000 for statistical validity."
            )
        validated["bca_resamples"] = resamples

    if "explain" in flattened:
        validated["explain"] = bool(flattened["explain"])

    for str_key in (
        "true_label_col",
        "predicted_label_col",
        "race_col",
        "gender_col",
        "age_col",
        "model_name",
        "dataset_name",
    ):
        if str_key in flattened and flattened[str_key] is not None:
            validated[str_key] = str(flattened[str_key])

    if "model_description" in flattened:
        desc = flattened["model_description"]
        validated["model_description"] = str(desc) if desc is not None else None

    logger.debug(
        "Loaded audit configuration with %d parameter(s) from %s",
        len(validated),
        path,
    )
    return validated
