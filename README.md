# Active Invariant Cloning (AIC)

## Status

Research Repository

Early Stage

Implementation and validation effort.

---

## Mission

Determine whether governing invariants can be replicated into multiple live,
binding, refusal-capable instances while preserving semantic equivalence across
mutation-capable paths.

The repository exists to test, measure, implement, and verify Active Invariant
Cloning (AIC).

The goal is not to assume the concept works.

The goal is to discover whether it works.

Evidence wins.

---

## Core Question

Can a governing invariant be replicated into multiple live, binding,
refusal-capable instances while preserving semantics across mutation-capable
paths?

---

## Relationship to BBIS

Boundary-to-Boundary Invariant Survival (BBIS) asks whether a governing
invariant can survive every mutation-capable boundary until the true
irreversible mutation authority.

AIC investigates a related but distinct architectural question:

If a governing invariant must survive across multiple mutation-capable
boundaries, can that invariant be instantiated as multiple active,
refusal-capable enforcement instances while preserving its governing semantics?

BBIS therefore concerns invariant survival across boundaries.

AIC concerns active instantiation and composition of that invariant across
those boundaries.

The two concepts are related but are not assumed to be identical.

---

## Motivation

Boundary-to-Boundary Invariant Survival (BBIS) establishes the problem of
governance continuity across mutation-capable execution paths.

AIC explores whether that governing invariant can be actively instantiated
at multiple points in the path without losing semantic identity or
enforcement authority.

This creates a fundamental research problem:

If multiple boundaries independently enforce portions of a governing invariant,
what prevents the individual decisions from becoming locally correct but
globally inconsistent?

AIC therefore investigates the composition problem between individually
correct enforcement components.

---

# Primordial Clone Hypothesis

A governing invariant may be replicated into multiple live, binding,
refusal-capable instances without loss of governing semantics.

Clone disagreement may provide evidence of:

- Semantic drift
- Translation failure
- Hidden mutation paths
- Governance failure
- Unauthorized mutation
- Path divergence
- Inconsistent state interpretation

The hypothesis is subject to falsification.

---

# Definitions

## Invariant

A governing constraint that defines what is permitted, prohibited, required,
or enforceable.

---

## Clone

An active instance of a governing invariant.

A clone is not:

- Documentation
- Audit evidence
- Historical approval
- A passive copy

A clone actively participates in governance.

---

## Live

The clone participates directly in the mutation path.

The clone is active during mutation.

The clone is not merely observed after execution.

---

## Binding

A mutation cannot proceed while violating the clone.

---

## Refusal-Capable

The clone retains the ability to prevent a mutation.

Detection alone is insufficient.

Warning alone is insufficient.

The clone must retain, directly or compositionally, an effective enforcement
path capable of preventing the governed mutation.

---

## Semantic Equivalence

Two invariant clones are semantically equivalent when they govern the same
mutation domain according to equivalent governing semantics despite differences
in representation, transport, implementation, or execution environment.

Semantic equivalence is a research property to be demonstrated, not assumed.

---

## Drift

Any deviation between clone semantics and intended invariant behavior.

Drift may arise from:

- State divergence
- Version divergence
- Translation
- Context loss
- Policy interpretation differences
- Implementation differences
- Timing differences
- Hidden mutation paths

---

# Architectural Composition Discipline

AIC does not claim to introduce a novel cryptographic primitive.

AIC does not claim to introduce a novel logical operator.

AIC uses ordinary architectural and cryptographic building blocks such as:

- Reference monitors
- Digital signatures
- Hashes
- State/version identifiers
- Route identifiers
- Attestation records
- Terminal verification
- Database or service commit guards

The research claim concerns how those components are composed.

AIC identifies a cross-boundary composition invariant requiring that a
governance-required authorization remain structurally bound to the identity
of the mutation as that mutation traverses each required enforcement
boundary.

The surviving architectural claim is therefore:

AIC is an Architectural Composition Discipline.

