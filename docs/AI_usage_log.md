# watchMe AI Usage Log

## Purpose

This document records how generative AI assistance was used during the development of the watchMe computer vision capstone project.

AI was used as a development assistant for brainstorming, code drafting, debugging, documentation, interpretation of test results, and project organization.

AI did not independently execute or validate the watchMe application on the development computer.

The student performed the local implementation, ran the application, supplied test results, identified whether outputs matched the actual behavior of the system, made project-scope decisions, and decided which AI suggestions to accept, reject, or modify.

The development process generally followed this pattern:

```text
Student defines goal or reports problem
        |
        v
AI suggests implementation or debugging approach
        |
        v
Student edits or replaces project file
        |
        v
Student runs code locally
        |
        v
Student reports actual output
        |
        v
AI and student analyze result
        |
        v
System is corrected, retained, or rejected
```

This process was iterative and included multiple AI suggestions that were incomplete or incorrect and had to be corrected using actual test evidence.

---

# AI Tools Used

The primary generative AI development assistant used during the project was:

- ChatGPT

AI assistance was used for:

- Project architecture discussion
- Python code drafting
- Agent interface design
- Debugging assistance
- Evaluation design
- Test-case planning
- Speech-recognition integration
- Live webcam integration
- Documentation drafting
- Ethical and security analysis
- README organization
- Failure analysis
- GitHub preparation planning

The actual computer vision and speech processing components used by watchMe include:

- MediaPipe Face Landmarker
- OpenCV
- OpenAI Whisper
- NumPy
- SoundDevice
- SoundFile

Whisper is part of the application's runtime speech-recognition pipeline and is separate from the conversational AI assistance used during project development.

---

# Student Responsibilities

The student remained responsible for:

- Selecting watchMe as the capstone concept
- Connecting watchMe to the larger MirrorMe concept
- Deciding the educational speech-practice use case
- Defining the project scope
- Running all local Python commands
- Running webcam tests
- Running microphone tests
- Speaking the test responses
- Reviewing camera behavior
- Reviewing Whisper output
- Reporting errors and trace results
- Determining whether a suggested change actually worked
- Deciding when the prototype had sufficient functionality
- Rejecting unnecessary feature expansion
- Preserving failure cases
- Determining the final project direction
- Preparing the repository for submission

AI-generated suggestions were not treated as proof that a feature worked.

Features were considered implemented only after local testing produced usable evidence.

---

# Early Project Architecture Assistance

AI assistance was used to organize the project into separate responsibilities instead of placing the entire application into one Python file.

The architecture developed around:

- Computer vision tools
- PerceptionAgent
- PlannerAgent
- LessonAgent
- Orchestrators
- Evaluation utilities
- Trace files
- Lesson files
- Documentation

AI suggested separating low-level computer vision functionality from higher-level reasoning.

This contributed to the architecture:

```text
Computer Vision Tools
        |
        v
PerceptionAgent
        |
        v
PlannerAgent
        |
        v
Action / Lesson
```

The student retained this architecture because it matched the course emphasis on computer vision agents.

---

# Face Detection Development

An early implementation used an OpenCV Haar cascade for face detection.

Testing by the student showed a false positive on:

`smiling.jpg`

The Haar detector placed a bounding box over background content instead of correctly identifying the learner.

The student supplied the observed result.

AI assistance was used to analyze the failure and discuss alternatives.

The decision was made to replace Haar cascade detection with MediaPipe Face Landmarker.

This change was based on actual observed behavior, not solely on an AI recommendation.

The failure was retained in the project documentation.

---

# MediaPipe Face Landmarker Integration

AI assistance was used to draft and organize code for:

- Image validation
- MediaPipe Face Landmarker execution
- Face-count extraction
- Bounding-box calculation
- Learner centering
- Relative face-size estimation
- Structured readiness states
- Trace output

The student ran the implementation against sample images and reported the observed outputs.

Prototype thresholds were adjusted and evaluated based on the resulting measurements.

