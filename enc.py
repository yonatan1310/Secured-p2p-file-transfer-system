import os
import random
import time
from random import randrange
import base64

from cryptography.exceptions import InvalidSignature
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

number_of_bytes = 5


def generate_key(password):
    salt = b'salt_'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


def encrypt(password, message):
    key = generate_key(password)
    print(key)
    f = Fernet(key)
    if type(message) == type(bytes()):
        return f.encrypt(message)
    return f.encrypt(message.encode())


def encrypt_file(password, file_name):
    with open(file_name, 'rb') as my_file:
        file_data = my_file.read()
    with open(file_name, 'wb') as my_file:
        my_file.write(encrypt(password, file_data))


def decrypt_file(password, file_name):
    with open(file_name, 'rb') as my_file:
        file_data = my_file.read()
    with open(file_name, 'wb') as my_file:
        my_file.write(decrypt(file_data, password))


def decrypt(encrypted, password):
    key = generate_key(password)
    print(key)
    f = Fernet(key)
    return f.decrypt(encrypted)