---

# The Composition Problem

Individually correct components do not necessarily imply globally correct
path authorization.

Formally:

    LocalCorrectness(B1)
    AND LocalCorrectness(B2)
    AND LocalCorrectness(TIMA)
    DOES NOT IMPLY
    PathAuthorization(M)

A downstream verifier may establish that valid attestations from required
boundaries exist without establishing that every boundary evaluated the
exact same mutation.

This creates a distinction between:

    Set Membership Verification

and:

    Transitive Authorization Verification

---

# Set Membership vs. Transitive Mutation Binding

A weak terminal verification model may effectively perform:

    PossessesAttestation(B1)
    AND
    PossessesAttestation(B2)
    =>
    Commit(TIMA, M)

This establishes that valid evidence exists.

It does not necessarily establish that:

    B1 evaluated M
    AND
    B2 evaluated M
    AND
    M is the mutation being committed.

AIC therefore investigates the stronger requirement:

    Every required boundary's authorization evidence
    must remain structurally bound to the same mutation identity
    throughout the authorization chain.

---

# Parallel Mutation Divergence

AIC identifies a concrete compositional attack against systems that validate
attestation membership without enforcing transitive mutation binding.

Consider:

    Client
      |
      v
    [ B1 ]
      |
      v
    [ B2 ]
      |
      v
    [ TIMA / Commit Authority ]

An attacker submits M1 to B1.

B1 correctly evaluates M1 and produces:

    T1 = Sign_K1(
        H(M1)
        ||
        Route
        ||
        StateVersion
    )

The attacker then constructs a different mutation M2.

B2 receives:

    M2 + T1

If B2 validates only the authenticity of T1, but does not verify that:

    PayloadHash(T1) == H(M2)

then B2 may legitimately perform its own local evaluation of M2 and produce:

    T2 = Sign_K2(
        H(M2)
        ||
        T1
        ||
        Route
        ||
        StateVersion
    )

TIMA may then observe:

    Valid(T1)
    AND
    Valid(T2)
    AND
    H(M2) == H(T2)
    AND
    StateVersionValid

and commit M2.

Every individual component may have satisfied its stated local contract.

Yet:

    B1 NEVER evaluated M2.

Therefore:

    LocalCorrectness(B1)
    AND LocalCorrectness(B2)
    AND LocalCorrectness(TIMA)
    DOES NOT IMPLY
    PathAuthorization(M2)

This is the Parallel Mutation Divergence problem.

---

# The AIC Composition Invariant

The central surviving AIC claim is the following:

    I_AIC

    For every governance-required boundary b_i in Req(M),
    the authorization evidence produced by b_i MUST remain
    structurally bound to:

        1. the exact mutation identity M,
        2. the declared execution route R,
        3. the applicable state/version bound V,
        4. the authorization evidence of the required predecessor boundary.

A representative attestation structure is:

    T1 =
        Sign_K1(
            H(M)
            ||
            RouteID
            ||
            StateVersion
            ||
            Step1
        )

    Ti =
        Sign_Ki(
            H(M)
            ||
            RouteID
            ||
            StateVersion
            ||
            Step_i
            ||
            H(T_(i-1))
        )

for i > 1.

The exact serialization, cryptographic algorithm, and protocol encoding are
implementation details.

The invariant is the requirement that mutation identity and authorization
lineage cannot be separated during composition.

---

# Intermediate Boundary Contract

For a boundary b_i to produce a valid authorization attestation T_i, the
boundary must establish:

    1. Local policy evaluation succeeds.

    2. The predecessor attestation is valid.

    3. The predecessor attestation is associated with the exact mutation
       being evaluated.

    4. The predecessor route identity matches the required route.

    5. Applicable state/version requirements are satisfied.

The critical condition is:

    PayloadHash(T_(i-1)) == H(M_current)

A valid signature over the wrong mutation is not sufficient authorization.

---

# Terminal Verification Contract

