"""
aic_harness/receipt.py

Terminal receipt construction for the AIC/BBIS V6.4.2
reference harness.

Every terminal attempt produces exactly one signed receipt.

This module records the terminal decision and the evidence
needed for an independent auditor to reconstruct that decision.

This module does not:
- evaluate Valid()
- perform authorization
- perform protected mutations
- alter terminal outcomes
- calculate expectedness
"""


from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from aic_harness.canonical import canonicalize
from aic_harness.crypto import (
    MalformedCryptoInput,
    sha256_hex,
    sign,
)


TERMINAL_OUTCOMES = frozenset({"COMMIT", "REFUSE"})


class ReceiptError(ValueError):
    """Base exception for malformed terminal receipts."""


class ReceiptSchemaError(ReceiptError):
    """Raised when receipt data is structurally invalid."""


@dataclass(frozen=True)
class TerminalReceipt:
    """
    Signed terminal receipt.

    The signature covers every receipt field except:
        - receipt_hash
        - signature

    receipt_hash is calculated over the unsigned receipt body.
    The signature then covers that body plus receipt_hash.
    """

    receipt_id: str
    timestamp: str
    terminal_authority: str
    ticket_id: str
    ticket_hash: str
    invariant_id: str
    invariant_version: str
    payload_hash: str
    tool: str
    observed_epoch: int
    observed_state_hash: str
    nonce: int
    bound_verified: bool
    fresh_verified: bool
    authorized_verified: bool
    invariant_verified: bool
    composite_valid_predicate: bool
    terminal_outcome: str
    reason_code: str
    mutation_hash: Optional[str]
    causal_trace_id: str
    sequence_number: int
    previous_receipt_hash: Optional[str]
    receipt_hash: str
    signature: str

    def unsigned_dict(self) -> Dict[str, Any]:
        """
        Return the receipt body used to calculate receipt_hash.

        The hash and signature are excluded.
        """
        return {
            "receipt_id": self.receipt_id,
            "timestamp": self.timestamp,
            "terminal_authority": self.terminal_authority,
            "ticket_id": self.ticket_id,
            "ticket_hash": self.ticket_hash,
            "invariant_id": self.invariant_id,
            "invariant_version": self.invariant_version,
            "payload_hash": self.payload_hash,
            "tool": self.tool,
            "observed_epoch": self.observed_epoch,
            "observed_state_hash": self.observed_state_hash,
            "nonce": self.nonce,
            "bound_verified": self.bound_verified,
            "fresh_verified": self.fresh_verified,
            "authorized_verified": self.authorized_verified,
            "invariant_verified": self.invariant_verified,
            "composite_valid_predicate": self.composite_valid_predicate,
            "terminal_outcome": self.terminal_outcome,
            "reason_code": self.reason_code,
            "mutation_hash": self.mutation_hash,
            "causal_trace_id": self.causal_trace_id,
            "sequence_number": self.sequence_number,
            "previous_receipt_hash": self.previous_receipt_hash,
        }

    def signed_dict(self) -> Dict[str, Any]:
        """Return the complete body covered by the signature."""
        data = self.unsigned_dict()
        data["receipt_hash"] = self.receipt_hash
        return data

    def to_dict(self) -> Dict[str, Any]:
        """Return the complete serialized receipt."""
        data = self.signed_dict()
        data["signature"] = self.signature
        return data

    def canonical_bytes(self) -> bytes:
        """Return canonical bytes of the signed receipt body."""
        return canonicalize(self.signed_dict())


