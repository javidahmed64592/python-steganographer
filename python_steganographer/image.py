"""Image classes for the steganographer application."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import skimage
from numpy.typing import NDArray

from python_steganographer.algorithms import AlgorithmBase, DCTAlgorithm, LSBAlgorithm
from python_steganographer.encryption import EncryptionHandler
from python_steganographer.helpers import bytes_to_str, str_to_bytes


class Image:
    """Image class for steganography operations."""

    def __init__(self, algorithm: AlgorithmBase) -> None:
        """Initialize the Image class."""
        self.algorithm = algorithm
        self.array: NDArray[np.uint8] = np.array([])

    @classmethod
    def lsb(cls, bits_per_pixel: int = 1) -> Image:
        """Initialize the image class with LSB algorithm.

        :param int bits_per_pixel: Number of LSB bits to use per pixel (currently only 1 is supported)
        :return Image: Image instance with LSB algorithm
        """
        return cls(algorithm=LSBAlgorithm(bits_per_pixel=bits_per_pixel))

    @classmethod
    def dct(cls, block_size: int = 8, dct_coefficient: int = 3, quantization_factor: int = 10) -> Image:
        """Initialize the image class with DCT algorithm.

        :param int block_size: Size of DCT blocks (typically 8x8)
        :param int dct_coefficient: Which DCT coefficient to modify (1-based indexing, avoid DC component)
        :param int quantization_factor: Quantization factor for embedding
        :return Image: Image instance with DCT algorithm
        """
        return cls(
            algorithm=DCTAlgorithm(
                block_size=block_size, dct_coefficient=dct_coefficient, quantization_factor=quantization_factor
            )
        )

    def load_image(self, filepath: Path) -> None:
        """Load image from file into array.

        :param Path filepath: Path to the image file to load
        """
        self.array = skimage.io.imread(filepath)

    def save_image(self, filepath: Path) -> None:
        """Save image array to file.

        :param Path filepath: Path to save the image file
        """
        skimage.io.imsave(filepath, self.array)

    def encode_channel(self, channel: int, msg: str) -> None:
        """Insert message into specific channel.

        :param int channel: Channel to insert message into (0, 1, 2 for R, G, B respectively)
        :param str msg: Message to insert
        """
        channel_data = self.array[:, :, channel]
        modified_channel = self.algorithm.embed_data(channel_data, msg)
        self.array[:, :, channel] = modified_channel

    def decode_channel(self, channel: int) -> str:
        """Extract message from specific channel.

        :param int channel: Channel to extract message from (0, 1, 2 for R, G, B respectively)
        :return str: Extracted message
        """
        channel_data = self.array[:, :, channel]
        return self.algorithm.extract_data(channel_data)

    def encode(self, msg: str) -> None:
        """Add encrypted message into image array.

        :param str msg: Message to insert into the image
        """
        encryption_handler = EncryptionHandler()
        encrypted_data, encrypted_aes_key = encryption_handler.encrypt(msg)

        encrypted_data_str = bytes_to_str(encrypted_data)
        encrypted_aes_key_str = bytes_to_str(encrypted_aes_key)
        private_key_str = EncryptionHandler.strip_pem_headers(
            EncryptionHandler.private_key_to_str(encryption_handler.private_key)
        )

        self.encode_channel(0, encrypted_data_str)
        self.encode_channel(1, encrypted_aes_key_str)
        self.encode_channel(2, private_key_str)

    def decode(self) -> str:
        """Extract encrypted message from image array.

        :return str: Extracted message after decryption
        """
        encrypted_data_str = self.decode_channel(0)
        encrypted_aes_key_str = self.decode_channel(1)
        private_key_str = EncryptionHandler.add_pem_headers(self.decode_channel(2))

        private_key = EncryptionHandler.str_to_private_key(private_key_str)
        encrypted_aes_key_bytes = str_to_bytes(encrypted_aes_key_str)
        encrypted_data_bytes = str_to_bytes(encrypted_data_str)

        encryption_handler = EncryptionHandler.from_encrypted(
            private_key=private_key, encrypted_aes_key=encrypted_aes_key_bytes, msg=encrypted_data_bytes
        )

        return encryption_handler.decrypt(encrypted_data_bytes)
