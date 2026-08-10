# watchMe

## A Computer Vision Speech Practice Agent for the MirrorMe Platform

watchMe is an interactive computer vision and speech practice prototype developed as part of the larger MirrorMe platform concept.

The system uses computer vision to determine whether a learner is visible, properly positioned, an appropriate distance from the camera, and showing a visible mouth before beginning a simple educational speech activity. Once the learner satisfies the visual readiness requirements, watchMe can automatically start a lesson, display prompts inside the live camera interface, record the learner's speech, transcribe the recording with Whisper, evaluate the response, and display the result.

The current prototype includes two lesson types:

- CVC word practice
- shape word practice

watchMe is an educational prototype. It is not a medical, diagnostic, clinical, or speech therapy system.

---

# Project Goals

The current version of watchMe demonstrates:

- still image input
- live webcam input
- face detection using MediaPipe Face Landmarker
- learner position analysis
- face size and approximate camera distance evaluation
- mouth visibility analysis
- mouth open and closed estimation
- temporal mouth movement detection
- blue and green learner readiness bounding boxes
- structured perception messages
- rule based agent reasoning
- automatic lesson readiness checks
- automatic lesson start after a readiness countdown
- optional keyboard start controls
- visible lesson prompts inside the camera window
- typed lesson input
- microphone lesson input
- local Whisper speech transcription
- CVC word evaluation
- shape word evaluation
- CORRECT, NEAR_MATCH, INCORRECT, and NO_INPUT response states
- structured JSON trace logging
- automated functional evaluation
- robustness and failure testing
- portable microphone configuration
- reproducible dependency setup

---

# System Architecture

watchMe follows a multi-agent perception, reasoning, and action architecture.

```text
Camera / Image
      |
      v
Computer Vision Tools
      |
      v
PerceptionAgent
      |
      | Structured Perception Message
      v
PlannerAgent
      |
      | Decision + Action
      v
LiveLessonOrchestrator
      |
      v
LessonAgent
      |
      +----------------------+
      |                      |
      v                      v
Typed Input          Microphone Input
                             |
                             v
                       Whisper ASR
                             |
                             v
                    Response Evaluation
                             |
                             v
                  Visual Lesson Feedback
                             |
                             v
                  Results + JSON Traces
```

The main agent responsibilities are:

### PerceptionAgent

The `PerceptionAgent` combines the computer vision tools into one structured perception message.

It reports information including:

- whether a face was detected
- number of faces
- learner position
- whether the learner is centered
- face size ratio
- visual readiness
- face bounding box coordinates
- mouth visibility
- mouth open ratio

### PlannerAgent

The `PlannerAgent` receives the structured perception message and decides what the learner should do next.

Possible decisions include:

- `WAIT_FOR_USER`
- `ONE_LEARNER_REQUIRED`
- `REPOSITION`
- `MOVE_CLOSER`
- `MOVE_BACK`
- `CHECK_MOUTH`
- `MOUTH_NOT_VISIBLE`
- `READY`

The planner produces both a decision and a human readable action message.

### LessonAgent

The `LessonAgent` controls the educational speech activity.

The current lesson types are:

- `cvc`
- `shapes`

The agent supports:

- typed input
- microphone input
- Whisper transcription
- lesson prompts
- response evaluation
- live status callbacks to the camera interface

### LiveLessonOrchestrator

The `LiveLessonOrchestrator` connects the perception, planning, and lesson agents into one live workflow.

It manages:

- webcam capture
- perception sampling
- learner readiness
- bounding box visualization
- lesson countdown
- automatic lesson start
- keyboard start controls
- lesson prompts
- microphone activity
- live results
- mouth movement tracking
- session trace creation

---

# Learner Readiness Interface

The live webcam window provides a visual cue for learner readiness.

### Blue Bounding Box

A blue bounding box means:

```text
LEARNER DETECTED
```

The learner is visible, but one or more readiness requirements have not yet been satisfied.

For example, the learner may need to:

- move closer
- move farther away
- move toward the center
- ensure the mouth is visible

### Green Bounding Box

A green bounding box means:

```text
LEARNER READY
```

The learner has satisfied the current visual readiness conditions.

After readiness remains stable, watchMe enters the `ARMED` state and begins a short countdown before starting the lesson.

---

# Lesson Start Behavior

Visual readiness and lesson start are treated as separate states.

The normal workflow is:

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
3 second countdown
        |
        v
LESSON_RUNNING
        |
        v
COMPLETE
```

This prevents the microphone from immediately beginning to record as soon as a learner briefly enters the correct position.

The current start methods are:

### Automatic Start

When the learner remains visually ready:

```text
READY
→ ARMED
→ countdown
→ lesson begins
```

### S Key

Press:

```text
S
```

to start the lesson early while the system is already in the READY/ARMED state.

This does not normally bypass the computer vision readiness check.

### M Key

Press:

```text
M
```

to use the manual demonstration override.

This allows the lesson pipeline to be demonstrated even when a particular webcam, lighting condition, or hardware configuration prevents the visual readiness check from succeeding.

Manual overrides are recorded in the session trace.

### Q Key

Press:

```text
Q
```

to end the live session, save the trace, and close the camera.

---

# Live Lesson Interface

Once a lesson starts, the webcam window becomes the learner-facing activity interface.

For example:

```text
SHAPES LESSON
Item 1/3

SAY: CIRCLE

LISTENING...
```

After transcription and evaluation, the interface can display:

```text
HEARD: circle.
RESULT: CORRECT
```

The lesson then advances to the next prompt.

This prevents the learner from needing to watch the terminal to know which word should be spoken.

---

# Lesson Types

## CVC Lesson

The CVC lesson currently contains:

```text
cat
dog
sun
hat
bed
```

The activity is intended to demonstrate simple word-level speech practice.

---

## Shapes Lesson

The Shapes lesson currently contains:

```text
circle
square
triangle
```

Shapes provide a second lesson category using the same LessonAgent and speech processing architecture.

---

# Response Evaluation

Speech responses are evaluated after Whisper transcription.

Possible outcomes are:

### CORRECT

The expected word appears in the normalized transcription.

For example:

```text
Prompt:
circle

Whisper:
"that? circle!"

Result:
CORRECT
```

### NEAR_MATCH

The transcription is similar to the expected word but is not an exact match.

A text similarity threshold is used for this state.

NEAR_MATCH is a text comparison after transcription. It is not a clinical pronunciation assessment.

### INCORRECT

Speech was detected and transcribed, but the response did not sufficiently match the expected word.

### NO_INPUT

The system did not receive enough usable speech input or Whisper did not produce a usable transcription.

---

# Speech Input

watchMe supports both typed and microphone input.

## Typed Input

Typed mode provides a hardware independent way to demonstrate the LessonAgent and response evaluation pipeline.

No microphone or Whisper audio configuration is required for typed input.

---

## Microphone + Whisper

Microphone mode records local audio and uses the Whisper `tiny.en` model for English speech transcription.

Current speech configuration:

```text
Sample rate: 16000 Hz
Channels: 1
Recording duration: 3 seconds
Whisper model: tiny.en
Silence threshold: 0.001
```

Recorded audio is stored under:

```text
results/audio/
```

---

# Microphone Configuration

Audio device numbers are machine specific.

watchMe does not permanently hard-code the microphone used during development.

The application first attempts to use the system's default microphone.

If the default microphone is not the desired input device, an optional environment variable can select another device.

## List Available Microphones

Run:

```powershell
& ".\.venv\Scripts\python.exe" -m tools.speech_input
```

Choose:

```text
2. List input devices
```

The program will display the available audio input devices and their device numbers.

---

## Set a Microphone Override on Windows PowerShell

For example:

```powershell
$env:WATCHME_MIC_DEVICE="7"
```

Then run watchMe normally.

The number `7` is only an example from the development computer. Another computer may use a completely different device number.

During development, device 7 corresponded to a working Intel Smart Sound Technology microphone array on the development Windows laptop.

The environment variable affects only the current PowerShell session unless configured permanently.

---

## Default Microphone Behavior

If `WATCHME_MIC_DEVICE` is not set:

```text
watchMe
   |
   v
