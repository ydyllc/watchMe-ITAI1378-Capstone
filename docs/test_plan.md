# watchMe Test Plan and Evaluation Record

## Purpose

This document records the testing, failures, corrections, evaluation results, robustness findings, and final multimodal validation performed during development of the watchMe computer vision speech-practice agent.

The purpose of the testing process was not only to produce successful outputs. Failures and unexpected behavior were retained because they helped identify weaknesses in the computer vision pipeline, agent communication, lesson logic, speech input, and live user interface.

The development process generally followed this pattern:

```text
Test
→ Observe failure or unexpected behavior
→ Identify likely cause
→ Modify the system
→ Retest
→ Preserve the result
```

watchMe is an educational prototype. Test results should not be interpreted as medical, clinical, or universal computer vision accuracy.

---

# Test Areas

The project was evaluated across several areas:

1. Face detection
2. Mouth analysis
3. PlannerAgent reasoning
4. Automated visual evaluation
5. Robustness testing
6. Live webcam processing
7. Temporal mouth movement
8. Speech input
9. Whisper transcription
10. Lesson evaluation
11. Camera and microphone concurrency
12. Multi-agent integration
13. Live learner interface
14. Microphone portability
15. Clean-environment reproducibility

---

# Failure Case: Haar Cascade Face Detection

The initial OpenCV Haar cascade detector produced a false positive on the `smiling.jpg` test image.

Instead of placing the bounding box around the learner's face, the detector placed a box over background content.

This showed that the Haar cascade approach was not sufficiently reliable for watchMe, especially when:

- The face was tilted
- The face was not perfectly frontal
- Background features resembled Haar detector patterns

The failure artifact was preserved under:

`results/images/haar_false_positive_smiling.jpg`

## Decision

The Haar cascade detector was replaced with MediaPipe Face Landmarker.

MediaPipe provided more reliable facial landmark information and also supported the later mouth-analysis features required by watchMe.

---

# Mouth Analysis Preliminary Tests

Several images were used to validate the first mouth-state heuristic.

| Test Input | Expected Result | Observed Result |
| --- | --- | --- |
| `manclosed.jpg` | Closed mouth | Closed, ratio `0.0000` |
| `manclosedsmiling.jpg` | Closed mouth | Closed, ratio `0.0139` |
| `man smiling.jpg` | Open mouth | Open, ratio `0.1134` |
| `womansmiling.jpg` | Open mouth | Open, ratio `0.1970` |
| `smiling.jpg` | Open mouth | Open, ratio `0.2407` |
| `manmouthopen.jpg` | Open mouth | Open, ratio `0.8200` |
| `dog smiling.jpg` | Reject non-human input | No human face detected |

The current mouth-open threshold is:

`0.08`

This value is a prototype heuristic based on development observations.

It is not a medically validated measurement.

---

# Preliminary Automated Agent Evaluation

An automated evaluation harness was created using:

`data/evaluation_cases.json`

and:

`tools/evaluate_agent.py`

The evaluator processes labeled scenarios through the agent workflow and compares the expected PlannerAgent decision against the actual result.

---

## First Evaluation Failure: Planner Response Schema

The first automated evaluation did not complete correctly on the missing-file test.

Normal PlannerAgent decisions were returned as structured dictionaries, but the perception-error path returned:

`STOP`

in a different format.

This produced an evaluation integration problem.

## Fix

The PlannerAgent response schema was standardized.

Every planner response now contains:

```text
agent
status
decision
    state
    reason
action
    message
```

The missing-file test then correctly produced:

`STOP`

through the same structured schema used by normal decisions.

This was an important early integration failure because the underlying decision was correct, but inconsistent message formatting prevented reliable orchestration and evaluation.

---

# Preliminary Eight-Case Baseline

After standardizing the PlannerAgent response schema, the initial evaluation produced:

- Total scenarios: `8`
- Passed: `8`
- Failed: `0`
- Preliminary task success rate: `100.00%`
- Average end-to-end latency: `181.76 ms`

Artifacts:

`results/evaluation_results.json`

`results/metrics.txt`

---

## Limitation of the Eight-Case Baseline

The initial 100 percent result was not considered sufficient evidence of final performance.

Most human examples in the initial set produced similar decisions, particularly:

`MOVE_CLOSER`

The evaluation did not yet provide enough coverage of the full PlannerAgent decision space.

Additional scenarios were therefore added for:

- `READY`
- `MOVE_BACK`
- `REPOSITION`
- `ONE_LEARNER_REQUIRED`
- Mouth visibility
- Missing input
- Non-human input

Robustness conditions were kept separate from the main functional evaluation.

This prevented the project from presenting an easy preliminary dataset as final evidence.

---

# Expanded 14-Scenario Evaluation

The controlled functional evaluation was expanded to:

`14` scenarios.

An intermediate run produced:

- Total scenarios: `14`
- Passed: `13`
- Failed: `1`
- Task success rate: `92.86%`

The remaining failure involved:

`leftsidesmile.jpg`

---

# Failure Case: Planner Priority Conflict

Direct perception testing showed that `leftsidesmile.jpg` correctly identified the learner as off center.

However, one version of PlannerAgent returned:

`MOVE_CLOSER`

instead of:

`REPOSITION`

The learner simultaneously satisfied more than one corrective condition:

- Off center
- Relatively far from the camera

The original planner evaluated distance before positioning.

## Decision

An explicit decision priority was introduced.

The final priority order is:

1. Perception error
2. No learner
3. Multiple learners
4. Learner position
5. Learner distance
6. Mouth analysis availability
7. Mouth visibility
8. Ready

The intended reasoning is that watchMe should first guide the learner into the accepted camera region before fine-tuning camera distance.

After the rule was corrected, the expected action for `leftsidesmile.jpg` became:

`REPOSITION`

---

# Evaluation Expectation Reconciliation

Another case involving:

`womansmiling.jpg`

initially raised concern because the observed action differed from an earlier expected label.

The actual perception measurements were inspected.

The learner was outside the configured vertical centering tolerance.

The existing PlannerAgent policy therefore correctly produced:

`REPOSITION`

The expected result was reconciled with the already-defined perception measurements and planner policy.

After this review, the evaluation labels were frozen.

This distinction is important because expected labels were not repeatedly changed simply to force the test suite to pass.

---

# Final Frozen Visual Evaluation

After the PlannerAgent priority rules and evaluation definitions were finalized, the controlled functional validation set produced:

- Total scenarios: `14`
- Passed: `14`
- Failed: `0`
- Controlled task success rate: `100.00%`
- Average observed latency: approximately `185.69 ms`

The correct interpretation of this result is:

> 100% task success on the current controlled 14-scenario functional validation set.

It should not be interpreted as:

- Universal face-detection accuracy
- Universal readiness accuracy
- Clinical validity
- Performance across every camera or environment

Definitions are stored under:

`data/evaluation_cases.json`

Results are stored under:

`results/evaluation_results.json`

Metrics are stored under:

`results/metrics.txt`

The original 13/14 intermediate result remains part of the development history because it exposed the planner priority issue.

---

# Robustness and Stress Testing

A separate robustness set was created using a previously valid learner image.

The purpose was to observe behavior outside the primary functional benchmark without altering the frozen 14-case evaluation.

Conditions included:

- Reduced brightness
- Heavy blur
- Grayscale
- 90-degree rotation
- Upside-down orientation
- Blank image
- Corrupt image

| Input | Observed Decision | Key Observation |
| --- | --- | --- |
| `dark.jpg` | READY | Face and mouth landmarks remained detectable under reduced brightness. |
| `blurry.jpg` | READY | Detection continued despite substantial blur. |
| `black_white.jpg` | READY | Grayscale conversion did not prevent facial landmark detection. |
| `rotated_left.jpg` | READY | Face was still detected after a 90-degree rotation. |
| `rotated_right.jpg` | READY | Face was still detected after a 90-degree rotation. |
| `upside_down.jpg` | REPOSITION | Orientation altered position and mouth measurements. |
| `blank.jpg` | WAIT_FOR_USER | No learner was detected and the system safely waited. |
| `corrupt.jpg` | STOP | Invalid input was propagated through the agent error path without crashing. |

---

## Robustness Findings

All eight robustness cases were handled without an unhandled application exception.

The corrupt-image case demonstrated successful error propagation:

```text
OpenCV decode failure
→ structured perception error
→ PlannerAgent
→ STOP
→ saved result
```

The rotation cases revealed an important limitation.

Some 90-degree rotated faces can still satisfy the current readiness rules because watchMe does not explicitly evaluate camera or head orientation.

Therefore:

`READY`

on a rotated image does not mean the input is appropriate for a real speech-practice session.

The upside-down test also changed mouth geometry measurements substantially.

