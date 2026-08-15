# AIC ROUND-4 — CLAIM-SCOPE SPECIFICATION

**Target:** Active Invariant Cloning (AIC)  
**Repository:** Active-Invariant-Cloning-Lab  
**Baseline:** AIC-BASELINE-v1  
**Status:** AUTHORITATIVE CLAIM-SCOPE RESOLUTION  
**Purpose:** Convert the surviving AIC claims into bounded, formally stated, evidence-bearing, falsifiable propositions.

---

# 1. PURPOSE

Round 4 does not attempt to restore claims of primitive novelty.

The purpose of this specification is to establish the strongest scientifically defensible form of AIC after adversarial review.

The central question is no longer:

> "Does AIC invent a new security primitive?"

The question is:

> "What precisely can AIC claim, under what assumptions, with what evidence, and what observation would falsify the claim?"

AIC therefore adopts an evidence-first claim structure:

    CLAIM
      ↓
    FORMAL OBJECT
      ↓
    ASSUMPTIONS
      ↓
    REQUIRED EVIDENCE
      ↓
    FALSIFICATION TEST
      ↓
    PASS / FAIL

---

# 2. AUTHORITATIVE POSITION

AIC does not claim to introduce a novel security primitive.

AIC is an architecture-relative governance and enforcement pattern for evaluating whether required enforcement conditions survive across a declared mutation-capable realization path.

The central distinction is:

    TerminalStateCorrectness(S)
        ≠
    PathEnforcementIntegrity(σ)

A realization may therefore be terminally correct while remaining governance-invalid because one or more required enforcement conditions were bypassed, omitted, reordered, invalidated, or rendered non-binding.

AIC calls this condition:

    InvalidRealization

The claim is bounded to a declared architecture model.

AIC does not automatically establish:

    - complete discovery of all possible mutation paths;
    - universal semantic equivalence of cloned predicates;
    - universal physical irreversibility;
    - autonomous enforcement of globally stateful predicates;
    - novel cryptographic or reference-monitor primitives;
    - counterfactual refusal capability from ordinary runtime traces alone.

---

# 3. CORE FORMAL OBJECT

Let:

    S = system state
    M = governed mutation
    σ = realization trace
    P = declared realization path
    R(M) = required enforcement boundaries for M
    T = Scoped TIMA
    V(S) = terminal-state correctness predicate

Define:

    PathEnforcementIntegrity(M, σ)

as the property that every enforcement condition required by the declared governance specification for M is satisfied on the declared realization path before the governed irreversible effect at T.

A bounded formulation is:

    PEI(M, σ, P, R, T)
    =
    ∀b ∈ R(M):

        Required(b, M)
        ∧ Present(b, P, σ)
        ∧ BoundToMutation(b, M, σ)
        ∧ ValidEvidence(b, M, σ)
        ∧ EnforcedBefore(b, T, σ)

subject to the declared architecture model and its assumptions.

Governance validity is then:

    GovernanceValid(M, σ)
    =
    TerminalStateCorrect(S_commit)
    ∧
    PEI(M, σ, P, R, T)

This permits:

    TerminalStateCorrect = TRUE
    PathEnforcementIntegrity = FALSE

therefore:

    GovernanceValid = FALSE

---

# 4. INVALID REALIZATION

Define:

    InvalidRealization(M, σ)

iff:

    TerminalStateCorrect(S_commit) = TRUE

and:

    PathEnforcementIntegrity(M, σ) = FALSE

Therefore:

    InvalidRealization
    =
    terminally correct
    +
    path-enforcement invalid

This is a taxonomy for a class of governance failures.

It is not claimed to be a novel security primitive.

It may overlap with existing concepts including:

    - authorization bypass;
    - reference-monitor bypass;
    - control-flow violations;
    - workflow violations;
    - protocol violations;
    - backend trust-boundary bypasses;
    - temporal safety violations.

The AIC contribution is the explicit architectural classification of these failures according to the distinction:

    "correct state"
        versus
    "correct realization path."

---

# 5. CLAIM 1 — PATH-DEPENDENT GOVERNANCE IS DISTINCT FROM TERMINAL CORRECTNESS

## Claim

Terminal-state correctness does not imply path-enforcement correctness.

## Formal proposition

There exists a realization σ such that:

    TerminalStateCorrect(S_commit) = TRUE

while:

    PathEnforcementIntegrity(M, σ) = FALSE

## Required evidence

