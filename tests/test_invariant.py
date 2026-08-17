from copy import deepcopy

from aic_harness.crypto import generate_keypair
from aic_harness.ticket import (
    create_ticket,
    ticket_from_dict,
    verify_ticket,
)


def make_ticket_data():
    return {
        "ticket_id": "T-INVARIANT-001",
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


def make_ticket():
    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        make_ticket_data(),
        private_key,
    )

    return ticket, private_key, public_key


def test_valid_invariant_ticket_verifies():
    ticket, _, public_key = make_ticket()

    assert ticket.invariant_id == "INV-001"
    assert ticket.invariant_version == "1"
    assert verify_ticket(ticket, public_key)


def test_invariant_id_mutation_is_rejected():
    ticket, _, public_key = make_ticket()

    mutated = deepcopy(ticket.to_dict())
    mutated["invariant_id"] = "INV-ATTACK"

    mutated_ticket = ticket_from_dict(mutated)

    assert not verify_ticket(
        mutated_ticket,
        public_key,
    )


def test_invariant_version_mutation_is_rejected():
    ticket, _, public_key = make_ticket()

    mutated = deepcopy(ticket.to_dict())
    mutated["invariant_version"] = "999"

    mutated_ticket = ticket_from_dict(mutated)

    assert not verify_ticket(
        mutated_ticket,
        public_key,
    )


def test_scope_mutation_is_rejected():
    ticket, _, public_key = make_ticket()

    mutated = deepcopy(ticket.to_dict())
    mutated["scope"] = "unrestricted"

    mutated_ticket = ticket_from_dict(mutated)

    assert not verify_ticket(
        mutated_ticket,
        public_key,
    )


def test_epoch_mutation_is_rejected():
    ticket, _, public_key = make_ticket()

    mutated = deepcopy(ticket.to_dict())
    mutated["epoch"] = 999

    mutated_ticket = ticket_from_dict(mutated)

    assert not verify_ticket(
        mutated_ticket,
        public_key,
    )


def test_nonce_mutation_is_rejected():
    ticket, _, public_key = make_ticket()

    mutated = deepcopy(ticket.to_dict())
    mutated["nonce"] = 999

    mutated_ticket = ticket_from_dict(mutated)

    assert not verify_ticket(
        mutated_ticket,
        public_key,
    )


def test_tool_mutation_is_rejected():
    ticket, _, public_key = make_ticket()

    mutated = deepcopy(ticket.to_dict())
    mutated["tool"] = "unauthorized-tool"

    mutated_ticket = ticket_from_dict(mutated)

    assert not verify_ticket(
        mutated_ticket,
        public_key,
    )


def test_subject_mutation_is_rejected():
    ticket, _, public_key = make_ticket()

    mutated = deepcopy(ticket.to_dict())
    mutated["subject"] = "different-subject"

    mutated_ticket = ticket_from_dict(mutated)

    assert not verify_ticket(
        mutated_ticket,
        public_key,
    )


def test_ticket_id_mutation_is_rejected():
    ticket, _, public_key = make_ticket()

    mutated = deepcopy(ticket.to_dict())
    mutated["ticket_id"] = "T-FORGED"

    mutated_ticket = ticket_from_dict(mutated)

    assert not verify_ticket(
        mutated_ticket,
        public_key,
    )


def test_signature_itself_cannot_be_reused_after_invariant_mutation():
    ticket, _, public_key = make_ticket()

    mutated = deepcopy(ticket.to_dict())
    mutated["invariant_id"] = "INV-FORGED"
    mutated["invariant_version"] = "999"

    mutated_ticket = ticket_from_dict(mutated)

    assert not verify_ticket(
        mutated_ticket,
        public_key,
    )
