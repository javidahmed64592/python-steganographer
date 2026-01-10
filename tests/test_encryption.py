"""Unit tests for the python_steganographer.encryption module."""

import os
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

from python_steganographer.encryption import EncryptionHandler

MOCK_MSG = b"Test message for encryption"
mock_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
mock_iv = os.urandom(16)
mock_aes = os.urandom(32)


@pytest.fixture
def mock_generate_private_key() -> Generator[MagicMock]:
    """Fixture to mock the generation of RSA private keys."""
    with patch("cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key") as mock:
        mock.return_value = mock_private_key
        yield mock


@pytest.fixture
def mock_os_urandom() -> Generator[MagicMock]:
    """Fixture to mock os.urandom calls for generating IV and AES key."""
    with patch("os.urandom") as mock:
        mock.side_effect = [mock_iv, mock_aes]
        yield mock


@pytest.fixture
def mock_encryption_handler(mock_os_urandom: MagicMock, mock_generate_private_key: MagicMock) -> EncryptionHandler:
    """Fixture to provide an EncryptionHandler instance with mocked keys."""
    return EncryptionHandler()


class TestEncryptionHandler:
    """Unit tests for the encryption methods."""

    def test_initialization(self, mock_encryption_handler: EncryptionHandler) -> None:
        """Test initialization of EncryptionHandler with and without provided keys."""
        assert mock_encryption_handler.private_key == mock_private_key
        assert mock_encryption_handler.public_key == mock_private_key.public_key()
        assert mock_encryption_handler.iv == mock_iv
        assert mock_encryption_handler.aes_key == mock_aes

    def test_private_key_to_str_and_str_to_private_key(self, mock_encryption_handler: EncryptionHandler) -> None:
        """Test conversion between RSAPrivateKey and its string representation."""
        private_key_str = mock_encryption_handler.private_key_to_str(mock_encryption_handler.private_key)
        restored_private_key = mock_encryption_handler.str_to_private_key(private_key_str)
        assert mock_encryption_handler.private_key.private_numbers() == restored_private_key.private_numbers()

    def test_strip_and_add_pem_headers(self, mock_encryption_handler: EncryptionHandler) -> None:
        """Test stripping and adding PEM headers to a key string."""
        private_key_str = mock_encryption_handler.private_key_to_str(mock_encryption_handler.private_key)
        stripped_key = mock_encryption_handler.strip_pem_headers(private_key_str)
        restored_key = mock_encryption_handler.add_pem_headers(stripped_key)
        assert private_key_str == restored_key

    def test_encrypt_and_decrypt_with_aes(self, mock_encryption_handler: EncryptionHandler) -> None:
        """Test AES encryption and decryption."""
        encrypted_msg = mock_encryption_handler.encrypt_with_aes(
            mock_encryption_handler.aes_key, mock_encryption_handler.iv, MOCK_MSG
        )
        decrypted_msg = mock_encryption_handler.decrypt_with_aes(
            mock_encryption_handler.aes_key, mock_encryption_handler.iv, encrypted_msg
        )
        assert MOCK_MSG == decrypted_msg.encode("utf-8")

    def test_encrypt_and_decrypt_with_rsa(self, mock_encryption_handler: EncryptionHandler) -> None:
        """Test RSA encryption and decryption."""
        encrypted_msg = mock_encryption_handler.encrypt_with_rsa(mock_encryption_handler.public_key, MOCK_MSG)
        decrypted_msg = mock_encryption_handler.decrypt_with_rsa(mock_encryption_handler.private_key, encrypted_msg)
        assert MOCK_MSG == decrypted_msg

    def test_encrypt_and_decrypt(self, mock_encryption_handler: EncryptionHandler) -> None:
        """Test combined encryption and decryption using AES and RSA."""
        encrypted_data, encrypted_aes_key = mock_encryption_handler.encrypt(
            mock_encryption_handler.aes_key,
            mock_encryption_handler.iv,
            mock_encryption_handler.public_key,
            MOCK_MSG.decode("utf-8"),
        )
        decrypted_msg = mock_encryption_handler.decrypt(
            encrypted_data, encrypted_aes_key, mock_encryption_handler.private_key
        )
        assert MOCK_MSG == decrypted_msg.encode("utf-8")