A test system must demonstrate:

1. A mutation reaches a terminal state satisfying all state predicates.
2. At least one mandatory enforcement boundary is bypassed.
3. The terminal state remains otherwise valid.
4. The bypass is observable in the realization trace.

## Falsification

The claim is falsified if no realizable system can exhibit:

    TerminalCorrect = TRUE
    ∧
    PathIntegrity = FALSE

under a governance model that requires path compliance.

## Status

SURVIVING CLAIM.

---

# 6. CLAIM 2 — INVALID REALIZATION IS A USEFUL FAILURE CLASS

## Claim

InvalidRealization provides a useful classification for terminally correct executions that violate mandatory realization-path requirements.

## Required evidence

Construct at least three distinct examples:

    A. authorization/guard bypass
    B. backend/direct-write bypass
    C. skipped mandatory enforcement boundary

Each must produce:

    TerminalCorrect = TRUE
    PathIntegrity = FALSE

## Falsification

The taxonomy is weakened if every example reduces without loss of explanatory value to an existing category and the InvalidRealization label provides no additional classification value.

## Status

USEFUL TAXONOMY; NOT CLAIMED AS NOVEL PRIMITIVE.

---

# 7. CLAIM 3 — AIC IS ARCHITECTURE-MODEL-RELATIVE

## Claim

AIC's path-integrity guarantee is conditional upon the correctness and completeness of the declared architecture model.

Let:

    DeclaredPaths
    ⊆
    ActualMutationPaths

unless a completeness assumption is established.

AIC therefore guarantees only:

    ∀P ∈ DeclaredPaths:
        PEI(P)

unless:

    ActualMutationPaths ⊆ DeclaredPaths

has independently been established.

## Required evidence

The implementation must identify:

    - mutation sources;
    - mutation-capable boundaries;
    - path transitions;
    - TIMA;
    - required enforcement boundaries;
    - known alternate paths.

## Falsification

A discovered mutation-capable path outside the declared model that permits a governed mutation to reach TIMA without required enforcement falsifies any claim of global path completeness.

It does NOT necessarily falsify the narrower declared-path property.

## Status

RETAINED WITH EXPLICIT SCOPE LIMITATION.

---

# 8. CLAIM 4 — REFUSAL CAPABILITY MUST BE DECOMPOSED

The term "Refusal Capability" must not be treated as a single directly observable property.

AIC distinguishes:

### R1 — Structural Mandatory Traversal

    Every modeled source→TIMA path contains B.

This is a graph property.

### R2 — Binding Enforcement

    A BLOCK decision at B prevents valid progression through
    the governed realization model.

This is an enforcement-semantics property.

### R3 — Observed Refusal

    B actually issued BLOCK during execution.

This is an observational property.

### R4 — Counterfactual Prevention

    Had B issued BLOCK, the governed irreversible effect
    would not have occurred.

This is a counterfactual/causal property.

These propositions are not equivalent.

In particular:

    R1 ≠ R2
    R2 ≠ R3
    R3 ≠ R4

and:

    R1 + R2 + R3

does not automatically establish:

    R4

without an appropriate causal model.

## Repository rule

The original unrestricted statement:

> "AIC proves Refusal Capability."

MUST NOT be used.

The preferred terminology is:

> "AIC evaluates structural traversal and binding enforcement conditions, while counterfactual refusal capability requires an explicit causal model."

---

# 9. CLAIM 5 — DOMINATOR STATUS IS NOT CAUSAL AUTHORITY

## Claim

A boundary dominating all modeled paths to TIMA does not, by itself, establish causal refusal authority.

Formally:

    Dominates(B, TIMA)
        ⇏
    CausallyBlocks(B, M)

## Counterexamples

The claim survives if any of the following can occur:

    - downstream ignores BLOCK;
    - concurrent execution commits M;
    - B produces an irreversible side effect before BLOCK;
    - an unmodeled path bypasses B;
    - duplicated mutation execution bypasses the intended authority;
    - local IPC bypasses network-level dominance.

## Required evidence

The architecture must separately demonstrate:

    Path dominance
    +
    Binding enforcement
    +
    Mutation binding
    +
    Side-effect ordering
    +
    Concurrency control

## Status

SURVIVING DISTINCTION.

---

# 10. CLAIM 6 — ACTIVE INTERDICTION IS NOT CLAIMED AS A NOVEL PRIMITIVE

AIC does not claim that active intermediate interdiction is a newly invented enforcement mechanism.