The final thresholds are documented as heuristics and not universal measurements.

---

# Mouth Analysis Assistance

AI assistance was used to organize the mouth-analysis implementation around MediaPipe facial landmarks.

The prototype calculated a mouth-open ratio using inner-lip and mouth-corner landmarks.

The student ran the code on several images and supplied measured ratios.

Examples included:

```text
manclosed.jpg
0.0000

manclosedsmiling.jpg
0.0139

man smiling.jpg
0.1134

womansmiling.jpg
0.1970

smiling.jpg
0.2407

manmouthopen.jpg
0.8200
```

The current mouth-open threshold of:

`0.08`

was retained as a prototype heuristic after reviewing these results.

AI did not generate these measurements independently. They came from student-run program output.

---

# PerceptionAgent Assistance

AI assistance was used to draft a PerceptionAgent that combined:

- Face detection
- Face count
- Position
- Size
- Mouth analysis
- Readiness
- Artifact paths
- Performance information

The student tested the agent locally and provided errors and outputs as development continued.

A later live-integration problem revealed that the PerceptionAgent message was not preserving every piece of information needed by the user interface.

That issue is documented later in this log.

---

# PlannerAgent Assistance

AI assistance was used to design the PlannerAgent as an explicit rule-based reasoning layer.

This was intentionally chosen instead of using a generative model to make readiness decisions.

The PlannerAgent evaluates states such as:

- No learner
- Multiple learners
- Learner position
- Learner distance
- Mouth visibility
- Ready

AI assistance was also used to organize the structured output into:

```text
state
reason
action
```

The student ran the planner against actual perception outputs.

---

# Planner Response Schema Failure

During automated evaluation, the student discovered that the missing-input case did not follow the same output structure as normal planner decisions.

Normal decisions were structured dictionaries while one error path returned:

`STOP`

differently.

AI assistance was used to identify the inconsistent schema.

The PlannerAgent was standardized so normal and error decisions followed the same structured format.

The student reran the evaluation to confirm the correction.

---

# Automated Evaluation Assistance

AI assistance was used to design:

`tools/evaluate_agent.py`

and the controlled evaluation workflow using:

`data/evaluation_cases.json`

The purpose was to avoid evaluating the project only through manually selected successful examples.

An initial evaluation produced:

```text
8 / 8 passed
100%
```

However, the student and AI review identified that this dataset was too limited because many examples resulted in the same action.

The student decided that additional scenarios were required.

The evaluation was expanded to 14 controlled scenarios.

---

# Planner Priority Failure

The expanded evaluation exposed a failure involving:

`leftsidesmile.jpg`

The PerceptionAgent correctly identified the learner as off center, but the PlannerAgent could return:

`MOVE_CLOSER`

because the learner was also relatively far from the camera.

AI assistance was used to analyze the competing conditions.

The student agreed that learner positioning should take priority over fine-tuning camera distance.

The planner priority was changed to evaluate positioning before distance.

An intermediate evaluation result of:

```text
13 / 14
92.86%
```

was preserved in the development history rather than removed.

After the planner policy and evaluation expectations were reconciled, the final frozen evaluation produced:

```text
14 / 14
```

The result is documented as controlled functional task success rather than universal model accuracy.

---

# Evaluation Expectation Review

A second evaluation issue involved:

`womansmiling.jpg`

The expected decision and actual decision differed.

Instead of changing the expected answer automatically, the student inspected the perception measurements.

The actual measurements showed that the learner was outside the configured centering tolerance.

The student and AI review determined that:

`REPOSITION`

was consistent with the already-defined planner policy.

The expected labels were then frozen.

This step was important to avoid modifying expected outputs merely to create a perfect evaluation score.

---

# Robustness Testing Assistance

AI assistance was used to design a separate robustness set rather than changing the original controlled functional evaluation.

Conditions included:

- Dark image
- Blurry image
- Grayscale image
- Rotated images
- Upside-down image
- Blank image
- Corrupt image

The student executed these tests locally.

