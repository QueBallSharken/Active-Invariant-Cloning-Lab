"""
aic_harness/crypto.py

Cryptographic primitives for the AIC/BBIS V6.4.2 reference harness.

Provides:
- Ed25519 key generation
- Ed25519 signing and verification
- SHA-256 hashing
- byte/hex conversion

Canonicalization is owned by aic_harness.canonical.
Evidence-chain semantics are owned by aic_harness.evidence.
"""

from __future__ import annotations

import hashlib
from typing import Union

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


SIGNATURE_LENGTH = 64
PUBLIC_KEY_LENGTH = 32
PRIVATE_KEY_LENGTH = 32
HASH_LENGTH = 32


class MalformedCryptoInput(ValueError):
    """Raised when cryptographic input is malformed."""


def generate_keypair() -> tuple[str, str]:
    """
    Generate a fresh Ed25519 key pair.

    Returns:
        Tuple of:
            private_key_hex
            public_key_hex
    """
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    return private_bytes.hex(), public_bytes.hex()


def sign(private_key_hex: str, data: bytes) -> str:
    """
    Sign arbitrary bytes with an Ed25519 private key.

    Returns:
        Hex-encoded 64-byte signature.

    Raises:
        MalformedCryptoInput:
            If the key encoding or key length is invalid.
        TypeError:
            If data is not bytes.
    """
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")

    try:
        private_bytes = bytes.fromhex(private_key_hex)
    except (TypeError, ValueError) as exc:
        raise MalformedCryptoInput(
            "private key is not valid hexadecimal"
        ) from exc

    if len(private_bytes) != PRIVATE_KEY_LENGTH:
        raise MalformedCryptoInput(
            f"private key must be {PRIVATE_KEY_LENGTH} bytes"
        )

    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(
        private_bytes
    )

    return private_key.sign(data).hex()


def verify(
    public_key_hex: str,
    signature_hex: str,
    data: bytes,
) -> bool:
    """
    Verify an Ed25519 signature.

    Returns:
        True when the signature is cryptographically valid.
        False when the signature is validly formed but incorrect.

    Raises:
        MalformedCryptoInput:
            If key or signature encoding/length is malformed.
        TypeError:
            If data is not bytes.
    """
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")

    try:
        public_bytes = bytes.fromhex(public_key_hex)
    except (TypeError, ValueError) as exc:
        raise MalformedCryptoInput(
            "public key is not valid hexadecimal"
        ) from exc

    try:
        signature_bytes = bytes.fromhex(signature_hex)
    except (TypeError, ValueError) as exc:
        raise MalformedCryptoInput(
            "signature is not valid hexadecimal"
        ) from exc

    if len(public_bytes) != PUBLIC_KEY_LENGTH:
        raise MalformedCryptoInput(
            f"public key must be {PUBLIC_KEY_LENGTH} bytes"
        )

    if len(signature_bytes) != SIGNATURE_LENGTH:
        raise MalformedCryptoInput(
            f"signature must be {SIGNATURE_LENGTH} bytes"
        )

    try:
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(
            public_bytes
        )
        public_key.verify(signature_bytes, data)
        return True
    except InvalidSignature:
        return False


def sha256(data: Union[str, bytes]) -> bytes:
    """
    Compute a SHA-256 digest.

    Strings are encoded as UTF-8.

    Returns:
        Raw 32-byte SHA-256 digest.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    if not isinstance(data, bytes):
        raise TypeError("data must be bytes or str")

    return hashlib.sha256(data).digest()


def sha256_hex(data: Union[str, bytes]) -> str:
    """
    Compute a SHA-256 digest and return lowercase hexadecimal.
    """
    return sha256(data).hex()


def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to lowercase hexadecimal."""
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")

    return data.hex()


def hex_to_bytes(value: str) -> bytes:
    """
    Convert hexadecimal text to bytes.

    Raises:
        MalformedCryptoInput:
            If the supplied value is not valid hexadecimal.
    """
    if not isinstance(value, str):
        raise TypeError("value must be str")

    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise MalformedCryptoInput(
            "value is not valid hexadecimal"
        ) from exc


__all__ = [
    "MalformedCryptoInput",
    "generate_keypair",
    "sign",
    "verify",
    "sha256",
    "sha256_hex",
    "bytes_to_hex",
    "hex_to_bytes",
    "SIGNATURE_LENGTH",
    "PUBLIC_KEY_LENGTH",
    "PRIVATE_KEY_LENGTH",
    "HASH_LENGTH",
]


if __name__ == "__main__":
    print("[*] Running crypto.py self-test...")

    private_key, public_key = generate_keypair()

    message = b"AIC/BBIS V6.4.2 crypto self-test"

    signature = sign(private_key, message)

    assert verify(
        public_key,
        signature,
        message,
    )

    assert not verify(
        public_key,
        signature,
        b"tampered message",
    )

    digest = sha256(message)

    assert len(digest) == HASH_LENGTH
    assert len(signature) == SIGNATURE_LENGTH * 2

    print("[+] Ed25519 signing: PASS")
    print("[+] Ed25519 verification: PASS")
    print("[+] Invalid signature detection: PASS")
    print("[+] SHA-256: PASS")
    print("[+] crypto.py self-test passed.")
