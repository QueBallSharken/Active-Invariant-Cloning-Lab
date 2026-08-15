# Mobile Contribution Rules

Repository: Active Invariant Cloning Lab

Status: Active

Purpose: Define repository editing procedures optimized for mobile contributors.

---

# Background

This repository is actively maintained from mobile devices.

Mobile editing increases the risk of:

- Accidental deletion
- Partial updates
- Lost content
- Incorrect merges
- Continuity failures

These procedures exist to reduce those risks.

---

# Repository Rule

Before modifying an existing file:

1. Open the current file.
2. Review the complete contents.
3. Copy the complete contents.
4. Provide the contents for review if collaboration is occurring.
5. Generate a complete replacement file or append-only addition.
6. Replace the file in full.

Repository state must be verified before modification.

---

# Preferred Update Methods

## Method 1

Full File Replacement

Preferred.

Procedure:

- Review current file.
- Generate complete updated file.
- Replace file contents.
- Commit changes.

---

## Method 2

Append To Bottom

Acceptable.

Procedure:

- Review current file.
- Generate new section.
- Append to end of file.
- Commit changes.

---

# Disallowed Workflow

Avoid:

- Mid-file insertion instructions
- Line-number edits
- Partial patch updates
- Assumed repository state
- Memory-based modifications

These methods are error-prone on mobile devices.

---

# Session Handoff Rule

SESSION_HANDOFF.md must always be updated through full-file replacement.

Never update SESSION_HANDOFF.md using partial edits.

The current file remains authoritative.

---

# AI Contributor Rule

Future AI contributors should:

1. Request the current file contents.
2. Review the entire file.
3. Generate a complete replacement or append-only update.
4. Avoid patch-style modifications.

Repository artifacts remain authoritative.

---

# Continuity Principle

Repository state should be verified before modification.

Current file contents outrank:

- Memory
- Assumptions
- Prior conversations
- Summaries

Repository artifacts remain authoritative.

---

# Final Statement

Mobile-first workflows prioritize continuity, verification, and safe modification practices.

Repository first.

Current file first.

Memory last.
