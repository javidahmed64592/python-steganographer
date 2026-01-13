"""Unit tests for the python_steganographer.image module."""

from python_steganographer.image import Image

MOCK_MSG = "Test"


class TestImage:
    """Unit tests for the Image class."""

    def test_encode_and_decode_channel(self, mock_image_instance_lsb: Image, mock_image_instance_dct: Image) -> None:
        """Test encoding and decoding a message in an image channel."""
        for image_instance in [mock_image_instance_lsb, mock_image_instance_dct]:
            for channel in [0, 1, 2]:
                image_instance.encode_channel(channel=channel, msg=MOCK_MSG)
                assert image_instance.decode_channel(channel=channel) == MOCK_MSG

    def test_encode_and_decode(self, mock_image_instance_lsb: Image, mock_image_instance_dct: Image) -> None:
        """Test encoding and decoding a message in an image."""
        for image_instance in [mock_image_instance_lsb, mock_image_instance_dct]:
            image_instance.encode(msg=MOCK_MSG)
            assert image_instance.decode() == MOCK_MSG