These behaviors are documented as limitations rather than hidden by modifying the test set.

---

# Live Webcam Mouth Movement Test

A live webcam test was completed using:

Camera index:

`0`

Observed results:

- Total frames processed: `337`
- Valid mouth frames: `337`
- Movement detected: `True`
- Movement score: `0.4427`
- Average frame-to-frame mouth delta: `0.026`
- Processing time: `31527.25 ms`

Trace:

`results/traces/camera_session_movement_trace.json`

This test confirmed that watchMe could:

- Access the webcam
- Detect a learner continuously
- Locate the learner's mouth
- Compare mouth geometry across frames
- Detect temporal mouth movement

This was an important step beyond isolated still-image analysis.

The implementation processed approximately 10 to 11 frames per second during this test.

A known performance limitation is that MediaPipe model handling could be optimized further instead of repeatedly performing expensive processing during sampled frames.

---

# Fresh Environment Reproducibility Test

A separate virtual environment named:

`.venv_test`

was created to test whether the original computer vision pipeline depended on undocumented packages from the development environment.

The original documented CV dependencies were:

```text
mediapipe==1.0.0
opencv-contrib-python==5.0.0.93
numpy==2.2.6
```

The complete 14-case visual evaluation was executed from the clean environment.

Result:

- `14` scenarios
- `14` passed
- `0` failed

This confirmed reproducibility of the core computer vision pipeline using the documented dependencies.

Speech dependencies were added later in development and are now pinned separately in the final `requirements.txt`.

---

# Speech and Lesson Functional Testing

watchMe was later expanded beyond visual readiness to include:

- Microphone recording
- Local Whisper transcription
- LessonAgent
- CVC practice
- Shapes practice
- Typed input
- Response scoring

The microphone path is:

```text
Microphone
    |
    v
sounddevice
    |
    v
Audio-level measurement
    |
    v
Silence validation
    |
    v
Saved WAV file
    |
    v
Whisper tiny.en
    |
    v
Transcription
    |
    v
Lesson evaluator
```

---

# Direct Microphone Test

A direct speech-input test was performed using microphone device:

`7`

on the development Windows computer.

The word:

`cat`

was spoken twice.

Observed result:

- Audio level: approximately `0.008266`
- Whisper transcription: `cat, cat.`
- Status: `success`

This confirmed:

- Microphone recording
- WAV generation
- Whisper model loading
- Local speech transcription
- Structured speech output

---

# Failure Case: Silence Threshold Too High

An early microphone lesson used a silence threshold of:

`0.003`

Observed approximate audio levels included:

| Target | Audio Level |
| --- | ---: |
| cat | `0.000038` |
| dog | `0.001931` |
| sun | `0.001868` |
| hat | `0.001960` |
| bed | `0.003182` |

Only the final `bed` recording exceeded the threshold.

Whisper successfully returned:

`bed.`

and the evaluator returned:

`CORRECT`

The earlier recordings were being rejected before Whisper could process them.

## Fix

The silence threshold was lowered from:

`0.003`

to:

`0.001`

The threshold change was based on observed test data.

---

# Failure Case: Repeated Words Marked Incorrect

A microphone test intentionally repeated each CVC word.

Whisper produced examples including:

- `cat cat`
- `dog. dog.`
- `sun sun`
- `hut, hut.`
- `bed. bed.`

The speech-recognition pipeline was clearly receiving audio.

However, the original evaluator compared the complete Whisper transcription string directly with the target.

For example:

```text
Expected:
cat

Transcription:
cat cat

Original result:
INCORRECT
```

This exposed an evaluator problem rather than a microphone problem.

## Fix

Responses were normalized into individual words.

The evaluator was changed so that if the expected target appears anywhere in the recognized words, the response can be marked:

`CORRECT`

Punctuation is also normalized before comparison.

---

# Normal-Volume CVC Test

After lowering the silence threshold and updating the response evaluator, another CVC microphone test produced:

| Target | Whisper Output | Outcome |
| --- | --- | --- |
| cat | `cat.` | CORRECT |
| dog | `frame all` | INCORRECT |
| sun | `sun.` | CORRECT |
| hat | `hat.` | CORRECT |
| bed | no transcription | NO_INPUT |

This run demonstrated multiple system states rather than only successful examples.

The test showed:

- Correct transcription
- Incorrect transcription
- Silence/no-input handling
- Structured evaluation

---