The results exposed a useful limitation:

Some 90-degree rotated faces could still return:

`READY`

AI assistance was used to interpret this as an orientation limitation rather than a reason to hide or remove the test.

All eight stress inputs were retained in the documentation.

---

# Temporal Mouth Movement Assistance

AI assistance was used to design:

`tools/mouth_movement.py`

The purpose was to move beyond still-image mouth analysis and add temporal computer vision.

The implementation compared mouth geometry across frames and calculated a movement score.

The student performed live webcam testing.

One student-run test produced:

```text
337 total frames
337 valid mouth frames
Movement detected: True
Movement score: 0.4427
Average delta: 0.026
```

AI assistance was used to interpret the timing and movement results.

The student decided that perfect real-time frame rate was not required for the capstone.

---

# Webcam Configuration Assistance

AI assistance was used while testing different OpenCV camera configurations.

The student ran camera tests using:

- Default OpenCV capture
- DirectShow
- Windows Media Foundation
- Multiple camera indices

Camera index:

`0`

worked on the development system at approximately:

`640 x 480`

Other indices failed.

The working configuration was based on actual student testing.

---

# Whisper Integration Assistance

AI assistance was used to add local Whisper speech recognition to watchMe.

The speech pipeline was organized as:

```text
Microphone
→ SoundDevice
→ Audio-level measurement
→ WAV artifact
→ Whisper tiny.en
→ Transcription
→ Lesson evaluation
```

The student installed and tested the required packages locally.

The final direct dependencies were recorded as:

```text
openai-whisper==20250625
sounddevice==0.5.5
soundfile==0.14.0
```

---

# Microphone Device Troubleshooting

Several microphone devices were tested.

Device `2` initially produced weak results.

Device `7` produced substantially better audio on the development Windows computer.

A direct student-run test produced approximately:

```text
Audio level: 0.008266
Transcription: cat, cat.
Status: success
```

This established device `7` as the known-good development microphone.

AI assistance was used to interpret microphone levels and device behavior.

The device number was later removed as a hard-coded application requirement because it is computer-specific.

---

# Silence Threshold Failure

The initial speech-input implementation used a silence threshold of:

`0.003`

Student testing produced quiet recordings such as:

```text
dog: 0.001931
sun: 0.001868
hat: 0.001960
```

These recordings were being rejected before Whisper could attempt transcription.

AI assistance was used to analyze the observed audio levels.

The threshold was changed to:

`0.001`

The change was based on actual student-run recordings.

---

# Repeated-Word Evaluation Failure

During one test, the student intentionally repeated lesson words.

Whisper returned responses including:

```text
cat cat
dog. dog.
sun sun
bed. bed.
```

The original evaluator marked some repeated correct responses as incorrect because it compared the complete transcription directly with the expected target.

The student reported the result.

AI assistance was used to identify the exact-string comparison as the problem.

The evaluator was updated to normalize punctuation and identify expected words within a longer response.

This is an example where testing changed the application logic.

---

# NEAR_MATCH Assistance

AI assistance was used to add a simple text-based:

`NEAR_MATCH`

state.

The student then performed deliberate near-match tests.

Examples included:

```text
cat → cap
dog → dot
hat → hot
```

The observed Whisper outputs were supplied by the student.

The feature was intentionally documented as text similarity rather than pronunciation analysis.

AI assistance was also used to ensure that project documentation did not make clinical claims about this feature.

---

# Background Speech Limitation

The student reported that some tests occurred while movie or television dialogue was present.

Whisper sometimes transcribed unrelated background speech.

AI assistance was used to analyze this as a real-world microphone and speech-recognition limitation.

The limitation was retained in the final documentation.

The project was not modified to pretend that every incorrect transcription came from learner pronunciation.

---

# Shapes Lesson Assistance

After the CVC lesson worked, AI assistance was used to create a second educational activity:

`Shapes`

The goal was to show that LessonAgent could support more than one lesson type without adding unnecessary scope.

The Shapes lesson uses:

- circle
- square
- triangle

