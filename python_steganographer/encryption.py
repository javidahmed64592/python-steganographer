"""Encryption methods for the steganography application."""

from __future__ import annotations

import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class EncryptionHandler:
    """Handler class for encryption and decryption operations."""

    def __init__(
        self,
        private_key: RSAPrivateKey | None = None,
        iv: bytes | None = None,
        aes_key: bytes | None = None,
        iv_size: int = 16,
        aes_key_size: int = 32,
    ) -> None:
        """Initialize the KeysType with RSA keys and AES key.

        :param RSAPrivateKey private_key: RSA private key for decryption
        :param bytes iv: Initialization vector for AES encryption/decryption
        :param bytes aes_key: AES key for encryption/decryption
        :param int iv_size: Size of the initialization vector (default: 16 bytes)
        :param int aes_key_size: Size of the AES key (default: 32 bytes)
        """
        self.private_key = private_key or rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        self.iv = iv or os.urandom(iv_size)
        self.aes_key = aes_key or os.urandom(aes_key_size)

    @staticmethod
    def private_key_to_str(private_key: RSAPrivateKey) -> str:
        """Convert RSAPrivateKey to a PEM formatted string.

        :param RSAPrivateKey private_key: RSAPrivateKey object
        :return str: PEM formatted string representation of the private key
        """
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return pem.decode("utf-8")

    @staticmethod
    def str_to_private_key(private_key_str: str) -> RSAPrivateKey:
        """Convert a PEM formatted string to an RSAPrivateKey.

        :param str private_key_str: PEM formatted string representation of the private key
        :return RSAPrivateKey: RSAPrivateKey object
        """
        pem = private_key_str.encode("utf-8")
        return serialization.load_pem_private_key(pem, password=None, backend=default_backend())

    @staticmethod
    def strip_pem_headers(private_key_str: str) -> str:
        """Strip PEM headers from a private key string.

        :param str private_key_str: PEM formatted string representation of the private key
        :return str: Private key body without PEM headers
        """
        key_body = (
            private_key_str.strip().replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
        )
        return key_body.strip()

    @staticmethod
    def add_pem_headers(private_key_body: str) -> str:
        """Add PEM headers to a private key body.

        :param str private_key_body: Private key body without PEM headers
        :return str: PEM formatted string representation of the private key with headers
        """
        return f"-----BEGIN PRIVATE KEY-----\n{private_key_body}\n-----END PRIVATE KEY-----\n"

    @staticmethod
    def encrypt_with_aes(aes_key: bytes, iv: bytes, msg: bytes) -> bytes:
        """Encrypt a message using AES encryption in CFB mode.

        :param bytes aes_key: AES key for encryption
        :param bytes iv: Initialization vector for encryption
        :param bytes msg: Message to encrypt
        :return bytes: Encrypted message
        """
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(msg) + encryptor.finalize()

    @staticmethod
    def decrypt_with_aes(aes_key: bytes, iv: bytes, encrypted_msg: bytes) -> str:
        """Decrypt a message using AES decryption in CFB mode.

        :param bytes aes_key: AES key for decryption
        :param bytes iv: Initialization vector for decryption
        :param bytes encrypted_msg: Encrypted message to decrypt
        :return str: Decrypted message
        """
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_msg = decryptor.update(encrypted_msg) + decryptor.finalize()
        return decrypted_msg.decode("utf-8")

    @staticmethod
    def encrypt_with_rsa(public_key: RSAPublicKey, msg: bytes) -> bytes:
        """Encrypt a message using RSA public key encryption.

        :param RSAPublicKey public_key: RSA public key for encryption
        :param bytes msg: Message to encrypt
        :return bytes: Encrypted message
        """
        return public_key.encrypt(
            msg, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

    @staticmethod
    def decrypt_with_rsa(private_key: RSAPrivateKey, encrypted_msg: bytes) -> bytes:
        """Decrypt a message using RSA private key decryption.

        :param RSAPrivateKey private_key: RSA private key for decryption
        :param bytes encrypted_msg: Encrypted message to decrypt
        :return bytes: Decrypted message
        """
        return private_key.decrypt(
            encrypted_msg,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
        )

    @staticmethod
    def encrypt(aes_key: bytes, iv: bytes, public_key: RSAPublicKey, msg: str) -> tuple[bytes, bytes]:
        """Encrypt a message using AES encryption and RSA public key encryption.

        :param bytes aes_key: AES key for encryption
        :param bytes iv: Initialization vector for encryption
        :param RSAPublicKey public_key: RSA public key for encrypting the AES key
        :param str msg: Message to encrypt
        :return tuple[bytes, bytes]: Encrypted data and encrypted AES key
        """
        encrypted_msg = EncryptionHandler.encrypt_with_aes(aes_key, iv, bytes(msg, "utf-8"))
        encrypted_aes_key = EncryptionHandler.encrypt_with_rsa(public_key, aes_key)
        encrypted_data = iv + encrypted_msg
        return encrypted_data, encrypted_aes_key

    @staticmethod
    def decrypt(msg: bytes, encrypted_aes_key: bytes, private_key: RSAPrivateKey) -> str:
        """Decrypt a message using AES decryption and RSA private key decryption.

        :param bytes msg: Encrypted message containing the IV and encrypted data
        :param bytes encrypted_aes_key: Encrypted AES key for decryption
        :param RSAPrivateKey private_key: RSA private key for decrypting the AES key
        :return str: Decrypted message
        """
        extracted_iv = msg[:16]
        extracted_encrypted_msg = msg[16:]
        decrypted_aes_key = EncryptionHandler.decrypt_with_rsa(private_key, encrypted_aes_key)
        return EncryptionHandler.decrypt_with_aes(decrypted_aes_key, extracted_iv, extracted_encrypted_msg)
