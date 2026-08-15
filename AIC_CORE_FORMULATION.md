# ACTIVE INVARIANT CLONING (AIC)
## LOCKED CORE FORMULATION
## Status: AUTHORITATIVE BASELINE

AIC is a mutation-binding composition invariant.

AIC is NOT an intent-preservation engine, semantic-equivalence
solver, policy-correctness verifier, benevolence detector, or
physical-safety mechanism.

AIC establishes a narrower and formally distinct property:

When every mutation-capable transition is explicitly represented,
cryptographically bound to its predecessor state and mutation
payload, authorized within the applicable authority context,
deterministically applied, and every composition operation
(including delegation, fork, join, rebind, and composition) is
itself reified as an explicit mutation subject to the same
verification discipline, terminal authorization remains
attributable to the exact composed mutation trajectory that
produced the live terminal state.

The core invariant is:

I_AIC:

For a terminal mutation T evaluated against live state S_N,

    V_AIC_TERM(S_N, T, A_T) = TRUE

implies that the authority enabling T is attributable through
an unbroken, verifiable chain of predecessor states and
mutations back to the authoritative root state S_0.

Formally, for trajectory

    π = (S_0, Δ_0, A_0, S_1, ...,
         S_N, Δ_T, A_T, S_{N+1})

where every mutation-capable transition satisfies the AIC
verification predicate and terminal verification is performed
against the exact live predecessor state:

    ValidTrajectory(π)
        ⇒
    AttributableLineage(T, π)

The attribution property requires:

1. Parent Binding

   Every mutation authorization is bound to the exact predecessor
   state against which it was evaluated.

2. Mutation Binding

   The authorization is bound to the exact mutation payload being
   authorized.

3. Authority Binding

   The mutation is attributable to the principal whose authority
   authorizes that mutation in the applicable state/context.

4. Context Binding

   The authorization is valid only within the applicable execution
   context, including any required terminal identity and temporal
   freshness constraints.

5. Exact Successor Derivation

   The successor state is the deterministic result of applying the
   authorized mutation to the exact predecessor state.

6. Composition Reification

   Delegation, fork, join, composition, rebind, and equivalent
   state-altering operations are themselves explicit mutations.
   There are no unmodeled state transitions.

7. Root-Anchored Authorization

   Authorization paths must be structurally well-founded and
   traceable to the authoritative root. Mere graph-edge membership
   or cyclic self-reference is not sufficient to establish
   authority.

8. Live Terminal Evaluation

   Terminal authorization is evaluated against the exact live
   state immediately governing the terminal mutation.

Under these conditions, an adversary cannot cause terminal
authorization to acquire a valid attributable lineage from outside
the actual mutation trajectory without violating at least one of
the AIC verification conditions or the structural assumptions of
the model.

------------------------------------------------------------
## WHAT AIC PROVES
------------------------------------------------------------

AIC proves structural mutation lineage and authorization
attribution.

Specifically:

    WHO authorized the mutation?
    WHAT exact mutation was authorized?
    AGAINST WHICH predecessor state?
    UNDER WHICH authority/context?
    HOW was the successor derived?
    THROUGH WHICH composed trajectory did authority reach
    the terminal mutation?

AIC therefore establishes:

    Local Mutation Attribution
    +
    Mutation-State Binding
    +
    Deterministic Successor Integrity
    +
    Compositional Authorization Lineage
    +
    Root-Anchored Terminal Attribution

------------------------------------------------------------
## WHAT AIC DOES NOT PROVE
------------------------------------------------------------

AIC alone does NOT prove:

    Semantic intent preservation
    Policy correctness
    Goal preservation
    Safety
    Benevolence of an authorized principal
    Prevention of authorized malice
    General semantic equivalence
    Physical execution correctness
    Physical safety
    Correctness of an external tool/compiler
    Immutability of the original policy
    Prevention of authorized policy erosion

These are separate properties requiring additional invariants.

------------------------------------------------------------
## CRITICAL DISTINCTION
------------------------------------------------------------

The following statements MUST NOT be conflated:

    "The mutation was authorized and attributable."

versus

    "The mutation preserved the original intent."

AIC establishes the first.

AIC does not, by itself, establish the second.

Therefore:

    AIC ≠ Intent Preservation

and:

    Intent Preservation ≠ AIC

