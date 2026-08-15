Project Structure

Purpose

This document defines the intended structure of the Active Invariant Cloning (AIC) repository.

The structure exists to support implementation, experimentation, measurement, verification, and continuity.

Repository organization should support evidence generation rather than complexity.

---

Root

README.md

MASTER_HANDOFF.md

SESSION_HANDOFF.md

CHANGE_CONTROL.md

PROJECT_STRUCTURE.md

COLLABORATION_PROTOCOL.md

OPEN_QUESTIONS.md

FOUNDERS_NOTES.md

LICENSE

---

Documentation

docs/

Purpose:

Repository documentation, specifications, terminology, methodology, and supporting materials.

Examples:

- AIC_SPECIFICATION.md
- CLONE_MODEL.md
- SEMANTIC_EQUIVALENCE.md
- DRIFT_DETECTION.md
- GOVERNED_EXECUTION.md
- GLOSSARY.md

---

Research

research/

Purpose:

Capture experiments, observations, findings, notes, and exploratory work.

Subdirectories may include:

- experiments/
- findings/
- notes/

---

Prototype

prototype/

Purpose:

Executable implementations used to test Active Invariant Cloning concepts.

Prototype work should prioritize minimal reproducible demonstrations.

---

Tests

tests/

Purpose:

Verification of repository claims.

Subdirectories may include:

- unit/
- integration/
- adversarial/

---

Receipts

receipts/

Purpose:

Evidence generated through implementation and testing.

Subdirectories may include:

- clone_creation/
- clone_survival/
- clone_failure/
- drift_detection/
- verification/

Evidence should be preserved whenever possible.

---

Archive

archive/

Purpose:

Preserve historical artifacts, deprecated materials, superseded experiments, and research history.

Subdirectories may include:

- historical/
- deprecated/

Archived materials remain part of repository history.

---

Repository Organization Rule

Experimental work belongs in:

research/

or

prototype/

until validated.

Validated findings should be documented and supported by evidence.

---

Repository Priority

Evidence

↓

Implementation

↓

Testing

↓

Measurement

↓

Documentation

↓

Discussion

---

Scope Rule

Every directory should support the repository mission:

Determine whether Active Invariant Cloning can be realized, tested, measured, and verified.

Anything outside that purpose requires justification.

---

Final Statement

Repository structure exists to support continuity, reproducibility, and evidence generation.

Organization should simplify verification rather than increase complexity.