The student decided not to add Numbers or Letters because CVC and Shapes already demonstrated reusable lesson behavior and further categories would add development time without proving a substantially new capability.

---

# Shapes Evaluator Failure

During a camera and microphone concurrency test, Whisper successfully transcribed:

```text
the circle.
square.
triangle.
```

However, the Shapes evaluator marked:

`the circle.`

incorrectly.

The CVC evaluator had already been improved to normalize longer responses, but Shapes had not received the same logic.

The student reported this discrepancy.

AI assistance was used to identify the inconsistent evaluator implementations.

Shapes was updated to use the same normalized response evaluation strategy as CVC.

---

# Camera and Microphone Concurrency Test

Before the final integrated application was created, AI assistance was used to plan a concurrency test.

The student ran:

`tools.mouth_movement.py`

and:

`agents.lesson_agent.py`

at the same time.

The student-run camera result included:

```text
331 frames
331 valid mouth frames
Movement detected: True
Movement score: 0.2999
```

Whisper simultaneously recognized the Shapes responses.

This confirmed that the webcam and microphone could operate at the same time on the development computer.

The result justified proceeding to single-process integration.

---

# Initial LiveLessonOrchestrator Assistance

AI assistance was used to draft a:

`LiveLessonOrchestrator`

to connect:

```text
Webcam
→ PerceptionAgent
→ PlannerAgent
→ readiness
→ LessonAgent
```

The first version did not work correctly.

The webcam displayed the learner, but the application reported:

```text
Perception updates: 0
Face detected: False
Face count: 0
```

The student supplied the local output.

---

# Misstep: Considering Additional Training or Sample Data

When the live application initially failed to recognize the learner, one possible explanation considered during debugging was insufficient sample data.

This turned out to be incorrect.

The student tested the actual saved webcam frame directly with:

`visual_perception.py`

The frame successfully returned:

```text
face_detected: True
face_count: 1
face_centered: True
face_position: center
readiness: ready
```

This proved that the computer vision model was functioning.

Additional training data would not have fixed the actual problem.

The failure existed in application integration.

This was an important debugging lesson: isolate the failing layer before changing the model or dataset.

---

# AI Integration Mistake: Incorrect PerceptionAgent API

One of the most important AI-generated mistakes occurred during the first live orchestration implementation.

The AI-assisted code assumed that PerceptionAgent might expose generic methods such as:

```text
run()
process()
analyze()
```

The actual class interface was:

```text
perceive()
```

The application produced:

```text
PerceptionAgent has no supported run/process/analyze method.
```

The student supplied the actual PerceptionAgent source and error output.

The AI-assisted implementation was corrected to use:

```text
PerceptionAgent.perceive()
PlannerAgent.plan()
LessonAgent.run()
```

This failure is retained because it demonstrates that AI-generated code must be checked against the real project API.

AI suggestions were not assumed to be correct simply because they compiled conceptually.

---

# PerceptionAgent Import Failure

During one integration rewrite, the application produced:

```text
ImportError:
cannot import name 'PerceptionAgent'
from 'agents.perception_agent'
```

The student reported the error.

AI assistance was used to reconstruct the module with the intended class structure.

The student then ran an import test locally to confirm that the class could be loaded.

Again, the successful import was determined through actual execution, not AI assumption.

---

# Bounding Box Handoff Failure

The visual perception tool already generated face-box coordinates.

However, the PerceptionAgent structured message did not preserve:

`face_boxes`

As a result, the live orchestrator could know that the learner was detected but could not draw the intended readiness bounding box.

The student supplied the relevant project file.

AI assistance was used to trace the missing field across the tool-to-agent boundary.

The PerceptionAgent message was updated to include:

```text
face:
    boxes
```

The student reran the application and confirmed that the learner-facing box could be displayed.

---

# Readiness Interface Assistance

AI assistance was used to design a simple readiness interface.

The student approved:

- Blue box for detected but not ready
- Green box for ready

The interface reflects the PlannerAgent result rather than replacing it.