def _validate_receipt_fields(
    receipt_data: Dict[str, Any],
) -> None:
    """Validate receipt structure and terminal semantics."""
    required = {
        "receipt_id",
        "timestamp",
        "terminal_authority",
        "ticket_id",
        "ticket_hash",
        "invariant_id",
        "invariant_version",
        "payload_hash",
        "tool",
        "observed_epoch",
        "observed_state_hash",
        "nonce",
        "bound_verified",
        "fresh_verified",
        "authorized_verified",
        "invariant_verified",
        "composite_valid_predicate",
        "terminal_outcome",
        "reason_code",
        "mutation_hash",
        "causal_trace_id",
        "sequence_number",
        "previous_receipt_hash",
        "receipt_hash",
        "signature",
    }

    missing = sorted(required - set(receipt_data))

    if missing:
        raise ReceiptSchemaError(
            "missing required receipt fields: "
            + ", ".join(missing)
        )

    string_fields = (
        "receipt_id",
        "timestamp",
        "terminal_authority",
        "ticket_id",
        "ticket_hash",
        "invariant_id",
        "invariant_version",
        "payload_hash",
        "tool",
        "observed_state_hash",
        "reason_code",
        "causal_trace_id",
        "receipt_hash",
        "signature",
    )

    for field in string_fields:
        if not isinstance(receipt_data[field], str):
            raise ReceiptSchemaError(
                f"{field} must be a string"
            )

    if receipt_data["mutation_hash"] is not None:
        if not isinstance(receipt_data["mutation_hash"], str):
            raise ReceiptSchemaError(
                "mutation_hash must be a string or None"
            )

    if receipt_data["previous_receipt_hash"] is not None:
        if not isinstance(receipt_data["previous_receipt_hash"], str):
            raise ReceiptSchemaError(
                "previous_receipt_hash must be a string or None"
            )

    integer_fields = (
        "observed_epoch",
        "nonce",
        "sequence_number",
    )

    for field in integer_fields:
        if (
            isinstance(receipt_data[field], bool)
            or not isinstance(receipt_data[field], int)
        ):
            raise ReceiptSchemaError(
                f"{field} must be an integer"
            )

    boolean_fields = (
        "bound_verified",
        "fresh_verified",
        "authorized_verified",
        "invariant_verified",
        "composite_valid_predicate",
    )

    for field in boolean_fields:
        if not isinstance(receipt_data[field], bool):
            raise ReceiptSchemaError(
                f"{field} must be boolean"
            )

    if receipt_data["terminal_outcome"] not in TERMINAL_OUTCOMES:
        raise ReceiptSchemaError(
            "terminal_outcome must be COMMIT or REFUSE"
        )

    if receipt_data["terminal_outcome"] == "COMMIT":
        if receipt_data["mutation_hash"] is None:
            raise ReceiptSchemaError(
                "COMMIT receipt requires mutation_hash"
            )

    if receipt_data["terminal_outcome"] == "REFUSE":
        if receipt_data["mutation_hash"] is not None:
            raise ReceiptSchemaError(
                "REFUSE receipt must not contain mutation_hash"
            )


def create_receipt(
    *,
    receipt_id: str,
    timestamp: str,
    terminal_authority: str,
    ticket_id: str,
    ticket_hash: str,
    invariant_id: str,
    invariant_version: str,
    payload_hash: str,
    tool: str,
    observed_epoch: int,
    observed_state_hash: str,
    nonce: int,
    bound_verified: bool,
    fresh_verified: bool,
    authorized_verified: bool,
    invariant_verified: bool,
    composite_valid_predicate: bool,
    terminal_outcome: str,
    reason_code: str,
    mutation_hash: Optional[str],
    causal_trace_id: str,
    sequence_number: int,
    previous_receipt_hash: Optional[str],
    private_key_hex: str,
) -> TerminalReceipt:
    """
    Create and sign one terminal receipt.

    The caller supplies the already-evaluated terminal outcome.
    This function does not evaluate Valid().
    """
    unsigned = {
        "receipt_id": receipt_id,
        "timestamp": timestamp,
        "terminal_authority": terminal_authority,
        "ticket_id": ticket_id,
        "ticket_hash": ticket_hash,
        "invariant_id": invariant_id,
        "invariant_version": invariant_version,
        "payload_hash": payload_hash,
        "tool": tool,
        "observed_epoch": observed_epoch,
        "observed_state_hash": observed_state_hash,
        "nonce": nonce,
        "bound_verified": bound_verified,
        "fresh_verified": fresh_verified,
        "authorized_verified": authorized_verified,
        "invariant_verified": invariant_verified,
        "composite_valid_predicate": composite_valid_predicate,
        "terminal_outcome": terminal_outcome,
        "reason_code": reason_code,
        "mutation_hash": mutation_hash,
        "causal_trace_id": causal_trace_id,
        "sequence_number": sequence_number,
        "previous_receipt_hash": previous_receipt_hash,
    }

    provisional = dict(unsigned)
    provisional["receipt_hash"] = sha256_hex(
        canonicalize(unsigned)
    )

    data_to_sign = canonicalize(provisional)

    try:
        signature = sign(
            private_key_hex,
            data_to_sign,
        )
    except MalformedCryptoInput as exc:
        raise ReceiptError(
            f"unable to sign receipt: {exc}"
        ) from exc

    complete = dict(provisional)
    complete["signature"] = signature

    _validate_receipt_fields(complete)

    return TerminalReceipt(
        receipt_id=receipt_id,
        timestamp=timestamp,
        terminal_authority=terminal_authority,
        ticket_id=ticket_id,
        ticket_hash=ticket_hash,
        invariant_id=invariant_id,
        invariant_version=invariant_version,
        payload_hash=payload_hash,
        tool=tool,
        observed_epoch=observed_epoch,
        observed_state_hash=observed_state_hash,
        nonce=nonce,
        bound_verified=bound_verified,
        fresh_verified=fresh_verified,
        authorized_verified=authorized_verified,
        invariant_verified=invariant_verified,
        composite_valid_predicate=composite_valid_predicate,
        terminal_outcome=terminal_outcome,
        reason_code=reason_code,
        mutation_hash=mutation_hash,
        causal_trace_id=causal_trace_id,
        sequence_number=sequence_number,
        previous_receipt_hash=previous_receipt_hash,
        receipt_hash=provisional["receipt_hash"],
        signature=signature,
    )


