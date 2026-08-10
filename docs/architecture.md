# watchMe CV Agent Architecture

## Project Overview

watchMe is an educational speech-practice application designed as part of the larger MirrorMe smart-mirror concept.

This capstone version focuses on building watchMe into a multimodal computer vision agent that can observe a learner, make an explicit readiness decision, begin an educational activity, capture a learner response, and produce structured feedback.

The current implementation combines:

- Computer vision
- Still-image analysis
- Live webcam processing
- Face landmark analysis
- Temporal mouth movement analysis
- Structured agent communication
- Rule-based reasoning
- Microphone input
- Local Whisper speech recognition
- Educational lesson logic
- Live learner-facing visual feedback
- Structured trace logging
- Functional evaluation
- Robustness testing

watchMe is an educational prototype.

It is not intended to diagnose speech disorders, perform clinical pronunciation analysis, or replace a speech-language professional.

---

# Required Agent Pipeline

## 1. Input Ingestion

Implemented inputs include:

- Single sample images
- Batch folders of sample images
- Live webcam input
- Microphone input
- Typed lesson input
- Saved WAV audio artifacts
- Prerecorded video support in the temporal mouth-movement tool

Live webcam and microphone input have both been validated.

The final live lesson workflow combines webcam input and microphone input inside one running application.

Prerecorded video support remains available in `mouth_movement.py`, although prerecorded video has not received the same amount of formal testing as the live webcam path.

---

## 2. Preprocessing

Implemented preprocessing and validation includes:

- Validate image files
- Check supported image formats
- Load images safely with OpenCV
- Handle corrupt or invalid inputs without crashing
- Validate face count before mouth analysis
- Save current webcam frames for agent perception
- Measure microphone audio level
- Detect nearly silent recordings
- Save WAV audio artifacts
- Normalize Whisper transcription before lesson evaluation
- Normalize punctuation and repeated words during response scoring

Brightness, blur, grayscale conversion, rotation, blank images, and corrupt images have also been used as controlled robustness conditions.

Automatic brightness and blur rejection are not currently part of the main PlannerAgent policy.

---

# 3. Perception

The computer vision layer currently includes three primary perception tools:

## `tools/visual_perception.py`

This tool performs:

- Image validation
- Image loading
- Face detection
- Face count
- Face bounding boxes
- Face centering
- Face position
- Face size ratio
- Horizontal and vertical offsets
- Visual readiness assessment
- Annotated image generation
- Processing-time measurement
- Structured trace output

MediaPipe Face Landmarker provides the facial landmarks used by the current system.

Current visual readiness states include:

- `no_face`
- `multiple_faces`
- `move_closer`
- `move_back`
- `reposition`
- `ready`

Current prototype thresholds include:

- Horizontal center tolerance: `0.20`
- Vertical center tolerance: `0.20`
- Too-far face-size threshold: `0.08`
- Too-close face-size threshold: `0.55`

These values are prototype thresholds created for the current controlled evaluation.

They should not be treated as universal computer vision thresholds.

---

## `tools/mouth_analysis.py`

This tool performs:

- Mouth landmark localization
- Mouth visibility analysis
- Mouth-open ratio calculation
- Open or closed mouth estimation
- Annotated mouth output
- Processing-time measurement

The current prototype uses a mouth-open threshold of:

`0.08`

This threshold is a heuristic.

It is not a medically validated measurement.

Observed development examples included values such as:

Closed-mouth examples:

- `0.0000`
- `0.0139`

Open-mouth examples:

- `0.1134`
- `0.1970`
- `0.2407`
- `0.8200`

These values were useful during development but should not be interpreted as clinical speech measurements.

---

## `tools/mouth_movement.py`

This tool performs temporal mouth analysis across multiple frames.

It can:

- Read prerecorded video
- Read live webcam input
- Calculate mouth-open ratio over time
- Compare consecutive frames
- Measure frame-to-frame changes
- Produce a mouth-movement score
- Determine whether visible mouth movement occurred
- Save a structured movement trace

Current development settings include:

- Movement delta threshold: `0.03`
- Minimum valid frames: `5`

Live webcam validation has been completed successfully.

One development webcam session produced:

- Total frames: `337`
- Valid mouth frames: `337`
- Movement detected: `True`
- Movement score: `0.4427`
- Average frame-to-frame delta: `0.026`
- Processing time: approximately `31527 ms`

The trace was saved under:

`results/traces/camera_session_movement_trace.json`

A later combined camera and speech test also successfully detected visible mouth movement while Whisper transcription was operating.

The implementation is functional but has not been optimized for maximum frame rate.

Prerecorded video remains supported but has not received the same testing depth as live webcam input.

---

# 4. Reasoning / Decision Making

The reasoning layer uses explicit rule-based logic rather than hiding the decision inside a black-box model.

The PlannerAgent consumes the structured PerceptionAgent message and can decide to:

- Stop because of an input or perception error
- Wait for a learner to enter the frame
- Require only one learner
- Ask the learner to reposition
- Ask the learner to move closer
- Ask the learner to move farther away
- Retry mouth analysis
- Ask the learner to make the mouth visible
- Mark the learner as ready

Current PlannerAgent states include:

- `STOP`
- `WAIT_FOR_USER`
- `ONE_LEARNER_REQUIRED`
- `REPOSITION`
- `MOVE_CLOSER`
- `MOVE_BACK`
- `CHECK_MOUTH`
- `MOUTH_NOT_VISIBLE`
- `READY`

Each planner result contains:

- Decision state
- Reason
- Human-readable action

This makes the reasoning inspectable and traceable.

---

# 5. Action / Output