The system also separates:

```text
READY
```

from:

```text
LESSON_RUNNING
```

through an:

`ARMED`

state and countdown.

The student decided that automatically recording immediately after readiness would be too abrupt.

---

# Automatic Lesson Start Assistance

AI assistance was used to implement:

```text
READY
→ readiness confirmation
→ ARMED
→ countdown
→ lesson
```

Additional controls included:

- `S` to start early while ready
- `M` for manual demonstration override
- `Q` to quit and save the trace

The manual override is intentionally recorded in the trace rather than hidden.

---

# First Successful Integrated Run

The first major integrated live test successfully connected:

- Webcam
- PerceptionAgent
- PlannerAgent
- Automatic readiness
- LessonAgent
- Microphone
- Mouth movement

The student-run session produced evidence including:

```text
Face detected: True
Face count: 1
Final state: COMPLETE
Start method: automatic_countdown
Mouth movement: True
Lesson completed: True
```

However, this success exposed a major usability problem.

---

# Failure: Lesson Prompt Hidden from Learner

The first integrated Shapes lesson technically worked, but the prompts were printed only in the terminal.

The student was watching the webcam window and could not see whether the lesson wanted:

- circle
- square
- triangle

The student therefore responded with unrelated speech such as:

`yes, yes, yes`

to verify that speech recording was active.

The problem was not computer vision or speech recognition.

It was the interface between LessonAgent and the learner-facing application.

AI assistance was used to design a callback system.

---

# Lesson Callback Assistance

The lesson files and LessonAgent were updated so the lesson could emit events such as:

```text
lesson_started
prompt
listening
response
outcome
lesson_complete
```

The LiveLessonOrchestrator receives these events and displays them inside the webcam window.

This allows the learner to see:

```text
SAY: CIRCLE
LISTENING...
```

followed by:

```text
HEARD: circle.
RESULT: CORRECT
```

The student reran the application to validate the interface.

---

# Integrated NO_INPUT Failure Run

One final live Shapes run completed the entire application workflow but produced:

```text
0 correct
0 near match
0 incorrect
3 no_input
```

The student-run session included:

```text
Frames: 644
Perception updates: 42
Face detected: True
Mouth movement: True
Movement events: 10
Lesson completed: True
```

The microphone audio levels were very low.

AI assistance was used to interpret this correctly.

The result was retained because it proves that:

```text
Visible mouth movement
```

does not automatically mean:

```text
Usable microphone speech
```

No attempt was made to hide this failure.

---

# Final Successful Integrated Run

The student then completed another live Shapes test.

Observed results included:

```text
Session:
live_lesson_20260809_155131

Frames:
667

Perception updates:
44

Face detected:
True

Face count:
1

Final visual readiness:
ready

Final state:
COMPLETE

Start method:
automatic_countdown

Mouth movement:
True

Movement events:
17

Maximum mouth delta:
0.4491

Lesson completed:
True
```

Lesson results included:

```text
circle
Whisper: "that? circle!"
Outcome: CORRECT

square
Whisper: "square."
Outcome: CORRECT

triangle
Outcome: NO_INPUT
```

Final lesson summary:

```text
2 correct
0 near match
0 incorrect
1 no input
```

AI assistance was used to interpret and document the run.

The result is not reported as 66.7 percent model accuracy.

It is used as evidence that the complete multimodal workflow operated successfully.

---

# Final Real-World Validation Decision

After the integrated system was working, the student performed a final Shapes lesson validation using the known-good development microphone through:

```powershell
$env:WATCHME_MIC_DEVICE="7"
```

The official final session was:

`live_lesson_20260809_212807`

Observed results included:

```text
Frames: 731
Perception updates: 48
Face detected: True
Face count: 1
Final state: COMPLETE
Start method: automatic_countdown
Mouth movement: True
Movement events: 18
Maximum mouth delta: 0.2841
Lesson completed: True
```

Lesson outcomes were:

```text
circle
Whisper: "circle."
Outcome: CORRECT

square
Whisper: "square. square."
Outcome: CORRECT

triangle
Whisper: "valve will explode."
Outcome: INCORRECT
```

Final lesson summary:

```text
2 correct
0 near match
1 incorrect
0 no input
```

The student explicitly decided not to continue repeating the test until a perfect score appeared.

The test environment could not be guaranteed to be completely silent, and the project is intended to demonstrate behavior under realistic conditions rather than only ideal laboratory conditions.

AI assistance was used to help interpret the final result and distinguish the failing layer.

The final evidence showed that:

```text
Computer vision perception worked
Planner/readiness logic worked
Automatic lesson start worked
Mouth movement detection worked
Microphone capture worked for all three items
Whisper produced one incorrect transcription
Lesson evaluation correctly classified that transcription as INCORRECT
The lesson still completed and saved a trace
```

The student chose to retain the 2-of-3 result as the official final validation because it demonstrates both successful operation and a realistic limitation.

A future improvement discussed with AI assistance was to make the speech interaction more tolerant by:

- Extending or adapting the listening window
- Allowing a limited number of retries when the expected word is not recognized
- Providing a skip or typed fallback after the retry limit

The student intentionally did not implement this additional feature before submission because the project scope had already been frozen.

---

# Microphone Portability Assistance

The original speech tool permanently used:

`MIC_DEVICE = 7`

The student raised concern that another computer would not necessarily assign the same number to its microphone.

AI assistance was used to change the design to:

```text
No override
→ system default microphone

WATCHME_MIC_DEVICE set
→ explicitly selected microphone
```

Typed lesson input remains available as a hardware-independent fallback.

---

# AI Mistake: SoundDevice Default Device Handling

The first AI-assisted portability implementation incorrectly assumed that:

`sd.default.device`

would behave like a normal integer, list, or tuple.

With the installed:

`sounddevice==0.5.5`

the student received:

```text
int() argument must be a string,
a bytes-like object or a real number,
not '_InputOutputPair'
```

The student supplied the actual error.

The AI-assisted code was corrected to support the `_InputOutputPair` behavior and extract the input device properly.

This is another example where an AI-generated implementation required validation against the exact installed library version.

---

# Default Microphone Test

After the portability correction, the student ran another speech test without an explicit microphone override.

The application successfully selected an operating-system default device and saved an audio file.

Observed result:

```text
status: no_input
audio_level: 4.418115713633597e-05
```

This showed that the portability code was functioning, but the Windows default microphone on the development machine was nearly silent.

The student decided not to hard-code device `7` again.

Instead:

- The repository remains portable
- Device `7` can be selected for the development demonstration
- Another user can identify their own microphone
- Typed input remains available

The README documents this behavior.

---

# Requirements Assistance

AI assistance was used to organize the final direct dependency list.

The student queried the installed environment and supplied the actual package versions.

The final requirements use:

```text
mediapipe==1.0.0
opencv-contrib-python==5.0.0.93
numpy==2.2.6
openai-whisper==20250625
sounddevice==0.5.5
soundfile==0.14.0
```

The versions were based on the student environment rather than invented by AI.

---

# Reproducibility Assistance

AI assistance was used to plan an isolated virtual-environment test.

The student created:

`.venv_test`

and installed the documented original computer vision requirements.

The student then reran the frozen visual evaluation.

Observed result:

```text
14 / 14 passed
```

This provided evidence that the core computer vision pipeline was not dependent on undocumented packages in the original environment.

Speech dependencies were added afterward and documented separately.

---

# Documentation Assistance

AI assistance was used extensively to organize project documentation.

Documents assisted by AI include:

- `README.md`
- `docs/architecture.md`
- `docs/test_plan.md`
- `docs/ethics.md`
- `docs/AI_usage_log.md`

The student supplied:

- Actual architecture
- Test results
- Error messages
- File names
- Local output
- Design preferences
- Final project-scope decisions

AI assistance was used to organize those details into readable documentation.

