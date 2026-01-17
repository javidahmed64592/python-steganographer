"""Unit tests for the python_steganographer.image module."""

from python_steganographer.image import Image
from python_steganographer.models import SteganographerServerConfig

MOCK_MSG = "Test"


class TestImage:
    """Unit tests for the Image class."""

    def test_encode_and_decode_channel(self, mock_image_instance_lsb: Image, mock_image_instance_dct: Image) -> None:
        """Test encoding and decoding a message in an image channel."""
        for image_instance in [mock_image_instance_lsb, mock_image_instance_dct]:
            for channel in [0, 1, 2]:
                image_instance.encode_channel(channel=channel, msg=MOCK_MSG)
                assert image_instance.decode_channel(channel=channel) == MOCK_MSG

    def test_encode_and_decode(
        self,
        mock_image_instance_lsb: Image,
        mock_image_instance_dct: Image,
        mock_steganographer_server_config: SteganographerServerConfig,
    ) -> None:
        """Test encoding and decoding a message in an image."""
        for image_instance in [mock_image_instance_lsb, mock_image_instance_dct]:
            image_instance.encode(
                msg=MOCK_MSG,
                private_key_size=mock_steganographer_server_config.steganography.private_key_size,
                iv_size=mock_steganographer_server_config.steganography.iv_size,
                aes_key_size=mock_steganographer_server_config.steganography.aes_key_size,
            )
            assert image_instance.decode(iv_size=mock_steganographer_server_config.steganography.iv_size) == MOCK_MSG

    def test_get_capacity(self, mock_image_instance_lsb: Image, mock_image_instance_dct: Image) -> None:
        """Test calculating the steganography capacity of an image."""
        for image_instance in [mock_image_instance_lsb, mock_image_instance_dct]:
            capacity = image_instance.get_capacity()
            assert isinstance(capacity, int)
            assert capacity > 0
