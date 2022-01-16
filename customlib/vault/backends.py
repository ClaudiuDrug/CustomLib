# -*- coding: UTF-8 -*-

from cryptography.fernet import InvalidToken
from keyring import set_password, get_password, delete_password
from keyring.errors import PasswordSetError, PasswordDeleteError

from .encryption import Cypher
from .exceptions import PasswordGetError


class KeyVault(object):
    """KeyRing interface."""

    def __init__(self):
        self.cypher = Cypher()

    def get_password(self, service: str, username: str) -> str:
        """Fetch & decrypt a password from the keyring."""
        try:
            password = get_password(service, username)
        except PasswordGetError as pwd_get_error:
            raise pwd_get_error
        else:
            if password is not None:
                try:
                    return self.cypher.decrypt(password)
                except InvalidToken as invalid_token:
                    raise invalid_token

    def set_password(self, service: str, username: str, password: str):
        """Encrypt & store a password into the keyring."""
        password = self.cypher.encrypt(password)
        try:
            set_password(service_name=service, username=username, password=password)
        except PasswordSetError as pwd_set_error:
            raise pwd_set_error

    @staticmethod
    def del_password(service: str, username: str):
        """Delete a password from the keystore."""
        try:
            delete_password(service_name=service, username=username)
        except PasswordDeleteError as pwd_del_error:
            raise pwd_del_error