Known mechanisms include:

    - reference monitoring;
    - access control;
    - capability systems;
    - control-flow enforcement;
    - distributed policy execution;
    - cryptographic attestation;
    - terminal verification;
    - transactional concurrency control.

AIC may compose these mechanisms into an architecture for satisfying path-enforcement requirements.

Therefore:

    AIC ≠ novel primitive

but:

    AIC = architecture/policy composition

may be claimed.

---

# 11. CLAIM 7 — ACTIVE INTERDICTION AND TERMINAL ATTESTATION

The correct relationship is:

    Conditional Behavioral Equivalence

not:

    Mechanism Identity

Active interdiction:

    B → BLOCK → progression stops

Terminal attestation:

    B → signed evidence → downstream execution
                         → TIMA verification
                         → COMMIT / REFUSE

They may produce equivalent commit/refusal outcomes under a defined threat model.

Required assumptions include:

    1. No irreversible intermediate side effects.
    2. Terminal verification is fail-closed.
    3. Evidence is cryptographically bound to M.
    4. Evidence is state-bound where required.
    5. Evidence is fresh and replay-resistant.
    6. Required ordering is enforced.
    7. Concurrency cannot invalidate authorization.
    8. TIMA correctly validates the evidence.
    9. No unmodeled mutation path exists within the claim scope.

Therefore:

    BehavioralEquivalence
        ≠
    MechanismIdentity

---

# 12. CLAIM 8 — PROVENANCE DOES NOT ALONE ESTABLISH ENFORCEMENT

Authenticated provenance can establish facts such as:

    - B issued approval;
    - B was present;
    - M was associated with B's evidence;
    - state/version information;
    - ordering;
    - evidence authenticity.

Provenance alone does not necessarily establish:

    - B could have prevented M;
    - B's refusal would have prevented M;
    - no alternate mutation path existed;
    - the enforcement decision was causally binding.

Therefore:

    Provenance
        ≠
    Complete enforcement proof

AIC may be implemented using provenance plus additional enforcement and architecture evidence.

---

# 13. CLAIM 9 — LTL CAPTURES THE TRACE COMPONENT, NOT THE ENTIRE CLAIM

A path-safety requirement can be expressed as a temporal trace property.

Example:

    □(
        Commit(TIMA, M)
        →
        ∧b∈R(M)
            Approved(b,M) Before Commit(TIMA,M)
    )

This captures the temporal relationship between required evidence and commit.

However, LTL does not independently determine:

    - the complete path universe;
    - governance requirements;
    - semantic equivalence of predicates;
    - causal refusal capability;
    - completeness of the architecture model.

Therefore:

    AIC
      ≠
    LTL alone

but:

    PathEnforcementTraceSafety
      ⊆
    properties expressible by temporal logic

under an appropriate event model.

---

# 14. CLAIM 10 — AUTHORITY CLONING IS LIMITED BY PREDICATE CLASS

AIC MUST NOT claim that every invariant can be independently cloned without coordination.

Classify predicates as:

    P_static
    P_context
    P_dynamic

where:

    P_static
        = independent of mutable global state

    P_context
        = dependent on boundary-local execution context

    P_dynamic
        = dependent on authoritative mutable state

Static and local-context predicates may be independently evaluated when semantic assumptions permit.

Dynamic predicates may require:

    - centralized authority;
    - consensus;
    - transactional locking;
    - state-machine replication;
    - MVCC;
    - leases;
    - terminal revalidation;
    - other synchronization mechanisms.

Therefore:

    "Active cloning" does not imply
    "independent autonomous replication of global authority."

The repository MUST explicitly distinguish:

    predicate replication
        from
    authority replication.

---

# 15. CLAIM 11 — TOCTOU IS A REQUIRED CONTROL CONDITION

AIC does not claim to invent a TOCTOU solution.

If:

    B evaluates M against S0

and:

    TIMA commits against S1

then authorization may become stale.

AIC therefore requires one or more recognized mechanisms where state-sensitive authorization crosses time:

    - state-version binding;
    - MVCC;
    - terminal revalidation;
    - transactional locking;
    - leases;
    - serializability;
    - equivalent concurrency control.

AIC's claim is:

> Path-enforcement validity requires protection against authorization becoming invalid between evaluation and irreversible commit.

AIC does not claim:

> AIC invented the mechanism that prevents this race.

---

