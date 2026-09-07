# Proposal Defense Questions: Image Inference and Scope

**Date:** 2026-09-07  
**Context:** Proposal defense follow-up and scope clarification  
**Status:** Proposal defense completed

## Question 1: How do we infer each image?

Each FairFace image follows this pipeline:

1. **Face detection:** dlib's CNN face detector locates the face in the image.
2. **Face alignment:** dlib's five-point shape predictor identifies facial landmarks and `get_face_chip` aligns and crops the face to a 224 x 224 image.
3. **Preprocessing:** Pillow converts the aligned crop to an image, and torchvision converts it to a tensor and applies ImageNet normalization.
4. **Model inference:** the image is passed through the pretrained FairFace ResNet-34 multitask classifier.
5. **Label decoding:** the highest-logit class is selected for each output head.
6. **Prediction record:** the predicted age, gender, and race labels are written to the predictions CSV for later auditing.

The implementation is in `scripts/predict.py`, primarily in `detect_and_align_face`, `predict_single_image`, and `run_batch_prediction`.

## Question 2: Which method is used to analyze the image?

The image is analyzed using a **pretrained FairFace ResNet-34 convolutional neural network**. It has three independent classification heads:

- **Age:** 9 classes
- **Gender:** 2 classes
- **Race:** 7 classes

The model checkpoint is `fairface_alldata_20191111.pt`. The model performs demographic classification; BiasAperture does not train or modify the model.

The preprocessing and localization method is:

- dlib CNN face detection
- dlib five-point landmark alignment
- 224 x 224 aligned face crop
- torchvision tensor conversion and ImageNet normalization

## Question 3: What exactly is BiasAperture analyzing?

BiasAperture analyzes the **prediction outcomes of an already-trained facial analysis model**. It groups predictions by demographic attributes and computes disparity metrics, statistical significance, confidence intervals, and compliance-oriented findings.

The project is not primarily a face-recognition or demographic-classification system. The FairFace ResNet-34 model is the reference model used for the current case study and inference demonstration.

## Narrowed Project Scope

> BiasAperture is a diagnostic framework for auditing demographic disparities in predictions produced by an existing facial analysis model. The current case study uses the pretrained FairFace ResNet-34 model on the FairFace dataset. The platform does not train, fine-tune, retrain, debias, or alter model weights, and it does not generate synthetic images.

The audit engine can consume:

- predictions exported by an external or black-box model, or
- predictions produced through an in-process model adapter.

This separates **model inference** from **bias auditing**:

- `scripts/predict.py` performs the reference FairFace inference pipeline.
- `src/bias_aperture/` validates and audits the resulting predictions.

## Important Technical Clarifications

- `predict.py` selects the class with the largest logit using `argmax`; it does not need to calculate softmax probabilities for the categorical output CSV.
- The current `--batch-size` argument is retained for command-line compatibility, but inference is currently performed one image at a time.
- The audit conclusions concern disparity in model predictions across demographic groups, not the inherent identity or appearance of an individual.
- FairFace is the primary runtime dataset. UTKFace is a research comparison that was profiled and removed from the active runtime scope because of label-quality concerns.

## Defense Answer in One Sentence

> We detect and align the face with dlib, classify it with a pretrained FairFace ResNet-34 multitask CNN into age, gender, and race labels, and then use BiasAperture to audit whether the model's prediction errors and outcomes differ across demographic groups; we do not retrain or debias the model.
