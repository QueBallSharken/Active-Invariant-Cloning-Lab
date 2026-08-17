"""
aic_harness/evidence.py

Evidence-chain construction and verification for the
AIC/BBIS V6.4.2 reference harness.

Frozen chain construction:

    H_n =
        SHA256(
            decision
            || ticket_hash
            || state_hash
            || receipt_hash
            || H_(n-1)
        )

This module owns evidence-chain semantics.

It does not:
- evaluate Valid()
- authorize mutations
- perform protected mutations
- change terminal outcomes
- calculate expectedness
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from aic_harness.crypto import sha256_hex
from aic_harness.receipt import TerminalReceipt


class EvidenceError(ValueError):
    """Base exception for evidence-chain failures."""


class EvidenceIntegrityError(EvidenceError):
    """Raised when evidence-chain integrity verification fails."""


@dataclass(frozen=True)
class EvidenceLink:
    """
    One cryptographic link in the AIC/BBIS evidence chain.
    """

    sequence_number: int
    decision: str
    ticket_hash: str
    state_hash: str
    receipt_hash: str
    previous_chain_hash: Optional[str]
    chain_hash: str

    def material(self) -> bytes:
        """
        Return the exact frozen chain material.

        The fields are concatenated in the order specified by
        the V6.4.2 contract.
        """
        return _chain_material(
            decision=self.decision,
            ticket_hash=self.ticket_hash,
            state_hash=self.state_hash,
            receipt_hash=self.receipt_hash,
            previous_chain_hash=self.previous_chain_hash,
        )


def _chain_material(
    *,
    decision: str,
    ticket_hash: str,
    state_hash: str,
    receipt_hash: str,
    previous_chain_hash: Optional[str],
) -> bytes:
    """
    Construct the exact byte sequence specified by V6.4.2.

    Textual fields are UTF-8 encoded and concatenated directly.
    The initial chain has an empty previous hash.
    """
    return (
        decision.encode("utf-8")
        + ticket_hash.encode("utf-8")
        + state_hash.encode("utf-8")
        + receipt_hash.encode("utf-8")
        + (previous_chain_hash or "").encode("utf-8")
    )


def _calculate_chain_hash(
    *,
    decision: str,
    ticket_hash: str,
    state_hash: str,
    receipt_hash: str,
    previous_chain_hash: Optional[str],
) -> str:
    """Calculate one frozen V6.4.2 evidence-chain hash."""
    return sha256_hex(
        _chain_material(
            decision=decision,
            ticket_hash=ticket_hash,
            state_hash=state_hash,
            receipt_hash=receipt_hash,
            previous_chain_hash=previous_chain_hash,
        )
    )


def create_evidence_link(
    receipt: TerminalReceipt,
    previous_chain_hash: Optional[str],
) -> EvidenceLink:
    """
    Construct one evidence-chain link from a finalized receipt.
    """
    if receipt.terminal_outcome not in {"COMMIT", "REFUSE"}:
        raise EvidenceError(
            "receipt has invalid terminal outcome"
        )

    chain_hash = _calculate_chain_hash(
        decision=receipt.terminal_outcome,
        ticket_hash=receipt.ticket_hash,
        state_hash=receipt.observed_state_hash,
        receipt_hash=receipt.receipt_hash,
        previous_chain_hash=previous_chain_hash,
    )

    return EvidenceLink(
        sequence_number=receipt.sequence_number,
        decision=receipt.terminal_outcome,
        ticket_hash=receipt.ticket_hash,
        state_hash=receipt.observed_state_hash,
        receipt_hash=receipt.receipt_hash,
        previous_chain_hash=previous_chain_hash,
        chain_hash=chain_hash,
    )


def verify_evidence_link(
    link: EvidenceLink,
) -> bool:
    """
    Verify the cryptographic integrity of one evidence-chain link.
    """
    expected = _calculate_chain_hash(
        decision=link.decision,
        ticket_hash=link.ticket_hash,
        state_hash=link.state_hash,
        receipt_hash=link.receipt_hash,
        previous_chain_hash=link.previous_chain_hash,
    )

    return expected == link.chain_hash


def build_evidence_chain(
    receipts: Iterable[TerminalReceipt],
) -> list[EvidenceLink]:
    """
    Build an evidence chain from terminal receipts.

    Receipts must already be ordered by sequence number.
    """
    chain: list[EvidenceLink] = []

    previous_hash: Optional[str] = None
    previous_sequence: Optional[int] = None

    for receipt in receipts:
        if (
            previous_sequence is not None
            and receipt.sequence_number != previous_sequence + 1
        ):
            raise EvidenceIntegrityError(
                "receipt sequence contains a gap or duplicate"
            )

        link = create_evidence_link(
            receipt,
            previous_hash,
        )

        chain.append(link)
        previous_hash = link.chain_hash
        previous_sequence = receipt.sequence_number

    return chain


def verify_evidence_chain(
    receipts: Iterable[TerminalReceipt],
    chain: Iterable[EvidenceLink],
) -> bool:
    """
    Verify the complete evidence chain against its receipts.

    Detects:
    - modified terminal outcomes
    - modified ticket hashes
    - modified state hashes
    - modified receipt hashes
    - broken previous-chain links
    - sequence gaps or duplicates
    - modified chain hashes
    """
    receipt_list = list(receipts)
    chain_list = list(chain)

    if len(receipt_list) != len(chain_list):
        return False

    previous_hash: Optional[str] = None
    previous_sequence: Optional[int] = None
    previous_receipt_hash: Optional[str] = None

    for receipt, link in zip(receipt_list, chain_list):
        if receipt.sequence_number != link.sequence_number:
            return False

        if (
            previous_sequence is not None
            and receipt.sequence_number != previous_sequence + 1
        ):
            return False

        if link.decision != receipt.terminal_outcome:
            return False

        if link.ticket_hash != receipt.ticket_hash:
            return False

        if link.state_hash != receipt.observed_state_hash:
            return False

        if link.receipt_hash != receipt.receipt_hash:
            return False

        if link.previous_chain_hash != previous_hash:
            return False

        if (
            receipt.previous_receipt_hash
            != previous_receipt_hash
        ):
            return False

        if not verify_evidence_link(link):
            return False

        previous_hash = link.chain_hash
        previous_sequence = receipt.sequence_number
        previous_receipt_hash = receipt.receipt_hash

    return True


def evidence_chain_head(
    chain: Iterable[EvidenceLink],
) -> Optional[str]:
    """Return the final chain hash, or None for an empty chain."""
    chain_list = list(chain)

    if not chain_list:
        return None

    return chain_list[-1].chain_hash


__all__ = [
    "EvidenceError",
    "EvidenceIntegrityError",
    "EvidenceLink",
    "create_evidence_link",
    "verify_evidence_link",
    "build_evidence_chain",
    "verify_evidence_chain",
    "evidence_chain_head",
]


if __name__ == "__main__":
    from aic_harness.crypto import generate_keypair
    from aic_harness.receipt import create_receipt

    print("[*] Running evidence.py self-test...")

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

    chain = build_evidence_chain([receipt])

    assert len(chain) == 1
    assert verify_evidence_chain([receipt], chain)
    assert evidence_chain_head(chain) == chain[0].chain_hash

    tampered = EvidenceLink(
        sequence_number=chain[0].sequence_number,
        decision="REFUSE",
        ticket_hash=chain[0].ticket_hash,
        state_hash=chain[0].state_hash,
        receipt_hash=chain[0].receipt_hash,
        previous_chain_hash=chain[0].previous_chain_hash,
        chain_hash=chain[0].chain_hash,
    )

    assert not verify_evidence_link(tampered)

    print("[+] Evidence-link construction: PASS")
    print("[+] Evidence-chain verification: PASS")
    print("[+] Terminal-outcome tampering detection: PASS")
    print("[+] evidence.py self-test passed.")
