
from dataclasses import replace

from aic_harness.crypto import generate_keypair
from aic_harness.ticket import create_ticket
from aic_harness.receipt import create_receipt

from aic_harness.verifier import (
    VerificationError,
    audit,
    verify_receipt_integrity,
    verify_receipt_signature,
    verify_terminal_receipt,
)
from aic_harness.evidence import (
    create_evidence_link,
    verify_evidence_link,
    verify_evidence_chain,
)

from tests.test_evidence import make_receipt_with_key


def test_audit_accepts_valid_receipt_and_chain():
    receipt, public_key = make_receipt_with_key(sequence_number=1)
    link = create_evidence_link(receipt, None)

    result = audit(
        receipt,
        public_key,
        receipts=[receipt],
        chain=[link],
    )

    assert result.receipt_integrity_valid
    assert result.evidence_link_valid
    assert result.evidence_chain_valid

def test_receipt_signature_substitution_is_rejected():
    receipt_a, public_key_a = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIG-A",
    )
    receipt_b, _ = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIG-B",
    )

    substituted = replace(
        receipt_a,
        signature=receipt_b.signature,
    )

    assert not verify_receipt_signature(
        substituted,
        public_key_a,
    )


def test_receipt_body_mutation_after_signing_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="BODY-MUTATION",
    )

    mutated = replace(
        receipt,
        terminal_outcome="REFUSE",
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )

    assert not verify_receipt_integrity(mutated)


def test_wrong_public_key_substitution_is_rejected():
    receipt, _ = make_receipt_with_key(
        sequence_number=1,
        chain_id="WRONG-KEY",
    )
    _, wrong_public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="OTHER-KEY",
    )

    assert not verify_receipt_signature(
        receipt,
        wrong_public_key,
    )

def test_truncated_receipt_signature_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIG-TRUNC",
    )

    truncated = replace(
        receipt,
        signature=receipt.signature[:-2],
    )

    try:
        verify_receipt_signature(
            truncated,
            public_key,
        )
    except VerificationError:
        pass
    else:
        raise AssertionError(
            "truncated receipt signature must be rejected"
        )


def test_single_bit_receipt_signature_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIG-BITFLIP",
    )

    first_byte = int(receipt.signature[:2], 16)
    mutated_byte = first_byte ^ 0x01

    mutated_signature = (
        f"{mutated_byte:02x}" + receipt.signature[2:]
    )

    mutated = replace(
        receipt,
        signature=mutated_signature,
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_single_bit_public_key_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="KEY-BITFLIP",
    )

    first_byte = int(public_key[:2], 16)
    mutated_byte = first_byte ^ 0x01

    mutated_public_key = (
        f"{mutated_byte:02x}" + public_key[2:]
    )

    assert not verify_receipt_signature(
        receipt,
        mutated_public_key,
    )

def test_truncated_receipt_signature_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIG-TRUNC",
    )

    truncated = replace(
        receipt,
        signature=receipt.signature[:-2],
    )

    try:
        verify_receipt_signature(
            truncated,
            public_key,
        )
    except VerificationError:
        pass
    else:
        raise AssertionError(
            "truncated receipt signature must be rejected"
        )


def test_single_bit_receipt_signature_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIG-BITFLIP",
    )

    first_byte = int(receipt.signature[:2], 16)
    mutated_byte = first_byte ^ 0x01

    mutated_signature = (
        f"{mutated_byte:02x}" + receipt.signature[2:]
    )

    mutated = replace(
        receipt,
        signature=mutated_signature,
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_single_bit_public_key_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="KEY-BITFLIP",
    )

    first_byte = int(public_key[:2], 16)
    mutated_byte = first_byte ^ 0x01

    mutated_public_key = (
        f"{mutated_byte:02x}" + public_key[2:]
    )

    assert not verify_receipt_signature(
        receipt,
        mutated_public_key,
    )

def test_empty_receipt_signature_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIG-EMPTY",
    )

    mutated = replace(
        receipt,
        signature="",
    )

    try:
        verify_receipt_signature(mutated, public_key)
    except VerificationError:
        pass
    else:
        raise AssertionError(
            "empty receipt signature must be rejected"
        )


def test_non_hex_receipt_signature_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIG-NONHEX",
    )

    mutated = replace(
        receipt,
        signature="z" * len(receipt.signature),
    )

    try:
        verify_receipt_signature(mutated, public_key)
    except VerificationError:
        pass
    else:
        raise AssertionError(
            "non-hex receipt signature must be rejected"
        )