Operating System Default Microphone
```

If an override is set:

```text
WATCHME_MIC_DEVICE
   |
   v
Selected Input Device
```

If microphone input cannot be configured, use typed input to demonstrate the lesson pipeline.

---

# Installation

## 1. Clone the Repository

```powershell
git clone <repository-url>
cd watchMe
```

Replace `<repository-url>` with the final GitHub repository URL.

---

## 2. Create a Virtual Environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 3. Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The current direct dependencies are pinned in `requirements.txt`.

```text
mediapipe==1.0.0
opencv-contrib-python==5.0.0.93
numpy==2.2.6
openai-whisper==20250625
sounddevice==0.5.5
soundfile==0.14.0
```

Whisper will install its required supporting Python packages as dependencies.

---

# Running watchMe

## Main Live Multimodal Demo

Run:

```powershell
& ".\.venv\Scripts\python.exe" -m agents.live_lesson_orchestrator
```

The program asks for a lesson:

```text
1. CVC
2. Shapes
```

Then asks for an input mode:

```text
1. Typed
2. Microphone + Whisper
```

For the complete multimodal demonstration, select a lesson and choose microphone input.

---

# Individual Component Tests

## Visual Perception

Run:

```powershell
& ".\.venv\Scripts\python.exe" -m tools.visual_perception
```

Enter an image path when prompted.

---

## PerceptionAgent

Run:

```powershell
& ".\.venv\Scripts\python.exe" -m agents.perception_agent
```

---

## LessonAgent

Run:

```powershell
& ".\.venv\Scripts\python.exe" -m agents.lesson_agent
```

---

## Speech Input

Run:

```powershell
& ".\.venv\Scripts\python.exe" -m tools.speech_input
```

The command can:

- test microphone speech capture
- list available input devices

---

## Camera Test

Run:

```powershell
& ".\.venv\Scripts\python.exe" -m tools.camera_test
```

---

## Mouth Movement Test

The temporal mouth movement tool can process webcam or video input to determine whether visible mouth movement occurred across multiple frames.

Results include:

- total frames
- valid mouth frames
- movement detected
- movement score
- average mouth change
- processing time

---

# Evaluation

## Controlled Visual Evaluation

The current frozen visual functional validation set contains 14 controlled scenarios.

Final result:

```text
14 / 14 passed
100% task success
```

This result should be interpreted as:

> 100% task success on the current controlled 14-scenario functional validation set.

It is not a claim of general computer vision accuracy across all people, cameras, environments, or lighting conditions.

Average processing latency during the controlled evaluation was approximately:

```text
185.69 ms
```

---

# Robustness Testing

A separate robustness set was created using conditions such as:

- dark images
- blurred images
- blank images
- corrupt files
- rotated images
- grayscale images

Eight robustness scenarios were tested without an unhandled application crash.

A corrupt input produces a structured error and STOP behavior rather than terminating the application unexpectedly.

One known limitation is image orientation. Some rotated images may still be interpreted as READY because orientation correction is not currently part of the perception pipeline.

---

# Live Multimodal Validation

The integrated system has been tested with the webcam, PerceptionAgent, PlannerAgent, LessonAgent, microphone, Whisper, and live lesson interface operating together.

The official final validation session was:

`live_lesson_20260809_212807`

Observed results:

```text
Frames: 731
Perception updates: 48
Face detected: True
Face count: 1
Final state: COMPLETE
Start method: automatic_countdown
Mouth movement: True
Movement events: 18
Max mouth delta: 0.2841
Lesson completed: True
```

Lesson responses were:

```text
circle
Whisper: "circle."
Outcome: CORRECT
Audio level: 0.001266

square
Whisper: "square. square."
Outcome: CORRECT
Audio level: 0.001731