# Deliberate Near-Match Test

A separate test intentionally used words similar to the expected CVC targets.

| Target | Intended Response | Whisper Output | Outcome |
| --- | --- | --- | --- |
| cat | cap | `strenght, cap.` | NEAR_MATCH |
| dog | dot | `dot.` | NEAR_MATCH |
| sun | son | `waters come ball` | INCORRECT |
| hat | hot | `hot` | NEAR_MATCH |
| bed | bad | `and` | INCORRECT |

This successfully demonstrated the:

`NEAR_MATCH`

state.

The near-match feature uses text similarity after Whisper transcription.

It is not pronunciation or acoustic analysis.

Across the CVC tests, watchMe demonstrated:

- `CORRECT`
- `NEAR_MATCH`
- `INCORRECT`
- `NO_INPUT`

---

# Background Audio Limitation

Some speech tests were performed while movie or television dialogue was playing in the environment.

Whisper occasionally incorporated unrelated background speech into the transcription.

This demonstrated that microphone mode can be affected by:

- Environmental dialogue
- Other speakers
- Low learner volume
- Microphone placement
- Recording timing

The current prototype does not include:

- Speaker identification
- Speaker isolation
- Beamforming
- Advanced noise suppression
- Directional microphone filtering

These are documented limitations.

---

# Live Camera and Microphone Concurrency Test

Before building the final single-process orchestrator, the camera and microphone pipelines were tested concurrently.

Two processes were run:

1. `tools.mouth_movement.py`
2. `agents.lesson_agent.py`

The purpose was to determine whether webcam processing and microphone/Whisper processing could operate at the same time without a hardware conflict.

---

## Camera Result

The live camera process produced:

- Total frames: `331`
- Valid mouth frames: `331`
- Movement detected: `True`
- Movement score: `0.2999`
- Average frame-to-frame delta: `0.0211`
- Processing time: `58950.56 ms`

The webcam remained active during speech capture and transcription.

---

## Speech Result

The Shapes lesson produced:

| Target | Whisper Output |
| --- | --- |
| circle | `the circle.` |
| square | `square.` |
| triangle | `triangle.` |

The camera and microphone did not produce a hardware conflict.

---

# Failure Case: Shapes Evaluator Inconsistency

Although Whisper returned:

`the circle.`

the Shapes evaluator initially marked the response incorrectly.

The CVC evaluator had already been improved to normalize punctuation and identify the expected target inside a longer transcription.

The Shapes evaluator had not yet received the same update.

This was a scoring inconsistency between lesson implementations.

## Fix

The Shapes evaluator was standardized to use the same response normalization and similarity logic as CVC.

This is important because the speech recognition itself had succeeded.

The problem existed in application scoring.

---

# LiveLessonOrchestrator Integration

The next stage connected the camera, PerceptionAgent, PlannerAgent, LessonAgent, microphone, and lesson interface into a single process.

Several failures occurred before the final workflow operated correctly.

---

# Failure Case: Learner Visible but Live Agent Reported No Detection

An early live orchestrator run displayed the learner clearly in the webcam window but produced:

```text
Perception updates: 0
Face detected: False
Face count: 0
Final state: ERROR
```

At first, additional sample data was considered as a possible solution.

However, this would have addressed the wrong layer of the system.

The saved live webcam frame was tested directly with:

`tools.visual_perception.py`

Observed result:

```text
status: success
face_detected: True
face_count: 1
face_centered: True
face_position: center
face_size_ratio: 0.1765
readiness: ready
```

Processing time:

approximately `349.26 ms`

This proved that:

- The webcam was working
- The saved frame was valid
- MediaPipe detected the learner
- The readiness system worked

The failure therefore existed in the agent integration layer.

---

# Failure Case: Incorrect PerceptionAgent Method

The first live orchestrator attempted to call generic methods including:

- `run()`
- `process()`
- `analyze()`

The actual PerceptionAgent class exposed:

`perceive()`

The live run therefore returned:

```text
PerceptionAgent has no supported run/process/analyze method.
```

## Fix

The actual source files were inspected.

The correct agent interfaces were confirmed:

```text
PerceptionAgent.perceive()
PlannerAgent.plan()
LessonAgent.run()
```

The orchestrator was updated to call the actual APIs rather than guessing method names.

---

# Failure Case: PerceptionAgent Import Problem

During the integration rewrite, one version of:

`agents/perception_agent.py`