The system currently performs actions including:

- Display readiness feedback
- Draw learner bounding boxes
- Change bounding-box color based on readiness
- Save annotated images
- Save structured agent traces
- Save batch results
- Save audio recordings
- Start educational lessons
- Present lesson prompts in the camera window
- Capture typed responses
- Capture microphone responses
- Run local Whisper transcription
- Evaluate lesson responses
- Display live lesson outcomes
- Save complete lesson results

The current lesson outcomes are:

- `CORRECT`
- `NEAR_MATCH`
- `INCORRECT`
- `NO_INPUT`

Persistent learner-progress memory is not required for the current capstone implementation and is retained as a possible future extension.

---

# 6. Logging / Traceability

watchMe saves structured evidence of its decisions and outputs.

Current traces can include:

- Session ID
- Input path
- Face state
- Face count
- Bounding box
- Learner position
- Visual readiness
- Mouth state
- Perception result
- Planner decision
- Planner reason
- Planner action
- Processing time
- Lesson type
- Input mode
- Lesson start method
- Lesson prompt
- Audio path
- Whisper transcription
- Lesson outcome
- Mouth movement
- Session timing

Computer vision and live-agent traces are stored under:

`results/traces/`

Generated audio is stored under:

`results/audio/`

Annotated images are stored under:

`results/images/`

Live session frames are stored under:

`results/live/`

Evaluation outputs are stored under:

`results/`

---

# Tier 2 Status

The original Tier 2 design focused on one workflow coordinating multiple computer vision and multimodal tools.

The current implementation demonstrates Tier 2 characteristics including:

- Multiple computer vision tools
- Structured tool outputs
- Explicit error handling
- Agent-level perception
- Rule-based reasoning
- Saved annotated outputs
- Automated trace generation
- Batch image processing
- Live webcam processing
- Temporal mouth movement
- Microphone input
- Whisper transcription
- Typed input fallback
- Lesson execution
- Structured lesson results

The visual Tier 2 pipeline has been fully implemented and evaluated.

---

# Tier 3 Status

watchMe now contains multiple specialized agents with distinct responsibilities.

Implemented agents include:

- `PerceptionAgent`
- `PlannerAgent`
- `LessonAgent`

These agents are connected through the live multimodal orchestrator.

The implemented live sequence is:

```text
Camera / Image
      |
      v
PerceptionAgent
      |
      v
Structured Perception Message
      |
      v
PlannerAgent
      |
      v
Decision + Action
      |
      v
LiveLessonOrchestrator
      |
      v
LessonAgent
      |
      v
Speech / Typed Response
      |
      v
Structured Lesson Result
```

The agents perform different responsibilities rather than existing only as separate class names.

The PerceptionAgent observes.

The PlannerAgent reasons.

The LessonAgent acts and teaches.

The LiveLessonOrchestrator coordinates their handoffs and the learner-facing interface.

A possible future `ProgressAgent` could add persistent memory, but it is not required for the current multi-agent capstone implementation.

---

# Current Implemented Architecture

## Computer Vision Tools

### `tools/visual_perception.py`

This tool currently handles:

- Image validation
- OpenCV image loading
- Human face detection using MediaPipe Face Landmarker
- Face count
- Face bounding boxes
- Face centering
- Face position
- Face size ratio
- Visual readiness classification
- Annotated image output
- Processing-time measurement
- Structured trace output

The current visual readiness states are:

- `no_face`
- `multiple_faces`
- `move_closer`
- `move_back`
- `reposition`
- `ready`

---

### `tools/mouth_analysis.py`

This tool currently handles:

- Mouth landmark localization
- Mouth visibility
- Mouth-open ratio
- Open or closed mouth classification
- Annotated output
- Processing-time measurement

The current mouth-open threshold is:

`0.08`

This is treated as a prototype heuristic.

---

### `tools/mouth_movement.py`

This tool performs temporal mouth movement analysis.

It can:

- Process prerecorded video
- Process live webcam input
- Compare mouth geometry across frames
- Measure temporal changes
- Produce a movement score
- Detect meaningful visible movement
- Save a trace

Current settings include:

- Movement delta threshold: `0.03`
- Minimum valid frames: `5`

Multiple successful webcam tests confirmed that temporal mouth movement can be detected during live interaction.

---

### `tools/camera_test.py`

A separate camera utility was used to test webcam configuration.

Camera index:

`0`

successfully returned frames.

Observed frame size:

`640 x 480`

Successful Windows interfaces included:

- Default OpenCV backend
- DirectShow
- Media Foundation

Other tested camera indices did not return usable frames on the development computer.

---

# Speech Input Tool

## `tools/speech_input.py`

This tool provides microphone recording and local speech transcription.

Current responsibilities include:

- System-default microphone selection
- Optional microphone-device override
- Device listing
- Audio recording
- RMS audio-level measurement
- Silence detection
- WAV artifact generation
- Local Whisper model loading
- Speech transcription
- Structured speech-result output

Current speech settings include:

- Sample rate: `16000 Hz`
- Channels: `1`
- Recording duration: `3 seconds`
- Whisper model: `tiny.en`
- Silence threshold: `0.001`

The final implementation no longer requires a hard-coded microphone number.

The system first attempts to use the operating system's default input device.

An optional environment variable can override this behavior:

`WATCHME_MIC_DEVICE`

For example, on the development Windows computer:

```powershell
$env:WATCHME_MIC_DEVICE="7"
```

Device `7` was confirmed to work well on the development machine.

This number is machine-specific and should not be assumed to be valid on another system.

The current speech tool can also list available input devices so that another user can identify the correct microphone index.