triangle
Whisper: "valve will explode."
Outcome: INCORRECT
Audio level: 0.001410
```

Final lesson result:

```text
2 correct
0 near match
1 incorrect
0 no input
```

This final run was intentionally treated as a real-world validation rather than a laboratory attempt to force a perfect score. Background noise, microphone placement, short isolated words, and Whisper transcription behavior can affect recognition. The important result is that the full multimodal system continued to produce structured outputs and completed the lesson without a `NO_INPUT` event.

The `triangle` result is interpreted as a speech-recognition error, not as a failure of the computer vision or orchestration pipeline. During the same session, watchMe successfully:

```text
detected learner
→ evaluated readiness
→ started automatically
→ displayed lesson prompts
→ observed mouth movement
→ captured all three audio attempts
→ transcribed speech
→ evaluated responses
→ completed the lesson
→ saved a structured trace
```

Earlier live runs are retained as development evidence, including one session with three `NO_INPUT` responses. Those runs demonstrate that visible mouth movement and usable microphone speech are separate signals.

A future production version could improve speech robustness by extending the listening window, allowing a limited number of retries when transcription is uncertain or incorrect, and providing a skip or typed fallback rather than moving on immediately.

---

# Failure Analysis and Iterative Development

Several failures were discovered during development and used to improve the system.

## Haar Cascade False Positive

An early face detection approach using Haar cascades produced unreliable detections.

The system was replaced with MediaPipe Face Landmarker.

---

## Planner Priority Conflict

An early planner configuration could prioritize distance before learner positioning.

The rules were updated so that major positioning problems are handled before distance-related readiness actions.

---

## Live Agent API Integration Failure

The initial `LiveLessonOrchestrator` attempted to call a generic method such as:

```text
PerceptionAgent.run()
```

The actual PerceptionAgent interface used:

```text
PerceptionAgent.perceive()
```

The orchestrator was corrected to use the real structured agent API.

---

## Bounding Box Handoff Failure

The visual perception tool generated face bounding boxes, but the original PerceptionAgent message did not preserve the bounding box coordinates.

The structured perception message was updated to include:

```text
face.boxes
```

This enabled the live learner readiness box.

---

## Speech Evaluation Issue

An early response evaluator could incorrectly reject Whisper outputs containing punctuation or repeated words.

Responses are now normalized before evaluation.

For example:

```text
"cat, cat."
```

can correctly match:

```text
cat
```

---

## Microphone Device Portability

Development initially used a hard-coded microphone device number.

Because audio device numbers are machine specific, the speech tool was updated to:

- use the system default input device when possible
- support `WATCHME_MIC_DEVICE`
- list available microphone devices
- preserve typed input as a hardware independent fallback

---

# Known Limitations

watchMe is a prototype and has several important limitations.

### Speech Recognition

Whisper transcription can be affected by:

- microphone placement
- low input volume
- background speech
- room noise
- timing
- selected input device

The current system evaluates Whisper's text transcription rather than performing acoustic pronunciation analysis.

### Camera Environment

Face detection and readiness may be affected by:

- lighting
- camera quality
- occlusion
- extreme head angles
- unusual image orientation

### Mouth Movement

Mouth movement is estimated from visible changes in mouth landmarks over time.

It should not be interpreted as proof that a particular sound or word was produced.

### Educational Scope

watchMe currently demonstrates simple word practice only.

It is not designed to:

- diagnose speech disorders
- evaluate clinical speech quality
- replace a speech language pathologist
- make medical decisions
- make high stakes decisions about a learner

---

# Privacy and Responsible Use

watchMe processes visual and audio information, which creates privacy considerations.

The prototype is designed for educational experimentation.

Recommended responsible deployment practices include:

- obtain permission before recording a learner
- minimize storage of identifiable camera or audio data
- avoid unnecessary cloud transmission
- protect stored traces and recordings
- provide users with clear notice when recording begins
- allow a human to review important outcomes
- do not interpret automated results as medical assessments

Audio recordings generated during tests are stored locally under:

```text
results/audio/
```

Developers should review these files before publishing a repository because voice recordings can contain identifiable information.

---

# Output and Trace Files

watchMe saves evidence from system operation under `results/`.

Typical outputs include:

```text
results/
├── audio/
├── images/
├── live/
├── traces/
├── evaluation_results.json
├── metrics.txt
└── batch_summary.json
```

Live lesson traces record information such as:

- session ID
- lesson type
- input mode
- start method
- camera frames
- perception updates
- face state
- planner decision
- mouth movement
- lesson prompts
- responses
- outcomes
- lesson results
- timestamps

These traces provide evidence of the handoffs between the computer vision, reasoning, and lesson components.

---

# Project Structure

```text
watchMe/
│
├── agents/
│   ├── perception_agent.py
│   ├── planner_agent.py
│   ├── lesson_agent.py
│   ├── live_lesson_orchestrator.py
│   └── orchestrator.py
│
├── tools/
│   ├── visual_perception.py
│   ├── mouth_analysis.py
│   ├── mouth_movement.py
│   ├── speech_input.py
│   ├── camera_test.py
│   ├── evaluate_agent.py
│   └── create_robustness_samples.py
│
├── lessons/
│   ├── cvc_lesson.py
│   └── shapes_lesson.py
│
├── data/
│   ├── sample/
│   ├── evaluation_cases.json
│   ├── robustness_cases.json
│   └── speech_evaluation_cases.json
│
├── models/
│   ├── face_landmarker.task
│   └── README.md
│
├── results/
│   ├── audio/
│   ├── images/
│   ├── live/
│   ├── traces/
│   ├── evaluation_results.json
│   └── metrics.txt
│
├── docs/
│   ├── architecture.md
│   ├── test_plan.md
│   ├── ethics.md
│   └── AI_usage_log.md
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

