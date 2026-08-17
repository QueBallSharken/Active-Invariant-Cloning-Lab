from dataclasses import replace

import pytest

from aic_harness.crypto import generate_keypair
from aic_harness.evidence import (
    EvidenceIntegrityError,
    create_evidence_link,
    verify_evidence_chain,
)
from aic_harness.receipt import create_receipt
from aic_harness.ticket import create_ticket


def make_receipt(
    sequence_number=1,
    previous_receipt_hash=None,
    terminal_outcome="COMMIT",
):
    private_key, public_key = generate_keypair()

    ticket_data = {
        "ticket_id": f"T-EVIDENCE-{sequence_number}",
        "subject": "subject-1",
        "object": "object-1",
        "action": "mutate",
        "payload_hash": "payload-hash",
        "tool": "test-tool",
        "epoch": 1,
        "nonce": sequence_number,
        "invariant_id": "INV-001",
        "invariant_version": "1",
        "scope": "test",
        "issued_at": "2026-08-17T00:00:00Z",
    }

    ticket = create_ticket(ticket_data, private_key)

    mutation_hash = (
        "mutation-hash"
        if terminal_outcome == "COMMIT"
        else None
    )

    receipt = create_receipt(
        receipt_id=f"R-EVIDENCE-{sequence_number}",
        timestamp="2026-08-17T00:00:01Z",
        terminal_authority="terminal-1",
        ticket_id=ticket.ticket_id,
        ticket_hash=ticket.ticket_hash(),
        invariant_id=ticket.invariant_id,
        invariant_version=ticket.invariant_version,
        payload_hash=ticket.payload_hash,
        tool=ticket.tool,
        observed_epoch=ticket.epoch,
        observed_state_hash=f"state-hash-{sequence_number}",
        nonce=ticket.nonce,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=terminal_outcome == "COMMIT",
        terminal_outcome=terminal_outcome,
        reason_code=(
            "AUTHORIZED"
            if terminal_outcome == "COMMIT"
            else "DENIED"
        ),
        mutation_hash=mutation_hash,
        causal_trace_id=f"trace-{sequence_number}",
        sequence_number=sequence_number,
        previous_receipt_hash=previous_receipt_hash,
        private_key_hex=private_key,
    )

    return receipt


def test_single_link_chain_verifies():
    receipt = make_receipt()

    link = create_evidence_link(receipt, None)

    assert verify_evidence_chain(
        [receipt],
        [link],
    )


def test_two_link_chain_verifies():
    first = make_receipt(sequence_number=1)

    first_link = create_evidence_link(
        first,
        None,
    )

    second = make_receipt(
        sequence_number=2,
    )

    second_link = create_evidence_link(
        second,
        first_link.chain_hash,
    )

    assert verify_evidence_chain(
        [first, second],
        [first_link, second_link],
    )


def test_tampered_decision_is_rejected():
    receipt = make_receipt()

    link = create_evidence_link(
        receipt,
        None,
    )

    tampered = replace(
        link,
        decision="REFUSE",
    )

    assert not verify_evidence_chain(
        [receipt],
        [tampered],
    )


def test_tampered_ticket_hash_is_rejected():
    receipt = make_receipt()

    link = create_evidence_link(
        receipt,
        None,
    )

    tampered = replace(
        link,
        ticket_hash="tampered-ticket-hash",
    )

    assert not verify_evidence_chain(
        [receipt],
        [tampered],
    )


def test_tampered_state_hash_is_rejected():
    receipt = make_receipt()

    link = create_evidence_link(
        receipt,
        None,
    )

    tampered = replace(
        link,
        state_hash="tampered-state-hash",
    )

    assert not verify_evidence_chain(
        [receipt],
        [tampered],
    )


def test_tampered_receipt_hash_is_rejected():
    receipt = make_receipt()

    link = create_evidence_link(
        receipt,
        None,
    )

    tampered = replace(
        link,
        receipt_hash="tampered-receipt-hash",
    )

    assert not verify_evidence_chain(
        [receipt],
        [tampered],
    )


def test_broken_previous_chain_link_is_rejected():
    first = make_receipt(sequence_number=1)

    first_link = create_evidence_link(
        first,
        None,
    )

    second = make_receipt(sequence_number=2)

    second_link = create_evidence_link(
        second,
        "wrong-previous-chain-hash",
    )

    assert not verify_evidence_chain(
        [first, second],
        [first_link, second_link],
    )


def test_sequence_gap_is_rejected():
    first = make_receipt(sequence_number=1)
    third = make_receipt(sequence_number=3)

    first_link = create_evidence_link(
        first,
        None,
    )

    third_link = create_evidence_link(
        third,
        first_link.chain_hash,
    )

    assert not verify_evidence_chain(
        [first, third],
        [first_link, third_link],
    )


def test_duplicate_sequence_is_rejected():
    first = make_receipt(sequence_number=1)
    duplicate = make_receipt(sequence_number=1)

    first_link = create_evidence_link(
        first,
        None,
    )

    duplicate_link = create_evidence_link(
        duplicate,
        first_link.chain_hash,
    )

    assert not verify_evidence_chain(
        [first, duplicate],
        [first_link, duplicate_link],
    )


def test_missing_chain_link_is_rejected():
    receipt = make_receipt()

    assert not verify_evidence_chain(
        [receipt],
        [],
    )
