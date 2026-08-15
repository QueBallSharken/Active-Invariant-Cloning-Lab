# Active Clone Demo Architecture

Repository: Active Invariant Cloning Lab

Status: Draft

Purpose: Define the smallest possible architecture capable of testing Active Invariant Cloning.

---

# Design Goal

Build the smallest executable system capable of demonstrating:

- Active invariant cloning
- Clone participation
- Clone agreement
- Clone disagreement
- Refusal capability
- Evidence generation

The objective is validation.

Not production deployment.

---

# Architectural Principle

Minimize complexity.

Every component must justify its existence.

If a component is not required to test a repository claim:

Do not add it.

---

# Minimal System

Request

↓

Invariant Source

↓

Clone A

↓

Clone B

↓

Decision Comparison

↓

Mutation Decision

↓

Evidence Record

---

# Component Definitions

## Request

Represents a proposed mutation.

Examples:

- Allow action
- Deny action
- Modify state
- Execute operation

The specific mutation type is not important during initial validation.

---

## Invariant Source

The original governing invariant.

Responsible for:

- Defining governance rules
- Creating clone instances
- Providing comparison baseline

---

## Clone A

Active governance participant.

Evaluates mutation requests.

Produces governance decisions.

---

## Clone B

Independent active governance participant.

Evaluates the same mutation requests.

Produces governance decisions.

---

## Decision Comparison

Compares clone outcomes.

Possible results:

- Agreement
- Disagreement

---

## Mutation Decision

Determines whether the requested mutation proceeds.

Possible outcomes:

- Approved
- Refused

---

## Evidence Record

Stores:

- Request
- Clone decisions
- Agreement state
- Final decision
- Timestamp

---

# Initial Assumptions

The first prototype assumes:

- Identical clone definitions
- Identical inputs
- Deterministic evaluation

These assumptions may be relaxed in future experiments.

---

# Initial Validation Target

The first validation target is:

Identical clones

+

Identical request

↓

Identical decision

If this cannot be demonstrated reliably, further AIC claims become difficult to support.

---

# Future Expansion

Future versions may introduce:

- Additional clones
- Drift injection
- Translation boundaries
- Distributed execution
- Clone coordination
- Clone legitimacy checks
- Hidden path discovery

Expansion should follow evidence.

---

# Out Of Scope

The initial prototype does not attempt to solve:

- Distributed consensus
- Network governance
- Hardware enforcement
- Global survivability
- Large-scale deployment

These concerns belong to later phases.

---

# Success Criteria

The architecture succeeds if:

- Active clones can be created
- Clones participate in governance
- Decisions can be compared
- Refusal can be demonstrated
- Evidence can be generated

---

# Final Statement

This architecture exists to test the smallest meaningful instance of Active Invariant Cloning.

Evidence wins.