# 16. CLAIM 12 — SCOPED TIMA REQUIRES EXPLICIT DERIVATION

TIMA MUST NOT be defined merely as:

> "whatever irreversible mutation is relevant to the claim."

The repository must document:

    1. governed mutation M;
    2. affected state variables V;
    3. irreversible effect E;
    4. component exercising commit authority;
    5. claim scope;
    6. assumptions about reversibility;
    7. any earlier side effects considered governed.

If multiple competent auditors can derive different TIMAs from the same system without a documented rule, the TIMA specification is underdetermined.

Therefore:

    TIMA derivation
        =
    an auditable architectural procedure

not:

    an implicit intuition.

---

# 17. CLAIM 13 — COMPENSATION DOES NOT ERASE PATH VIOLATION

If:

    Bypass(B1)
        →
    Commit(M)
        →
    Compensation(C)
        →
    StateRestored

then:

    TerminalStateCorrect = TRUE

may coexist with:

    PathEnforcementIntegrity = FALSE

and therefore:

    GovernanceValid = FALSE

when path compliance is part of the governance contract.

Compensation restores state.

It does not retroactively establish that the required enforcement path occurred.

---

# 18. MINIMUM SURVIVING FORMAL CORE

The minimal operational form is:

    Valid(M, σ)
    ⇔
    TerminalCorrect(S_commit)
    ∧
    ∀b ∈ Req(M):

        Present(b, σ)
        ∧
        Bound(b, M)
        ∧
        ValidEvidence(b)
        ∧
        EnforcedBeforeCommit(b)

This core is implementable using existing mechanisms.

Therefore AIC does not claim primitive novelty.

Its architectural contribution is the explicit composition and classification of these requirements around path-dependent governance validity.

---

# 19. NOVELTY CLASSIFICATION

| Dimension | Classification |
|---|---|
| New cryptographic primitive | NO |
| New reference-monitor primitive | NO |
| New concurrency mechanism | NO |
| New provenance mechanism | NO |
| New temporal logic | NO |
| New control-flow mechanism | NO |
| New distributed consensus mechanism | NO |
| Distinct governance framing | YES |
| Distinct failure taxonomy | YES |
| Architecture-level synthesis | YES |
| Novel security primitive | NOT ESTABLISHED |

The repository MUST NOT use "novel security primitive" as an unqualified claim.

---

# 20. REQUIRED EXPERIMENTAL PROGRAM

The surviving claims must be tested empirically.

## Experiment A — Invalid Realization

Construct:

    B1 → B2 → TIMA

where B2 is mandatory.

Attack:

    B1 → TIMA

Measure:

    TerminalStateCorrect
    PathEnforcementIntegrity
    GovernanceValid

Expected result:

    TRUE
    FALSE
    FALSE

Falsification:

If the system cannot distinguish the two executions, the proposed operationalization fails.

---

## Experiment B — Terminal Attestation

Compare:

    System A:
        active interdiction

    System B:
        signed path attestation + terminal verification

Test:

    - missing boundary;
    - reordered boundary;
    - forged evidence;
    - replay;
    - stale state;
    - concurrent mutation;
    - alternate route.

Measure whether both systems produce equivalent commit/refusal outcomes under the declared assumptions.

The experiment MUST NOT claim mechanism identity merely because outcomes coincide.

---

## Experiment C — Path Discovery

Introduce an intentionally undisclosed mutation path.

Determine whether the architecture detects:

    ActualPaths
        ≠
    DeclaredPaths

This experiment establishes the practical importance of architecture completeness.

---

## Experiment D — Clone Drift

Deploy:

    B1 invariant
    B2 clone
    B3 clone

Introduce controlled semantic drift.

Measure:

    detection latency;
    false negatives;
    false positives;
    decision divergence.

This determines whether invariant cloning provides measurable engineering value even without primitive novelty.

---

## Experiment E — TOCTOU

Perform:

    B1 evaluation against S0
    concurrent mutation S0 → S1
    TIMA commit attempt

Compare:

    no version binding;
    state-version binding;
    terminal revalidation;
    transactional locking.

AIC MUST demonstrate that its path-validity claim does not silently assume stale authorization remains valid.

---

# 21. FALSIFICATION MATRIX

