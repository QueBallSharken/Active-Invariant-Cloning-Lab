from dataclasses import replace

import pytest

from aic_harness.crypto import generate_keypair
from aic_harness.evidence import (
    EvidenceIntegrityError,
    create_evidence_link,
    verify_evidence_chain,
    verify_evidence_link,
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



def test_evidence_chain_accepts_receipt_with_invariant_substitution_from_ticket():
    private_key, _ = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-EVIDENCE-CONTINUITY-001",
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
        receipt_id="R-EVIDENCE-CONTINUITY-001",
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

    assert verify_evidence_chain(
        [receipt],
        [link],
    )


def test_aic_evidence_chain_accepts_invariant_substitution():
    """
    Empirical AIC boundary experiment.

    The receipt carries an invariant identity different from the
    authoritative ticket. The evidence link derives its binding from
    the receipt, so the evidence chain can remain valid without
    independently establishing ticket-to-receipt invariant continuity.
    """
    private_key, _ = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-EVIDENCE-001",
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
        receipt_id="R-AIC-EVIDENCE-001",
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

    assert verify_evidence_chain(
        [receipt],
        [link],
    )


def test_aic_evidence_link_accepts_invariant_substitution():
    """
    Empirical AIC boundary experiment.

    EvidenceLink verification validates the link's own cryptographic
    material and does not independently establish invariant identity
    continuity against the authoritative ticket.
    """
    private_key, _ = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-LINK-001",
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
        receipt_id="R-AIC-LINK-001",
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

    assert verify_evidence_link(link)


def test_aic_evidence_chain_accepts_invariant_version_substitution():
    """
    Empirical AIC boundary experiment.

    The authoritative ticket carries invariant version 1 while the
    terminal receipt carries version 2. The evidence chain remains
    cryptographically valid because EvidenceLink does not independently
    bind invariant version to the authoritative ticket.
    """
    private_key, _ = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-VERSION-LINK-001",
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
        receipt_id="R-AIC-VERSION-LINK-001",
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

    link = create_evidence_link(receipt, None)

    assert ticket.invariant_version != receipt.invariant_version
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_evidence_link(link)
    assert verify_evidence_chain(
        [receipt],
        [link],
    )


def test_aic_evidence_chain_accepts_ticket_id_substitution():
    """
    Empirical AIC boundary experiment.

    The authoritative ticket has one ticket_id while the terminal receipt
    carries a different ticket_id but preserves the authoritative
    ticket_hash. The evidence chain validates the receipt/link relationship
    without independently resolving ticket_id against the authoritative
    ticket object.
    """
    private_key, _ = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-TICKET-ID-LINK-001",
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
        receipt_id="R-AIC-TICKET-ID-LINK-001",
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

    link = create_evidence_link(receipt, None)

    assert ticket.ticket_id != receipt.ticket_id
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_evidence_link(link)
    assert verify_evidence_chain(
        [receipt],
        [link],
    )


def test_aic_evidence_chain_accepts_payload_hash_substitution():
    """
    Empirical AIC boundary experiment.

    The authoritative ticket carries one payload hash while the terminal
    receipt carries another. The receipt preserves the authoritative
    ticket_hash, and the evidence chain validates the receipt/link
    relationship without independently binding payload_hash to the ticket.
    """
    private_key, _ = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-PAYLOAD-LINK-001",
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
        receipt_id="R-AIC-PAYLOAD-LINK-001",
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

    link = create_evidence_link(receipt, None)

    assert ticket.payload_hash != receipt.payload_hash
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_evidence_link(link)
    assert verify_evidence_chain(
        [receipt],
        [link],
    )


def test_aic_evidence_chain_accepts_tool_substitution():
    """
    Empirical AIC boundary experiment.

    The authoritative ticket names one tool while the terminal receipt
    names another. The receipt preserves the authoritative ticket hash,
    and the evidence chain validates the receipt/link relationship
    without independently binding tool identity to the ticket.
    """
    private_key, _ = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-TOOL-LINK-001",
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
        receipt_id="R-AIC-TOOL-LINK-001",
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

    link = create_evidence_link(receipt, None)

    assert ticket.tool != receipt.tool
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_evidence_link(link)
    assert verify_evidence_chain(
        [receipt],
        [link],
    )


def test_aic_evidence_chain_accepts_epoch_substitution():
    """
    Empirical AIC boundary experiment.

    The authoritative ticket carries epoch 1 while the terminal receipt
    carries epoch 2. The receipt preserves the authoritative ticket hash,
    and the evidence chain validates the receipt/link relationship without
    independently binding observed_epoch to the ticket.
    """
    private_key, _ = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-EPOCH-LINK-001",
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
        receipt_id="R-AIC-EPOCH-LINK-001",
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

    link = create_evidence_link(receipt, None)

    assert ticket.epoch != receipt.observed_epoch
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_evidence_link(link)
    assert verify_evidence_chain(
        [receipt],
        [link],
    )


def test_aic_evidence_chain_accepts_nonce_substitution():
    """
    Empirical AIC boundary experiment.

    The authoritative ticket carries nonce 1 while the terminal receipt
    carries nonce 2. The receipt preserves the authoritative ticket hash,
    and the evidence chain validates the receipt/link relationship without
    independently binding nonce to the ticket.
    """
    private_key, _ = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-NONCE-LINK-001",
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
        receipt_id="R-AIC-NONCE-LINK-001",
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

    link = create_evidence_link(receipt, None)

    assert ticket.nonce != receipt.nonce
    assert receipt.ticket_hash == ticket.ticket_hash()

    assert verify_evidence_link(link)
    assert verify_evidence_chain(
        [receipt],
        [link],
    )


def test_aic_evidence_chain_accepts_state_hash_substitution():
    """Empirical AIC boundary experiment: state hash substitution."""
    private_key, _ = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-STATE-LINK-001",
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
        receipt_id="R-AIC-STATE-LINK-001",
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

    link = create_evidence_link(receipt, None)

    assert verify_evidence_link(link)
    assert verify_evidence_chain([receipt], [link])


def test_aic_evidence_chain_accepts_authority_substitution():
    """Empirical AIC boundary experiment: terminal authority substitution."""
    private_key, _ = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-AUTH-LINK-001",
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
        receipt_id="R-AIC-AUTH-LINK-001",
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

    link = create_evidence_link(receipt, None)

    assert verify_evidence_link(link)
    assert verify_evidence_chain([receipt], [link])


def test_aic_evidence_chain_accepts_invariant_substitution():
    """
    Empirical AIC boundary experiment.

    The authoritative ticket carries INV-001 while the terminal receipt
    carries INV-ATTACKED. The evidence chain remains cryptographically
    valid because chain verification follows the receipt/link relationship
    and does not independently compare invariant identity to the ticket.
    """
    private_key, _ = generate_keypair()

    ticket = create_ticket(
        {
            "ticket_id": "T-AIC-CHAIN-001",
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
        receipt_id="R-AIC-CHAIN-001",
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

    assert verify_evidence_chain(
        [receipt],
        [link],
    )
