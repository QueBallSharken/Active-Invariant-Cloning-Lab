# Active Invariant Cloning (AIC) Falsification Plan

## Status

Research protocol for empirical evaluation of AIC claims.

Repository state at protocol creation:

- All tests passing
- 103/103 passing
- Invariant continuity gap demonstrated between ticket and receipt

---

# 1. Core AIC Claim

A governing invariant can survive every mutation-capable boundary as an active authorization condition until the irreversible primitive is reached.

In practical terms:

A mutation-capable boundary must not be able to silently replace, weaken, substitute, or drift the governing invariant without detection.

---

# 2. Null Hypothesis (H0)

A mutation-capable boundary can alter invariant lineage while all local cryptographic and structural verification checks continue to pass.

If demonstrated, the AIC claim is weakened or falsified.

---

# 3. Alternative Hypothesis (H1)

Any invariant lineage alteration is either:

- prevented, or
- detected

before an irreversible mutation is accepted.

---

# 4. Required Falsification Tests

## Test A: Invariant Substitution

Goal:
Attempt to replace the governing invariant between ticket issuance and terminal receipt generation.

Success Condition:
Mismatch detected.

Failure Condition:
Mutation accepted while lineage drift remains undetected.

## Test B: Invariant Weakening

Goal:
Replace a restrictive invariant with a weaker invariant.

Success Condition:
Terminal authorization fails.

Failure Condition:
Mutation commits under weakened invariant.

## Test C: Invariant Removal

Goal:
Remove invariant identity entirely.

Success Condition:
Execution refuses.

Failure Condition:
Execution commits.

## Test D: Multi-Boundary Drift

Goal:
Introduce invariant substitutions across multiple boundaries.

Success Condition:
At least one boundary detects drift.

Failure Condition:
Drift survives end-to-end.

## Test E: Clone Divergence

Goal:
Run multiple cloned authorities with different invariant states.

Success Condition:
Divergence detected.

Failure Condition:
Conflicting invariant histories appear equivalent.

## Test F: Receipt Forgery

Goal:
Generate receipts that appear valid while referencing a different governing invariant.

Success Condition:
Forgery rejected.

Failure Condition:
Forgery accepted.

## Test G: Evidence Chain Rewrite

Goal:
Rebuild evidence history around a substituted invariant.

Success Condition:
Rewrite detected.

Failure Condition:
Chain accepted.

---

# 5. Measurement Criteria

For each attack record:

- Attack Type
- Boundary Location
- Detection Layer
- Commit/Refuse Outcome
- Evidence Integrity Result
- Invariant Integrity Result
- Final Verdict

---

# 6. Falsification Rule

AIC is considered falsified if a mutation-capable boundary can:

1. Alter governing invariant lineage.
2. Commit an irreversible mutation.
3. Produce cryptographically valid evidence.
4. Avoid detection.

All four conditions must be satisfied.

Otherwise the claim survives the test.