def test_non_hex_public_key_is_rejected():
    receipt, _ = make_receipt_with_key(
        sequence_number=1,
        chain_id="KEY-NONHEX",
    )

    invalid_public_key = "z" * 64

    try:
        verify_receipt_signature(
            receipt,
            invalid_public_key,
        )
    except VerificationError:
        pass
    else:
        raise AssertionError(
            "non-hex public key must be rejected"
        )

def test_receipt_hash_substitution_is_rejected():
    receipt, _ = make_receipt_with_key(
        sequence_number=1,
        chain_id="HASH-SUB",
    )

    other, _ = make_receipt_with_key(
        sequence_number=1,
        chain_id="HASH-OTHER",
    )

    mutated = replace(
        receipt,
        receipt_hash=other.receipt_hash,
    )

    assert not verify_receipt_integrity(mutated)


def test_receipt_hash_truncation_is_rejected():
    receipt, _ = make_receipt_with_key(
        sequence_number=1,
        chain_id="HASH-TRUNC",
    )

    mutated = replace(
        receipt,
        receipt_hash=receipt.receipt_hash[:-2],
    )

    assert not verify_receipt_integrity(mutated)


def test_receipt_hash_single_bit_mutation_is_rejected():
    receipt, _ = make_receipt_with_key(
        sequence_number=1,
        chain_id="HASH-BITFLIP",
    )

    first_byte = int(receipt.receipt_hash[:2], 16)
    mutated_byte = first_byte ^ 0x01

    mutated_hash = (
        f"{mutated_byte:02x}" + receipt.receipt_hash[2:]
    )

    mutated = replace(
        receipt,
        receipt_hash=mutated_hash,
    )

    assert not verify_receipt_integrity(mutated)

def test_signed_receipt_terminal_outcome_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-OUTCOME",
        terminal_outcome="COMMIT",
    )

    mutated = replace(
        receipt,
        terminal_outcome="REFUSE",
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_ticket_hash_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-TICKET",
    )

    mutated = replace(
        receipt,
        ticket_hash="0" * len(receipt.ticket_hash),
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_sequence_number_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-SEQUENCE",
    )

    mutated = replace(
        receipt,
        sequence_number=2,
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )

def test_signed_receipt_id_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-ID",
    )

    mutated = replace(
        receipt,
        receipt_id="R-TAMPERED-1",
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_timestamp_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-TIME",
    )

    mutated = replace(
        receipt,
        timestamp="2026-08-17T00:00:02Z",
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_invariant_version_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-VERSION",
    )

    mutated = replace(
        receipt,
        invariant_version="2",
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )

def test_signed_receipt_terminal_authority_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-AUTHORITY",
    )

    mutated = replace(
        receipt,
        terminal_authority="attacker-terminal",
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_tool_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-TOOL",
    )

    mutated = replace(
        receipt,
        tool="attacker-tool",
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_invariant_id_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-INVARIANT",
    )

    mutated = replace(
        receipt,
        invariant_id="INV-ATTACKED",
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_observed_state_hash_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-STATE",
    )

    mutated = replace(
        receipt,
        observed_state_hash="attacker-state",
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )

def test_signed_receipt_payload_hash_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-PAYLOAD",
    )

    mutated = replace(
        receipt,
        payload_hash="attacker-payload",
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_observed_epoch_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-EPOCH",
    )

    mutated = replace(
        receipt,
        observed_epoch=999,
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_nonce_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-NONCE",
    )

    mutated = replace(
        receipt,
        nonce=999,
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_reason_code_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-REASON",
    )

    mutated = replace(
        receipt,
        reason_code="ATTACKER_AUTHORIZED",
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_causal_trace_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-TRACE",
    )

    mutated = replace(
        receipt,
        causal_trace_id="attacker-trace",
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )

def test_signed_receipt_bound_verified_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-BOUND",
    )

    mutated = replace(
        receipt,
        bound_verified=False,
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_fresh_verified_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-FRESH",
    )

    mutated = replace(
        receipt,
        fresh_verified=False,
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_authorized_verified_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-AUTH",
    )

    mutated = replace(
        receipt,
        authorized_verified=False,
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_invariant_verified_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-INVARIANT-VERIFIED",
    )

    mutated = replace(
        receipt,
        invariant_verified=False,
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_composite_predicate_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-COMPOSITE",
        terminal_outcome="COMMIT",
    )

    mutated = replace(
        receipt,
        composite_valid_predicate=False,
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )

def test_signed_receipt_bound_verified_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-BOUND",
    )

    mutated = replace(
        receipt,
        bound_verified=False,
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_fresh_verified_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-FRESH",
    )

    mutated = replace(
        receipt,
        fresh_verified=False,
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_authorized_verified_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-AUTH",
    )

    mutated = replace(
        receipt,
        authorized_verified=False,
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_invariant_verified_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-INVARIANT-VERIFIED",
    )

    mutated = replace(
        receipt,
        invariant_verified=False,
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_composite_predicate_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-COMPOSITE",
        terminal_outcome="COMMIT",
    )

    mutated = replace(
        receipt,
        composite_valid_predicate=False,
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )

def test_signed_receipt_mutation_hash_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-MUTATION",
    )

    mutated = replace(
        receipt,
        mutation_hash="attacker-mutation",
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_terminal_outcome_refuse_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNED-REFUSE",
        terminal_outcome="REFUSE",
    )

    mutated = replace(
        receipt,
        terminal_outcome="COMMIT",
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_previous_hash_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        previous_receipt_hash="previous-hash",
        chain_id="SIGNED-PREVIOUS",
    )

    mutated = replace(
        receipt,
        previous_receipt_hash="attacker-previous-hash",
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signed_receipt_chain_sequence_mutation_is_rejected():
    receipt, public_key = make_receipt_with_key(
        sequence_number=5,
        chain_id="SIGNED-CHAIN-SEQ",
    )

    mutated = replace(
        receipt,
        sequence_number=6,
    )

    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_valid_receipt_integrity_remains_true():
    receipt, _ = make_receipt_with_key(
        sequence_number=1,
        chain_id="INTEGRITY-VALID",
    )

    assert verify_receipt_integrity(receipt)


def test_valid_receipt_signature_remains_true():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIGNATURE-VALID",
    )

    assert verify_receipt_signature(
        receipt,
        public_key,
    )


def test_receipt_hash_and_signature_are_independent_checks():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="INDEPENDENT-CHECKS",
    )

    assert verify_receipt_integrity(receipt)
    assert verify_receipt_signature(
        receipt,
        public_key,
    )

    mutated = replace(
        receipt,
        receipt_hash="0" * len(receipt.receipt_hash),
    )

    assert not verify_receipt_integrity(mutated)
    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_signature_failure_does_not_change_receipt_integrity():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="SIG-VS-INTEGRITY",
    )

    first_byte = int(receipt.signature[:2], 16)
    mutated_signature = (
        f"{first_byte ^ 0x01:02x}"
        + receipt.signature[2:]
    )

    mutated = replace(
        receipt,
        signature=mutated_signature,
    )

    assert verify_receipt_integrity(receipt)
    assert verify_receipt_integrity(mutated)
    assert not verify_receipt_signature(
        mutated,
        public_key,
    )


def test_integrity_failure_does_not_modify_receipt():
    receipt, _ = make_receipt_with_key(
        sequence_number=1,
        chain_id="IMMUTABLE-RECEIPT",
    )

    original_hash = receipt.receipt_hash

    mutated = replace(
        receipt,
        receipt_hash="0" * len(receipt.receipt_hash),
    )

    assert receipt.receipt_hash == original_hash
    assert mutated.receipt_hash != original_hash
    assert not verify_receipt_integrity(mutated)


def test_valid_evidence_link_remains_verifiable_after_receipt_checks():
    receipt, _ = make_receipt_with_key(
        sequence_number=1,
        chain_id="EVIDENCE-AFTER-VERIFY",
    )

    link = create_evidence_link(receipt, None)

    assert verify_receipt_integrity(receipt)
    assert verify_evidence_link(link)


def test_full_valid_receipt_evidence_pair_remains_valid():
    receipt, public_key = make_receipt_with_key(
        sequence_number=1,
        chain_id="FULL-VALID",
    )

    link = create_evidence_link(receipt, None)

    assert verify_receipt_signature(
        receipt,
        public_key,
    )
    assert verify_receipt_integrity(receipt)
    assert verify_evidence_link(link)
    assert verify_evidence_chain(
        [receipt],
        [link],
    )

def test_verify_evidence_chain_rejects_swapped_order():
    r1, _ = make_receipt_with_key(
        sequence_number=1,
        chain_id="SWAP",
    )

    r2, _ = make_receipt_with_key(
        sequence_number=2,
        previous_receipt_hash=r1.receipt_hash,
        chain_id="SWAP",
    )

    l1 = create_evidence_link(r1, None)
    l2 = create_evidence_link(r2, l1.chain_hash)

    assert not verify_evidence_chain(
        [r2, r1],
        [l1, l2],
    )