def receipt_from_dict(
    data: Dict[str, Any],
) -> TerminalReceipt:
    """Construct a TerminalReceipt from serialized data."""
    _validate_receipt_fields(data)

    return TerminalReceipt(
        receipt_id=data["receipt_id"],
        timestamp=data["timestamp"],
        terminal_authority=data["terminal_authority"],
        ticket_id=data["ticket_id"],
        ticket_hash=data["ticket_hash"],
        invariant_id=data["invariant_id"],
        invariant_version=data["invariant_version"],
        payload_hash=data["payload_hash"],
        tool=data["tool"],
        observed_epoch=data["observed_epoch"],
        observed_state_hash=data["observed_state_hash"],
        nonce=data["nonce"],
        bound_verified=data["bound_verified"],
        fresh_verified=data["fresh_verified"],
        authorized_verified=data["authorized_verified"],
        invariant_verified=data["invariant_verified"],
        composite_valid_predicate=data["composite_valid_predicate"],
        terminal_outcome=data["terminal_outcome"],
        reason_code=data["reason_code"],
        mutation_hash=data["mutation_hash"],
        causal_trace_id=data["causal_trace_id"],
        sequence_number=data["sequence_number"],
        previous_receipt_hash=data["previous_receipt_hash"],
        receipt_hash=data["receipt_hash"],
        signature=data["signature"],
    )


def receipt_to_dict(
    receipt: TerminalReceipt,
) -> Dict[str, Any]:
    """Serialize a TerminalReceipt to a dictionary."""
    return receipt.to_dict()


__all__ = [
    "TerminalReceipt",
    "ReceiptError",
    "ReceiptSchemaError",
    "TERMINAL_OUTCOMES",
    "create_receipt",
    "receipt_from_dict",
    "receipt_to_dict",
]


if __name__ == "__main__":
    from aic_harness.crypto import generate_keypair

    print("[*] Running receipt.py self-test...")

    private_key, _ = generate_keypair()

    receipt = create_receipt(
        receipt_id="RECEIPT-0001",
        timestamp="2026-08-17T00:00:00Z",
        terminal_authority="terminal-01",
        ticket_id="TICKET-0001",
        ticket_hash="a" * 64,
        invariant_id="INV-001",
        invariant_version="1.0",
        payload_hash="b" * 64,
        tool="example-tool",
        observed_epoch=1,
        observed_state_hash="c" * 64,
        nonce=1,
        bound_verified=True,
        fresh_verified=True,
        authorized_verified=True,
        invariant_verified=True,
        composite_valid_predicate=True,
        terminal_outcome="COMMIT",
        reason_code="VALID",
        mutation_hash="d" * 64,
        causal_trace_id="TRACE-0001",
        sequence_number=1,
        previous_receipt_hash=None,
        private_key_hex=private_key,
    )

    assert receipt.terminal_outcome == "COMMIT"
    assert receipt.mutation_hash == "d" * 64
    assert len(receipt.receipt_hash) == 64
    assert len(receipt.signature) == 128

    restored = receipt_from_dict(receipt.to_dict())

    assert restored == receipt

    print("[+] Receipt construction: PASS")
    print("[+] Receipt hash generation: PASS")
    print("[+] Receipt signing: PASS")
    print("[+] Receipt round-trip: PASS")
    print("[+] receipt.py self-test passed.")
