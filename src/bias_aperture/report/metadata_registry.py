"""Model and dataset metadata registry for autonomous report generation.

Provides automated resolution of model architecture parameters, input dimensions,
citations, and descriptions to eliminate hardcoded model cards and prevent
metadata drift across pre-compiled and dynamic compliance dossiers.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ModelMetadata:
    """Standardized metadata representation for Model Card rendering."""

    name: str
    architecture: str
    parameters: str
    backbone_family: str
    input_shape: str
    tasks: list[str] = field(
        default_factory=lambda: [
            "Race Classification",
            "Gender Classification",
            "Age Classification",
        ]
    )
    description: str = ""
    citation: str = ""
    license: str = "Academic Research Only"
    intended_use: str = (
        "Diagnostic benchmarking and demographic disparity auditing in facial analysis "
        "models. Not intended for production biometrics, identity verification, or automated "
        "surveillance decision systems."
    )


class ModelMetadataRegistry:
    """Registry and dynamic resolver for vision model architectures."""

    _REGISTRY: dict[str, ModelMetadata] = {
        "resnet34": ModelMetadata(
            name="FairFace ResNet-34 Multi-Task Classifier",
            architecture="ResNet-34 (Residual Neural Network)",
            parameters="21.3 Million",
            backbone_family="ResNet",
            input_shape="224 × 224 × 3",
            tasks=["Race (7 classes)", "Gender (2 classes)", "Age (9 classes)"],
            description=(
                "ImageNet-pretrained ResNet-34 terminating in an 18-unit linear multi-task head "
                "sliced for race (7), gender (2), and age (9) classification."
            ),
            citation="Kärkkäinen & Joo, 'FairFace: Face Attribute Dataset for Balanced Race, Gender, and Age', WACV 2021.",
            license="CC BY 4.0 (FairFace Benchmark Weights)",
            intended_use=(
                "Diagnostic demographic fairness auditing on balanced facial attribute benchmarks. "
                "Explicitly prohibited from deployment in unconstrained surveillance or punitive legal systems."
            ),
        ),
        "resnet50": ModelMetadata(
            name="ResNet-50 (FairFace Baseline)",
            architecture="ResNet-50 (50-layer Deep Residual Network)",
            parameters="25.6 Million",
            backbone_family="ResNet",
            input_shape="224 × 224 × 3",
            tasks=["Race (7 classes)", "Gender (2 classes)", "Age (9 classes)"],
            description=(
                "ImageNet-1k pretrained ResNet-50 feature extractor fine-tuned on the FairFace balanced "
                "demographic training split, evaluating baseline residual scaling on subgroup disparity."
            ),
            citation="He et al., 'Deep Residual Learning for Image Recognition', CVPR 2016.",
            license="Academic Research Only",
            intended_use=(
                "Baseline demographic disparity profiling and comparative fairness auditing against "
                "ResNet-34 and Vision Transformer architectures."
            ),
        ),
        "mobilenet": ModelMetadata(
            name="MobileNetV2 (FairFace Baseline)",
            architecture="MobileNetV2 (Inverted Residuals & Linear Bottlenecks)",
            parameters="3.5 Million",
            backbone_family="MobileNet",
            input_shape="224 × 224 × 3",
            tasks=["Race (7 classes)", "Gender (2 classes)", "Age (9 classes)"],
            description=(
                "Lightweight MobileNetV2 architecture with depthwise separable convolutions and inverted "
                "residual blocks fine-tuned on FairFace, evaluating edge-scale model fairness trade-offs."
            ),
            citation="Sandler et al., 'MobileNetV2: Inverted Residuals and Linear Bottlenecks', CVPR 2018.",
            license="Apache 2.0 / Academic Research",
            intended_use=(
                "Edge-tier demographic parity evaluation and mobile efficiency disparity benchmarking."
            ),
        ),
        "vit": ModelMetadata(
            name="ViT-B/16 (FairFace Baseline)",
            architecture="Vision Transformer Base (ViT-B/16, Patch size 16×16)",
            parameters="86.6 Million",
            backbone_family="Vision Transformer",
            input_shape="224 × 224 × 3",
            tasks=["Race (7 classes)", "Gender (2 classes)", "Age (9 classes)"],
            description=(
                "Vision Transformer (ViT-B/16) pre-trained on ImageNet-21k / ImageNet-1k and fine-tuned "
                "on FairFace, evaluating self-attention mechanisms against demographic disparity propagation."
            ),
            citation="Dosovitskiy et al., 'An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale', ICLR 2021.",
            license="Apache 2.0 / Academic Research",
            intended_use=(
                "Attention-based demographic disparity benchmarking and cross-architecture disparity comparison."
            ),
        ),
    }

    @classmethod
    def resolve(
        cls,
        model_name: str,
        target_axis: str = "race",
        custom_description: str | None = None,
    ) -> ModelMetadata:
        """Resolve a model name or string pattern into a structured ModelMetadata instance.

        If custom_description is explicitly provided and non-empty, it overrides the default
        description for the resolved architecture.
        """
        normalized = model_name.strip().lower()

        matched_key: str | None = None
        if "vit" in normalized or "transformer" in normalized:
            matched_key = "vit"
        elif "mobilenet" in normalized or "mobile" in normalized:
            matched_key = "mobilenet"
        elif "resnet50" in normalized or "resnet-50" in normalized:
            matched_key = "resnet50"
        elif (
            "resnet34" in normalized
            or "resnet-34" in normalized
            or "fairface" in normalized
            or "baseline" in normalized
        ):
            matched_key = "resnet34"

        if matched_key and matched_key in cls._REGISTRY:
            meta = cls._REGISTRY[matched_key]
            if custom_description:
                return ModelMetadata(
                    name=model_name if model_name else meta.name,
                    architecture=meta.architecture,
                    parameters=meta.parameters,
                    backbone_family=meta.backbone_family,
                    input_shape=meta.input_shape,
                    tasks=list(meta.tasks),
                    description=custom_description,
                    citation=meta.citation,
                    license=meta.license,
                    intended_use=meta.intended_use,
                )
            # If model_name was specific, retain exact casing
            if model_name and model_name != meta.name:
                return ModelMetadata(
                    name=model_name,
                    architecture=meta.architecture,
                    parameters=meta.parameters,
                    backbone_family=meta.backbone_family,
                    input_shape=meta.input_shape,
                    tasks=list(meta.tasks),
                    description=meta.description,
                    citation=meta.citation,
                    license=meta.license,
                    intended_use=meta.intended_use,
                )
            return meta

        # Fallback for arbitrary / unseen model architectures
        clean_name = (
            model_name.strip() if model_name.strip() else "Custom Vision Classifier"
        )
        desc = (
            custom_description
            if custom_description
            else (
                f"Custom computer vision architecture evaluated for demographic disparities across "
                f"protected demographic axis '{target_axis}'."
            )
        )
        return ModelMetadata(
            name=clean_name,
            architecture="Custom Facial Analysis Model",
            parameters="Unspecified",
            backbone_family="Custom",
            input_shape="224 × 224 × 3 (Standard)",
            tasks=[f"{target_axis.capitalize()} Disparity Auditing"],
            description=desc,
            citation="Unspecified",
            license="Academic Research Only",
            intended_use=(
                "Diagnostic demographic fairness auditing on facial analysis benchmarks. "
                "Not certified for production facial recognition or high-risk legal/surveillance deployment."
            ),
        )
