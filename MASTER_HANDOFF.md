# MASTER_HANDOFF

Version: 0.2
Status: Active
Purpose: Repository Continuity Synthesis Artifact
Repository: AIC (Active Invariant Cloning)
Author: Steven Kyle Hensley (QueBallSharken)

---

# IMPORTANT RULE

The repository is the source of truth.

This file is not the source of truth.

This file is a synthesized representation of repository truth.

If disagreement exists between:

- MASTER_HANDOFF.md
- SESSION_HANDOFF.md
- AI summaries
- Human recollection
- Conversations
- Assumptions

and

Repository artifacts

The repository wins.

Always.

---

# Purpose

MASTER_HANDOFF exists to preserve repository continuity.

It is generated from repository artifacts.

It summarizes:

- Repository identity
- Repository mission
- Core definitions
- Current understanding
- Established discoveries
- Research progression
- Open questions
- Development status

MASTER_HANDOFF is a continuity artifact.

Not an authority artifact.

---

# Repository Name

AIC

Active Invariant Cloning

---

# Mission

Determine whether a governing invariant can be actively cloned across every reachable mutation path while remaining:

- Live
- Binding
- Refusal-Capable

at every participating boundary.

---

# Core Research Question

If a governing invariant can survive a mutation path,

can that invariant be actively cloned,

distributed,

coordinated,

and maintained

across all reachable mutation paths simultaneously?

---

# Repository Philosophy

Evidence before belief.

Implementation before theory.

Verification before conclusion.

Continuity before convenience.

---

# Current Research State

The repository has progressed beyond initialization and specification
into executable empirical testing.

The current harness contains adversarial tests that probe whether
invariant identity survives across mutation-capable verification
boundaries.

Current verified test result:

109 passed.

The working tree is clean at the current research checkpoint.

---

# Established Empirical Findings

## 1. Ticket-to-Receipt Invariant Substitution

A terminal receipt can currently be constructed with:

Ticket:

    invariant_id = INV-001

Receipt:

    invariant_id = INV-ATTACKED

while retaining:

- The same ticket_id
- The same ticket_hash
- The same invariant_version
- The same payload_hash
- The same tool
- The same epoch
- The same nonce

The receipt can still be cryptographically signed.

The receipt hash remains internally valid.

This demonstrates that receipt cryptographic integrity does not,
by itself, establish invariant identity continuity from the originating
ticket.

---

## 2. Terminal Verification Boundary

The current terminal receipt verifier performs:

- Receipt signature verification
- Receipt integrity verification

It does not independently compare the receipt's invariant identity
against the originating ticket.

An adversarial receipt containing:

    ticket.invariant_id  = INV-001
    receipt.invariant_id = INV-ATTACKED

therefore passes:

- verify_receipt_signature()
- verify_receipt_integrity()
- verify_terminal_receipt()

This behavior is covered by an executable regression test.

---

## 3. Evidence-Chain Boundary

The evidence-chain layer currently binds the receipt to the
ticket through ticket_hash.

EvidenceLink does not independently contain invariant identity fields.

An evidence chain can therefore be constructed from a receipt whose
invariant identity has been substituted while its ticket_hash remains
unchanged.

The resulting evidence chain currently passes verification.

This behavior is covered by executable tests.

---

# Current Evidence Model

The current evidence establishes a distinction between:

Cryptographic integrity

and

Invariant continuity.

A valid signature demonstrates that the signed receipt has not been
altered after signing.

A valid receipt hash demonstrates that the receipt's recorded body
matches its recorded hash.

A matching ticket_hash demonstrates linkage to the ticket artifact.

None of those checks, in the current implementation, independently
establish that the receipt's invariant identity is the same invariant
identity carried by the originating ticket.

This distinction is an empirical repository finding.

It is not, by itself, a claim that AIC has been universally proven or
that the observed implementation gap exists in every architecture.

---

# Repository Progression

Initialization

↓

Definitions

↓

Specification

↓

Prototype

↓

Adversarial Testing

↓

Empirical Boundary Analysis

↓

Measurement

↓

Verification

---

# Current Research Phase

Phase:

Empirical Boundary Analysis

Primary objective:

Identify mutation-capable boundaries where invariant identity can
diverge from the originating governing artifact while existing
cryptographic and evidence verification mechanisms continue to accept
the resulting state.

Research method:

1. Construct the smallest adversarial case.
2. Execute it against the current harness.
3. Record the observed result.
4. Preserve the result as an executable test.
5. Run the complete regression suite.
6. Commit the evidence.
7. Only then consider implementation changes.

---

# Verified Test Checkpoint

Current full-suite result:

    109 passed

The repository must continue to preserve this regression baseline
unless a deliberate research change documents why the expected result
changes.

---

# Source Artifacts

MASTER_HANDOFF derives understanding from:

- README.md
- PROJECT_STRUCTURE.md
- OPEN_QUESTIONS.md
- FOUNDERS_NOTES.md
- SESSION_HANDOFF.md
- Specification Documents
- Research Documents
- Prototype Documents
- Test Results

---

# Direction Lock

The purpose of this repository is:

- Discover
- Implement
- Test
- Measure
- Verify

The purpose is not:

- Assume success
- Assume failure
- Protect conclusions
- Force outcomes

---

# Repository Status

Phase:

Empirical Boundary Analysis

Current Objective:

Continue testing invariant continuity across remaining
mutation-capable and verification boundaries before modifying the
implementation.

---

# Open Questions

1. Which boundary is the authoritative source of invariant identity
   for terminal execution?

2. Where should invariant identity continuity be structurally bound?

3. Should EvidenceLink explicitly carry invariant identity or another
   independently verifiable invariant binding?

4. Should terminal verification accept a receipt independently, or
   require a ticket-aware continuity check?

5. What additional mutation paths can produce the same divergence?

6. What is the smallest implementation change that enforces the
   desired continuity property without masking the empirical result?

---

# Contributor Rule

Contributors should treat repository artifacts as authoritative.

MASTER_HANDOFF is a continuity aid.

Repository artifacts remain primary.

Do not modify production behavior merely to make an adversarial test
pass without first documenting the observed behavior and the intended
invariant being enforced.

---

# Regeneration Rule

MASTER_HANDOFF should be regenerated whenever repository understanding
materially changes.

Generation should be based on repository artifacts.

Not memory.

Not assumptions.

Not prior conversations.

---

# Final Statement

This file exists to preserve continuity.

The repository exists to discover truth.

If repository evidence contradicts this file:

The repository wins.
