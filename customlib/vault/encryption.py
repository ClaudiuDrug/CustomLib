# -*- coding: UTF-8 -*-

from base64 import b64encode
from random import choice
from string import ascii_uppercase, ascii_lowercase, digits, punctuation
from typing import Union

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..utils import decode, encode


class Symmetric(object):
    """
    Symmetric key generator.
    NOTE: Can only be used once per instance.
    """

    def __init__(self, salt: Union[bytes, str]):
        self._kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=encode(salt),
            iterations=200000,
            backend=default_backend()
        )

    def __derive(self, value: bytes) -> bytes:
        """Generate and return a new derived key."""
        return self._kdf.derive(value)

    def key(self, value: Union[bytes, str]) -> bytes:
        """Generate a new derived key and encode it using Base64 alphabet."""
        derived = self.__derive(encode(value))
        return b64encode(derived)


class Cypher(object):
    """Encryption handle."""

    @staticmethod
    def _random(length: int) -> str:
        """Generates a completely random string of size `length`."""
        chars = ascii_uppercase + ascii_lowercase + digits + punctuation
        return "".join(choice(chars) for x in range(length))

    def __init__(self):
        self.__cypher = Fernet
        self.__key = None

    def generate(self, length: int = 16) -> str:
        """Return a new random password of size `length`."""
        return self._random(length)

    def password(self, value: Union[bytes, str], salt: Union[bytes, str]):
        """Set a new symmetrically derived encryption key."""
        self.__key = Symmetric(encode(salt)).key(encode(value))

    def encrypt(self, value: Union[bytes, str]) -> str:
        """Encrypt the `value` using the symmetrically derived encryption key."""
        return decode(self.__cypher(self.__key).encrypt(encode(value)))

    def decrypt(self, value: Union[bytes, str]) -> str:
        """Decrypt the `value` using the symmetrically derived encryption key."""
        try:
            return decode(self.__cypher(self.__key).decrypt(encode(value)))
        except InvalidToken as invalid_token:
            raise invalid_token
