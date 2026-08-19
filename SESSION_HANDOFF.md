# Session Handoff
MANDATORY

This file must be updated after significant repository work.

Repository continuity depends on this file.

---

## Session Checkpoint

Date: 2026-08-19
Contributor: Steven Kyle Hensley (QueBallSharken)

Branch: main

Current Commit:
ad87ee0 Record AIC boundary substitution experiments

Repository State:

- Working tree clean
- Full test suite: 133 passed
- Targeted AIC terminal-boundary suite: 13 passed, 47 deselected
- `git diff --check`: clean
- `origin/main` points to `ad87ee0`
- Local `main` is synchronized with `origin/main`
- No uncommitted changes

---

## Current Research Phase

Empirical Boundary Analysis

The repository has progressed beyond:

- Initialization
- Governance establishment
- Specification development
- Prototype development

and is now performing executable adversarial testing of invariant
continuity across mutation-capable boundaries.

The current research state is an observational evidence phase.

No production verifier behavior has been changed to close the observed
boundaries.

---

## Original AIC Research Question

Can a governing invariant survive every mutation-capable boundary as a
live, independently verifiable refusal condition, rather than merely
surviving as a cryptographically referenced artifact?

The current experiments test this proposition empirically by attempting
controlled substitutions at individual verification boundaries.

---

## Current Research Objective

Determine where invariant identity and other authoritative ticket
attributes can diverge from the originating governing artifact while
existing cryptographic, terminal, receipt, audit, and evidence-chain
verification mechanisms continue to accept the resulting state.

The current method is:

1. Construct the smallest adversarial case.
2. Execute it against the current harness.
3. Record the observed behavior.
4. Preserve the behavior as an executable regression test.
5. Run the complete regression suite.
6. Commit the evidence.
7. Only then consider implementation changes.

---

## Work Completed This Research Cycle

### Ticket-to-Receipt Boundary

Established executable evidence that a receipt can contain a different
invariant identity from its originating ticket while retaining the
authoritative ticket hash.

Observed state:

    ticket.invariant_id  = INV-001
    receipt.invariant_id = INV-ATTACKED

The receipt remains independently cryptographically valid.

This establishes an observed distinction between:

- cryptographic validity of the receipt
- semantic continuity between the receipt and originating ticket

---

### Terminal Verification Boundary

The terminal verifier has now been tested against a family of
controlled substitutions.

The focused experiment:

    pytest -q tests/test_verifier.py \
      -k "aic_terminal_boundary or terminal_verifier_accepts_receipt_with_substituted_invariant"

Result:

    13 passed, 47 deselected

The 13 passing adversarial cases demonstrate acceptance of independently
signed receipts containing substitutions involving:

- invariant identity
- invariant version
- full invariant identity/version
- ticket reference
- ticket ID
- payload hash
- tool
- epoch
- nonce
- state hash
- terminal authority
- reason code

The experiments preserve the authoritative ticket hash where the
specific test is examining substitution of another field.

The observed behavior is that the terminal verifier validates the
receipt's own cryptographic integrity but does not independently
establish semantic continuity between the supplied receipt fields and
the authoritative ticket object.

This is an observed property of the current implementation.

---

## Evidence-Chain Boundary

The evidence layer was extended with executable adversarial experiments.

The experiments establish that EvidenceLink and evidence-chain
verification can validate the receipt/link relationship while not
independently establishing continuity between the authoritative ticket
and substituted receipt attributes.

Observed substitutions include:

- invariant identity
- invariant version
- ticket ID
- payload hash
- tool
- epoch
- nonce
- state hash
- terminal authority

The evidence link derives its binding from the receipt and its ticket
hash. It does not independently reproduce and verify the authoritative
ticket's invariant identity against the receipt's invariant identity.

Therefore a receipt may contain substituted semantic fields while the
receipt/link cryptographic relationship and evidence-chain structure
remain valid.

---

## Audit Boundary

An audit experiment was also added showing that the complete receipt and
evidence-chain audit can return valid receipt and evidence results for a
receipt whose invariant identity differs from the originating ticket.

The audit path currently has no ticket object as an input for establishing
ticket-to-receipt invariant identity continuity.

The observed result is therefore:

- receipt signature valid
- receipt integrity valid
- evidence link valid
- evidence chain valid

