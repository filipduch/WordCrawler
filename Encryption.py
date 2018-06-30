from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

from Config import Config


class Encryption(object):
    @staticmethod
    def encrypt(data):
        with open(Config['public_key_path'], "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read(), default_backend())
            cipher_text = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA512()),
                    algorithm=hashes.SHA512(),
                    label=None
                )
            )
            return cipher_text

    @staticmethod
    def decrypt(cipher_text):
        with open(Config['private_key_path'], "rb") as key_file:
            private_key = serialization.load_pem_private_key(key_file.read(), None, default_backend())
            plain_text = private_key.decrypt(
                cipher_text,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA512()),
                    algorithm=hashes.SHA512(),
                    label=None
                )
            )
            return plain_text.decode()