Intent-preservation mechanisms may be layered above AIC without
changing the identity of AIC, provided those mechanisms introduce
additional semantic or policy invariants rather than being silently
attributed to AIC itself.

------------------------------------------------------------
## ROUND 2 FALSIFICATION — CORRECT INTERPRETATION
------------------------------------------------------------

The authorized weight-erosion attack demonstrated that a sequence
of individually valid and authorized mutations can progressively
alter the governing objective.

Therefore:

    Local authorization
        does NOT imply
    preservation of the original semantic objective.

This falsifies any claim that AIC alone guarantees semantic intent
continuity.

It does NOT falsify the narrower AIC composition claim.

The attack is therefore classified as:

    FALSIFICATION OF INTENT-PRESERVATION CLAIM

not:

    FALSIFICATION OF MUTATION-BINDING COMPOSITION

------------------------------------------------------------
## ROUND 3 RESULT
------------------------------------------------------------

Round 3 subjected the AIC composition invariant to adversarial
testing involving:

    Authorized delegation
    Concurrent branches
    Revocation
    Join
    Rebind
    Cyclic delegation
    Terminal authorization
    Root-lineage disruption

The strongest attempted counterexample was a cyclic delegation
composition in which two branches could potentially create a
self-referential authorization cycle after revocation.

The attack succeeds only if authorization is defined as naive
graph membership.

Under the AIC composition model, authorization must instead be
root-anchored and well-founded.

Therefore a delegation cycle with no valid derivation path from
the authoritative root does not constitute authority.

The terminal verifier must reject such a capability.

Accordingly, under the stated model and boundary conditions:

    I_AIC survives Round 3.

------------------------------------------------------------
## STRONGEST SURVIVING THEOREM
------------------------------------------------------------

THEOREM — TERMINAL COMPOSITION LINEAGE INTEGRITY

Let π be a finite execution trajectory beginning at authoritative
state S_0.

Assume:

    1. Every mutation-capable transition is explicitly represented.
    2. Every transition passes AIC verification.
    3. Apply is deterministic.
    4. Successor state derivation is cryptographically bound to the
       predecessor state and mutation.
    5. Delegation, fork, join, composition, and rebind are explicit
       mutations.
    6. Authorization is root-anchored and well-founded.
    7. Terminal verification uses the exact live predecessor state.
    8. Required terminal identity and freshness bindings are present.
    9. Cryptographic primitives and authority keys are uncompromised.

Then:

    ValidTrajectory(π)
        ⇒
    AttributableLineage(T, π)

That is:

    A terminal mutation accepted by AIC possesses an attributable
    structural authorization lineage through the exact mutation
    trajectory that produced the live terminal state.

------------------------------------------------------------
## RESEARCH BOUNDARY
------------------------------------------------------------

AIC answers:

    "Can terminal authorization be attributed to the exact
     mutation trajectory that produced the state?"

AIC does NOT answer:

    "Was that trajectory semantically correct?"

Those are deliberately separate research questions.

The first is the domain of AIC.

The second requires additional invariants.

------------------------------------------------------------
## LOCKED POSITION
------------------------------------------------------------

AIC is retained as a valid foundational primitive for:

    Mutation-Bound Authorization
    Structural Lineage
    Compositional Authorization Attribution
    Terminal Authorization Traceability

AIC's identity SHALL NOT be broadened to include:

    Intent Preservation
    Semantic Safety
    Policy Correctness
    Physical Safety

Any future mechanism addressing those properties must be
identified as an additional invariant or higher-layer mechanism.

The central AIC statement is therefore:

    AUTHORITY MUST SURVIVE COMPOSITION AS AN
    ATTRIBUTABLE BINDING TO THE EXACT MUTATION
    TRAJECTORY THAT PRODUCED THE TERMINAL STATE.

Not:

    "Every authorized mutation is good."

And not:

    "Every authorized mutation preserves the original intent."

AIC guarantees attribution of authorized change.

It does not guarantee correctness of the change.

------------------------------------------------------------
## STATUS
------------------------------------------------------------

AIC CORE FORMULATION: LOCKED

Round 2:
    Intent-preservation claim — FALSIFIED.

Round 3:
    AIC composition invariant — SURVIVES.

Current research position:

    AIC = structural mutation-binding composition invariant.

    Higher-level semantic/policy invariants may be composed above AIC.

    No future analysis may silently transfer those higher-level
    guarantees back onto AIC itself.
