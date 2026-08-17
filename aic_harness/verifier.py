"""
aic_harness/verifier.py

Independent verification layer for the AIC/BBIS V6.4.2
reference harness.

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

from aic_harness.canonical import canonicalize
from aic_harness.crypto import (
    MalformedCryptoInput,
    sha256_hex,
    verify,
)
from aic_harness.evidence import (
    EvidenceLink,
    verify_evidence_chain,
    verify_evidence_link,
)
from aic_harness.receipt import TerminalReceipt


class VerificationError(ValueError):
    """Base exception for verification failures."""


@dataclass(frozen=True)
class VerificationResult:
    """
    Result of independent terminal-evidence verification.

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


def _receipt_signing_bytes(
    receipt: TerminalReceipt,
) -> bytes:
    """
    Return the canonical bytes covered by the receipt signature.

    TerminalReceipt.canonical_bytes() returns the canonical
    representation of the signed receipt body, including
    receipt_hash and excluding signature.
    """
    return receipt.canonical_bytes()


def _calculate_receipt_hash(
    receipt: TerminalReceipt,
) -> str:
    """
    Recalculate the receipt hash from the unsigned receipt body.

    The receipt hash is defined as:

        SHA256(
            RFC8785_CANONICALIZE(
                receipt.unsigned_dict()
            )
        )
    """
    return sha256_hex(
        canonicalize(receipt.unsigned_dict())
    )


def verify_receipt_signature(
    receipt: TerminalReceipt,
    terminal_public_key_hex: str,
) -> bool:
    """
    Independently verify a terminal receipt signature.

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
    except MalformedCryptoInput as exc:
        raise VerificationError(
            f"malformed receipt cryptographic material: {exc}"
        ) from exc


def verify_receipt_integrity(
    receipt: TerminalReceipt,
) -> bool:
    """
    Verify the receipt's internally recorded hash.

    The calculated hash is compared against receipt.receipt_hash.
    """
    calculated = _calculate_receipt_hash(receipt)

    return calculated == receipt.receipt_hash


def verify_terminal_receipt(
    receipt: TerminalReceipt,
    terminal_public_key_hex: str,
) -> bool:
    """
    Perform independent verification of one terminal receipt.

    Both the receipt hash and its Ed25519 signature must verify.
    """
    signature_valid = verify_receipt_signature(
        receipt,
        terminal_public_key_hex,
    )

    integrity_valid = verify_receipt_integrity(
        receipt,
    )

    return signature_valid and integrity_valid


def verify_evidence(
    receipts: Iterable[TerminalReceipt],
    chain: Iterable[EvidenceLink],
) -> bool:
    """
    Verify an entire receipt/evidence relationship.

    Verification includes:
        - receipt/chain correspondence
        - evidence-link integrity
        - previous-chain linkage
        - sequence continuity
        - terminal-outcome consistency
    """
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
    """
    Perform an independent evidence audit.

    No execution behavior is changed by this function.

    If a chain is supplied, the matching evidence link for the
    supplied receipt must exist and verify.

    If receipts are also supplied, the complete evidence chain
    is verified against those receipts.
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


if __name__ == "__main__":
    from aic_harness.crypto import generate_keypair
    from aic_harness.evidence import build_evidence_chain
    from aic_harness.receipt import create_receipt

    print("[*] Running verifier.py self-test...")

    private_key, public_key = generate_keypair()

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

    chain = build_evidence_chain([receipt])

    assert verify_receipt_signature(
        receipt,
        public_key,
    )

    assert verify_receipt_integrity(
        receipt,
    )

    assert verify_terminal_receipt(
        receipt,
        public_key,
    )

    assert verify_evidence(
        [receipt],
        chain,
    )

    result = audit(
        receipt,
        public_key,
        [receipt],
        chain,
    )

    assert result.receipt_signature_valid
    assert result.receipt_integrity_valid
    assert result.evidence_link_valid
    assert result.evidence_chain_valid
    assert result.valid

    print("[+] Receipt signature verification: PASS")
    print("[+] Receipt integrity verification: PASS")
    print("[+] Terminal receipt verification: PASS")
    print("[+] Evidence verification: PASS")
    print("[+] Independent audit: PASS")
    print("[+] verifier.py self-test passed.")