failed to expose the `PerceptionAgent` class correctly.

The application produced:

```text
ImportError:
cannot import name 'PerceptionAgent'
from 'agents.perception_agent'
```

The file was rewritten with a clean module structure and the class was verified using a direct import test.

This was a software-structure failure rather than a computer vision failure.

---

# Failure Case: Bounding Box Lost Between Tool and Agent

The lower-level visual perception tool already produced:

`face_boxes`

For example:

```text
x_min: 229
y_min: 153
x_max: 440
y_max: 410
```

However, the first PerceptionAgent message did not include those coordinates.

The live system could identify learner readiness but could not draw the intended blue/green readiness box.

## Fix

The structured PerceptionAgent face message was updated to preserve:

`face.boxes`

The LiveLessonOrchestrator then used those coordinates to draw the learner-facing visual readiness indicator.

---

# Successful Readiness Integration

After correcting the agent interfaces and bounding-box handoff, a live Shapes session successfully produced:

- Face detected: `True`
- Face count: `1`
- Final visual readiness: `ready`
- Final state: `COMPLETE`
- Start method: `automatic_countdown`
- Mouth movement: `True`
- Movement events: `5`
- Maximum mouth delta: `0.1952`
- Lesson completed: `True`

This confirmed that the integrated system could:

```text
Webcam
→ PerceptionAgent
→ PlannerAgent
→ READY
→ ARMED
→ automatic countdown
→ LessonAgent
```

However, this test exposed another usability problem.

---

# Failure Case: Lesson Prompt Not Visible to Learner

The integrated lesson was technically running, but the prompt was printed only in the terminal.

The learner was looking at the webcam interface and could not see that the system was asking for:

- `circle`
- `square`
- `triangle`

During testing, unrelated speech such as:

`yes, yes, yes`

was used simply to confirm that the microphone was active.

The lesson therefore completed, but the output was not meaningful as a learner activity.

## Diagnosis

The LessonAgent returned the complete lesson result only after the lesson finished.

The live interface had no item-level information while the activity was running.

## Fix

A status callback system was added.

The lesson files now send events such as:

- `lesson_started`
- `prompt`
- `listening`
- `response`
- `outcome`
- `lesson_complete`

The LiveLessonOrchestrator receives these events and displays them directly in the camera interface.

A short prompt delay was also added before microphone recording begins.

This gives the learner time to see the requested target.

---

# Live Learner Interface Test

The final webcam interface can display:

```text
SHAPES LESSON
Item 1/3

SAY: CIRCLE

LISTENING...
```

After Whisper processes the response, the interface can display:

```text
HEARD: circle.
RESULT: CORRECT
```

The lesson then advances to the next item.

This converted the webcam display from a development diagnostic window into the actual learner-facing lesson interface.

---

# Final Integrated Failure Run: No Usable Audio

One complete Shapes live session produced:

- Session: `live_lesson_20260809_155018`
- Frames: `644`
- Perception updates: `42`
- Face detected: `True`
- Face count: `1`
- Final state: `COMPLETE`
- Start method: `automatic_countdown`
- Mouth movement: `True`
- Movement events: `10`
- Maximum mouth delta: `0.4828`
- Lesson completed: `True`

Lesson score:

- Correct: `0`
- Near match: `0`
- Incorrect: `0`
- No input: `3`

Observed audio levels were:

- circle: approximately `0.000457`
- square: approximately `0.000445`
- triangle: approximately `0.000365`

All three responses returned:

`NO_INPUT`

This session is retained as a useful failure case.

The visual pipeline succeeded and visible mouth movement occurred, but microphone input was insufficient.

This demonstrates that:

> Visible mouth movement and usable microphone speech are separate signals.

watchMe should not assume that detected mouth movement guarantees successful speech capture.

---

# Final Successful Integrated Shapes Run

An earlier successful integrated Shapes session (`live_lesson_20260809_155131`) demonstrated the complete workflow with two correct responses and one `NO_INPUT`.

The official final validation was then run again under a normal real-world environment rather than repeating tests until a perfect score appeared.

Final session:

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

The final visual readiness reported `move_closer` at the end of the session because the learner moved after the lesson had already started. The lesson itself still reached `COMPLETE`, so this did not invalidate the readiness gate or lesson execution.

The system successfully completed the entire live multimodal workflow.

---

## Final Shapes Lesson Results

### Circle

Target:

`circle`

Whisper output:

`circle.`

Outcome:

`CORRECT`

Audio level:

approximately `0.001266`

---

### Square

Target:

`square`

Whisper output:

`square. square.`

Outcome:

`CORRECT`

Audio level:

approximately `0.001731`

---

### Triangle

Target:

`triangle`

Whisper output:

`valve will explode.`

Outcome:

`INCORRECT`

Audio level:

approximately `0.001410`

---

## Final Lesson Score

- Correct: `2`
- Near match: `0`
- Incorrect: `1`
- No input: `0`

This result is intentionally not presented as a general speech-recognition accuracy percentage.

The objective of the final test was to validate the full system in a realistic setting where background noise, microphone placement, timing, and short-word transcription can affect Whisper. The test was not repeated until a perfect output appeared.

The final run demonstrated:

```text
Learner enters camera
→ face detected
→ learner readiness evaluated
→ READY confirmed
→ lesson armed
→ automatic countdown
→ lesson begins
→ visual prompt displayed
→ microphone captures all three attempts
→ mouth movement detected
→ Whisper transcribes each attempt
→ response evaluator scores each target
→ visual outcome displayed
→ lesson completes
→ trace saved
```

The incorrect `triangle` transcription is treated as a speech-recognition limitation, not a failure of the computer vision or multi-agent orchestration.

A possible future improvement is:

```text
Prompt
→ listen
→ evaluate transcription
→ if correct: continue
→ if uncertain or incorrect: allow limited retry
→ after maximum attempts: skip or use typed confirmation
```

A longer or adaptive listening window could also improve recognition in noisy environments while avoiding an indefinite wait state.

This session is the primary final multimodal validation result.

---

# Microphone Portability Testing

Development originally used a hard-coded microphone device:

`7`

This worked well on the development Windows laptop.

However, audio device numbers are machine-specific.

A final portable configuration was created.

The intended selection logic is:

```text
WATCHME_MIC_DEVICE set
→ use explicit device

No override
→ use operating-system default input
```

Typed input remains available as a hardware-independent fallback.

---

# Failure Case: SoundDevice Default Device Type

The first portable microphone implementation assumed:

`sd.default.device`

would return a normal integer, list, or tuple.

With:

`sounddevice==0.5.5`

the value was represented by an internal:

`_InputOutputPair`

object.

The speech test failed with:

```text
int() argument must be a string,
a bytes-like object or a real number,
not '_InputOutputPair'
```

## Fix

The microphone resolver was updated to support SoundDevice's input/output-pair object and correctly extract the input-device index.

---

# Default Microphone Quality Test

After correcting the resolver, the system successfully selected the operating-system default microphone.

The recording completed without a software error.

Observed result:

- Status: `no_input`
- Audio level: approximately `0.000044`
- Audio artifact successfully saved

The Windows default microphone on the development laptop was therefore technically accessible but produced a nearly silent recording.

This was treated as a hardware/configuration issue rather than an application crash.

The known-good development microphone remains accessible through:

```powershell
$env:WATCHME_MIC_DEVICE="7"
```

Another computer should identify its own input device rather than assuming device `7`.

The README documents how to:

- Test speech input
- List microphone devices
- Set an optional override
- Use typed input if microphone hardware is unavailable

---

# Final Dependency Set

The final direct dependencies are pinned as:

```text
mediapipe==1.0.0
opencv-contrib-python==5.0.0.93
numpy==2.2.6
openai-whisper==20250625
sounddevice==0.5.5
soundfile==0.14.0
```

The earlier clean-environment test validated the computer vision dependencies.

The final repository review should confirm that the speech dependencies are also included and documented.

---

# Major Failure and Correction Summary

