from copy import deepcopy

import pytest

from aic_harness.crypto import generate_keypair
from aic_harness.receipt import (
    ReceiptSchemaError,
    create_receipt,
)
from aic_harness.ticket import create_ticket


def make_ticket():
    private_key, public_key = generate_keypair()

    ticket_data = {
        "ticket_id": "T-RECEIPT-001",
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
    }

    ticket = create_ticket(ticket_data, private_key)

    return ticket, private_key, public_key


def make_receipt(
    ticket,
    private_key,
    *,
    terminal_outcome="COMMIT",
    mutation_hash="mutation-hash",
    composite_valid_predicate=None,
):
    if composite_valid_predicate is None:
        composite_valid_predicate = terminal_outcome == "COMMIT"

    return create_receipt(
        receipt_id="R-RECEIPT-001",
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
        composite_valid_predicate=composite_valid_predicate,
        terminal_outcome=terminal_outcome,
        reason_code="AUTHORIZED",
        mutation_hash=mutation_hash,
        causal_trace_id="trace-001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )


def test_receipt_creation():
    ticket, private_key, _ = make_ticket()

    receipt = make_receipt(
        ticket,
        private_key,
    )

    assert receipt.receipt_id == "R-RECEIPT-001"
    assert receipt.terminal_outcome == "COMMIT"
    assert receipt.mutation_hash == "mutation-hash"


def test_receipt_hash_is_present():
    ticket, private_key, _ = make_ticket()

    receipt = make_receipt(
        ticket,
        private_key,
    )

    assert isinstance(receipt.receipt_hash, str)
    assert receipt.receipt_hash


def test_receipt_signature_is_present():
    ticket, private_key, _ = make_ticket()

    receipt = make_receipt(
        ticket,
        private_key,
    )

    assert isinstance(receipt.signature, str)
    assert receipt.signature


def test_commit_requires_mutation_hash():
    ticket, private_key, _ = make_ticket()

    with pytest.raises(ReceiptSchemaError):
        create_receipt(
            receipt_id="R-INVALID-001",
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
            reason_code="AUTHORIZED",
            mutation_hash=None,
            causal_trace_id="trace-001",
            sequence_number=1,
            previous_receipt_hash=None,
            private_key_hex=private_key,
        )


def test_refuse_must_not_have_mutation_hash():
    ticket, private_key, _ = make_ticket()

    with pytest.raises(ReceiptSchemaError):
        create_receipt(
            receipt_id="R-INVALID-002",
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
            composite_valid_predicate=False,
            terminal_outcome="REFUSE",
            reason_code="DENIED",
            mutation_hash="mutation-hash",
            causal_trace_id="trace-001",
            sequence_number=1,
            previous_receipt_hash=None,
            private_key_hex=private_key,
        )


def test_receipt_round_trip_dict():
    ticket, private_key, _ = make_ticket()

    receipt = make_receipt(
        ticket,
        private_key,
    )

    serialized = receipt.to_dict()

    assert serialized["receipt_id"] == receipt.receipt_id
    assert serialized["receipt_hash"] == receipt.receipt_hash
    assert serialized["signature"] == receipt.signature


def test_receipt_field_mutation_changes_canonical_body():
    ticket, private_key, _ = make_ticket()

    receipt = make_receipt(
        ticket,
        private_key,
    )

    original = receipt.canonical_bytes()

    mutated = deepcopy(receipt.signed_dict())
    mutated["terminal_outcome"] = "REFUSE"

    from aic_harness.canonical import canonicalize

    mutated_bytes = canonicalize(mutated)

    assert original != mutated_bytes
    assert mutated["terminal_outcome"] != receipt.terminal_outcome


def test_refusal_receipt_can_be_created():
    ticket, private_key, _ = make_ticket()

    receipt = make_receipt(
        ticket,
        private_key,
        terminal_outcome="REFUSE",
        mutation_hash=None,
    )

    assert receipt.terminal_outcome == "REFUSE"
    assert receipt.mutation_hash is None


def test_commit_cannot_be_signed_with_false_composite_predicate():
    ticket, private_key, _ = make_ticket()

    with pytest.raises(ReceiptSchemaError):
        create_receipt(
            receipt_id="R-CONTRADICTION-001",
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
            composite_valid_predicate=False,
            terminal_outcome="COMMIT",
            reason_code="AUTHORIZED",
            mutation_hash="mutation-hash",
            causal_trace_id="trace-001",
            sequence_number=1,
            previous_receipt_hash=None,
            private_key_hex=private_key,
        )


def test_receipt_hash_and_signature_verify_independently():
    from aic_harness.canonical import canonicalize
    from aic_harness.crypto import sha256_hex, verify

    ticket, private_key, public_key = make_ticket()

    receipt = make_receipt(
        ticket,
        private_key,
    )

    unsigned = receipt.unsigned_dict()

    expected_receipt_hash = sha256_hex(
        canonicalize(unsigned)
    )

    assert receipt.receipt_hash == expected_receipt_hash

    signed_body = receipt.signed_dict()

    assert verify(
        public_key,
        receipt.signature,
        canonicalize(signed_body),
    )


def test_receipt_signature_rejects_tampered_signed_field():
    from aic_harness.canonical import canonicalize
    from aic_harness.crypto import verify

    ticket, private_key, public_key = make_ticket()

    receipt = make_receipt(
        ticket,
        private_key,
    )

    tampered = receipt.signed_dict()
    tampered["tool"] = "tampered-tool"

    assert not verify(
        public_key,
        receipt.signature,
        canonicalize(tampered),
    )