def test_terminal_verifier_accepts_receipt_with_substituted_invariant():

    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-TERMINAL-CONTINUITY-001",
            "subject": "subject-1",
            "object": "object-1",
            "action": "mutate",
            "payload_hash": "payload-hash",
            "tool": "test-tool",
            "epoch": 1,
            "nonce": 1,
            "invariant_id": "INV-001",
            "invariant_version": "1",
            "scope": "test",
            "issued_at": "2026-08-17T00:00:00Z",
        },
        private_key,
    )

    receipt = create_receipt(
        receipt_id="R-TERMINAL-CONTINUITY-001",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="terminal-1",
        ticket_id=ticket.ticket_id,
        ticket_hash=ticket.ticket_hash(),
        invariant_id="INV-ATTACKED",
        invariant_version=ticket.invariant_version,
        payload_hash=ticket.payload_hash,
        tool=ticket.tool,
        observed_epoch=ticket.epoch,
        observed_state_hash="state-hash",
        nonce=ticket.nonce,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="AUTHORIZED",
        mutation_hash="mutation-hash",
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    assert ticket.invariant_id != receipt.invariant_id
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_receipt_signature(
        receipt,
        public_key,
    )

    assert verify_receipt_integrity(
        receipt,
    )

    assert verify_terminal_receipt(
        receipt,
        public_key,
    )


def test_aic_terminal_boundary_invariant_substitution_is_detectable():
    """
    Empirical AIC boundary experiment.

    The authoritative ticket carries INV-001 while the terminal receipt
    carries INV-ATTACKED. The receipt remains cryptographically valid
    because the receipt signs its own supplied invariant identity.

    This test records the observed boundary condition without changing
    verifier behavior.
    """

    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-REGRESSION-001",
            "subject": "subject-1",
            "object": "object-1",
            "action": "mutate",
            "payload_hash": "payload-hash",
            "tool": "test-tool",
            "epoch": 1,
            "nonce": 1,
            "invariant_id": "INV-001",
            "invariant_version": "1",
            "scope": "test",
            "issued_at": "2026-08-17T00:00:00Z",
        },
        private_key,
    )

    receipt = create_receipt(
        receipt_id="R-AIC-REGRESSION-001",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="terminal-1",
        ticket_id=ticket.ticket_id,
        ticket_hash=ticket.ticket_hash(),
        invariant_id="INV-ATTACKED",
        invariant_version=ticket.invariant_version,
        payload_hash=ticket.payload_hash,
        tool=ticket.tool,
        observed_epoch=ticket.epoch,
        observed_state_hash="state-hash",
        nonce=ticket.nonce,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="AUTHORIZED",
        mutation_hash="mutation-hash",
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    assert ticket.invariant_id != receipt.invariant_id
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_terminal_receipt(
        receipt,
        public_key,
    )


def test_aic_audit_accepts_terminal_invariant_substitution():
    """
    Empirical AIC boundary experiment.

    The authoritative ticket carries INV-001 while the terminal receipt
    carries INV-ATTACKED. The complete receipt/evidence audit has no
    ticket input and therefore verifies the receipt and evidence chain
    without establishing invariant identity continuity to the ticket.
    """
    from aic_harness.evidence import create_evidence_link

    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-AUDIT-001",
            "subject": "subject-1",
            "object": "object-1",
            "action": "mutate",
            "payload_hash": "payload-hash",
            "tool": "test-tool",
            "epoch": 1,
            "nonce": 1,
            "invariant_id": "INV-001",
            "invariant_version": "1",
            "scope": "test",
            "issued_at": "2026-08-17T00:00:00Z",
        },
        private_key,
    )

    receipt = create_receipt(
        receipt_id="R-AIC-AUDIT-001",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="terminal-1",
        ticket_id=ticket.ticket_id,
        ticket_hash=ticket.ticket_hash(),
        invariant_id="INV-ATTACKED",
        invariant_version=ticket.invariant_version,
        payload_hash=ticket.payload_hash,
        tool=ticket.tool,
        observed_epoch=ticket.epoch,
        observed_state_hash="state-hash",
        nonce=ticket.nonce,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="AUTHORIZED",
        mutation_hash="mutation-hash",
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    link = create_evidence_link(receipt, None)

    result = audit(
        receipt,
        public_key,
        receipts=[receipt],
        chain=[link],
    )

    assert ticket.invariant_id != receipt.invariant_id
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert result.receipt_signature_valid
    assert result.receipt_integrity_valid
    assert result.evidence_link_valid
    assert result.evidence_chain_valid


def test_aic_terminal_boundary_invariant_version_substitution_is_accepted():
    """
    Empirical AIC boundary experiment.

    The authoritative ticket carries invariant version 1 while the
    terminal receipt carries version 2. The receipt remains
    cryptographically valid because the substituted version is part of
    the receipt's own signed body.
    """

    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-VERSION-001",
            "subject": "subject-1",
            "object": "object-1",
            "action": "mutate",
            "payload_hash": "payload-hash",
            "tool": "test-tool",
            "epoch": 1,
            "nonce": 1,
            "invariant_id": "INV-001",
            "invariant_version": "1",
            "scope": "test",
            "issued_at": "2026-08-17T00:00:00Z",
        },
        private_key,
    )

    receipt = create_receipt(
        receipt_id="R-AIC-VERSION-001",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="terminal-1",
        ticket_id=ticket.ticket_id,
        ticket_hash=ticket.ticket_hash(),
        invariant_id=ticket.invariant_id,
        invariant_version="2",
        payload_hash=ticket.payload_hash,
        tool=ticket.tool,
        observed_epoch=ticket.epoch,
        observed_state_hash="state-hash",
        nonce=ticket.nonce,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="AUTHORIZED",
        mutation_hash="mutation-hash",
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    assert ticket.invariant_version != receipt.invariant_version
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_terminal_receipt(
        receipt,
        public_key,
    )


def test_aic_terminal_boundary_full_invariant_substitution_is_accepted():
    """
    Empirical AIC boundary experiment.

    The authoritative ticket carries invariant INV-001 version 1 while
    the terminal receipt carries INV-ATTACKED version 99. The receipt
    remains independently cryptographically valid.
    """

    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-FULL-INVARIANT-001",
            "subject": "subject-1",
            "object": "object-1",
            "action": "mutate",
            "payload_hash": "payload-hash",
            "tool": "test-tool",
            "epoch": 1,
            "nonce": 1,
            "invariant_id": "INV-001",
            "invariant_version": "1",
            "scope": "test",
            "issued_at": "2026-08-17T00:00:00Z",
        },
        private_key,
    )

    receipt = create_receipt(
        receipt_id="R-AIC-FULL-INVARIANT-001",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="terminal-1",
        ticket_id=ticket.ticket_id,
        ticket_hash=ticket.ticket_hash(),
        invariant_id="INV-ATTACKED",
        invariant_version="99",
        payload_hash=ticket.payload_hash,
        tool=ticket.tool,
        observed_epoch=ticket.epoch,
        observed_state_hash="state-hash",
        nonce=ticket.nonce,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="AUTHORIZED",
        mutation_hash="mutation-hash",
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    assert ticket.invariant_id != receipt.invariant_id
    assert ticket.invariant_version != receipt.invariant_version
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_terminal_receipt(
        receipt,
        public_key,
    )


def test_aic_terminal_boundary_ticket_reference_substitution_is_accepted():
    """
    Empirical AIC boundary experiment.

    The receipt references a different ticket_id while retaining the
    authoritative ticket_hash. The terminal verifier has no ticket
    object against which to establish ticket_id/hash correspondence.
    """

    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-AUTHORITATIVE-001",
            "subject": "subject-1",
            "object": "object-1",
            "action": "mutate",
            "payload_hash": "payload-hash",
            "tool": "test-tool",
            "epoch": 1,
            "nonce": 1,
            "invariant_id": "INV-001",
            "invariant_version": "1",
            "scope": "test",
            "issued_at": "2026-08-17T00:00:00Z",
        },
        private_key,
    )

    receipt = create_receipt(
        receipt_id="R-AIC-TICKET-REFERENCE-001",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="terminal-1",
        ticket_id="T-AIC-ATTACKED-999",
        ticket_hash=ticket.ticket_hash(),
        invariant_id=ticket.invariant_id,
        invariant_version=ticket.invariant_version,
        payload_hash=ticket.payload_hash,
        tool=ticket.tool,
        observed_epoch=ticket.epoch,
        observed_state_hash="state-hash",
        nonce=ticket.nonce,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="AUTHORIZED",
        mutation_hash="mutation-hash",
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    assert ticket.ticket_id != receipt.ticket_id
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_terminal_receipt(
        receipt,
        public_key,
    )


def test_aic_terminal_boundary_invariant_version_substitution_is_accepted():
    """
    Empirical AIC boundary experiment.

    The authoritative ticket carries invariant version 1 while the
    terminal receipt carries version 2. The receipt remains
    cryptographically valid because the receipt signs its own supplied
    invariant version.
    """

    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-VERSION-001",
            "subject": "subject-1",
            "object": "object-1",
            "action": "mutate",
            "payload_hash": "payload-hash",
            "tool": "test-tool",
            "epoch": 1,
            "nonce": 1,
            "invariant_id": "INV-001",
            "invariant_version": "1",
            "scope": "test",
            "issued_at": "2026-08-17T00:00:00Z",
        },
        private_key,
    )

    receipt = create_receipt(
        receipt_id="R-AIC-VERSION-001",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="terminal-1",
        ticket_id=ticket.ticket_id,
        ticket_hash=ticket.ticket_hash(),
        invariant_id=ticket.invariant_id,
        invariant_version="2",
        payload_hash=ticket.payload_hash,
        tool=ticket.tool,
        observed_epoch=ticket.epoch,
        observed_state_hash="state-hash",
        nonce=ticket.nonce,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="AUTHORIZED",
        mutation_hash="mutation-hash",
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    assert ticket.invariant_version != receipt.invariant_version
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_terminal_receipt(
        receipt,
        public_key,
    )


def test_aic_terminal_boundary_ticket_id_substitution_is_accepted():
    """
    Empirical AIC boundary experiment.

    The receipt preserves the authoritative ticket hash but substitutes
    the ticket identifier. The terminal verifier validates the receipt's
    own signed fields and does not independently resolve ticket_id
    against the authoritative ticket object.
    """

    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-TICKET-ID-001",
            "subject": "subject-1",
            "object": "object-1",
            "action": "mutate",
            "payload_hash": "payload-hash",
            "tool": "test-tool",
            "epoch": 1,
            "nonce": 1,
            "invariant_id": "INV-001",
            "invariant_version": "1",
            "scope": "test",
            "issued_at": "2026-08-17T00:00:00Z",
        },
        private_key,
    )

    receipt = create_receipt(
        receipt_id="R-AIC-TICKET-ID-001",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="terminal-1",
        ticket_id="T-ATTACKED",
        ticket_hash=ticket.ticket_hash(),
        invariant_id=ticket.invariant_id,
        invariant_version=ticket.invariant_version,
        payload_hash=ticket.payload_hash,
        tool=ticket.tool,
        observed_epoch=ticket.epoch,
        observed_state_hash="state-hash",
        nonce=ticket.nonce,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="AUTHORIZED",
        mutation_hash="mutation-hash",
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    assert ticket.ticket_id != receipt.ticket_id
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_terminal_receipt(
        receipt,
        public_key,
    )


def test_aic_terminal_boundary_payload_hash_substitution_is_accepted():
    """
    Empirical AIC boundary experiment.

    The authoritative ticket carries one payload hash while the terminal
    receipt carries a different payload hash but preserves the ticket hash.
    The terminal verifier validates the receipt's own signed contents and
    does not independently compare payload_hash against the authoritative
    ticket.
    """

    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-PAYLOAD-001",
            "subject": "subject-1",
            "object": "object-1",
            "action": "mutate",
            "payload_hash": "payload-hash",
            "tool": "test-tool",
            "epoch": 1,
            "nonce": 1,
            "invariant_id": "INV-001",
            "invariant_version": "1",
            "scope": "test",
            "issued_at": "2026-08-17T00:00:00Z",
        },
        private_key,
    )

    receipt = create_receipt(
        receipt_id="R-AIC-PAYLOAD-001",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="terminal-1",
        ticket_id=ticket.ticket_id,
        ticket_hash=ticket.ticket_hash(),
        invariant_id=ticket.invariant_id,
        invariant_version=ticket.invariant_version,
        payload_hash="ATTACKED-PAYLOAD-HASH",
        tool=ticket.tool,
        observed_epoch=ticket.epoch,
        observed_state_hash="state-hash",
        nonce=ticket.nonce,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="AUTHORIZED",
        mutation_hash="mutation-hash",
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    assert ticket.payload_hash != receipt.payload_hash
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_terminal_receipt(
        receipt,
        public_key,
    )


def test_aic_terminal_boundary_tool_substitution_is_accepted():
    """
    Empirical AIC boundary experiment.

    The authoritative ticket names one tool while the terminal receipt
    names another. The receipt preserves the authoritative ticket hash.
    The terminal verifier validates the receipt's own signed contents
    without independently comparing tool identity against the ticket.
    """

    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-TOOL-001",
            "subject": "subject-1",
            "object": "object-1",
            "action": "mutate",
            "payload_hash": "payload-hash",
            "tool": "authorized-tool",
            "epoch": 1,
            "nonce": 1,
            "invariant_id": "INV-001",
            "invariant_version": "1",
            "scope": "test",
            "issued_at": "2026-08-17T00:00:00Z",
        },
        private_key,
    )

    receipt = create_receipt(
        receipt_id="R-AIC-TOOL-001",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="terminal-1",
        ticket_id=ticket.ticket_id,
        ticket_hash=ticket.ticket_hash(),
        invariant_id=ticket.invariant_id,
        invariant_version=ticket.invariant_version,
        payload_hash=ticket.payload_hash,
        tool="attacker-tool",
        observed_epoch=ticket.epoch,
        observed_state_hash="state-hash",
        nonce=ticket.nonce,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="AUTHORIZED",
        mutation_hash="mutation-hash",
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    assert ticket.tool != receipt.tool
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_terminal_receipt(
        receipt,
        public_key,
    )


def test_aic_terminal_boundary_epoch_substitution_is_accepted():
    """
    Empirical AIC boundary experiment.

    The authoritative ticket carries epoch 1 while the terminal receipt
    carries epoch 2. The receipt preserves the authoritative ticket hash.
    The terminal verifier validates the receipt's own signed contents
    without independently comparing observed_epoch against the ticket.
    """

    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-EPOCH-001",
            "subject": "subject-1",
            "object": "object-1",
            "action": "mutate",
            "payload_hash": "payload-hash",
            "tool": "test-tool",
            "epoch": 1,
            "nonce": 1,
            "invariant_id": "INV-001",
            "invariant_version": "1",
            "scope": "test",
            "issued_at": "2026-08-17T00:00:00Z",
        },
        private_key,
    )

    receipt = create_receipt(
        receipt_id="R-AIC-EPOCH-001",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="terminal-1",
        ticket_id=ticket.ticket_id,
        ticket_hash=ticket.ticket_hash(),
        invariant_id=ticket.invariant_id,
        invariant_version=ticket.invariant_version,
        payload_hash=ticket.payload_hash,
        tool=ticket.tool,
        observed_epoch=2,
        observed_state_hash="state-hash",
        nonce=ticket.nonce,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="AUTHORIZED",
        mutation_hash="mutation-hash",
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    assert ticket.epoch != receipt.observed_epoch
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_terminal_receipt(
        receipt,
        public_key,
    )


def test_aic_terminal_boundary_nonce_substitution_is_accepted():
    """
    Empirical AIC boundary experiment.

    The authoritative ticket carries nonce 1 while the terminal receipt
    carries nonce 2. The receipt preserves the authoritative ticket hash.
    The terminal verifier validates the receipt's own signed contents
    without independently comparing nonce against the ticket.
    """

    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-NONCE-001",
            "subject": "subject-1",
            "object": "object-1",
            "action": "mutate",
            "payload_hash": "payload-hash",
            "tool": "test-tool",
            "epoch": 1,
            "nonce": 1,
            "invariant_id": "INV-001",
            "invariant_version": "1",
            "scope": "test",
            "issued_at": "2026-08-17T00:00:00Z",
        },
        private_key,
    )

    receipt = create_receipt(
        receipt_id="R-AIC-NONCE-001",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="terminal-1",
        ticket_id=ticket.ticket_id,
        ticket_hash=ticket.ticket_hash(),
        invariant_id=ticket.invariant_id,
        invariant_version=ticket.invariant_version,
        payload_hash=ticket.payload_hash,
        tool=ticket.tool,
        observed_epoch=ticket.epoch,
        observed_state_hash="state-hash",
        nonce=2,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="AUTHORIZED",
        mutation_hash="mutation-hash",
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    assert ticket.nonce != receipt.nonce
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_terminal_receipt(
        receipt,
        public_key,
    )


def test_aic_terminal_boundary_state_hash_substitution_is_accepted():
    """Empirical AIC boundary experiment: state hash substitution."""

    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-STATE-001",
            "subject": "subject-1",
            "object": "object-1",
            "action": "mutate",
            "payload_hash": "payload-hash",
            "tool": "test-tool",
            "epoch": 1,
            "nonce": 1,
            "invariant_id": "INV-001",
            "invariant_version": "1",
            "scope": "test",
            "issued_at": "2026-08-17T00:00:00Z",
        },
        private_key,
    )

    receipt = create_receipt(
        receipt_id="R-AIC-STATE-001",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="terminal-1",
        ticket_id=ticket.ticket_id,
        ticket_hash=ticket.ticket_hash(),
        invariant_id=ticket.invariant_id,
        invariant_version=ticket.invariant_version,
        payload_hash=ticket.payload_hash,
        tool=ticket.tool,
        observed_epoch=ticket.epoch,
        observed_state_hash="ATTACKED-STATE",
        nonce=ticket.nonce,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="AUTHORIZED",
        mutation_hash="mutation-hash",
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    assert verify_terminal_receipt(receipt, public_key)


def test_aic_terminal_boundary_authority_substitution_is_accepted():
    """Empirical AIC boundary experiment: terminal authority substitution."""

    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-AUTH-001",
            "subject": "subject-1",
            "object": "object-1",
            "action": "mutate",
            "payload_hash": "payload-hash",
            "tool": "test-tool",
            "epoch": 1,
            "nonce": 1,
            "invariant_id": "INV-001",
            "invariant_version": "1",
            "scope": "test",
            "issued_at": "2026-08-17T00:00:00Z",
        },
        private_key,
    )

    receipt = create_receipt(
        receipt_id="R-AIC-AUTH-001",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="ATTACKED-AUTHORITY",
        ticket_id=ticket.ticket_id,
        ticket_hash=ticket.ticket_hash(),
        invariant_id=ticket.invariant_id,
        invariant_version=ticket.invariant_version,
        payload_hash=ticket.payload_hash,
        tool=ticket.tool,
        observed_epoch=ticket.epoch,
        observed_state_hash="state-hash",
        nonce=ticket.nonce,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="AUTHORIZED",
        mutation_hash="mutation-hash",
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    assert verify_terminal_receipt(receipt, public_key)


def test_aic_terminal_boundary_reason_code_substitution_is_accepted():
    """Empirical AIC boundary experiment: reason-code substitution."""

    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-REASON-001",
            "subject": "subject-1",
            "object": "object-1",
            "action": "mutate",
            "payload_hash": "payload-hash",
            "tool": "test-tool",
            "epoch": 1,
            "nonce": 1,
            "invariant_id": "INV-001",
            "invariant_version": "1",
            "scope": "test",
            "issued_at": "2026-08-17T00:00:00Z",
        },
        private_key,
    )

    receipt = create_receipt(
        receipt_id="R-AIC-REASON-001",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="terminal-1",
        ticket_id=ticket.ticket_id,
        ticket_hash=ticket.ticket_hash(),
        invariant_id=ticket.invariant_id,
        invariant_version=ticket.invariant_version,
        payload_hash=ticket.payload_hash,
        tool=ticket.tool,
        observed_epoch=ticket.epoch,
        observed_state_hash="state-hash",
        nonce=ticket.nonce,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="ATTACKED-REASON",
        mutation_hash="mutation-hash",
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    assert verify_terminal_receipt(receipt, public_key)


def test_aic_audit_accepts_invariant_substitution():
    """
    Empirical AIC boundary experiment.

    The ticket carries INV-001 while the signed terminal receipt carries
    INV-ATTACKED. The audit path verifies the receipt and evidence chain,
    but does not independently compare receipt invariant identity with
    the authoritative ticket.
    """
    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-AUDIT-001",
            "subject": "subject-1",
            "object": "object-1",
            "action": "mutate",
            "payload_hash": "payload-hash",
            "tool": "test-tool",
            "epoch": 1,
            "nonce": 1,
            "invariant_id": "INV-001",
            "invariant_version": "1",
            "scope": "test",
            "issued_at": "2026-08-17T00:00:00Z",
        },
        private_key,
    )

    receipt = create_receipt(
        receipt_id="R-AIC-AUDIT-001",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="terminal-1",
        ticket_id=ticket.ticket_id,
        ticket_hash=ticket.ticket_hash(),
        invariant_id="INV-ATTACKED",
        invariant_version=ticket.invariant_version,
        payload_hash=ticket.payload_hash,
        tool=ticket.tool,
        observed_epoch=ticket.epoch,
        observed_state_hash="state-hash",
        nonce=ticket.nonce,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="AUTHORIZED",
        mutation_hash="mutation-hash",
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    link = create_evidence_link(receipt, None)

    assert ticket.invariant_id != receipt.invariant_id
    assert receipt.ticket_hash == ticket.ticket_hash()

    result = audit(
        receipt,
        public_key,
        receipts=[receipt],
        chain=[link],
    )

    assert result.receipt_signature_valid
    assert result.receipt_integrity_valid
    assert result.evidence_link_valid
    assert result.evidence_chain_valid