Typed lesson input remains available as a hardware-independent fallback.

---

# Microphone Development Testing

Several microphone devices were tested during development.

An Intel Smart Sound Technology microphone array appeared as device `7` on the development computer and provided usable speech input.

A direct speech test using device `7` produced approximately:

- Audio level: `0.008266`
- Spoken response: `cat` repeated twice
- Whisper transcription: `cat, cat.`
- Status: `success`

This confirmed successful:

- Microphone capture
- WAV artifact creation
- Whisper loading
- Local transcription
- Structured speech output

A later portability test used the system-default microphone successfully at the software level, but the selected Windows default input produced a nearly silent recording.

Observed result:

- Status: `no_input`
- Audio level: approximately `0.000044`

This demonstrated why audio device selection must remain configurable.

The final implementation therefore supports:

```text
No override
→ operating system default microphone

WATCHME_MIC_DEVICE set
→ selected input device

Microphone unavailable
→ typed lesson input remains available
```

---

# Perception Agent

## `agents/perception_agent.py`

The PerceptionAgent coordinates the visual tools and converts their results into one structured perception message.

The current workflow is:

1. Receive an image.
2. Run `visual_perception.py`.
3. Check the number of detected faces.
4. Run mouth analysis when exactly one face is detected.
5. Preserve face bounding-box information.
6. Combine visual and mouth information.
7. Return one structured perception message.

Current structured face fields include:

- `detected`
- `count`
- `centered`
- `position`
- `size_ratio`
- `offset_x_ratio`
- `offset_y_ratio`
- `boxes`

Current mouth fields include:

- `analyzed`
- `visible`
- `open`
- `open_ratio`

Additional message fields include:

- Visual readiness
- Overall perception readiness
- Artifact paths
- Processing latency

The inclusion of `face.boxes` became important during live-interface development because the bounding box had originally been generated by the lower-level tool but was not preserved by the PerceptionAgent.

That handoff was corrected so the live interface could draw a readiness box around the learner.

---

# Planner Agent

## `agents/planner_agent.py`

The PlannerAgent receives the structured PerceptionAgent message and applies explicit rule-based reasoning.

Current decision states include:

- `STOP`
- `WAIT_FOR_USER`
- `ONE_LEARNER_REQUIRED`
- `MOVE_CLOSER`
- `MOVE_BACK`
- `REPOSITION`
- `CHECK_MOUTH`
- `MOUTH_NOT_VISIBLE`
- `READY`

Each response includes:

```text
agent
status
decision
    state
    reason
action
    message
```

The PlannerAgent provides an inspectable reasoning layer between perception and action.

---

# Visual Orchestrator

## `agents/orchestrator.py`

The original Orchestrator remains responsible for the still-image visual readiness pipeline.

Its current workflow is:

```text
Input
→ PerceptionAgent
→ PlannerAgent
→ Final Action
→ Agent Trace
→ Batch Summary
```

It supports:

- Single-image input
- Folder-based batch processing
- Supported-image filtering
- Individual agent trace generation
- Batch summaries
- Final action output

A successful batch test processed seven images from:

`data/sample/`

The batch summary is stored under:

`results/batch_summary.json`

This orchestrator remains useful for isolated visual evaluation even though the live multimodal system now uses a separate `LiveLessonOrchestrator`.

---

# Lesson Agent

## `agents/lesson_agent.py`

The LessonAgent adds the educational action layer.

Current responsibilities include:

1. Receive a lesson type.
2. Select the requested activity.
3. Select typed or microphone input.
4. Run the activity.
5. Call the speech-input tool when microphone mode is selected.
6. Evaluate the learner response.
7. Send live callback events to the learner interface.
8. Return a structured lesson result.

Current supported lessons are:

- CVC word practice
- Shapes practice

Current input modes are:

- Typed input
- Microphone input with Whisper

The LessonAgent is intentionally separate from the PerceptionAgent and PlannerAgent because it performs a different responsibility.

```text
PerceptionAgent
→ observes

PlannerAgent
→ decides

LessonAgent
→ acts / teaches
```

---

# Live Lesson Orchestrator

## `agents/live_lesson_orchestrator.py`

The LiveLessonOrchestrator connects the visual readiness system and educational speech system into one live application.

Its responsibilities include:

- Open the webcam
- Continuously display video
- Periodically sample frames for perception
- Call `PerceptionAgent.perceive()`
- Pass the structured result to `PlannerAgent.plan()`
- Draw the learner bounding box
- Display readiness information
- Manage the readiness state machine
- Manage lesson start behavior
- Start LessonAgent in a background thread
- Keep the camera window active while speech recording occurs
- Receive live LessonAgent callback messages
- Display lesson prompts
- Display listening status
- Display Whisper responses
- Display lesson outcomes
- Track visible mouth movement
- Save a complete live session trace

The final live state sequence is:

```text
WAITING_FOR_LEARNER
        |
        v
POSITIONING
        |
        v
READY
        |
        v
ARMED
        |
        v
COUNTDOWN
        |
        v
LESSON_RUNNING
        |
        v
COMPLETE
```

---

# Learner Readiness Bounding Box

The live camera window uses a bounding box as a human-facing readiness cue.

The box does not create the face detection.

MediaPipe performs the detection.

The bounding box communicates the system state to the learner.

## Blue Bounding Box

A blue box indicates:

```text
LEARNER DETECTED
```

The learner is visible but has not yet satisfied every readiness condition.

Possible corrections include:

- Reposition
- Move closer
- Move back
- Make the mouth visible
- Ensure only one learner is visible

## Green Bounding Box

A green box indicates:

```text
LEARNER READY
```

