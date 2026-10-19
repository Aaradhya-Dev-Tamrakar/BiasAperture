"""Task-label transformations that preserve demographic record fields."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from bias_aperture.schema import SubjectRecord


class OvRTransformer:
    r"""
    Multi-Class One-vs-Rest (OvR) evaluation helper.

    Transforms a multi-class SubjectRecord dataset into an M-way set of
    binary tasks $Y^{(m)} = \mathbb{I}(Y = c_m)$ and
    $\hat{Y}^{(m)} = \mathbb{I}(\hat{Y} = c_m)$ preserving demographic axes.
    """

    @staticmethod
    def get_classes(
        records: Sequence[SubjectRecord],
        axis: Literal["true", "predicted", "both"] = "both",
    ) -> list[str]:
        """Extract unique classes present across true, predicted, or both labels."""
        classes: set[str] = set()
        for r in records:
            if axis in ("true", "both"):
                classes.add(str(r.true_label))
            if axis in ("predicted", "both"):
                classes.add(str(r.predicted_label))
        return sorted(classes)

    @staticmethod
    def binarize(
        records: Sequence[SubjectRecord],
        target_class: str,
        *,
        positive_label: str = "1",
        negative_label: str = "0",
    ) -> list[SubjectRecord]:
        """
        Binarize ground truth and predictions against the specified target class.
        """
        target_str = str(target_class)
        binarized: list[SubjectRecord] = []
        for r in records:
            y_bin = (
                positive_label if str(r.true_label) == target_str else negative_label
            )
            y_hat_bin = (
                positive_label
                if str(r.predicted_label) == target_str
                else negative_label
            )
            binarized.append(
                SubjectRecord(
                    image_id=r.image_id,
                    race=r.race,
                    gender=r.gender,
                    age=r.age,
                    true_label=y_bin,
                    predicted_label=y_hat_bin,
                )
            )
        return binarized

    @classmethod
    def decompose_all(
        cls,
        records: Sequence[SubjectRecord],
        classes: Sequence[str] | None = None,
        *,
        positive_label: str = "1",
        negative_label: str = "0",
    ) -> dict[str, list[SubjectRecord]]:
        """
        Decompose a multi-class dataset into M distinct binary OvR datasets.
        """
        target_classes = (
            list(classes) if classes is not None else cls.get_classes(records)
        )
        return {
            c: cls.binarize(
                records,
                c,
                positive_label=positive_label,
                negative_label=negative_label,
            )
            for c in target_classes
        }
