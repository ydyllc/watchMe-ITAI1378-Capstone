# watchMe Ethics, Responsibility, Privacy, and Security

## Purpose

watchMe is an educational computer vision and speech-practice prototype developed as part of the larger MirrorMe platform concept.

Because watchMe processes live camera input, facial landmarks, mouth movement, microphone recordings, speech transcriptions, and lesson results, the project raises important ethical, privacy, security, and responsible AI concerns.

The system is designed to assist a learner during simple educational speech-practice activities.

It is not designed to make medical, clinical, diagnostic, disciplinary, or other high-stakes decisions.

A core responsible-use principle for watchMe is:

> The system should assist the learner and provide feedback, not make autonomous high-stakes judgments about the learner.

---

# Responsible AI Scope

watchMe should only be used within the scope for which it was designed.

Appropriate prototype uses include:

- Checking whether a learner is visible to the camera
- Helping a learner move into a useful camera position
- Presenting simple educational practice words
- Recording short speech responses
- Transcribing short responses with Whisper
- Comparing the transcription with an expected lesson word
- Providing simple practice feedback
- Recording technical results for development and evaluation

watchMe should not be used to:

- Diagnose a speech disorder
- Determine whether a child has a disability
- Replace a speech-language pathologist
- Make medical recommendations
- Make school-placement decisions
- Grade a learner in a high-stakes setting without human review
- Determine intelligence or ability
- Make employment decisions
- Perform surveillance unrelated to the educational activity
- Identify a person from biometric data
- Track a person without their knowledge or consent

The current system is a classroom prototype, not a validated clinical system.

---

# Human Oversight

watchMe should remain a human-in-the-loop system.

The computer vision and speech outputs should be treated as assistance rather than final truth.

For example, Whisper may transcribe:

```text
frame all
```

when the learner intended to say:

```text
dog
```

The correct responsible response is not to assume that the learner pronounced the word incorrectly.

The failure may have been caused by:

- Whisper
- Background noise
- Microphone placement
- Recording timing
- Low speech volume
- Hardware selection

The system therefore reports a lesson outcome, but a teacher, parent, clinician, or other responsible adult should be able to review or ignore that result.

This is especially important if watchMe were ever extended beyond a classroom prototype.

---

# Transparency

Users should understand what watchMe is doing.

The system should clearly communicate when it is:

- Detecting a learner
- Checking readiness
- Recording audio
- Listening for speech
- Running speech recognition
- Evaluating a lesson response
- Saving an artifact

The live interface supports this principle by displaying states such as:

```text
LEARNER DETECTED
LEARNER READY
LISTENING...
HEARD: square.
RESULT: CORRECT
```

These messages reduce the chance that audio or video processing occurs without the learner understanding that the system is active.

A future production version should provide an even clearer recording indicator.

---

# Consent

Camera and microphone data should not be collected without appropriate consent.

Before a learner uses watchMe, the responsible user should understand that the system may process:

- Facial images
- Facial landmarks
- Mouth movement
- Voice recordings
- Speech transcriptions
- Lesson responses

For minors, a parent, guardian, school, or other authorized responsible party may need to provide consent depending on the deployment environment and applicable policies.

Users should not be secretly recorded.

The system should also allow the learner to stop the session.

The current prototype includes:

```text
Q
```

to exit a live session.

---

# Privacy

watchMe processes information that can be personally identifiable.

Examples include:

- A person's face
- A person's voice
- Camera snapshots
- Audio recordings
- Speech transcriptions
- Session traces

Even if watchMe is not designed for identity recognition, these artifacts can still reveal identity.

For that reason, the project should follow a data-minimization principle:

> Collect and retain only the information required for the educational activity and system evaluation.

---

# Local Processing

An important privacy decision in the current prototype is the use of local processing where practical.

Current components such as:

- MediaPipe face analysis
- OpenCV image processing
- Whisper transcription

can operate locally on the development computer.

This reduces the need to transmit raw camera or microphone data to an external cloud service.

Local processing does not remove every privacy risk, but it reduces unnecessary data exposure.

A future production system should continue to prefer local processing when possible, especially for children's camera and voice data.

---

# Audio Privacy

Microphone mode creates WAV recordings under:

```text
results/audio/
```

Voice recordings can contain identifiable or sensitive information.

Before publishing the GitHub repository, raw audio should be reviewed.

Development recordings should not automatically be included in a public repository.