The learner has satisfied the current readiness policy.

This creates a clear visual transition between detection and readiness.

---

# Lesson Start Design

An important design decision is that visual readiness does not immediately activate the microphone.

The states are intentionally separated:

```text
READY
→ ARMED
→ COUNTDOWN
→ LESSON_RUNNING
```

This gives the learner time to recognize that the system is ready.

It also helps reduce cases where the microphone begins recording before the learner understands that the lesson has started.

Current start methods include:

## Automatic Countdown

After stable readiness is confirmed:

```text
READY
→ ARMED
→ 3-second countdown
→ lesson begins
```

## Keyboard `S`

The `S` key allows an already-ready learner to begin before the countdown completes.

It does not normally bypass visual readiness.

## Keyboard `M`

The `M` key is an explicit manual demonstration override.

This allows the lesson pipeline to run even if webcam conditions prevent visual readiness.

The trace records that the session used:

`manual_demo_override`

This is useful for reproducibility and demonstration without hiding that the visual gate was bypassed.

## Keyboard `Q`

The `Q` key saves the current session trace and exits the camera window.

---

# Live Lesson Interface

The webcam window now displays the educational activity directly.

This corrected an earlier usability problem in which the lesson was running in the terminal while the learner was looking at the camera window.

The current interface can display:

```text
SHAPES LESSON
Item 1/3

SAY: CIRCLE

LISTENING...
```

After Whisper transcription:

```text
HEARD: circle.
RESULT: CORRECT
```

The lesson then advances to the next prompt.

A short delay is used after the prompt is displayed so the learner can see the target before recording begins.

This reduces the chance that the recording window starts before the learner knows what to say.

---

# CVC Lesson

## `lessons/cvc_lesson.py`

The current CVC lesson contains:

- `cat`
- `dog`
- `sun`
- `hat`
- `bed`

Each item supports:

- Typed input
- Microphone input

For microphone input, the lesson calls:

`tools/speech_input.py`

The speech tool records audio and returns a Whisper transcription.

The lesson normalizes the transcription and evaluates the response.

Current outcomes include:

- `CORRECT`
- `NEAR_MATCH`
- `INCORRECT`
- `NO_INPUT`

The lesson now also sends live status callbacks including:

- Lesson started
- Prompt
- Listening
- Response
- Outcome
- Lesson complete

These messages allow the live camera interface to remain synchronized with the lesson.

---

# Shapes Lesson

## `lessons/shapes_lesson.py`

The Shapes lesson demonstrates that LessonAgent is reusable across more than one activity type.

Current prompts include:

- `circle`
- `square`
- `triangle`

The Shapes lesson supports:

- Typed input
- Microphone input
- Whisper transcription
- Response evaluation
- Live interface callbacks

CVC and Shapes are intentionally sufficient for the current capstone because they demonstrate two distinct educational activity types without unnecessarily expanding the project scope.

Additional lesson categories are treated as future work.

---

# Lesson Response Evaluation

The lesson system currently supports four output states.

## `CORRECT`

A response is `CORRECT` when the expected target appears in the normalized transcription.

Example:

Target:

`circle`

Whisper:

`that? circle!`

Outcome:

`CORRECT`

The evaluator also supports repeated responses.

For example:

Target:

`cat`

Whisper:

`cat cat`

Outcome:

`CORRECT`

---

## `NEAR_MATCH`

A response is `NEAR_MATCH` when the expected word is not present exactly but another recognized word reaches the configured text-similarity threshold.

The current similarity threshold is:

`0.65`

Example:

Target:

`cat`

Whisper:

`strenght, cap.`

Outcome:

`NEAR_MATCH`

Another example:

Target:

`hat`

Whisper:

`hot`

Outcome:

`NEAR_MATCH`

This is text similarity after Whisper transcription.

It is not acoustic pronunciation analysis.

---

## `INCORRECT`

A response is `INCORRECT` when usable speech is transcribed but the recognized words do not sufficiently match the target.

Example:

Target:

`sun`

Whisper:

`waters come ball`

Outcome:

`INCORRECT`

---

## `NO_INPUT`

A response is `NO_INPUT` when insufficient usable speech is received or no usable transcription is produced.

This state has been observed during:

- Low-volume speech
- Incorrect microphone selection
- Poor microphone placement
- Speech timing problems

---

# Speech Functional Testing

Several live microphone tests were performed.

## Direct Microphone Test

A direct speech test using the development microphone produced:

- Audio level: approximately `0.008266`
- Whisper transcription: `cat, cat.`
- Status: `success`

This confirmed:

- Recording
- WAV output
- Whisper model loading
- Local transcription
- Structured speech output

---

# Initial Silence-Threshold Testing

An early CVC microphone test used a silence threshold of:

`0.003`

Several recordings were rejected before Whisper could process them.

Observed approximate audio levels included:

- cat: `0.000038`
- dog: `0.001931`
- sun: `0.001868`
- hat: `0.001960`
- bed: `0.003182`

Only `bed` exceeded the original threshold.

Whisper returned:

`bed.`

The lesson produced:

`CORRECT`

This test showed that the silence threshold was too strict.

It was lowered to:

`0.001`

The change was based on observed microphone results rather than chosen arbitrarily.

---

# Repeated-Word Evaluation Failure

Another CVC test intentionally repeated each target.

Whisper produced examples including:

- `cat cat`
- `dog. dog.`
- `sun sun`
- `hut, hut.`
- `bed. bed.`

The microphone pipeline was clearly capturing speech.

However, the original evaluator compared the complete transcription string directly against the expected word.

This caused repeated correct words to be marked incorrectly.

