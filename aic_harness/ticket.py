"""
aic_harness/ticket.py

Execution-ticket construction and verification for the
AIC/BBIS V6.4.2 reference harness.

The ticket binds the minimum fields required by the frozen
V6.4.2 contract and is signed over the canonical ticket body.

This module does not:
- evaluate Valid()
- authorize execution
- perform mutations
- make terminal decisions
- determine expectedness
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping

from aic_harness.canonical import canonicalize
from aic_harness.crypto import (
    MalformedCryptoInput,
    sha256_hex,
    sign,
    verify,
)


REQUIRED_FIELDS = (
    "ticket_id",
    "subject",
    "object",
    "action",
    "payload_hash",
    "tool",
    "epoch",
    "nonce",
    "invariant_id",
    "invariant_version",
    "scope",
    "issued_at",
)


class TicketError(ValueError):
    """Base exception for malformed or invalid tickets."""


class TicketSchemaError(TicketError):
    """Raised when a ticket is structurally invalid."""


class TicketSignatureError(TicketError):
    """Raised when a ticket signature is invalid."""


@dataclass(frozen=True)
class ExecutionTicket:
    """
    Signed execution ticket.

    The signature is not included in the signed body.
    The signature covers the canonical representation of all
    required ticket fields.
    """

    ticket_id: str
    subject: str
    object: str
    action: str
    payload_hash: str
    tool: str
    epoch: int
    nonce: int
    invariant_id: str
    invariant_version: str
    scope: str
    issued_at: str
    signature: str

    def unsigned_dict(self) -> Dict[str, Any]:
        """Return the exact ticket body covered by the signature."""
        return {
            "ticket_id": self.ticket_id,
            "subject": self.subject,
            "object": self.object,
            "action": self.action,
            "payload_hash": self.payload_hash,
            "tool": self.tool,
            "epoch": self.epoch,
            "nonce": self.nonce,
            "invariant_id": self.invariant_id,
            "invariant_version": self.invariant_version,
            "scope": self.scope,
            "issued_at": self.issued_at,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Return the complete serialized ticket."""
        result = self.unsigned_dict()
        result["signature"] = self.signature
        return result

    def canonical_bytes(self) -> bytes:
        """Return canonical bytes of the signed ticket body."""
        return canonicalize(self.unsigned_dict())

    def ticket_hash(self) -> str:
        """Return SHA-256 hash of the canonical signed ticket body."""
        return sha256_hex(self.canonical_bytes())


def _validate_ticket_fields(ticket_data: Mapping[str, Any]) -> None:
    """Validate required ticket fields and their basic types."""
    if not isinstance(ticket_data, Mapping):
        raise TicketSchemaError("ticket must be a mapping")

    missing = [
        field
        for field in REQUIRED_FIELDS
        if field not in ticket_data
    ]

    if missing:
        raise TicketSchemaError(
            f"missing required ticket fields: {', '.join(missing)}"
        )

    string_fields = (
        "ticket_id",
        "subject",
        "object",
        "action",
        "payload_hash",
        "tool",
        "invariant_id",
        "invariant_version",
        "scope",
        "issued_at",
    )

    for field in string_fields:
        if not isinstance(ticket_data[field], str):
            raise TicketSchemaError(
                f"{field} must be a string"
            )

    if (
        isinstance(ticket_data["epoch"], bool)
        or not isinstance(ticket_data["epoch"], int)
    ):
        raise TicketSchemaError("epoch must be an integer")

    if (
        isinstance(ticket_data["nonce"], bool)
        or not isinstance(ticket_data["nonce"], int)
    ):
        raise TicketSchemaError("nonce must be an integer")

    if "signature" in ticket_data:
        if not isinstance(ticket_data["signature"], str):
            raise TicketSchemaError("signature must be a string")