Recommended practice includes:

- Delete recordings that are no longer needed
- Avoid publishing identifiable voice recordings
- Keep only demonstration-safe artifacts when necessary
- Do not collect longer recordings than required
- Do not record continuously when the lesson is inactive

The current recording window is intentionally short.

---

# Image Privacy

Still-image and webcam artifacts can also contain identifiable information.

Before publishing:

```text
results/images/
results/live/
data/sample/
```

all images should be reviewed.

Personal webcam captures should not be published unnecessarily.

If example images are needed for a public repository, it is preferable to use:

- Properly licensed sample images
- Synthetic images
- Images with clear permission
- Non-identifiable demonstration material

---

# Data Retention

watchMe should not retain information indefinitely by default.

A production version should define clear retention rules.

For example:

```text
Temporary camera frame
→ process
→ discard

Short lesson audio
→ transcribe
→ optionally discard

Structured lesson result
→ retain only if needed
```

The current prototype keeps artifacts for development evidence, debugging, and evaluation.

That is acceptable for a course project, but the same retention behavior should not automatically be carried into a real educational deployment.

---

# Security

Privacy protections are not useful if stored information is insecure.

Potential watchMe data includes:

- Images
- Webcam captures
- Audio recordings
- Transcriptions
- JSON traces
- Future learner history

These files should be protected from unauthorized access.

Important security practices include:

- Do not store secrets in source code
- Do not commit API keys or credentials
- Use `.gitignore` for private configuration
- Review files before GitHub publication
- Limit access to saved recordings
- Keep dependencies updated
- Avoid unnecessary network exposure
- Validate external files before processing
- Handle corrupt files safely
- Use least privilege when adding cloud or database services

The current project uses:

`.env.example`

for configuration documentation while:

`.env`

should remain excluded from source control.

---

# Secure Input Handling

watchMe accepts image, audio, webcam, and user-response input.

Invalid input should not be allowed to crash the system unexpectedly.

The current computer vision pipeline already demonstrates structured handling of:

- Missing image files
- Corrupt images
- Blank images
- Unsupported conditions

For example:

```text
Corrupt image
→ OpenCV cannot decode
→ structured perception error
→ PlannerAgent
→ STOP
```

The program records the failure instead of continuing with invalid data.

This is both a reliability and security principle.

---

# Dependency Security

watchMe depends on external Python packages including:

- MediaPipe
- OpenCV
- NumPy
- Whisper
- SoundDevice
- SoundFile

Dependencies should be installed from trusted package sources.

The project pins direct package versions in:

`requirements.txt`

Pinning improves reproducibility, but a production project would also need to monitor packages for:

- Security vulnerabilities
- Unsupported versions
- Supply-chain risks
- Breaking changes

A future deployment should periodically update and retest dependencies instead of permanently remaining on old versions.

---

# Biometric Considerations

watchMe uses facial landmarks and mouth geometry.

Although the current system is not designed to identify a learner, facial information can still be sensitive.

watchMe should not be extended casually into:

- Face recognition
- Identity tracking
- Attendance surveillance
- Behavioral profiling
- Emotional inference

without additional legal, ethical, privacy, and technical review.

The present system asks only the visual questions necessary for the activity:

```text
Is a learner visible?
Is there one learner?
Is the learner positioned appropriately?
Is the mouth visible?
```

It does not need to know who the learner is.

That limitation should be preserved when identity is unnecessary.

---

# Bias and Fairness

Computer vision systems can perform differently across people and environments.

Potential sources of unequal performance include:

- Skin tone
- Face shape
- Facial hair
- Glasses
- Head coverings
- Age
- Camera quality
- Lighting
- Camera angle
- Physical differences in facial movement

The current evaluation dataset is small and cannot establish fairness across all populations.

Therefore, the final visual result:

```text
14 / 14
```

should not be interpreted as evidence that the system performs equally well for every learner.

A production-quality system would require a much larger and more diverse validation dataset.

---

# Accessibility

Because watchMe is intended to support learning, accessibility should be part of future development.

The system should not require only one form of interaction.

The current prototype already provides two response modes:

- Microphone input
- Typed input

Typed input also serves as a useful fallback when microphone hardware fails.

Possible future accessibility improvements include:

- Larger interface text
- High-contrast display options
- Audio prompts
- Touchscreen controls
- Adjustable lesson timing
- Alternative input methods
- Support for users who cannot remain centered in a conventional camera position