while the independently retained authoritative ticket demonstrates a
different invariant identity.

---

## Test Evidence

Current full regression result:

    133 passed in 0.82s

The focused terminal-boundary experiment:

    13 passed, 47 deselected

The focused tests were also run with verbose output and all 13 selected
tests passed individually.

`git diff --check` passed before the final commit.

The adversarial cases are preserved as executable tests rather than
being represented only as narrative claims.

---

## Repository Findings

### Finding 1 — Cryptographic integrity is not invariant continuity

A valid signature proves that the signed receipt was not altered after
signing.

A valid receipt hash proves that the receipt body matches its recorded
hash.

Neither check independently proves that the receipt's invariant identity
matches the invariant identity of the originating ticket.

---

### Finding 2 — Ticket-hash binding is insufficient by itself

The current receipt can retain the originating ticket hash while
independently recording substituted semantic fields.

The receipt can therefore remain cryptographically valid even when
selected receipt attributes differ from the originating ticket.

Ticket-hash linkage alone does not currently establish continuity of
those independently represented fields.

---

### Finding 3 — Terminal verification is receipt-centric

The current terminal verifier validates the receipt's cryptographic
claims.

It does not independently resolve the receipt against the authoritative
ticket object for the tested semantic fields.

Consequently, a signed substitution can be accepted as a valid terminal
receipt.

---

### Finding 4 — Evidence-chain verification is relationship-centric

The current evidence chain establishes the structural and
cryptographic relationship represented by the receipt and EvidenceLink.

It does not independently establish invariant identity continuity from
the authoritative ticket into the receipt.

Consequently, evidence-chain validity can coexist with an observed
receipt/ticket invariant substitution.

---

### Finding 5 — Independent signatures do not create semantic authority

The experiments demonstrate that signing a substituted field makes the
substituted field cryptographically authentic to the signer.

It does not establish that the substituted value is the authoritative
value from the originating governing artifact.

This distinction is central to the current AIC empirical investigation.

---

## Important Research Boundary

These findings describe the current AIC reference harness.

They do NOT establish:

- Universal failure of all architectures
- Universal impossibility of invariant continuity
- That AIC itself has already been proven
- That every implementation has the same weakness
- That cryptography is ineffective
- That the observed verifier behavior is necessarily the final design

The current result is narrower:

The present harness contains identifiable verification boundaries where
cryptographic validity and structural evidence validity do not, by
themselves, establish invariant continuity against the originating
authoritative ticket.

---

## Files Changed During This Research Cycle

### Tests

- tests/test_evidence.py
- tests/test_verifier.py

The current committed experiment adds the adversarial evidence and
terminal-boundary tests without changing production verification
behavior.

---

## Authoritative Commit

The latest preserved empirical checkpoint is:

    ad87ee0 Record AIC boundary substitution experiments

Committed changes:

    2 files changed
    1692 insertions
    3 deletions

Remote synchronization:

    main -> origin/main

The Git repository is authoritative for the exact executable evidence.

---

## Current Production-Code Status

No production verification behavior has been changed as a result of
these findings.

The current work intentionally preserves the observed behavior and
captures it as executable evidence before proposing enforcement changes.

This separation remains mandatory:

    Observation first.

    Enforcement second.

No enforcement implementation has been authorized by this checkpoint.

---

## Current Open Questions

1. What artifact is the authoritative source of invariant identity at
   each mutation-capable boundary?

2. Where must invariant identity continuity be structurally bound so that
   downstream cryptographic verification cannot authenticate a
   substituted value as though it were authoritative?

3. Should EvidenceLink explicitly carry invariant identity, invariant
   version, or another independently verifiable invariant binding?

4. Which additional ticket-derived fields require continuity guarantees,
   and which are merely observational metadata?

5. At what exact boundary does AIC require the invariant to remain a live
   refusal condition rather than merely a signed or hashed field?

---

## Next-Thread Continuity Rule

Do not repeat the completed terminal-boundary experiments.

Do not modify production verifier behavior merely because the observed
substitution is accepted.

Treat commit `ad87ee0` and this handoff as the authoritative empirical
checkpoint.

The next research step must begin from the preserved evidence and
continue the empirical boundary analysis without erasing or weakening
the recorded observations.
