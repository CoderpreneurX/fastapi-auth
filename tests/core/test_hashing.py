from fastapi_auth.core.hashing import Hashing as Hasher


def test_hash_returns_different_value():
    value = "super-secret"

    hashed = Hasher.hash(value)

    assert hashed != value


def test_verify_correct_value():
    value = "super-secret"

    hashed = Hasher.hash(value)

    assert Hasher.verify(value, hashed)


def test_verify_wrong_value():
    hashed = Hasher.hash("super-secret")

    assert not Hasher.verify("wrong-secret", hashed)


def test_same_value_produces_different_hashes():
    value = "super-secret"

    hash1 = Hasher.hash(value)
    hash2 = Hasher.hash(value)

    assert hash1 != hash2
    assert Hasher.verify(value, hash1)
    assert Hasher.verify(value, hash2)
