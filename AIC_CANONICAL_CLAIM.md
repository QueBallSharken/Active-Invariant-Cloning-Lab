# Active Invariant Cloning (AIC)
## Canonical Research Claim

Status: LOCKED CANONICAL FORMULATION
Scope: Architecture / Composition / Enforcement Evidence
Claim Class: Architectural Composition Discipline


## 1. CORE CLAIM

Active Invariant Cloning (AIC) is an architectural composition
discipline, not a novel cryptographic primitive or logical
formalism.

AIC identifies a compositional gap between local enforcement
correctness and global path authorization.

Independent correctness of reference monitors, cryptographic
attestations, state-version checks, and terminal verification
does not, by itself, establish that every governance-required
boundary evaluated the same mutation that ultimately commits.

AIC therefore requires preservation of mutation identity across
the governed execution path.


## 2. THE COMPOSITIONAL GAP

Let:

    LC =
        ∧ᵢ Correct(Bᵢ)
        ∧ Correct(TIMA)
        ∧ ValidCrypto
        ∧ ValidStateVersion

represent local component correctness.

Let:

    PA(M) =
        ∀ bᵢ ∈ Req(M),
            Eval(bᵢ, M, R, V)

represent path authorization for mutation M under route R and
applicable state/version context V.

The Parallel Mutation Divergence attack demonstrates that:

    LC ∧ ¬PA(M)

is possible.

Therefore:

    LocalCorrectness
        ≠
    PathAuthorization

unless an additional compositional condition establishes the
relationship between the individual boundary decisions.


## 3. SET MEMBERSHIP IS NOT TRANSITIVE AUTHORIZATION

A terminal verifier may perform a set-membership check:

    PossessesAttestation(B₁)
    ∧
    PossessesAttestation(B₂)
        ⇒
    Commit(TIMA, M)

This establishes that valid attestations exist.

It does not necessarily establish:

    Eval(B₁, M)
    ∧
    Eval(B₂, M)

unless the evidence structure preserves mutation identity
transitively.

The distinction is:

    Set Membership Verification
        ≠
    Transitive Mutation Authorization


## 4. PARALLEL MUTATION DIVERGENCE

Consider:

    M₁ → B₁ → T₁
    M₂ + T₁ → B₂ → T₂
    M₂ + {T₁,T₂} → TIMA

where:

    T₁ = Attest(B₁, M₁)

and:

    T₂ = Attest(B₂, M₂, T₁)

If B₂ verifies only that T₁ is authentic, without verifying that
T₁ is bound to M₂, then all individual component contracts may
remain locally satisfied while B₁'s authorization is effectively
reused for a different mutation.

The resulting condition is:

    Correct(B₁)
    ∧ Correct(B₂)
    ∧ Correct(TIMA)
    ∧ ValidCrypto
    ∧ ValidStateVersion
    ∧ TerminalStateCorrect

while simultaneously:

    ¬Eval(B₁, M₂)

The terminal state may therefore be correct while the governed
execution path is invalid.


## 5. THE AIC COMPOSITION INVARIANT

Let:

    M = mutation payload
    R = declared route identifier
    V = applicable state/version envelope
    b₁...bₙ = governance-required boundaries

AIC requires an evidence structure that preserves the following
invariant:

    I_AIC(M,R,V) ≜

        ∀ i ∈ Req(M):

            ValidSig(Tᵢ,Kᵢ)
            ∧ Payload(Tᵢ) = H(M)
            ∧ Route(Tᵢ) = R
            ∧ Step(Tᵢ) = i
            ∧ Version(Tᵢ) ∈ ValidEnvelope(V)
            ∧
            (
                i = 1
                ∨
                Prev(Tᵢ) = H(Tᵢ₋₁)
            )


## 6. STRONG TRANSITIVE ATTESTATION

The first boundary produces:

    T₁ =
        Sign(K₁,
            H(M)
            ∥ R
            ∥ V₀
            ∥ Step₁)

Each subsequent boundary produces:

    Tᵢ =
        Sign(Kᵢ,
            H(M)
            ∥ R
            ∥ V₀
            ∥ Stepᵢ
            ∥ H(Tᵢ₋₁))

for i > 1.

