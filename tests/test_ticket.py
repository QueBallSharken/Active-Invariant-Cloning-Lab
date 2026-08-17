from copy import deepcopy

from aic_harness.crypto import generate_keypair
from aic_harness.ticket import (
    TicketSchemaError,
    create_ticket,
    ticket_from_dict,
    verify_ticket,
)


def make_ticket_data():
    return {
        "ticket_id": "T-TEST-001",
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


def test_ticket_creation_and_verification():
    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        make_ticket_data(),
        private_key,
    )

    assert verify_ticket(ticket, public_key)


def test_ticket_round_trip():
    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        make_ticket_data(),
        private_key,
    )

    restored = ticket_from_dict(ticket.to_dict())

    assert restored == ticket
    assert verify_ticket(restored, public_key)


def test_ticket_action_mutation_is_rejected():
    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        make_ticket_data(),
        private_key,
    )

    mutated = deepcopy(ticket.to_dict())
    mutated["action"] = "unauthorized-action"

    mutated_ticket = ticket_from_dict(mutated)

    assert not verify_ticket(
        mutated_ticket,
        public_key,
    )


def test_ticket_object_mutation_is_rejected():
    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        make_ticket_data(),
        private_key,
    )

    mutated = deepcopy(ticket.to_dict())
    mutated["object"] = "different-object"

    mutated_ticket = ticket_from_dict(mutated)

    assert not verify_ticket(
        mutated_ticket,
        public_key,
    )


def test_ticket_payload_hash_mutation_is_rejected():
    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        make_ticket_data(),
        private_key,
    )

    mutated = deepcopy(ticket.to_dict())
    mutated["payload_hash"] = "different-payload"

    mutated_ticket = ticket_from_dict(mutated)

    assert not verify_ticket(
        mutated_ticket,
        public_key,
    )


def test_ticket_invariant_version_mutation_is_rejected():
    private_key, public_key = generate_keypair()

    ticket = create_ticket(
        make_ticket_data(),
        private_key,
    )

    mutated = deepcopy(ticket.to_dict())
    mutated["invariant_version"] = "999"

    mutated_ticket = ticket_from_dict(mutated)

    assert not verify_ticket(
        mutated_ticket,
        public_key,
    )


def test_missing_ticket_field_is_rejected():
    private_key, _ = generate_keypair()

    data = make_ticket_data()
    del data["invariant_id"]

    try:
        create_ticket(data, private_key)
    except TicketSchemaError:
        return

    raise AssertionError(
        "ticket without invariant_id was accepted"
    )