The evaluator was changed so the expected target can match any normalized recognized word.

This failure improved the response-evaluation logic.

---

# Normal-Volume CVC Test

After the threshold and normalization changes, another CVC microphone test produced:

| Target | Whisper Output | Outcome |
| --- | --- | --- |
| cat | cat. | CORRECT |
| dog | frame all | INCORRECT |
| sun | sun. | CORRECT |
| hat | hat. | CORRECT |
| bed | no transcription | NO_INPUT |

This test demonstrated:

- Correct recognition
- Incorrect recognition
- Silence/no-input handling
- Structured response evaluation

---

# Deliberate Near-Match Test

A deliberate near-match test produced:

| Target | Intended Response | Whisper Output | Outcome |
| --- | --- | --- | --- |
| cat | cap | strenght, cap. | NEAR_MATCH |
| dog | dot | dot. | NEAR_MATCH |
| sun | son | waters come ball | INCORRECT |
| hat | hot | hot | NEAR_MATCH |
| bed | bad | and | INCORRECT |

This test successfully demonstrated the `NEAR_MATCH` path.

Across development, all four lesson outcomes have been observed:

- `CORRECT`
- `NEAR_MATCH`
- `INCORRECT`
- `NO_INPUT`

---

# Speech Recognition and Background Audio Limitation

Some microphone tests were performed while movie or television dialogue was present.

Whisper occasionally incorporated unrelated environmental speech.

Examples included intended one-word responses becoming unrelated multi-word phrases.

The current prototype does not perform:

- Speaker identification
- Speaker isolation
- Beamforming
- Advanced noise suppression
- Directional filtering

This limitation is retained as part of the evaluation evidence.

Possible future improvements include:

- Voice activity detection
- Noise suppression
- Longer or adaptive listening windows
- Limited retry behavior for uncertain or incorrect transcriptions
- Speaker isolation
- Improved microphone positioning
- Adaptive recording windows
- Larger Whisper models
- Confidence-aware transcription handling

---

# Camera and Speech Concurrency Validation

Live camera processing and microphone-based Whisper transcription were tested at the same time.

During one combined test, the camera processed:

- `331` frames
- `331` valid mouth frames

The camera reported:

- Movement detected: `True`
- Movement score: `0.2999`
- Average delta: `0.0211`

During the same test, Whisper returned:

- `the circle.`
- `square.`
- `triangle.`

No camera/microphone hardware conflict occurred.

This demonstrated that both subsystems could operate concurrently before they were connected into the final single-process orchestrator.

---

# Final Integrated Live Validation

The final LiveLessonOrchestrator successfully connected:

```text
Webcam
→ PerceptionAgent
→ PlannerAgent
→ Visual readiness
→ Automatic countdown
→ LessonAgent
→ Microphone
→ Whisper
→ Response evaluation
→ Live feedback
→ Trace
```

The official final Shapes validation session was:

`live_lesson_20260809_212807`

Observed results:

- Frames: `731`
- Perception updates: `48`
- Face detected: `True`
- Face count: `1`
- Final state: `COMPLETE`
- Start method: `automatic_countdown`
- Mouth movement: `True`
- Movement events: `18`
- Maximum mouth delta: `0.2841`
- Lesson completed: `True`

The learner's final visual readiness at the end of the session had shifted to `move_closer`, but the lesson had already reached `COMPLETE`. This is expected in a live system because the learner can move after the readiness gate has already started the lesson.

Lesson results included:

### Circle

Prompt:

`circle`

Whisper:

`circle.`

Outcome:

`CORRECT`

Audio level:

approximately `0.001266`

### Square

Prompt:

`square`

Whisper:

`square. square.`

Outcome:

`CORRECT`

Audio level:

approximately `0.001731`

### Triangle

Prompt:

`triangle`

Whisper:

`valve will explode.`

Outcome:

`INCORRECT`

Audio level:

approximately `0.001410`

Final result:

```text
2 correct
0 near match
1 incorrect
0 no input
```

This final run was intentionally accepted as realistic multimodal evidence rather than repeated until a perfect speech score appeared. The environment was not guaranteed to be silent, and short isolated-word recognition can be affected by background noise, microphone placement, timing, and Whisper behavior.

The result is therefore not reported as general speech-recognition accuracy. It demonstrates that the complete architecture remained operational while one subsystem produced an imperfect result:

```text
Computer vision / readiness: operational
Agent orchestration: operational
Mouth movement tracking: operational
Audio capture: operational
Whisper transcription: imperfect on one item
Lesson evaluation: operational
Trace creation: operational
```

A future version could improve this interaction by allowing a longer or adaptive listening window and a limited retry policy when the expected challenge word is not recognized. After a maximum number of attempts, the learner could skip the item or use typed confirmation so the lesson cannot become stuck indefinitely.

---

# Live Failure / No-Input Validation

A separate Shapes live session produced:

- Face detected: `True`
- Face count: `1`
- Lesson completed: `True`
- Mouth movement detected: `True`
- 3 `NO_INPUT` lesson results

This failure is useful because it demonstrates the difference between:

- Visual activity being detected
- Microphone input being usable

A learner can visibly move their mouth while the selected microphone still records insufficient usable speech.

This reinforces the need to treat visual mouth activity and audio recognition as separate signals.

---

# Current End-to-End Workflow

The final implemented workflow is:

## 1. Input

watchMe can receive:

- Single images
- Image folders
- Live webcam input
- Typed lesson responses
- Microphone responses
- Prerecorded video for temporal mouth testing

## 2. Validation

The system checks:

- File existence
- Safe image decoding
- Supported image input
- Face count
- Mouth-analysis eligibility
- Microphone audio level