The effect-relative Terminal Irreversible Mutation Authority (TIMA) must
verify the complete authorization chain before the irreversible mutation
occurs.

Conceptually:

    T_n
      |
      v
    T_(n-1)
      |
      v
    ...
      |
      v
    T_1

TIMA must establish that every required authorization artifact is bound to
the mutation being committed.

Formally:

    FOR ALL i in Req(M):

        ExtractPayloadHash(T_i)
        ==
        H(M_commit)

and the route, state/version, predecessor relationship, and required
boundary identity must satisfy the applicable governance specification.

Only after these checks succeed may the effect-relative TIMA permit the
irreversible mutation.

---

# Effect-Relative TIMA

AIC does not define the Terminal Irreversible Mutation Authority solely as a
database write boundary.

A database transaction may be reversible while an external effect is not.

Examples include:

- External payment dispatch
- Wire transfer initiation
- SMS transmission
- Hardware actuation
- Third-party API effects
- Immutable external logging
- Other externally observable irreversible actions

Therefore, the relevant TIMA is effect-relative.

Conceptually:

    TIMA(M) = first execution step after which no available
              compensation can restore the externally observable
              world state to an observationally equivalent condition.

This distinction is critical.

Terminal database correctness does not necessarily imply pre-terminal effect
correctness.

Therefore:

    TerminalIntegrity
    !=
    PreTerminalEffectIntegrity

If a mutation-capable boundary produces an irreversible external side effect
before terminal verification, terminal database refusal may be too late.

---

# Pure Evaluation Boundary Axiom

Terminal attestation can only replace physical or inline interdiction for a
given boundary when evaluation itself does not produce an irreversible
effect.

A representative condition is:

    FOR ALL b_i in Boundaries:

        StateChange(b_i) = empty

        during evaluation of M

If evaluation produces an irreversible side effect, that boundary may itself
constitute an effect-relative TIMA and must be treated accordingly.

---

# BEAF and AIC

BEAF and AIC address different levels of the enforcement problem.

## BEAF

Boundary Evidence & Authorization Framework.

BEAF asks:

    Does the evidence produced at boundary B_i
    actually prove that B_i evaluated the applicable
    policy for the mutation?

BEAF therefore focuses on local boundary evidence and authorization truth.

---

## AIC

Active Invariant Cloning.

AIC asks:

    Does the authorization evidence remain bound to the
    exact same mutation identity as it traverses all
    governance-required boundaries?

AIC therefore focuses on transitive path composition.

Conceptually:

    BEAF
      |
      +--> Local Boundary Integrity
           "Did B_i actually evaluate what it claims to have evaluated?"

    AIC
      |
      +--> Transitive Path Composition
           "Does the authorization chain prove that every required
            boundary evaluated the exact same mutation?"

AIC does not replace BEAF.

AIC composes boundary-level evidence into a path-level authorization
discipline.

---

# What AIC Does Not Claim

AIC does NOT claim:

- A new cryptographic primitive.
- A new signature algorithm.
- A new logical operator.
- Automatic semantic equivalence.
- Automatic prevention of all mutation bypasses.
- Automatic prevention of irreversible side effects.
- Automatic protection against a compromised enforcement authority.
- Automatic physical-world safety.
- That terminal verification alone can undo pre-terminal effects.

AIC instead claims a specific architectural requirement:

    Authorization evidence must preserve mutation identity,
    route identity, and authorization lineage across the
    required enforcement path.

---

# Formal Reduction Position

AIC can be expressed using existing formal mechanisms.

For example, temporal logic can represent trace-safety properties.

Cryptographic provenance can represent authorization evidence.

Distributed reference monitors can perform local policy decisions.

State/version controls can address temporal validity.

Terminal reference monitors can enforce final commit conditions.

Therefore, AIC does not require a novel mathematical primitive.

However, the existence of equivalent building blocks does not by itself prove
that the composition invariant is redundant.