| Failure / Misstep | Evidence | Correction |
| --- | --- | --- |
| Haar cascade false positive | Background classified as face | Replaced with MediaPipe Face Landmarker |
| Planner error schema mismatch | `STOP` returned differently from normal decisions | Standardized PlannerAgent schema |
| Preliminary evaluation too easy | 8/8 but limited decision diversity | Expanded to 14 controlled scenarios |
| Planner distance/position conflict | `leftsidesmile.jpg` returned MOVE_CLOSER | Prioritized positioning before distance |
| Rotated face still READY | 90-degree robustness tests | Documented orientation limitation |
| Silence threshold too high | Quiet speech rejected at `0.003` | Lowered threshold to `0.001` |
| Repeated words marked incorrect | `cat cat` failed exact string comparison | Added normalized word matching |
| Shapes scoring inconsistency | `the circle.` marked incorrect | Standardized CVC and Shapes evaluators |
| Background dialogue entered Whisper | Unrelated multi-word transcriptions | Documented environmental audio limitation |
| Live learner not recognized | Webcam visible but zero perception updates | Tested saved frame and isolated integration layer |
| Wrong PerceptionAgent API | `run/process/analyze` not present | Used actual `perceive()` API |
| PerceptionAgent import failure | Class could not be imported | Rebuilt clean module structure |
| Bounding box disappeared in agent handoff | `face_boxes` existed in tool output only | Added `face.boxes` to PerceptionAgent |
| Lesson prompt hidden in terminal | Learner did not know what to say | Added callback-driven live lesson UI |
| Full lesson returned NO_INPUT | Mouth movement detected but mic weak | Retained as multimodal failure evidence |
| Portable microphone resolver failed | `_InputOutputPair` conversion error | Added version-compatible device resolution |
| Windows default mic nearly silent | Software worked but audio level `0.000044` | Documented optional device override |

---

# Final Evaluation Summary

## Controlled Visual Functional Evaluation

```text
14 / 14 passed
100% controlled task success
Average latency: ~185.69 ms
```

Interpretation:

> 100% task success on the current controlled 14-scenario functional validation set.

---

## Robustness Evaluation

```text
8 robustness conditions
0 unhandled application crashes
```

The robustness evaluation also exposed known limitations, especially image orientation.

---

## Temporal Webcam Validation

```text
337 frames
337 valid mouth frames
Movement detected: True
Movement score: 0.4427
```

---

## Camera + Microphone Concurrency Validation

```text
331 camera frames
331 valid mouth frames
Movement detected: True
Whisper captured circle, square, triangle
No camera/microphone hardware conflict
```

---

## Final Live Multimodal Validation

Official final session:

`live_lesson_20260809_212807`

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

Lesson result:

```text
circle → CORRECT
square → CORRECT
triangle → INCORRECT
0 NO_INPUT
```

The primary result is that the complete multimodal agent pipeline successfully operated as one live system under realistic environmental conditions. The single incorrect item was a Whisper transcription error and is retained as representative real-world evidence rather than removed through repeated testing.

---

# Test Conclusions

The final testing process demonstrated that watchMe can:

- Detect a human learner
- Reject non-human visual input
- Count faces
- Evaluate learner position
- Estimate relative camera distance
- Analyze mouth visibility
- Analyze mouth opening
- Detect temporal mouth movement
- Process live webcam video
- Produce structured perception messages
- Apply inspectable planner rules
- Display learner readiness
- Automatically start a lesson
- Display lesson prompts inside the camera window
- Record microphone input
- Run local Whisper transcription
- Evaluate lesson responses
- Distinguish CORRECT, NEAR_MATCH, INCORRECT, and NO_INPUT
- Process camera and microphone input concurrently
- Save structured traces
- Handle corrupt and missing input safely
- Operate with configurable microphone hardware

The testing also demonstrated that failures remain possible due to:

- Lighting
- Orientation
- Microphone selection
- Microphone placement
- Background speech
- Short-word Whisper errors
- Low speech volume
- Recording timing

These limitations are retained in the final project documentation.

The development history shows that watchMe was improved through repeated testing rather than by hiding failed cases or changing evaluation expectations only to produce successful metrics.

---

# Final Test Status

Implemented and validated:

- [x] Face detection
- [x] Mouth analysis
- [x] Temporal mouth movement
- [x] PerceptionAgent
- [x] PlannerAgent
- [x] LessonAgent
- [x] LiveLessonOrchestrator
- [x] Automated visual evaluation
- [x] Robustness testing
- [x] Clean-environment visual test
- [x] Typed lesson input
- [x] Microphone recording
- [x] Whisper transcription
- [x] CVC lesson
- [x] Shapes lesson
- [x] CORRECT evaluation
- [x] NEAR_MATCH evaluation
- [x] INCORRECT evaluation
- [x] NO_INPUT evaluation
- [x] Camera + microphone concurrency
- [x] Live readiness interface
- [x] Automatic lesson start
- [x] Visible lesson prompts
- [x] Full integrated live multimodal run
- [x] Optional microphone-device override
- [x] Structured failure documentation

Formal testing is now frozen. Remaining work is final GitHub publication, repository verification, and presentation/submission preparation rather than additional feature development.