Readiness rules should not become barriers for learners with physical or accessibility needs.

---

# Risk of False Positives and False Negatives

watchMe can make incorrect decisions.

Examples observed during development include:

- Haar Cascade detecting a background region as a face
- Rotated images receiving `READY`
- Whisper returning unrelated words
- A quiet microphone producing `NO_INPUT`
- A correct repeated word being marked incorrect before evaluator normalization

These failures show why automated results should not be treated as unquestionable truth.

A false negative might incorrectly suggest that a learner did not respond.

A false positive might suggest that a learner is ready when the camera orientation is inappropriate.

The system should therefore fail safely and allow human correction.

---

# Separation of Visual and Audio Evidence

An important finding during live testing was that:

```text
Mouth movement detected
```

does not necessarily mean:

```text
Usable speech captured
```

One complete live session detected substantial mouth movement while all three microphone responses returned:

`NO_INPUT`

This demonstrates why watchMe does not infer speech solely from visible mouth movement.

Likewise, Whisper transcription should not be treated as proof of pronunciation quality.

Visual and audio signals represent different observations and should remain distinct.

---

# Responsible Interpretation of NEAR_MATCH

The `NEAR_MATCH` lesson result is based on text similarity.

For example:

```text
Target:
hat

Whisper:
hot

Result:
NEAR_MATCH
```

This does not prove that the learner's pronunciation was clinically close to the target.

It only means that the recognized text was similar according to the current string-comparison rule.

The system should therefore describe this feature as:

> Text-based near-match feedback

and not:

> Pronunciation scoring

This wording is important for responsible deployment.

---

# Medical and Clinical Boundary

watchMe is not a medical device.

The project does not currently measure:

- Articulation accuracy
- Speech pathology
- Oral-motor disorders
- Fluency disorders
- Language disorders
- Neurological conditions

No output should be presented as a diagnosis.

If the MirrorMe platform were ever extended into a clinical environment, it would require significantly more work including:

- Clinical validation
- Appropriate professional oversight
- Privacy and security controls
- Regulatory review
- Diverse population testing
- Clear consent procedures
- Appropriate data governance

---

# Child Safety

Because an educational speech system may eventually be used by children, child safety deserves special consideration.

A child-facing version should minimize:

- Data collection
- Account complexity
- Public sharing
- Unnecessary cloud processing
- Long-term storage of voice or face recordings

A child should also not receive harsh or misleading feedback because an AI model failed.

For example, if Whisper mishears a word, the interface should avoid language such as:

```text
You said it wrong.
```

A more appropriate response would be:

```text
I didn't catch that clearly. Try again.
```

This design approach recognizes uncertainty instead of blaming the learner for a model failure.

---

# Security of Future Persistent Memory

A future ProgressAgent may use SQLite to maintain session history.

If that feature is implemented, the database could contain:

- Lesson type
- Prompt
- Response
- Outcome
- Timestamp
- Audio reference
- Session identifier

Such a database could reveal information about an individual learner's history.

It should therefore not be treated as harmless application data.

A future implementation should consider:

- Encryption
- Access control
- Retention limits
- User deletion rights
- Minimal identifiers
- Avoidance of unnecessary personal information

Persistent memory is intentionally not part of the current final capstone implementation.

---

# Security of Agent Architecture

Multi-agent systems create additional security and reliability concerns because one component can pass incorrect or manipulated information to another.

The current watchMe architecture uses structured handoffs:

```text
PerceptionAgent
→ PlannerAgent
→ LiveLessonOrchestrator
→ LessonAgent
```

Structured messages make it easier to:

- Validate fields
- Identify missing values
- Trace failures
- Limit unexpected behavior
- Audit why an action occurred

The PlannerAgent also uses explicit rule-based decisions rather than allowing an unrestricted language model to decide whether a learner is ready.

This reduces unpredictability for the current educational task.

---

# Least Privilege

Each component should have only the permissions it needs.

For example:

### PerceptionAgent

Needs:

- Image access
- Computer vision tools

Does not need:

- Internet access
- User account credentials

### PlannerAgent

Needs:

- Structured perception data

Does not need:

- Direct microphone control
- File-system access beyond required traces

### LessonAgent

Needs:

- Lesson definitions
- Typed or microphone input
- Speech transcription

Does not need:

- Access to unrelated personal files