A boundary bᵢ MUST NOT produce Tᵢ unless:

    1. Local policy evaluation succeeds:

        Pᵢ(M, Context) = ALLOW

    2. The predecessor attestation is valid.

    3. The predecessor attestation is bound to the exact
       mutation being evaluated:

        PayloadHash(Tᵢ₋₁) = H(M)

    4. The predecessor attestation is bound to the required route:

        Route(Tᵢ₋₁) = R

    5. The predecessor represents the required prior route step.


## 7. TERMINAL VERIFICATION

The effect-relative TIMA MUST reject the mutation unless it can
unroll the authorization chain:

    Tₙ → Tₙ₋₁ → ... → T₁

and establish:

    ∀ i ∈ {1,...,n}:

        ExtractPayloadHash(Tᵢ)
            =
        H(M_commit)

together with the required route, step, signature, and
state/version constraints.

Subject to the execution contracts that require attestations to
be issued only after successful local evaluation:

    Tₙ
        ⇒
    ∧_{bᵢ ∈ Req(M)}
        Eval(bᵢ, M, R, V)

The critical property is therefore not merely possession of
valid tokens.

It is transitive evidence that every required predecessor
authorized the same mutation.


## 8. STRUCTURAL LOCATION OF THE INVARIANT

AIC does not depend upon claiming that the invariant is
"not policy."

Any security requirement can be expressed as a policy statement.

The distinction is where the enforcement obligation is embodied.

Informal policy:

    "B₁ must approve every mutation before TIMA."

is insufficient if the protocol permits TIMA to accept an
unrelated B₁ token.

The AIC architectural requirement is:

    The authorization evidence structure and verification
    contracts MUST make mutation identity, route position,
    predecessor dependency, and applicable state/version
    constraints verifiable at the enforcement boundary.

The invariant is therefore embodied in the protocol/evidence
composition and its verifier contracts rather than existing
only as prose.


## 9. AIC AND BEAF

BEAF and AIC address different dimensions of enforcement evidence.

BEAF:

    LOCAL BOUNDARY INTEGRITY

    Question:
        Does boundary Bᵢ possess verifiable evidence supporting
        the enforcement claim attributed to Bᵢ?

AIC:

    TRANSITIVE PATH COMPOSITION INTEGRITY

    Question:
        Does the evidence chain preserve mutation identity and
        governance obligations across all required boundaries
        until the effect-relative TIMA?

Therefore:

    BEAF
        =
    evidence-to-boundary integrity

and:

    AIC
        =
    invariant-to-path integrity


## 10. COMBINED MODEL

The combined enforcement model is:

    Governance Claim
          │
          ▼
    ┌───────────────┐
    │     BEAF      │
    │               │
    │ Does each     │
    │ boundary have │
    │ evidence for  │
    │ its decision? │
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │      AIC      │
    │               │
    │ Does evidence │
    │ remain bound   │
    │ to the same    │
    │ mutation along │
    │ the path?      │
    └───────┬───────┘
            │
            ▼
    Effect-Relative TIMA
            │
            ▼
    Irreversible Effect


## 11. WHAT AIC DOES NOT CLAIM

AIC does NOT claim:

    - invention of digital signatures;
    - invention of cryptographic hashes;
    - invention of reference monitors;
    - invention of state/version control;
    - invention of LTL or trace safety;
    - invention of cryptographic chaining;
    - universal superiority over every alternative architecture;
    - that AIC is the only mechanism capable of enforcing
      transitive mutation binding.

AIC instead claims that:

    local correctness of constituent mechanisms does not
    necessarily entail global path authorization.


## 12. FORMAL REDUCTION STATUS

AIC is not claimed to introduce a new logical operator.

Its desired properties can be represented using existing formal
methods, including trace properties and cryptographic verification.

However, formal expressibility does not eliminate the architectural
problem.

The relevant distinction is:

    "Can the property be expressed formally?"

versus:

    "Is the property entailed by the independently specified
     contracts of the constituent components?"

AIC concerns the second question.

A property may be formally expressible while remaining absent
from the composition of otherwise-correct components.


## 13. EFFECT-RELATIVE TIMA

TIMA MUST be defined relative to the first execution point at
which an effect becomes observationally irreversible, rather than
merely the final database write.

