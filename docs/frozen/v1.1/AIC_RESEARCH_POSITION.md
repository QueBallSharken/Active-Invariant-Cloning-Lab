# AIC RESEARCH POSITION (v1.1 – Frozen)

## Status

**Research Position: Frozen**

This document establishes the current evidentiary position of Active Invariant Cloning (AIC) following adversarial replication and reduction analysis.

It does **not** declare AIC a novel security primitive.

It defines the property under investigation, the strongest surviving interpretation, the known reductions, and the empirical conditions under which the claim may be strengthened or falsified.

---

# 1. Core Research Question

The central question is:

> Does the requirement that every mandatory enforcement condition remain causally binding upon irreversible realization constitute a useful, measurable architectural security property that is not adequately captured by existing provenance, authorization, capability, information-flow, or terminal-enforcement models?

This question remains open.

Novelty is therefore treated as a **research hypothesis**, not as an axiom.

---

# 2. AIC Core Property

AIC is concerned with the relationship between the validity of a terminal state and the enforcement conditions that governed its realization path.

The original formulation was:

\[
Validity(S) =
StateValidity(S)
\land
\bigwedge_{e \in Path(S)} CanBlock(e,M)
\]

This formulation is retained as the conceptual starting point but requires clarification of the meaning of `CanBlock`.

The research-critical distinction is:

> The existence of a guard is not equivalent to the guard possessing effective causal authority over the realization of a specific mutation.

A guard may exist, evaluate a mutation, or produce an observation without possessing any ability to prevent that mutation from reaching irreversible realization.

---

# 3. Causal Realization Integrity

For research purposes, the property under investigation is designated:

**Causal Realization Integrity (CRI)**

CRI asks:

> Can the protected state transition achieve irreversible realization without satisfying every mandatory enforcement condition on its claimed realization path?

If the answer is yes, the enforcement condition is not causally binding upon that realization.

If the answer is no, the condition remains causally binding.

AIC therefore investigates:

\[
CRI(M) =
\bigwedge_{e \in RequiredPath(M)}
CausalVeto(e,M)
\]

where `CausalVeto(e,M)` means:

> Boundary `e` possesses an enforceable condition such that, absent valid satisfaction of that condition, mutation `M` cannot achieve the protected irreversible realization.

---

# 4. Causal Veto Is Broader Than Synchronous Blocking

`CausalVeto` must not be interpreted as requiring a particular implementation mechanism.

At least two implementation classes may satisfy the property.

### Synchronous Enforcement

```text
M
│
▼
Boundary A
│
├── refuse ──► STOP
│
▼
Boundary B
│
├── refuse ──► STOP
│
▼
TIMA