The relevant question is:

    Does independent correctness of the standard components
    logically imply the AIC composition invariant?

The Parallel Mutation Divergence construction demonstrates a candidate
counterexample.

Therefore, the surviving research question is architectural:

    Is transitive mutation binding already guaranteed by common
    reference-monitor, attestation, provenance, and terminal-verification
    compositions, or must it be explicitly specified?

---

# Structural Property vs. Vocabulary Overlay

AIC should not be defended merely by introducing new terminology.

The invariant must correspond to an independently testable structural
condition.

The distinction is:

    Vocabulary Overlay:

        Existing components are described using new terminology,
        but no new constraint or measurable behavior results.

    Architectural Composition Discipline:

        Existing components are required to satisfy an additional
        cross-boundary relation whose violation produces an
        observable security failure.

AIC survives as a composition discipline only if the latter can be
demonstrated.

---

# Research Objectives

## Objective 1

Define a formal clone model.

---

## Objective 2

Define semantic equivalence requirements.

---

## Objective 3

Define mutation identity and authorization lineage requirements.

---

## Objective 4

Develop clone survivability metrics.

---

## Objective 5

Detect clone drift.

---

## Objective 6

Detect hidden mutation paths through clone disagreement.

---

## Objective 7

Demonstrate governed execution using active clones.

---

## Objective 8

Determine whether transitive mutation binding is already guaranteed by
standard architectures.

---

## Objective 9

Measure the security and operational delta introduced by explicitly enforcing
the AIC composition invariant.

---

# Research Questions

1. What constitutes a valid invariant clone?

2. Can clone semantics be preserved across translation boundaries?

3. How is clone drift detected?

4. How are clone contradictions resolved?

5. Can clones refuse independently?

6. Is a canonical clone required?

7. Can hidden mutation paths be discovered through clone divergence?

8. What evidence proves clone survivability?

9. How is clone legitimacy established?

10. Can active cloning improve governance survivability?

11. Does independent component correctness imply path authorization?

12. Is transitive mutation binding implicit in existing architectures?

13. If not, what architectural assumptions are required to enforce it?

14. Can the AIC composition invariant be independently measured?

---

# Empirical Adversarial Benchmark

AIC must be evaluated against a baseline implementation.

The purpose of the benchmark is not to demonstrate that AIC can prevent an
attack after explicitly adding AIC rules.

The purpose is to determine whether the claimed composition invariant exists
independently of the terminology.

---

## Test Architecture

    Attacker
       |
       v
    +--------+
    |   B1   |
    +--------+
       |
       v
    +--------+
    |   B2   |
    +--------+
       |
       v
    +-------------+
    | TIMA / DB   |
    +-------------+

B1 evaluates the first governance requirement.

B2 evaluates the second governance requirement.

TIMA controls the effect-relative commit boundary.

---

# Attack A1: Parallel Mutation Divergence

### Baseline

1. Submit M1 to B1.

2. B1 approves M1 and produces T1(M1).

3. Submit M2 to B2 together with valid T1(M1).

4. B2 validates T1 as authentic but does not require:

       H(M1) == H(M2)

5. B2 approves M2.

6. B2 produces T2(M2, T1).

7. TIMA validates the signatures and commits M2.

Expected failure:

    B1 never evaluated M2.

Yet the system accepts M2 as though the required path was satisfied.

---

# AIC-Constrained Configuration

The AIC-constrained implementation requires B2 to verify:

    PayloadHash(T1) == H(M2)

and requires TIMA to verify the complete transitive chain.

Therefore:

    T1(M1) + M2

must be rejected when:

    H(M1) != H(M2)

Expected result:

    COMMIT REJECTED

---

# Falsification Criterion

AIC's composition claim is falsifiable.

If a standard, off-the-shelf microservice architecture using ordinary
reference monitors, standard authorization tokens, cryptographic
signatures, and terminal database guards naturally prevents the Parallel
Mutation Divergence attack without requiring an equivalent transitive
mutation-binding constraint, then the claimed AIC invariant may be
redundant.

