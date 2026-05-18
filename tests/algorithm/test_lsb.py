"""Unit tests for the python_steganographer.algorithm.lsb module."""

import numpy as np
import pytest
from numpy.typing import NDArray

from python_steganographer.algorithm import LSBAlgorithm
from python_steganographer.constants import NUM_BITS


class TestHelperFunctions:
    """Test the LSB helper functions."""

    def test_even_img(self, mock_image_channel: NDArray[np.uint8]) -> None:
        """Test the even_img function."""
        result = LSBAlgorithm.even_img(mock_image_channel)
        assert np.all(result % 2 == 0)
        assert result.shape == mock_image_channel.shape
        assert result.dtype == mock_image_channel.dtype

    def test_insert_msg_basic(self, mock_image_channel: NDArray[np.uint8]) -> None:
        """Test basic message insertion."""
        # Create a simple test image (all even values) and flatten it
        test_img = LSBAlgorithm.even_img(mock_image_channel).flatten()

        # Insert simple message
        message = "A"  # ASCII 65 = 1000001 in binary (7 bits)
        result = LSBAlgorithm.insert_msg(test_img, message)

        # Check that message bits are embedded
        extracted_bits = result % 2
        expected_bits = [1, 0, 0, 0, 0, 0, 1, 0]  # "A" + null terminator start

        assert len(extracted_bits) >= len(expected_bits)
        np.testing.assert_array_equal(extracted_bits[:7], expected_bits[:7])

    def test_insert_msg_capacity_error(self) -> None:
        """Test that insert_msg raises error when message is too large."""
        small_img = np.array([0, 2, 4], dtype=np.uint8)  # Only 3 pixels
        long_message = "This message is way too long"

        with pytest.raises(ValueError, match="Message too large for image"):
            LSBAlgorithm.insert_msg(small_img, long_message)

    def test_extract_msg_basic(self) -> None:
        """Test basic message extraction."""
        # Create image with known LSBs
        test_img = np.array([1, 0, 0, 0, 0, 0, 1, 0], dtype=np.uint8)  # "A" in LSBs

        # Extract should find the message
        result = LSBAlgorithm.extract_msg(test_img)
        assert "A" in result

    def test_roundtrip_message(self, mock_image_channel: NDArray[np.uint8]) -> None:
        """Test that a message can be inserted and extracted correctly."""
        original_msg = "Hello!"
        flattened = mock_image_channel.flatten()

        # Insert message
        modified = LSBAlgorithm.insert_msg(flattened, original_msg)

        # Extract message
        extracted = LSBAlgorithm.extract_msg(modified)

        # Should be able to find the original message
        assert original_msg in extracted


class TestAlgorithm:
    """Test the LSBAlgorithm class."""

    def test_embed_data(self, lsb_algorithm: LSBAlgorithm, mock_image_channel: NDArray[np.uint8]) -> None:
        """Test basic data embedding."""
        test_message = "Test"

        result = lsb_algorithm.embed_data(mock_image_channel, test_message)

        assert isinstance(result, np.ndarray)
        assert result.shape == mock_image_channel.shape
        assert result.dtype == mock_image_channel.dtype

    def test_embed_data_message_too_large(
        self, lsb_algorithm: LSBAlgorithm, mock_image_channel: NDArray[np.uint8]
    ) -> None:
        """Test that embedding fails when message is too large."""
        large_message = "A" * 1000

        with pytest.raises(ValueError, match="Message too large for image"):
            lsb_algorithm.embed_data(mock_image_channel, large_message)

    def test_extract_data(self, lsb_algorithm: LSBAlgorithm, mock_image_channel: NDArray[np.uint8]) -> None:
        """Test basic data extraction."""
        result = lsb_algorithm.extract_data(mock_image_channel)

        assert isinstance(result, str)

    def test_embed_extract_roundtrip(self, lsb_algorithm: LSBAlgorithm, mock_image_channel: NDArray[np.uint8]) -> None:
        """Test complete embed and extract cycle."""
        original_message = "Secret message!"

        # Embed the message
        embedded_channel = lsb_algorithm.embed_data(mock_image_channel, original_message)

        # Extract the message
        extracted_message = lsb_algorithm.extract_data(embedded_channel)

        # The original message should be contained in the extracted message
        assert original_message in extracted_message

    @pytest.mark.parametrize(
        ("shape", "expected_capacity"),
        [
            ((64, 64), (64 * 64) // NUM_BITS),
            ((128, 128), (128 * 128) // NUM_BITS),
            ((10, 20), (10 * 20) // NUM_BITS),
        ],
    )
    def test_calculate_capacity(
        self, lsb_algorithm: LSBAlgorithm, shape: tuple[int, int], expected_capacity: int
    ) -> None:
        """Test capacity calculation."""
        capacity = lsb_algorithm.calculate_capacity(shape)
        assert capacity == expected_capacity
