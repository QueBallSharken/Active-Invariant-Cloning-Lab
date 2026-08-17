"""
aic_harness/verifier.py

Independent verification layer for the AIC/BBIS V6.4.2 reference harness.

Responsibilities:
- verify terminal receipt signatures
- verify receipt integrity
- verify evidence-chain integrity
- detect altered terminal outcomes
- detect broken evidence links

This module MUST NOT:
- authorize mutations
- perform mutations
- alter terminal outcomes
- calculate execution decisions
- reinterpret expectedness
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from aic_harness.crypto import MalformedCryptoInput, verify, sha256_hex
from aic_harness.evidence import (
    EvidenceLink,
    verify_evidence_chain,
    verify_evidence_link,
)
from aic_harness.receipt import TerminalReceipt
from aic_harness.canonical import canonicalize


class VerificationError(ValueError):
    """Base exception for verification failures."""


@dataclass(frozen=True)
class VerificationResult:
    """Result of independent terminal-evidence verification.

    This describes evidence integrity only.
    It does not replace terminal_outcome.
    """

    receipt_signature_valid: bool
    receipt_integrity_valid: bool
    evidence_link_valid: bool
    evidence_chain_valid: bool

    @property
    def valid(self) -> bool:
        """Return True only when all verification checks pass."""
        return (
            self.receipt_signature_valid
            and self.receipt_integrity_valid
            and self.evidence_link_valid
            and self.evidence_chain_valid
        )


def _receipt_signing_bytes(receipt: TerminalReceipt) -> bytes:
    """Return the canonical bytes covered by the receipt signature.

    receipt.py defines canonical_bytes() as the canonical representation
    of signed_dict(), which includes receipt_hash and excludes signature.
    """
    try:
        return receipt.canonical_bytes()
    except AttributeError as exc:
        raise VerificationError(
            "TerminalReceipt does not expose canonical_bytes()"
        ) from exc


def _calculate_receipt_hash(receipt: TerminalReceipt) -> str:
    """Recalculate the receipt hash from the unsigned receipt body."""
    try:
        unsigned = receipt.unsigned_dict()
    except AttributeError as exc:
        raise VerificationError(
            "TerminalReceipt does not expose unsigned_dict()"
        ) from exc

    return sha256_hex(canonicalize(unsigned))


def verify_receipt_signature(
    receipt: TerminalReceipt,
    terminal_public_key_hex: str,
) -> bool:
    """Independently verify a terminal receipt signature.

    Returns:
        True when the signature is cryptographically valid.
        False when the signature is cryptographically incorrect.

    Raises:
        VerificationError:
            If cryptographic material is malformed.
    """
    try:
        return verify(
            terminal_public_key_hex,
            receipt.signature,
            _receipt_signing_bytes(receipt),
        )
    except (MalformedCryptoInput, TypeError, ValueError) as exc:
        raise VerificationError(
            "malformed receipt cryptographic material"
        ) from exc


def verify_receipt_integrity(
    receipt: TerminalReceipt,
) -> bool:
    """Verify the receipt's internally recorded hash.

    The receipt hash is defined as SHA-256 over the canonical
    unsigned receipt body.
    """
    calculated = _calculate_receipt_hash(receipt)
    return calculated == receipt.receipt_hash


def verify_terminal_receipt(
    receipt: TerminalReceipt,
    terminal_public_key_hex: str,
) -> bool:
    """Perform independent verification of one terminal receipt."""
    signature_valid = verify_receipt_signature(
        receipt,
        terminal_public_key_hex,
    )

    integrity_valid = verify_receipt_integrity(receipt)

    return signature_valid and integrity_valid


def verify_evidence(
    receipts: Iterable[TerminalReceipt],
    chain: Iterable[EvidenceLink],
) -> bool:
    """Verify an entire receipt/evidence relationship."""
    receipt_list = list(receipts)
    chain_list = list(chain)

    if len(receipt_list) != len(chain_list):
        return False

    for link in chain_list:
        if not verify_evidence_link(link):
            return False

    return verify_evidence_chain(
        receipt_list,
        chain_list,
    )


def audit(
    receipt: TerminalReceipt,
    terminal_public_key_hex: str,
    receipts: Optional[Iterable[TerminalReceipt]] = None,
    chain: Optional[Iterable[EvidenceLink]] = None,
) -> VerificationResult:
    """Perform an independent evidence audit.

    No execution behavior is changed by this function.
    """
    receipt_signature_valid = verify_receipt_signature(
        receipt,
        terminal_public_key_hex,
    )

    receipt_integrity_valid = verify_receipt_integrity(
        receipt,
    )

    evidence_link_valid = True
    evidence_chain_valid = True

    if chain is not None:
        chain_list = list(chain)

        matching_links = [
            link
            for link in chain_list
            if link.sequence_number == receipt.sequence_number
        ]

        if not matching_links:
            evidence_link_valid = False
        else:
            evidence_link_valid = all(
                verify_evidence_link(link)
                for link in matching_links
            )

        if receipts is not None:
            evidence_chain_valid = verify_evidence(
                receipts,
                chain_list,
            )

    return VerificationResult(
        receipt_signature_valid=receipt_signature_valid,
        receipt_integrity_valid=receipt_integrity_valid,
        evidence_link_valid=evidence_link_valid,
        evidence_chain_valid=evidence_chain_valid,
    )


__all__ = [
    "VerificationError",
    "VerificationResult",
    "verify_receipt_signature",
    "verify_receipt_integrity",
    "verify_terminal_receipt",
    "verify_evidence",
    "audit",
]
