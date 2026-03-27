from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def hasher(password: str) -> str:
    return ph.hash(password)

def verifier(password: str, hash_: str) -> bool:
    try:
        return ph.verify(hash_, password)
    except VerifyMismatchError:
        return False
