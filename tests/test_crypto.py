from aic_harness.crypto import (
    HASH_LENGTH,
    SIGNATURE_LENGTH,
    generate_keypair,
    sha256,
    sign,
    verify,
)


def test_keypair_generation():
    private_key, public_key = generate_keypair()

    assert len(bytes.fromhex(private_key)) == 32
    assert len(bytes.fromhex(public_key)) == 32


def test_ed25519_signature_verifies():
    private_key, public_key = generate_keypair()

    message = b"AIC/BBIS test message"

    signature = sign(private_key, message)

    assert len(bytes.fromhex(signature)) == SIGNATURE_LENGTH
    assert verify(public_key, signature, message)


def test_tampered_message_is_rejected():
    private_key, public_key = generate_keypair()

    signature = sign(
        private_key,
        b"authorized mutation",
    )

    assert not verify(
        public_key,
        signature,
        b"unauthorized mutation",
    )


def test_sha256_is_deterministic():
    message = b"AIC/BBIS deterministic hash"

    first = sha256(message)
    second = sha256(message)

    assert first == second
    assert len(first) == HASH_LENGTH