Conversely, if:

    Baseline accepts M2

while:

    AIC-constrained architecture rejects M2

and the only material difference is enforcement of the transitive mutation
binding requirement, then the experiment demonstrates an operational security
delta attributable to that composition constraint.

The result does not automatically prove that AIC is universally necessary.

It establishes that the tested baseline did not guarantee the invariant.

---

# Attack Suite

The initial adversarial suite includes:

## A1 — Direct Path Bypass

Attacker bypasses a required upstream boundary.

Target:

    Path Integrity

---

## A2 — Intermediate Replay

Attacker reuses valid authorization evidence after relevant state changes.

Target:

    State / Version Binding

---

## A3 — Payload Substitution

Attacker uses authorization evidence generated for M1 with a different
mutation M2.

Target:

    Mutation Identity Binding

---

## A4 — Route Substitution

Attacker uses valid authorization evidence from one declared route on another
route.

Target:

    Route Binding

---

## A5 — Pre-Terminal Side Effect

A boundary produces an irreversible external effect before terminal
verification fails.

Target:

    Effect-Relative TIMA Placement

---

## A6 — Parallel Mutation Divergence

Different boundaries authorize different mutation identities while the
terminal verifier observes apparently valid individual attestations.

Target:

    Transitive Authorization Integrity

---

# Metrics

## Detection Rate

    DetectionRate =
        BlockedAttackInstances
        /
        TotalAttackInstances

---

## False Acceptance Rate

    FAR =
        InvalidRealizationsCommitted
        /
        InvalidRealizationAttempts

---

## Latency Overhead

    DeltaT =
        AICCommitTime
        -
        BaselineCommitTime

---

## Clone Agreement Rate

    CloneAgreementRate =
        SemanticallyEquivalentDecisions
        /
        ComparableEvaluationInstances

---

## Drift Detection Rate

    DriftDetectionRate =
        DetectedDriftInstances
        /
        InjectedDriftInstances

---

# Success Criteria

AIC succeeds as a research result if evidence demonstrates that:

- Clones remain live.
- Clones remain binding.
- Clones remain refusal-capable.
- Semantic equivalence can be specified and tested.
- Drift can be detected.
- Governed execution can be verified.
- Mutation identity can remain bound across required boundaries.
- Path divergence can be detected before the effect-relative TIMA.
- The composition invariant produces a measurable security delta where the
  baseline does not provide equivalent protection.

---

# Failure Criteria

AIC fails, or its claims must be narrowed, if evidence demonstrates that:

- Clone semantics cannot be preserved.
- Governance authority is lost during cloning.
- Drift cannot be reliably detected.
- Refusal capability cannot be maintained.
- Survivability claims cannot be reproduced.
- Standard architectures already guarantee the claimed composition invariant
  without an equivalent explicit constraint.
- The proposed invariant provides no measurable security delta.
- The invariant cannot be distinguished from existing architectural
  requirements.

Failure is an acceptable outcome.

Failure is evidence.

---

# Current Architectural Synthesis

The current research position is intentionally narrow.

AIC is not presently claimed to be:

    A new primitive.

AIC is not presently claimed to be:

    A new formal logic.

AIC is presently investigated as:

    An Architectural Composition Discipline.

The surviving composition invariant is:

    Every governance-required enforcement boundary must produce
    authorization evidence that remains structurally bound to the
    exact mutation identity, required route, applicable state/version,
    and authorization lineage necessary to establish that the required
    predecessor boundaries evaluated that same mutation before the
    effect-relative TIMA permits irreversible execution.

This is the central proposition to be implemented, attacked, measured,
and potentially falsified.

---

# Relationship Between the Layers