This separation reduces the damage that could occur if one component fails or is later extended incorrectly.

---

# Traceability and Accountability

watchMe saves structured traces so important system behavior can be reviewed after a run.

Traceability allows developers to answer questions such as:

- What did the camera detect?
- What did PerceptionAgent report?
- Why did PlannerAgent select REPOSITION?
- Was the lesson started automatically or manually?
- What did Whisper return?
- Why was the result classified as NO_INPUT?
- Was mouth movement detected?

This makes errors easier to investigate and provides greater accountability than an unexplained final decision.

---

# Manual Override

The live application includes a manual demonstration override through:

`M`

This bypass should not be hidden.

When used, the session trace records:

`manual_demo_override`

This is important because a reviewer should be able to distinguish between:

```text
Lesson started because visual readiness passed
```

and:

```text
Lesson started because a human intentionally bypassed readiness
```

A production system should apply the same transparency to administrator overrides.

---

# Failure Handling

watchMe is designed to return safe states when possible.

Examples include:

```text
No learner
→ WAIT_FOR_USER
```

```text
Multiple learners
→ ONE_LEARNER_REQUIRED
```

```text
Corrupt image
→ STOP
```

```text
Nearly silent recording
→ NO_INPUT
```

These outputs are preferable to silently guessing.

When confidence is low or input is unusable, the system should request another attempt or human review.

---

# Environmental Security

A future MirrorMe device may operate in homes, schools, clinics, or other environments.

Physical security would then matter as well.

Potential considerations include:

- Who can access the device?
- Can stored recordings be copied?
- Is the camera visibly active?
- Can another person trigger the microphone?
- Can unauthorized users read learner history?
- Are software updates authenticated?
- Is remote administration enabled?

These risks are outside the current classroom prototype but should be considered before real-world deployment.

---

# Responsible AI Design Decisions in the Current Prototype

Several design decisions were intentionally made to reduce risk.

### Local Whisper

Speech transcription is performed locally rather than requiring cloud transmission.

### No Identity Recognition

watchMe checks whether a learner is visible but does not attempt to determine identity.

### Explicit Planner Rules

Readiness decisions are based on visible, documented rules.

### Typed Fallback

A learner does not have to depend entirely on microphone hardware.

### Structured Failure States

The application exposes failures such as `NO_INPUT` rather than silently producing a score.

### Human-Readable Reasons

PlannerAgent records why each action was selected.

### Manual Exit

The learner or operator can terminate the session.

### Educational Boundary

The project documentation explicitly avoids clinical claims.

---

# Ethical Limitations of the Evaluation

The current project evaluation demonstrates technical functionality, not universal fairness or safety.

For example:

```text
14 / 14 visual scenarios passed
```

does not prove:

- Equal performance across demographic groups
- Safe deployment with children
- Clinical effectiveness
- Security against every attack
- Reliability across every camera
- Reliability across every microphone

Likewise, successful Whisper transcription on selected examples does not establish universal speech-recognition reliability.

These limitations should remain visible in the final report and presentation.

---

# Recommendations for a Future Production Version

Before watchMe could move from educational prototype to real-world deployment, additional work should include:

1. Create a diverse visual validation dataset.
2. Evaluate performance across different ages, appearances, cameras, and lighting.
3. Perform structured speech-recognition evaluation.
4. Add clear consent and recording indicators.
5. Define strict data-retention rules.
6. Encrypt sensitive stored information.
7. Add role-based access controls.
8. Perform security testing.
9. Conduct privacy review.
10. Add accessible interface options.
11. Provide data deletion controls.
12. Establish an incident-response process.
13. Perform professional clinical review before making any speech-related health claims.
14. Avoid unnecessary identity recognition.
15. Maintain human oversight for important decisions.

---

# Responsible Use Summary

The responsible use model for watchMe can be summarized as:

```text
Observe only what is needed
        |
        v
Explain what the system is doing
        |
        v
Ask for appropriate consent
        |
        v
Process locally when practical
        |
        v
Make limited, transparent decisions
        |
        v
Allow human review
        |
        v
Store as little sensitive data as possible
        |
        v
Protect anything that must be stored
```

watchMe demonstrates how computer vision, speech recognition, and agent-based systems can support an educational activity.

The same capabilities also create responsibilities.

A technically successful system should not automatically be considered safe, fair, private, or appropriate for every environment.

Responsible deployment requires considering those questions throughout the entire system design.