Therefore:

    DatabaseRollback
        ≠
    WorldStateRollback

when an intermediate operation has already produced an external
effect such as:

    - an irreversible third-party API action;
    - a payment dispatch;
    - a physical actuation;
    - an externally observable notification;
    - another effect that cannot be restored to observational
      equivalence.

The relevant enforcement boundary is:

    Effect-Relative TIMA

not necessarily:

    Database Commit


## 14. EMPIRICAL TEST

The Parallel Mutation Divergence attack provides a direct,
repeatable test.

Attack:

    1. Submit M₁ to B₁.
    2. Obtain valid T₁(M₁).
    3. Construct M₂ ≠ M₁.
    4. Submit M₂ + T₁(M₁) to B₂.
    5. Have B₂ produce T₂ if its local contract permits.
    6. Submit M₂ + {T₁,T₂} to TIMA.

The test asks:

    Can M₂ commit even though B₁ never evaluated M₂?


## 15. FALSIFICATION CRITERION

AIC is empirically falsifiable.

The claim is weakened or falsified for a specified architectural
class if independently specified component contracts, without
explicit transitive mutation binding, reliably prevent the
Parallel Mutation Divergence attack under the same threat model.

Possible implementations may use:

    - sidecars;
    - OAuth/JWT;
    - mTLS;
    - capability tokens;
    - cryptographic signatures;
    - database guards;
    - distributed policy engines;
    - other mechanisms.

The implementation name is irrelevant.

What matters is whether the required compositional property is
already entailed by the architecture.

If an architecture prevents the attack through an equivalent
mechanism, then AIC does not claim that its particular attestation
construction is uniquely necessary.

Instead, the result demonstrates that the architecture already
implements an equivalent form of the AIC invariant.


## 16. EMPIRICAL SECURITY DELTA

For the specified testbed:

    FAR =
        Invalid Realizations Committed
        /
        Invalid Realization Attempts

The experiment compares:

    Baseline Architecture
        versus
    Architecture enforcing I_AIC

A baseline acceptance demonstrates that the tested component
contracts are insufficient to guarantee path authorization.

An AIC-constrained rejection demonstrates that transitive
mutation binding prevents the tested divergence attack.

The result establishes an operational security delta for the
tested architectural class.

It does NOT, by itself, establish universal necessity.


## 17. FINAL ARCHITECTURAL STATEMENT

Active Invariant Cloning (AIC) is an architectural composition
discipline requiring that a governance invariant governing
mutation M remain structurally bound to M's identity as M
traverses each mutation-capable enforcement boundary.

AIC does not introduce a novel cryptographic primitive or logical
formalism.

Instead, AIC identifies and formalizes a cross-boundary
Composition Invariant that is not necessarily implied by the
independent correctness of standard reference monitors,
cryptographic signatures, state-versioning mechanisms, or
terminal verifiers.

A downstream authorization is valid under AIC only when its
evidence structure transitively establishes that every
governance-required predecessor boundary evaluated the exact same
mutation identity M under the required execution route R and
applicable state/version bounds V before the effect-relative TIMA
permits the irreversible effect.

The central architectural distinction is therefore:

    Local Correctness
        ≠
    Path Authorization

unless the composition explicitly preserves sufficient evidence
to establish the latter from the former.


## 18. LOCKED RESEARCH POSITION

The AIC research position is therefore:

    Primitive Level:
        NO novel primitive claimed.

    Logical Level:
        NO novel logical operator claimed.

    Formal-Method Level:
        Existing formal methods can represent the property.

    Architecture Level:
        AIC identifies a non-trivial compositional requirement
        concerning transitive mutation/path binding.

    Security Level:
        The requirement addresses a class of failures in which
        individually valid authorization evidence composes into
        an authorization for a mutation that was not evaluated
        by every required predecessor.

    Empirical Level:
        The claim is testable through adversarial mutation,
        payload-substitution, route-substitution, replay, and
        pre-terminal-effect experiments.

The research question is no longer:

    "Did AIC invent the primitives?"

The research question is:

    "Does independent local enforcement correctness entail
     global path authorization, or is an additional
     transitive composition invariant required?"

AIC asserts the latter and provides a formal invariant and
falsifiable experimental method for testing that assertion.