The documentation was not intended to invent tests that were never performed.

---

# Ethics and Responsible AI Assistance

AI assistance was used to identify ethical and security considerations associated with a camera-and-microphone educational system.

Topics included:

- Consent
- Privacy
- Camera data
- Voice data
- Child safety
- Human oversight
- Bias
- Accessibility
- Local processing
- Data minimization
- Least privilege
- Security of future persistent memory
- Transparent failure states
- Avoiding medical claims

The student decided to define watchMe explicitly as an educational prototype rather than a diagnostic system.

---

# Scope Decisions Made by the Student

AI assistance occasionally suggested possible additional capabilities.

Examples included:

- ProgressAgent
- SQLite persistent session memory
- Additional lesson categories
- Numbers
- Letters
- More extensive progress tracking

The student decided not to continue expanding the feature set.

The final scope was intentionally frozen around:

- CVC practice
- Shapes practice
- PerceptionAgent
- PlannerAgent
- LessonAgent
- LiveLessonOrchestrator
- Camera input
- Mouth movement
- Microphone/Whisper input
- Typed fallback
- Evaluation
- Traceability

ProgressAgent and SQLite were moved to future work.

Numbers and Letters were not implemented.

This is important because final project decisions were made by the student rather than automatically following every AI suggestion.

---

# Examples of AI Suggestions That Required Correction

Several AI-assisted ideas or implementations required correction during the project.

## Incorrect PerceptionAgent method assumptions

AI assumed methods such as:

`run()`

instead of inspecting the actual:

`perceive()`

interface.

## SoundDevice type assumption

AI initially mishandled:

`_InputOutputPair`

during microphone portability work.

## Initial live debugging direction

Additional training/sample data was briefly considered even though the real problem was integration.

Direct testing of the saved webcam frame disproved that hypothesis.

## Hidden lesson-interface problem

The original integration focused on connecting components technically but did not initially provide learner-facing lesson prompts.

Real use exposed the missing UI requirement.

These cases demonstrate why AI assistance was treated as a development aid rather than an unquestionable source.

---

# Validation Principle

Throughout development, the project used the following rule:

> AI-generated code or analysis is not considered validated until the student runs the system and reviews the result.

For example:

An AI suggestion that:

```text
This should detect the learner
```

was not sufficient evidence.

The project instead relied on outputs such as:

```text
face_detected: True
face_count: 1
readiness: ready
```

generated during actual local execution.

Likewise, a lesson was not considered functional until the student:

- Saw the prompt
- Spoke the response
- Observed Whisper output
- Observed the lesson result
- Verified completion

---

# How AI Changed the Development Process

AI assistance helped accelerate:

- Code drafting
- Debugging hypothesis generation
- Project organization
- Documentation
- Comparison of expected and observed results

However, the iterative process also demonstrated several limitations of AI-assisted development.

AI can:

- Assume interfaces incorrectly
- Produce code incompatible with a specific library version
- Miss usability problems
- Suggest unnecessary features
- Misidentify the failing layer of a system

For that reason, actual testing remained necessary throughout the project.

---

# Final AI Usage Summary

Generative AI was used as a collaborative programming and documentation assistant throughout watchMe development.

The student remained responsible for:

```text
Project concept
→ requirements
→ implementation decisions
→ local execution
→ hardware testing
→ interpretation of actual outputs
→ feature acceptance or rejection
→ final scope
→ submission
```

AI primarily assisted with:

```text
Brainstorming
→ drafting
→ debugging suggestions
→ code organization
→ documentation
→ interpretation
```

The final watchMe project therefore represents an AI-assisted development workflow rather than an automatically generated and unverified application. The final multimodal validation was also preserved with an imperfect 2-of-3 speech result instead of being repeated until a perfect score appeared.

One of the most important lessons from the project was that AI-generated suggestions still require the same engineering discipline as any other proposed solution:

```text
Inspect
→ Test
→ Measure
→ Debug
→ Document
```

The failures recorded throughout the project demonstrate that process.