The research can be viewed as three related questions:

    BBIS
      |
      |  Can the governing invariant survive every
      |  mutation-capable boundary?
      v
    AIC
      |
      |  Can the invariant be actively instantiated and
      |  compositionally preserved across those boundaries?
      v
    BEAF
      |
      |  Does each boundary possess verifiable evidence
      |  that its claimed governance decision actually occurred?
      v
    TIMA
      |
      |  Does the final effect authority reject execution
      |  unless the required evidence and invariants hold?
      v
    EFFECT

These layers are analytically distinct.

No layer should be assumed to automatically prove another.

---

# Repository Principles

Evidence over assumptions.

Implementation over speculation.

Working demonstrations over theory.

Continuity over convenience.

Truth over attachment.

Falsifiability over advocacy.

Explicit assumptions over hidden assumptions.

---

# Development Path

## Phase 1

Define Active Invariant Cloning.

---

## Phase 2

Define clone lifecycle.

---

## Phase 3

Define semantic equivalence model.

---

## Phase 4

Define mutation identity and transitive authorization model.

---

## Phase 5

Implement clone survivability testing.

---

## Phase 6

Implement drift detection.

---

## Phase 7

Implement adversarial composition tests.

---

## Phase 8

Implement governed execution prototype.

---

## Phase 9

Measure baseline versus AIC-constrained architectures.

---

## Phase 10

Analyze results and narrow, strengthen, or falsify the claims.

---

# Repository Structure

    /
    ├── README.md
    ├── LICENSE
    ├── MASTER_HANDOFF.md
    ├── SESSION_HANDOFF.md
    ├── CHANGE_CONTROL.md
    ├── PROJECT_STRUCTURE.md
    ├── OPEN_QUESTIONS.md
    ├── COLLABORATION_PROTOCOL.md
    │
    ├── docs/
    │   ├── AIC_SPECIFICATION.md
    │   ├── CLONE_MODEL.md
    │   ├── SEMANTIC_EQUIVALENCE.md
    │   ├── DRIFT_DETECTION.md
    │   ├── GOVERNED_EXECUTION.md
    │   └── GLOSSARY.md
    │
    ├── research/
    │   ├── experiments/
    │   ├── findings/
    │   └── notes/
    │
    └── prototype/
        └── active_clone_demo/

---

# Collaboration

Contributors are encouraged to:

- Challenge assumptions.
- Attempt adversarial bypasses.
- Stress-test claims.
- Produce counterexamples.
- Produce evidence.
- Document failures.
- Document successes.
- Attempt independent reductions to existing mechanisms.
- Identify hidden assumptions.
- Attempt to falsify the composition invariant.

The objective is not to defend a theory.

The objective is to discover the truth.

---

# Final Research Statement

Active Invariant Cloning (AIC) is an architectural composition discipline
for preserving governing invariant identity across mutation-capable execution
boundaries.

AIC does not introduce a novel cryptographic primitive or logical operator.

Instead, AIC identifies and tests a cross-boundary Composition Invariant:

    A downstream authorization is valid only when its evidence
    structurally and transitively proves that every required
    predecessor boundary evaluated the exact same mutation identity,
    under the required route and applicable state/version bounds,
    before the effect-relative Terminal Irreversible Mutation Authority
    permits the irreversible effect.

The central distinction is:

    Local authorization evidence
    !=
    Transitive path authorization

and:

    Attestation set membership
    !=
    Proof that every required boundary evaluated the same mutation.

The Parallel Mutation Divergence attack provides a concrete test of this
distinction.

The research therefore does not ask:

    "Can AIC be described using existing primitives?"

It can.

The research asks:

    "Do existing primitives, when independently composed according to
     their ordinary contracts, already guarantee the AIC composition
     invariant?"

If yes, AIC's architectural claim is redundant and must be narrowed.

If no, and explicit transitive mutation binding produces a reproducible
security delta, then AIC identifies a previously unstated composition
requirement in the tested architecture class.

That question is empirical.

The repository exists to answer it.

---

Implementation before innovation.

Evidence before belief.

Continuity before convenience.

Truth survives even when execution does not.
