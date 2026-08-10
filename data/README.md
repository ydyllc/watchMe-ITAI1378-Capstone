# watchMe Data

## Purpose

This directory contains controlled test definitions and sample inputs used during watchMe development and evaluation.

The data is divided into functional evaluation, robustness testing, speech evaluation definitions, and sample image inputs.

---

## Evaluation Files

### `evaluation_cases.json`

Contains the frozen 14-scenario visual functional evaluation set.

This dataset is used to evaluate the PerceptionAgent and PlannerAgent decision pipeline.

The final controlled result was:

`14 / 14 passed`

This result represents task success only on the current controlled validation set and should not be interpreted as universal computer vision accuracy.

---

### `robustness_cases.json`

Contains robustness and stress-test definitions.

Conditions include:

- reduced brightness
- blur
- grayscale
- rotated images
- upside-down images
- blank input
- corrupt input

These cases are kept separate from the frozen functional evaluation.

---

### `speech_evaluation_cases.json`

Contains controlled speech and lesson evaluation definitions.

Speech scenarios include:

- correct response
- near match
- incorrect response
- no input

Speech evaluation is separated from visual evaluation so later multimodal features do not change the original computer vision benchmark.

---

## Sample Images

Sample images are stored under:

`data/sample/`

They are used for development and classroom evaluation of:

- face detection
- face count
- learner position
- face size
- mouth visibility
- mouth opening
- non-human rejection
- multiple-person detection
- robustness testing

Some robustness images were derived from existing sample images by applying transformations such as:

- grayscale conversion
- reduced brightness
- blur
- rotation

---

## Licensing and Public Repository Notice

Sample images should be reviewed before public distribution.

Images should only remain in the public repository if their source and redistribution rights are known or if they were created specifically for this project.

If redistribution rights cannot be confirmed, the safest approach is to remove those images from the public GitHub repository while keeping the JSON evaluation structure and documented results.

Generated webcam images and personal recordings should also be reviewed before publication.

---

## Runtime Data

Runtime-generated outputs are not stored in this directory.

Generated files are saved under:

`results/`

including:

- annotated images
- evaluation results
- agent traces
- webcam snapshots
- audio recordings