| Claim | Evidence Required | Falsification |
|---|---|---|
| Terminal correctness ≠ path integrity | Valid terminal state + invalid path | No separable example |
| InvalidRealization is useful | Multiple distinguishable examples | Existing taxonomy explains all cases equally without loss |
| Declared-path claim is bounded | Explicit architecture model | Hidden global claim |
| Dominator ≠ causal authority | Counterexample | P1 consistently establishes causal blocking |
| Provenance ≠ enforcement alone | Provenance/enforcement separation | Provenance alone establishes binding prevention |
| LTL captures trace component | Formal trace encoding | Required trace property cannot be represented |
| Dynamic predicates require coordination | Drift/race experiment | Independent replicas remain decision-equivalent under adversarial mutation |
| TOCTOU matters | Concurrent state mutation | Earlier authorization remains valid without synchronization |
| Compensation doesn't erase path violation | Restore-after-bypass experiment | Governance model treats restoration as retroactive path compliance |
| AIC has no demonstrated novel primitive | Existing mechanism reproduction | AIC requires a demonstrably new mechanism |

---

# 22. EVIDENCE HIERARCHY

AIC adopts the following evidence hierarchy:

    Level 0 — Assertion
        "The architecture says B is mandatory."

    Level 1 — Specification
        Formal requirement identifies B.

    Level 2 — Structural Evidence
        Architecture/code demonstrates B lies on declared paths.

    Level 3 — Behavioral Evidence
        Runtime demonstrates B evaluates M.

    Level 4 — Enforcement Evidence
        BLOCK/approval semantics demonstrably constrain progression.

    Level 5 — Cryptographic Evidence
        Evidence is mutation/state/path bound and verifiable.

    Level 6 — Adversarial Evidence
        Bypass, replay, race, drift, and alternate-path tests fail
        as expected.

    Level 7 — Independent Reproduction
        Another evaluator reproduces the result.

No lower evidence level should be presented as equivalent to a higher one.

---

# 23. CLAIM LANGUAGE RULES

The following language is prohibited unless separately demonstrated:

    "AIC proves system-wide security."

    "AIC guarantees complete path coverage."

    "AIC introduces a novel security primitive."

    "AIC proves counterfactual refusal capability."

    "AIC eliminates TOCTOU."

    "AIC independently replicates global authority."

    "AIC proves semantic equivalence of all clones."

Preferred language:

    "AIC evaluates..."

    "AIC specifies..."

    "AIC classifies..."

    "AIC provides an architecture-relative condition..."

    "The implementation demonstrates..."

    "Under the declared assumptions..."

    "For the declared realization path..."

    "The evidence establishes..."

---

# 24. FINAL AUTHORITATIVE CLAIM

The strongest scientifically defensible AIC claim is:

> AIC provides an architecture-relative governance and enforcement pattern for evaluating whether required enforcement conditions survive across a declared mutation-capable realization path. It distinguishes terminal-state correctness from path-enforcement integrity and classifies executions that are terminally correct but path-invalid as Invalid Realizations. AIC does not claim a novel security primitive, universal path completeness, universal semantic equivalence, or directly observable counterfactual refusal capability. Its guarantees are conditional upon the declared architecture model, governance specification, TIMA definition, evidence validity, and enforcement assumptions.

---

# 25. FINAL STATUS

    PROPERTY EXISTENCE
        SURVIVES

    OPERATIONALIZABILITY
        SURVIVES WITH BOUNDARY CONDITIONS

    ENFORCEMENT DISTINCTIVENESS
        NOT NOVEL

    PRIMITIVE NOVELTY
        NOT ESTABLISHED

    GOVERNANCE TAXONOMY
        SURVIVES

    ARCHITECTURAL SYNTHESIS
        SURVIVES

    COUNTERFACTUAL REFUSAL CAPABILITY
        REQUIRES SEPARATE CAUSAL MODEL

    GLOBAL PATH COMPLETENESS
        NOT CLAIMED

    EVIDENCE STANDARD
        EXPLICIT

    FALSIFIABILITY
        REQUIRED

---

# 26. ROUND-4 RESOLUTION

The AIC research program therefore proceeds under the following locked principle:

> **Do not defend a stronger claim than the evidence can establish.**

AIC's value is not dependent upon proving primitive novelty.

The surviving research question is:

> **Can path-dependent governance validity be specified, evidenced, tested, and falsified independently of terminal-state correctness?**

That question is empirically testable.

Round 4 therefore closes the novelty dispute and moves AIC from speculative primitive discovery toward experimentally testable architecture and governance research.

---

**END OF AIC ROUND-4 CLAIM-SCOPE SPECIFICATION**