def create_ticket(
    ticket_data: Mapping[str, Any],
    private_key_hex: str,
) -> ExecutionTicket:
    """
    Create and sign an execution ticket.

    The signature covers only the canonical unsigned ticket body.
    """
    _validate_ticket_fields(ticket_data)

    unsigned = {
        field: ticket_data[field]
        for field in REQUIRED_FIELDS
    }

    canonical_body = canonicalize(unsigned)

    try:
        signature = sign(private_key_hex, canonical_body)
    except MalformedCryptoInput as exc:
        raise TicketError(
            f"unable to sign ticket: {exc}"
        ) from exc

    return ExecutionTicket(
        ticket_id=unsigned["ticket_id"],
        subject=unsigned["subject"],
        object=unsigned["object"],
        action=unsigned["action"],
        payload_hash=unsigned["payload_hash"],
        tool=unsigned["tool"],
        epoch=unsigned["epoch"],
        nonce=unsigned["nonce"],
        invariant_id=unsigned["invariant_id"],
        invariant_version=unsigned["invariant_version"],
        scope=unsigned["scope"],
        issued_at=unsigned["issued_at"],
        signature=signature,
    )


def verify_ticket(
    ticket: ExecutionTicket,
    public_key_hex: str,
) -> bool:
    """
    Verify the Ed25519 signature over the canonical ticket body.

    Returns:
        True if the ticket is structurally valid and signed correctly.
        False if the signature is cryptographically incorrect.

    Raises:
        TicketSchemaError:
            If the ticket is malformed.
        TicketError:
            If cryptographic input is malformed.
    """
    _validate_ticket_fields(ticket.to_dict())

    try:
        return verify(
            public_key_hex,
            ticket.signature,
            ticket.canonical_bytes(),
        )
    except MalformedCryptoInput as exc:
        raise TicketError(
            f"malformed cryptographic input: {exc}"
        ) from exc


def ticket_from_dict(data: Mapping[str, Any]) -> ExecutionTicket:
    """
    Construct an ExecutionTicket from a serialized mapping.
    """
    _validate_ticket_fields(data)

    if "signature" not in data:
        raise TicketSchemaError("missing required ticket field: signature")

    return ExecutionTicket(
        ticket_id=data["ticket_id"],
        subject=data["subject"],
        object=data["object"],
        action=data["action"],
        payload_hash=data["payload_hash"],
        tool=data["tool"],
        epoch=data["epoch"],
        nonce=data["nonce"],
        invariant_id=data["invariant_id"],
        invariant_version=data["invariant_version"],
        scope=data["scope"],
        issued_at=data["issued_at"],
        signature=data["signature"],
    )


def ticket_to_dict(ticket: ExecutionTicket) -> Dict[str, Any]:
    """Serialize an ExecutionTicket to a dictionary."""
    return ticket.to_dict()


__all__ = [
    "ExecutionTicket",
    "TicketError",
    "TicketSchemaError",
    "TicketSignatureError",
    "REQUIRED_FIELDS",
    "create_ticket",
    "verify_ticket",
    "ticket_from_dict",
    "ticket_to_dict",
]


if __name__ == "__main__":
    print("[*] Running ticket.py self-test...")

    from aic_harness.crypto import generate_keypair

    private_key, public_key = generate_keypair()

    payload = b'{"mutation":"example"}'
    payload_hash = sha256_hex(payload)

    ticket_data = {
        "ticket_id": "TICKET-0001",
        "subject": "agent-01",
        "object": "resource-01",
        "action": "mutate",
        "payload_hash": payload_hash,
        "tool": "example-tool",
        "epoch": 1,
        "nonce": 1,
        "invariant_id": "INV-001",
        "invariant_version": "1.0",
        "scope": "resource-01",
        "issued_at": "2026-08-17T00:00:00Z",
    }

    ticket = create_ticket(ticket_data, private_key)

    assert verify_ticket(ticket, public_key)

    altered = ExecutionTicket(
        ticket_id=ticket.ticket_id,
        subject=ticket.subject,
        object=ticket.object,
        action="different-action",
        payload_hash=ticket.payload_hash,
        tool=ticket.tool,
        epoch=ticket.epoch,
        nonce=ticket.nonce,
        invariant_id=ticket.invariant_id,
        invariant_version=ticket.invariant_version,
        scope=ticket.scope,
        issued_at=ticket.issued_at,
        signature=ticket.signature,
    )

    assert not verify_ticket(altered, public_key)

    print("[+] Ticket creation: PASS")
    print("[+] Ticket signature verification: PASS")
    print("[+] Ticket mutation detection: PASS")
    print("[+] ticket.py self-test passed.")
