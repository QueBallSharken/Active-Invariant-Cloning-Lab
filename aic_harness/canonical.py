"""
aic_harness/canonical.py

Single canonicalization authority for the AIC/BBIS V6.4.2
reference harness.

Uses RFC 8785 JSON Canonicalization Scheme (JCS) through
the rfc8785 package.

This module owns serialization only.

It does not perform:
- authorization
- invariant evaluation
- ticket validation
- terminal decisions
- signing
- evidence-chain semantics
"""

from __future__ import annotations

from typing import Any

import rfc8785

from aic_harness.crypto import sha256


def canonicalize(data: Any) -> bytes:
    """
    Produce the RFC 8785 canonical byte representation of data.

    Args:
        data:
            A JSON-compatible Python value.

    Returns:
        Canonical UTF-8 JSON bytes.

    Raises:
        ValueError:
            If the supplied value cannot be represented according
            to RFC 8785 / JSON Canonicalization Scheme.
    """
    try:
        return rfc8785.dumps(data)
    except Exception as exc:
        raise ValueError(
            f"failed to produce RFC 8785 canonical representation: {exc}"
        ) from exc


def canonical_hash(data: Any) -> bytes:
    """
    Canonicalize data and compute its SHA-256 digest.

    Canonicalization is performed exclusively by this module.
    Hashing is delegated exclusively to aic_harness.crypto.
    """
    return sha256(canonicalize(data))


__all__ = [
    "canonicalize",
    "canonical_hash",
]


if __name__ == "__main__":
    print("[*] Running canonical.py self-test...")

    first = {
        "b": 2,
        "a": 1,
        "nested": {
            "z": 26,
            "y": 25,
        },
    }

    second = {
        "nested": {
            "y": 25,
            "z": 26,
        },
        "a": 1,
        "b": 2,
    }

    canonical_first = canonicalize(first)
    canonical_second = canonicalize(second)

    assert canonical_first == canonical_second

    assert canonical_first == (
        b'{"a":1,"b":2,"nested":{"y":25,"z":26}}'
    )

    digest = canonical_hash(first)

    assert len(digest) == 32

    print("[+] RFC 8785 canonicalization: PASS")
    print("[+] Deterministic key ordering: PASS")
    print("[+] Canonical SHA-256: PASS")
    print("[+] canonical.py self-test passed.")