## 3. Computer Vision Perception

MediaPipe and OpenCV extract:

- Face presence
- Face count
- Bounding box
- Learner centering
- Face position
- Relative face size
- Mouth visibility
- Mouth-open ratio

## 4. PerceptionAgent

The PerceptionAgent combines the CV outputs into a structured message.

## 5. PlannerAgent

The PlannerAgent applies explicit readiness rules.

## 6. Learner Feedback

The live interface displays:

- Learner bounding box
- Position status
- Readiness
- Corrective action

## 7. Readiness State

The learner transitions through:

```text
WAITING
→ POSITIONING
→ READY
→ ARMED
```

## 8. Lesson Start

The lesson can begin through:

- Automatic countdown
- `S` early-start control
- `M` demonstration override

## 9. LessonAgent

The LessonAgent runs:

- CVC practice
- Shapes practice

## 10. Live Prompt

The camera interface displays the current lesson target before microphone recording begins.

## 11. Speech Processing

For microphone input:

1. Record audio.
2. Measure audio level.
3. Save WAV artifact.
4. Reject nearly silent input when appropriate.
5. Run Whisper.
6. Normalize transcription.
7. Evaluate target match.

## 12. Live Result

The camera window displays information such as:

```text
HEARD: square.
RESULT: CORRECT
```

## 13. Traceability

The session trace records the multi-agent and lesson workflow.

---

# Planner Decision Priority

Testing showed that a learner may violate more than one readiness condition simultaneously.

For example, a learner could be:

- Too far away
- Off center

The PlannerAgent therefore uses explicit priority.

Current priority:

1. Perception error
2. No learner
3. Multiple learners
4. Positioning
5. Distance
6. Mouth analysis availability
7. Mouth visibility
8. Ready

Positioning is evaluated before distance.

This policy was added after `leftsidesmile.jpg` exposed a case where the original planner selected `MOVE_CLOSER` even though the learner was outside the accepted horizontal position.

After the policy was corrected, the appropriate decision became:

`REPOSITION`

Another evaluation involving `womansmiling.jpg` showed that the learner was outside the configured vertical centering tolerance.

The expected result was reconciled with the actual measurements and existing policy before the final evaluation set was frozen.

Expected labels were not repeatedly changed simply to force successful results.

---

# Evaluation Status

The controlled visual functional evaluation contains:

- 14 scenarios
- 14 passed
- 0 failed
- 100.00% controlled task success

Average observed latency:

`185.69 ms`

The correct interpretation is:

> 100% task success on the current controlled 14-scenario functional validation set.

It should not be described as universal computer vision accuracy.

The evaluation includes scenarios such as:

- No face
- One centered learner
- Learner too far
- Learner too close
- Learner off center
- Multiple faces
- Mouth visible
- Mouth unavailable
- Non-human input
- Missing input

Definitions are stored under:

`data/evaluation_cases.json`

Results are stored under:

`results/evaluation_results.json`

Metrics are stored under:

`results/metrics.txt`

Speech evaluation remains separate so the frozen visual benchmark is not changed by later multimodal development.

---

# Robustness Evaluation

The robustness set includes:

- Dark image
- Blurry image
- Grayscale image
- 90-degree left rotation
- 90-degree right rotation
- Upside-down image
- Blank image
- Corrupt image

Observed behavior included:

| Condition | Result |
| --- | --- |
| Dark image | READY |
| Blurry image | READY |
| Grayscale image | READY |
| Rotated left | READY |
| Rotated right | READY |
| Upside down | REPOSITION |
| Blank input | WAIT_FOR_USER |
| Corrupt input | STOP |

All eight robustness cases were handled without an unhandled crash.

The corrupt case demonstrates the error-handling chain:

```text
Decode failure
→ structured perception error
→ PlannerAgent
→ STOP
→ saved result
```

---

# Speech Evaluation Dataset

Speech behavior is maintained separately from the frozen visual evaluation.

The speech test-definition file is:

`data/speech_evaluation_cases.json`

It contains scenarios representing:

- Correct response
- Near match
- Incorrect response
- No input

This separation prevents the original visual benchmark from changing as speech functionality evolves.

---

# Evaluation Data and Runtime Artifacts

## Controlled Test Definitions

### `data/evaluation_cases.json`

Purpose:

Frozen 14-case visual functional evaluation.

### `data/robustness_cases.json`

Purpose:

Visual robustness and stress testing.

### `data/speech_evaluation_cases.json`

Purpose:

Speech and lesson response scenarios.

---

## Runtime Artifacts

Annotated images:

`results/images/`

Audio recordings:

`results/audio/`

Live frame snapshots:

`results/live/`

Agent and tool traces:

`results/traces/`

Visual evaluation results:

`results/evaluation_results.json`

Metrics:

`results/metrics.txt`

Batch summary:

`results/batch_summary.json`

---

# Development Failure Case: Haar Cascade False Positive

An earlier face-detection implementation used Haar Cascade.

Testing showed that this approach could incorrectly classify background content as a human face.

A failure artifact was preserved as:

`results/images/haar_false_positive_smiling.jpg`

This failure contributed to replacing the earlier detector with MediaPipe Face Landmarker.

---

# Development Failure Case: Planner Priority Conflict

The original PlannerAgent could prioritize distance before learner position.

Testing with:

`leftsidesmile.jpg`

exposed this issue.

The planner was updated so learner positioning is handled before distance corrections.

---

# Development Failure Case: Live Agent API Mismatch

During live integration, the first orchestrator implementation attempted to call methods such as:

`PerceptionAgent.run()`

The actual PerceptionAgent API was:

`PerceptionAgent.perceive()`

The standalone visual tool worked correctly, but the live orchestrator failed because the agent interface had been guessed incorrectly.

The saved webcam frame was tested directly with `visual_perception.py`.

It returned:

- `face_detected: True`
- `face_count: 1`
- `face_centered: True`
- `face_position: center`
- `face_size_ratio: 0.1765`
- `readiness: ready`

This isolated the failure to the agent integration rather than the CV model.

The LiveLessonOrchestrator was corrected to call the actual agent APIs.

---

# Development Failure Case: Bounding Box Handoff

The lower-level visual perception tool already generated:

`face_boxes`

However, the original PerceptionAgent structured message did not preserve those coordinates.

As a result, the live interface could know that a learner existed but could not draw the learner-facing readiness box.

The PerceptionAgent was updated to preserve:

`face.boxes`

This enabled the live blue/green bounding box.

---

# Development Failure Case: Hidden Lesson Prompt

An early integrated live session successfully:

- Detected the learner
- Reached READY
- Started automatically
- Detected mouth movement
- Ran the Shapes lesson

However, the lesson prompt was visible only in the terminal.

The learner did not know which word to say while looking at the camera interface.

This produced unusable responses even though the underlying lesson system was running.

The lesson files and LessonAgent were updated to support status callbacks.

The LiveLessonOrchestrator now receives live events including:

- Prompt
- Listening
- Response
- Outcome
- Completion

The camera window displays these events directly.

This converted the webcam display from a diagnostic window into a learner-facing lesson interface.

---

# Development Limitation: Image Orientation

Robustness testing showed that some 90-degree rotated images can still receive:

`READY`

because explicit head orientation is not currently modeled as part of the readiness policy.

This limitation is intentionally documented.

---

# Development Limitation: Whisper Recognition

Whisper can produce unreliable results when:

- Speech is very quiet
- Short isolated words are used
- Background dialogue is present
- Another speaker is captured
- Microphone placement is poor
- The selected microphone is not the intended device
- The recording window does not align with the learner response

Observed failures have been retained rather than hidden.

---

# Development Limitation: Default Microphone Selection

The final speech tool can use the operating-system default microphone.

On the development machine, the system default microphone could be selected programmatically but produced a nearly silent recording.

A known-good development device was therefore selected with:

```powershell
$env:WATCHME_MIC_DEVICE="7"
```

This does not mean device `7` should be used on another computer.

The device number is machine-specific.

The repository documents how another user can list available devices and select the appropriate input.

---

# Reproducibility

A separate clean virtual environment was created earlier in development to verify that the original computer vision pipeline did not rely on undocumented packages.

The documented CV dependencies were installed.

The frozen visual evaluation was rerun.

Result:

- 14 passed
- 0 failed

The project later added speech dependencies.

The final pinned direct requirements now include:

```text
mediapipe==1.0.0
opencv-contrib-python==5.0.0.93
numpy==2.2.6
openai-whisper==20250625
sounddevice==0.5.5
soundfile==0.14.0
```

A final repository-level reproducibility review should confirm that:

- These requirements are present
- No hard-coded local paths are required
- Microphone override remains optional
- Typed input works as a hardware-independent fallback
- The main documented command starts the application

The primary live application command is:

```powershell
& ".\.venv\Scripts\python.exe" -m agents.live_lesson_orchestrator
```

---

# Current Agent Responsibilities

## PerceptionAgent

Primary responsibility:

**Perceive**

Current duties:

- Interpret image input
- Detect learner presence
- Count faces
- Preserve bounding boxes
- Measure learner position
- Estimate relative distance
- Analyze mouth state
- Produce structured perception data

---

## PlannerAgent

Primary responsibility:

**Reason**

Current duties:

- Interpret perception results
- Apply readiness rules
- Resolve competing corrective conditions
- Select an action
- Return an explicit reason

---

## LessonAgent

Primary responsibility:

**Act / Teach**

Current duties:

- Select lesson activity
- Present prompts
- Capture typed responses
- Capture microphone responses
- Call Whisper
- Evaluate responses
- Send live UI events
- Return structured lesson results

---

## LiveLessonOrchestrator

Primary responsibility:

**Coordinate**

Current duties:

- Manage the webcam
- Coordinate PerceptionAgent
- Coordinate PlannerAgent
- Manage readiness state
- Start LessonAgent
- Manage learner-facing visual feedback
- Keep camera and lesson operation concurrent
- Track mouth movement
- Save complete session traces

---

# Future ProgressAgent

A future `ProgressAgent` could provide persistent learner-session memory.

Possible responsibilities include:

- Store lesson attempts
- Store session history
- Store prompt history
- Store Whisper transcription
- Store response outcome
- Track repeated attempts
- Generate progress summaries

A local SQLite database could contain fields such as:

- `session_id`
- `lesson_type`
- `prompt`
- `response`
- `outcome`
- `attempt`
- `input_mode`
- `audio_path`
- `timestamp`

This future extension would add persistent memory:

```text
Perceive
→ Reason
→ Act
→ Remember
```

SQLite and ProgressAgent are not required for the current capstone implementation.

---

# Current Multimodal Architecture

The implemented architecture is now:

```text
Image / Live Webcam
        |
        v
Visual Perception Tools
        |
        v
PerceptionAgent
        |
        v
Structured Perception Message
        |
        v
PlannerAgent
        |
        v
Readiness Decision + Action
        |
        v
LiveLessonOrchestrator
        |
        +---------------------------+
        |                           |
        v                           v
Readiness Interface           Lesson Start
Blue / Green Box                   |
                                    v
                               LessonAgent
                                    |
                    +---------------+---------------+
                    |                               |
                    v                               v
               Typed Input                  Microphone Input
                                                    |
                                                    v
                                             Audio Validation
                                                    |
                                                    v
                                             Whisper tiny.en
                                                    |
                                                    v
                                              Transcription
                                                    |
                                                    v
                                           Lesson Evaluation
                                                    |
                                                    v
                         CORRECT / NEAR_MATCH / INCORRECT / NO_INPUT
                                                    |
                                                    v
                                           Live Visual Feedback
                                                    |
                                                    v
                                             Session Trace
```

The visual and educational speech systems are no longer separate planned components.

They are connected in one working live multimodal application.

---

# Responsible Use

watchMe is intended as an educational support prototype.

It should not be used as:

- A speech-disorder diagnostic tool
- A medical diagnostic system
- A replacement for a speech-language pathologist
- An autonomous high-stakes educational evaluator

The system can be affected by:

- Lighting
- Camera placement
- Camera quality
- Face orientation
- Microphone quality
- Microphone selection
- Speaker volume
- Environmental noise
- Background speech
- Whisper model limitations

The CVC and Shapes near-match features use text comparison after speech recognition.

They do not measure acoustic pronunciation quality.

Human oversight should remain part of any higher-stakes use.

---

# Privacy Considerations

watchMe can generate identifiable visual and audio artifacts.

Runtime outputs may include:

- Webcam snapshots
- Annotated face images
- WAV recordings
- Whisper transcription
- JSON traces

Before publishing the repository:

- Review raw audio recordings
- Avoid publishing unnecessary identifiable voice data
- Review sample-image licensing
- Review generated traces for personal information
- Avoid including secrets or local credentials

Audio recordings are currently stored under:

`results/audio/`

These recordings should be reviewed before public GitHub publication.

---

# Current Known Limitations

Current limitations include:

- Small controlled evaluation dataset
- Prototype centering thresholds
- Prototype face-size thresholds
- Heuristic mouth-open threshold
- No clinical pronunciation analysis
- Text-based near-match logic
- Background speech can affect Whisper
- Quiet speech can fall below the silence threshold
- Short isolated words can be misrecognized
- Microphone device quality varies by machine
- System-default microphone may not always be the desired device
- Explicit head orientation is not modeled
- Rotated images can sometimes satisfy readiness
- Live webcam processing is functional but not optimized for maximum frame rate
- Prerecorded video has less validation than live webcam processing
- Only two lesson categories are currently implemented
- No persistent learner progress database

These limitations define the scope of the current capstone rather than preventing the prototype from demonstrating its intended agent workflow.

---

# Final Architecture Status

Implemented:

- [x] Still-image perception
- [x] Batch visual processing
- [x] MediaPipe face detection
- [x] Face bounding boxes
- [x] Learner position analysis
- [x] Face-size readiness
- [x] Mouth visibility analysis
- [x] Mouth-open analysis
- [x] Temporal mouth movement
- [x] Live webcam processing
- [x] PerceptionAgent
- [x] PlannerAgent
- [x] LessonAgent
- [x] LiveLessonOrchestrator
- [x] Structured agent handoffs
- [x] Blue/green readiness interface
- [x] READY / ARMED state separation
- [x] Automatic countdown
- [x] Keyboard start controls
- [x] CVC lesson
- [x] Shapes lesson
- [x] Typed input
- [x] Microphone input
- [x] Whisper transcription
- [x] Visible live lesson prompts
- [x] Live response feedback
- [x] CORRECT handling
- [x] NEAR_MATCH handling
- [x] INCORRECT handling
- [x] NO_INPUT handling
- [x] Structured traces
- [x] Controlled visual evaluation
- [x] Robustness evaluation
- [x] Camera and microphone concurrency validation
- [x] Full integrated live multimodal validation
- [x] Portable microphone-device selection
- [x] Optional microphone override
- [x] Pinned speech dependencies

---

# Remaining Submission Work

Feature development and formal testing are now frozen.

The remaining work is packaging and submission:

1. Commit the final synchronized documentation and evidence.
2. Upload the repository to GitHub.
3. Verify that the published README provides a usable clone-and-run path.
4. Confirm that private audio recordings remain excluded from Git tracking.
5. Prepare the optional pitch deck / presentation bonus submission.

No additional lesson categories are required for the current capstone.

No ProgressAgent or SQLite implementation is required for the current submission.

---

# Future Work

Possible future development includes:

- ProgressAgent
- SQLite learner-session memory
- Persistent progress history
- Additional lesson categories
- Voice-based lesson-start commands
- Touchscreen controls
- Gesture-based controls
- Improved microphone-selection UI
- Noise suppression
- Longer or adaptive listening windows
- Limited retry behavior for uncertain or incorrect transcriptions
- Speaker isolation
- Voice activity detection
- Larger speech-recognition models
- Improved orientation analysis
- More diverse visual datasets
- More diverse speech datasets
- Improved real-time performance
- Adaptive lesson selection

These features would extend the existing architecture rather than replace it.

---

# Architecture Summary

The final capstone architecture demonstrates a complete agent loop:

```text
SEE
PerceptionAgent
        |
        v
THINK
PlannerAgent
        |
        v
COORDINATE
LiveLessonOrchestrator
        |
        v
ACT / TEACH
LessonAgent
        |
        v
OBSERVE RESPONSE
Camera + Microphone + Whisper
        |
        v
EVALUATE
Lesson outcome
        |
        v
LOG
Structured session trace
```

watchMe therefore functions as an interactive multimodal computer vision agent rather than only a static image-classification or face-detection script.