Some generated result files may be excluded from the public repository depending on privacy, licensing, and file size considerations.

---

# Reproducibility

The project uses pinned direct dependencies through:

```text
requirements.txt
```

The application avoids requiring a specific microphone device number in source code.

For a fresh setup:

```text
clone repository
→ create virtual environment
→ install requirements
→ verify camera
→ verify microphone or use typed input
→ run live lesson orchestrator
```

The main full-pipeline command is:

```powershell
& ".\.venv\Scripts\python.exe" -m agents.live_lesson_orchestrator
```

---

# Final Project Status

The current prototype has implemented:

- [x] MediaPipe face perception
- [x] still image analysis
- [x] live webcam processing
- [x] learner position analysis
- [x] distance/readiness heuristics
- [x] mouth visibility analysis
- [x] temporal mouth movement analysis
- [x] PerceptionAgent
- [x] PlannerAgent
- [x] LessonAgent
- [x] multi-agent handoffs
- [x] live lesson orchestration
- [x] blue/green readiness bounding box
- [x] automatic readiness countdown
- [x] keyboard start controls
- [x] visible lesson prompts
- [x] typed input
- [x] microphone input
- [x] local Whisper transcription
- [x] CVC lesson
- [x] Shapes lesson
- [x] response evaluation
- [x] functional evaluation
- [x] robustness testing
- [x] structured trace logging
- [x] microphone portability handling
- [x] pinned speech dependencies

Remaining submission tasks:

- [x] update final architecture documentation
- [x] update final test plan
- [x] update AI usage log with final integration work
- [x] capture final live validation evidence
- [x] confirm generated WAV recordings are excluded from Git tracking
- [ ] complete final GitHub commit and repository upload
- [ ] verify the published repository from the README instructions
- [ ] prepare the optional pitch deck / presentation bonus submission

---

# Future Work

Future development could extend watchMe with:

- additional lesson categories
- persistent learner progress
- session history
- optional local database storage
- more robust audio device selection interfaces
- improved real time performance
- longer or adaptive speech listening windows
- limited retry behavior for uncertain or incorrect transcriptions
- orientation handling
- additional visual prompts
- accessibility controls
- optional voice commands
- touchscreen lesson controls
- gesture based lesson start
- additional evaluation datasets

These are future extensions and are not required for the current computer vision capstone prototype.

---

# Course Context

watchMe was developed as a computer vision capstone project for:

**ITAI 1378 Computer Vision - Artificial Intelligence**

The project combines concepts from computer vision, image processing, neural networks, face landmark analysis, video processing, multimodal AI, agent based systems, model evaluation, robustness testing, and responsible AI design.