# Model Files

## MediaPipe Face Landmarker

The file:

`face_landmarker.task`

is the pretrained MediaPipe Face Landmarker model used by watchMe.

The model provides facial landmark detection used for:

- human face detection
- face bounding boxes
- learner positioning
- face-size estimation
- mouth landmark localization
- mouth-open analysis
- temporal mouth-movement analysis

watchMe does not train or fine-tune this model.

The pretrained model is used as the perception foundation for the computer vision pipeline.

The application's custom work is implemented in the surrounding computer vision tools, structured agent messages, readiness logic, temporal processing, lesson orchestration, evaluation, and live multimodal interface.

For model information and licensing, refer to the official MediaPipe documentation and model distribution terms.

The model file is stored locally so the application does not need to download the model every time it runs.