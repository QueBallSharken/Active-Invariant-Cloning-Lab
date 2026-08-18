
from dataclasses import replace

from aic_harness.verifier import (
    VerificationError,
    audit,
    verify_receipt_integrity,
    verify_receipt_signature,
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
