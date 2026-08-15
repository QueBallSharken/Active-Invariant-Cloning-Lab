RESOLVED ARCHITECTURAL CRITICISMS
=================================

Document Status: LOCKED
Baseline: AIC-BASELINE-v1

RC-001 — "TIMA Is Unknowable"
-----------------------------

Previous objection:

Distributed systems may contain asynchronous effects, eventual
consistency, speculative execution, external APIs, and multiple
irreversible consequences. Therefore no universal TIMA can exist.

Resolution:

AIC does not require a universal TIMA.

TIMA is scoped to the governance claim.

A valid claim MUST explicitly identify the irreversible primitive
relevant to that claim.

Disposition:

    RESOLVED BY SCOPE BOUNDING


RC-002 — "Co-Location Collapse"
--------------------------------

Previous objection:

Upstream invariant checks are either redundant with the terminal
authority or operate on incomplete/stale state.

Resolution:

AIC does not require upstream boundaries to reproduce the terminal
dynamic predicate.

Invariant conditions may be decomposed into:

    P_static
    P_context
    P_dynamic

Static and appropriately bounded contextual predicates can be
enforced before the terminal dynamic state evaluation.

The terminal authority remains responsible for predicates requiring
authoritative transactional state.

Disposition:

    RESOLVED AS A GENERAL FATAL OBJECTION

    REMAINS VALID AS A DESIGN CONSTRAINT FOR NON-MONOTONIC
    OR STATE-DEPENDENT UPSTREAM PREDICATES


RC-003 — "AIC Is Merely Observability"
--------------------------------------

Previous objection:

If a system merely records that an invariant was preserved, AIC
adds no enforcement mechanism.

Resolution:

AIC distinguishes:

    observation

from:

    refusal capability.

A boundary capable of preventing progression before the relevant
mutation authority is reached is an enforcement boundary.

A passive log cannot substitute for that capability.

Disposition:

    RESOLVED


RC-004 — "Invariant Cloning Means Authority Cloning"
----------------------------------------------------

Previous objection:

The word "cloning" implies that refusal authority and state context
are duplicated across boundaries.

Resolution:

AIC does not require authority duplication.

The implementation concept is:

    Refusal-Capable Constraint Propagation

Authority remains scoped to the boundary possessing the legitimate
ability to refuse the governed transition.

The invariant's identity and applicable constraint semantics are
propagated; authority is not assumed to be globally cloned.

Disposition:

    TERMINOLOGY REFINEMENT REQUIRED


RC-005 — "Continuity Is Just Provenance"
---------------------------------------

Previous objection:

A complete provenance record can reconstruct the entire execution
path, making continuity unnecessary.

Resolution:

Provenance records what happened.

Continuity evaluates whether required refusal capability remained
binding during the path.

A provenance record can therefore prove that a Continuity Gap
occurred without itself preventing the gap.

Disposition:

    DISTINCT PROPERTY


RC-006 — "Continuity Is Just Authorization"
-------------------------------------------

Previous objection:

If every executor is authorized, end-to-end continuity adds nothing.

Resolution:

Per-hop authorization does not establish that every required
governance condition remained active across the entire realization
path.

AIC evaluates the path-level preservation of required refusal
conditions.

Disposition:

    DISTINCT PATH PROPERTY


LOCK RULE
---------

These resolutions are part of the AIC architectural baseline.

Future audits may challenge the formal validity of the resolutions,
but MUST NOT silently revert AIC to the broader definitions that
generated the original objections.

Any change to a locked definition creates a new baseline version.

END
===
