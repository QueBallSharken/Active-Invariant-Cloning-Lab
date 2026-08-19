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
    chain_id="EVIDENCE",
):
    private_key, public_key = generate_keypair()

    ticket_data = {
        "ticket_id": f"T-{chain_id}-{sequence_number}",
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
        receipt_id=f"R-{chain_id}-{sequence_number}",
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
        causal_trace_id=f"trace-{chain_id}-{sequence_number}",
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
        previous_receipt_hash=first.receipt_hash,
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

def test_tampered_chain_hash_is_rejected():
    receipt = make_receipt()

    link = create_evidence_link(
        receipt,
        None,
    )

    tampered = replace(
        link,
        chain_hash="tampered-chain-hash",
    )

    assert not verify_evidence_chain(
        [receipt],
        [tampered],
    )

def test_sequence_number_mismatch_is_rejected():
    receipt = make_receipt(sequence_number=1)

    link = create_evidence_link(
        receipt,
        None,
    )

    tampered = replace(
        link,
        sequence_number=999,
    )

    assert not verify_evidence_chain(
        [receipt],
        [tampered],
    )


def test_extra_chain_link_is_rejected():
    receipt = make_receipt()

    link = create_evidence_link(
        receipt,
        None,
    )

    assert not verify_evidence_chain(
        [receipt],
        [link, link],
    )

def test_previous_receipt_hash_mismatch_is_rejected():
    first = make_receipt(sequence_number=1)

    first_link = create_evidence_link(
        first,
        None,
    )

    second = make_receipt(
        sequence_number=2,
        previous_receipt_hash="fake-previous-hash",
    )

    second_link = create_evidence_link(
        second,
        first_link.chain_hash,
    )

    assert not verify_evidence_chain(
        [first, second],
        [first_link, second_link],
    )

def test_receipt_order_swap_is_rejected():
    first = make_receipt(sequence_number=1)
    first_link = create_evidence_link(first, None)

    second = make_receipt(
        sequence_number=2,
        previous_receipt_hash=first.receipt_hash,
    )
    second_link = create_evidence_link(
        second,
        first_link.chain_hash,
    )

    assert not verify_evidence_chain(
        [second, first],
        [second_link, first_link],
    )

def test_cross_chain_splice_is_rejected():
    a1 = make_receipt(sequence_number=1)
    a1_link = create_evidence_link(a1, None)

    a2 = make_receipt(
        sequence_number=2,
        previous_receipt_hash=a1.receipt_hash,
    )
    a2_link = create_evidence_link(
        a2,
        a1_link.chain_hash,
    )

    b1 = make_receipt(sequence_number=1, chain_id="B")
    b1_link = create_evidence_link(b1, None)

    b2 = make_receipt(
        sequence_number=2,
        previous_receipt_hash=b1.receipt_hash,
        chain_id="B",
    )
    b2_link = create_evidence_link(
        b2,
        b1_link.chain_hash,
    )

    assert not verify_evidence_chain(
        [a1, a2],
        [a1_link, b2_link],
    )

def test_replayed_receipt_is_rejected():
    first = make_receipt(sequence_number=1)
    first_link = create_evidence_link(first, None)

    second = make_receipt(
        sequence_number=2,
        previous_receipt_hash=first.receipt_hash,
    )
    second_link = create_evidence_link(
        second,
        first_link.chain_hash,
    )

    assert verify_evidence_chain(
        [first, second],
        [first_link, second_link],
    )

    assert not verify_evidence_chain(
        [first, second, second],
        [first_link, second_link, second_link],
    )

def test_foreign_continuation_is_rejected():
    a1 = make_receipt(sequence_number=1, chain_id="A")
    a1_link = create_evidence_link(a1, None)

    a2 = make_receipt(
        sequence_number=2,
        previous_receipt_hash=a1.receipt_hash,
        chain_id="A",
    )
    a2_link = create_evidence_link(
        a2,
        a1_link.chain_hash,
    )

    b1 = make_receipt(sequence_number=1, chain_id="B")
    b1_link = create_evidence_link(b1, None)

    b2 = make_receipt(
        sequence_number=2,
        previous_receipt_hash=b1.receipt_hash,
        chain_id="B",
    )
    b2_link = create_evidence_link(
        b2,
        b1_link.chain_hash,
    )

    b3 = make_receipt(
        sequence_number=3,
        previous_receipt_hash=b2.receipt_hash,
        chain_id="B",
    )
    b3_link = create_evidence_link(
        b3,
        b2_link.chain_hash,
    )

    assert not verify_evidence_chain(
        [a1, a2, b3],
        [a1_link, a2_link, b3_link],
    )

def test_tampered_predecessor_is_rejected():
    first = make_receipt(sequence_number=1)
    first_link = create_evidence_link(first, None)

    second = make_receipt(
        sequence_number=2,
        previous_receipt_hash=first.receipt_hash,
    )
    second_link = create_evidence_link(
        second,
        first_link.chain_hash,
    )

    tampered_first = replace(
        first,
        terminal_outcome="REFUSE",
    )

    assert not verify_evidence_chain(
        [tampered_first, second],
        [first_link, second_link],
    )

def test_tampered_middle_receipt_is_rejected():
    first = make_receipt(sequence_number=1)
    first_link = create_evidence_link(first, None)

    second = make_receipt(
        sequence_number=2,
        previous_receipt_hash=first.receipt_hash,
    )
    second_link = create_evidence_link(
        second,
        first_link.chain_hash,
    )

    third = make_receipt(
        sequence_number=3,
        previous_receipt_hash=second.receipt_hash,
    )
    third_link = create_evidence_link(
        third,
        second_link.chain_hash,
    )

    tampered_second = replace(
        second,
        terminal_outcome="REFUSE",
    )

    assert not verify_evidence_chain(
        [first, tampered_second, third],
        [first_link, second_link, third_link],
    )

def test_chain_head_substitution_is_rejected():
    first = make_receipt(sequence_number=1)
    first_link = create_evidence_link(first, None)

    second = make_receipt(
        sequence_number=2,
        previous_receipt_hash=first.receipt_hash,
    )
    second_link = create_evidence_link(
        second,
        first_link.chain_hash,
    )

    foreign_root = make_receipt(
        sequence_number=1,
        terminal_outcome="REFUSE",
    )
    foreign_root_link = create_evidence_link(
        foreign_root,
        None,
    )

    assert not verify_evidence_chain(
        [first, second],
        [foreign_root_link, second_link],
    )

def test_foreign_middle_link_substitution_is_rejected():
    a1 = make_receipt(sequence_number=1)
    a1_link = create_evidence_link(a1, None)

    a2 = make_receipt(
        sequence_number=2,
        previous_receipt_hash=a1.receipt_hash,
    )
    a2_link = create_evidence_link(
        a2,
        a1_link.chain_hash,
    )

    a3 = make_receipt(
        sequence_number=3,
        previous_receipt_hash=a2.receipt_hash,
    )
    a3_link = create_evidence_link(
        a3,
        a2_link.chain_hash,
    )

    b2 = make_receipt(
        sequence_number=2,
        previous_receipt_hash=a1.receipt_hash,
        terminal_outcome="REFUSE",
    )
    b2_link = create_evidence_link(
        b2,
        a1_link.chain_hash,
    )

    assert not verify_evidence_chain(
        [a1, a2, a3],
        [a1_link, b2_link, a3_link],
    )

def test_foreign_terminal_link_substitution_is_rejected():
    first = make_receipt(sequence_number=1)
    first_link = create_evidence_link(first, None)

    second = make_receipt(
        sequence_number=2,
        previous_receipt_hash=first.receipt_hash,
    )
    second_link = create_evidence_link(
        second,
        first_link.chain_hash,
    )

    foreign = make_receipt(
        sequence_number=2,
        previous_receipt_hash=first.receipt_hash,
        terminal_outcome="REFUSE",
    )
    foreign_link = create_evidence_link(
        foreign,
        first_link.chain_hash,
    )

    assert not verify_evidence_chain(
        [first, second],
        [first_link, foreign_link],
    )

def test_previous_receipt_pointer_forgery_is_rejected():
    first = make_receipt(sequence_number=1)
    first_link = create_evidence_link(first, None)

    second = make_receipt(
        sequence_number=2,
        previous_receipt_hash="forged-receipt-hash",
    )
    second_link = create_evidence_link(
        second,
        first_link.chain_hash,
    )

    assert not verify_evidence_chain(
        [first, second],
        [first_link, second_link],
    )

def test_receipt_link_cross_pair_substitution_is_rejected():
    a = make_receipt(
        sequence_number=1,
        terminal_outcome="COMMIT",
    )
    a_link = create_evidence_link(a, None)

    b = make_receipt(
        sequence_number=1,
        terminal_outcome="REFUSE",
    )
    b_link = create_evidence_link(b, None)

    assert a.receipt_hash != b.receipt_hash

    assert not verify_evidence_chain(
        [a],
        [b_link],
    )


def make_receipt_with_key(
    sequence_number=1,
    previous_receipt_hash=None,
    terminal_outcome="COMMIT",
    chain_id="EVIDENCE",
):
    private_key, public_key = generate_keypair()

    ticket_data = {
        "ticket_id": f"T-{chain_id}-{sequence_number}",
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
        receipt_id=f"R-{chain_id}-{sequence_number}",
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
        causal_trace_id=f"trace-{chain_id}-{sequence_number}",
        sequence_number=sequence_number,
        previous_receipt_hash=previous_receipt_hash,
        private_key_hex=private_key,
    )

    return receipt, public_key

def test_evidence_chain_does_not_explicitly_bind_invariant_identity():
    receipt = make_receipt()

    link = create_evidence_link(
        receipt,
        None,
    )

    assert link.ticket_hash == receipt.ticket_hash

    # EvidenceLink currently contains no invariant identity fields.
    assert not hasattr(link, "invariant_id")
    assert not hasattr(link, "invariant_version")


def test_receipt_with_substituted_invariant_still_builds_evidence_chain():
    from dataclasses import replace

    receipt = make_receipt()

    substituted = replace(
        receipt,
        invariant_id="INV-ATTACKED",
    )

    link = create_evidence_link(
        substituted,
        None,
    )

    assert verify_evidence_chain(
        [substituted],
        [link],
    )

