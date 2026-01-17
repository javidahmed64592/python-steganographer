"""Unit tests for the python_steganographer.algorithms module."""

import numpy as np
import pytest

from python_steganographer.algorithms import DCTAlgorithm, LSBAlgorithm
from python_steganographer.constants import NUM_BITS
from python_steganographer.models import SteganographerServerConfig


class TestLSBHelperFunctions:
    """Test the LSB helper functions."""

    def test_even_img(self, mock_image_channel: np.ndarray[np.uint8]) -> None:
        """Test the even_img function."""
        result = LSBAlgorithm.even_img(mock_image_channel)
        assert np.all(result % 2 == 0)
        assert result.shape == mock_image_channel.shape
        assert result.dtype == mock_image_channel.dtype

    def test_insert_msg_basic(self, mock_image_channel: np.ndarray[np.uint8]) -> None:
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

    def test_roundtrip_message(self, mock_image_channel: np.ndarray[np.uint8]) -> None:
        """Test that a message can be inserted and extracted correctly."""
        original_msg = "Hello!"
        flattened = mock_image_channel.flatten()

        # Insert message
        modified = LSBAlgorithm.insert_msg(flattened, original_msg)

        # Extract message
        extracted = LSBAlgorithm.extract_msg(modified)

        # Should be able to find the original message
        assert original_msg in extracted


class TestLSBAlgorithm:
    """Test the LSBAlgorithm class."""

    def test_embed_data(self, lsb_algorithm: LSBAlgorithm, mock_image_channel: np.ndarray[np.uint8]) -> None:
        """Test basic data embedding."""
        test_message = "Test"

        result = lsb_algorithm.embed_data(mock_image_channel, test_message)

        assert isinstance(result, np.ndarray)
        assert result.shape == mock_image_channel.shape
        assert result.dtype == mock_image_channel.dtype

    def test_embed_data_message_too_large(
        self, lsb_algorithm: LSBAlgorithm, mock_image_channel: np.ndarray[np.uint8]
    ) -> None:
        """Test that embedding fails when message is too large."""
        large_message = "A" * 1000

        with pytest.raises(ValueError, match="Message too large for image"):
            lsb_algorithm.embed_data(mock_image_channel, large_message)

    def test_extract_data(self, lsb_algorithm: LSBAlgorithm, mock_image_channel: np.ndarray[np.uint8]) -> None:
        """Test basic data extraction."""
        result = lsb_algorithm.extract_data(mock_image_channel)

        assert isinstance(result, str)

    def test_embed_extract_roundtrip(
        self, lsb_algorithm: LSBAlgorithm, mock_image_channel: np.ndarray[np.uint8]
    ) -> None:
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


class TestDCTHelperFunctions:
    """Test the DCT helper functions."""

    def test_apply_dct_2d_basic(self) -> None:
        """Test basic 2D DCT application."""
        # Create a simple 8x8 block
        block = np.full((8, 8), 128, dtype=np.float64)

        # Apply DCT
        dct_result = DCTAlgorithm.apply_dct_2d(block)

        # Should return same shape
        assert dct_result.shape == (8, 8)

        # For a constant block, only DC component should be non-zero
        assert dct_result[0, 0] != 0  # DC component

        # Other components should be very small (near zero)
        assert np.allclose(dct_result[1:, :], 0, atol=1e-10)
        assert np.allclose(dct_result[0, 1:], 0, atol=1e-10)

    def test_apply_idct_2d_basic(self) -> None:
        """Test basic 2D inverse DCT application."""
        # Create DCT coefficients with only DC component
        dct_block = np.zeros((8, 8), dtype=np.float64)
        dct_block[0, 0] = 1024.0  # DC value for constant 128

        # Apply inverse DCT
        result = DCTAlgorithm.apply_idct_2d(dct_block)

        # Should return same shape
        assert result.shape == (8, 8)

        # Should reconstruct to approximately constant value
        expected = np.full((8, 8), 128.0)
        assert np.allclose(result, expected, atol=1e-10)

    def test_dct_idct_roundtrip(self) -> None:
        """Test that DCT followed by IDCT reconstructs the original."""
        # Create a random 8x8 block
        rng = np.random.default_rng(42)
        original_block = rng.random((8, 8)).astype(np.float64) * 255

        # Apply DCT then IDCT
        dct_result = DCTAlgorithm.apply_dct_2d(original_block)
        reconstructed = DCTAlgorithm.apply_idct_2d(dct_result)

        # Should be very close to original
        assert np.allclose(original_block, reconstructed, atol=1e-10)

    def test_split_into_blocks_exact_division(self) -> None:
        """Test splitting when image size is exactly divisible by block size."""
        # Create 16x16 image (2x2 blocks of 8x8)
        image = np.arange(256, dtype=np.uint8).reshape(16, 16)
        blocks = DCTAlgorithm.split_into_blocks(image, block_size=8)

        # Should have 4 blocks (2x2)
        assert len(blocks) == 4  # noqa: PLR2004

        # Each block should be 8x8
        for block in blocks:
            assert block.shape == (8, 8)
            assert block.dtype == np.float64

    def test_split_into_blocks_non_exact_division(self) -> None:
        """Test splitting when image size is not exactly divisible."""
        # Create 15x15 image (should only get 1 8x8 block)
        image = np.arange(225, dtype=np.uint8).reshape(15, 15)

        blocks = DCTAlgorithm.split_into_blocks(image, block_size=8)

        # Should have 1 block (only complete 8x8 fits)
        assert len(blocks) == 1
        assert blocks[0].shape == (8, 8)

    def test_reconstruct_from_blocks_exact(self) -> None:
        """Test reconstruction when blocks fit exactly."""
        # Create original image
        original = np.arange(64, dtype=np.uint8).reshape(8, 8)

        # Split and reconstruct
        blocks = DCTAlgorithm.split_into_blocks(original, block_size=8)
        reconstructed = DCTAlgorithm.reconstruct_from_blocks(blocks, original.shape, block_size=8)

        # Should be identical to original
        np.testing.assert_array_equal(reconstructed, original)

    def test_reconstruct_from_blocks_clipping(self) -> None:
        """Test that reconstruction clips values to valid range."""
        # Create blocks with out-of-range values
        max_val = 255
        delta = 55
        blocks = [
            np.full((8, 8), max_val + delta, dtype=np.float64),  # Above 255
            np.full((8, 8), -delta, dtype=np.float64),  # Below 0
        ]

        reconstructed = DCTAlgorithm.reconstruct_from_blocks(blocks, (8, 16), block_size=8)

        # Values should be clipped to [0, 255]
        assert np.all(reconstructed >= 0)
        assert np.all(reconstructed <= max_val)
        assert reconstructed.dtype == np.uint8

    @pytest.mark.parametrize(
        ("coeff", "expected"),
        [
            (10.5, 0),
            (15.3, 20),
            (20.7, 20),
            (25.1, 20),
        ],
    )
    def test_embed_bit_in_dct_coefficient_bit(self, coeff: float, expected: int) -> None:
        """Test embedding bit in DCT coefficient."""
        quantization = 10
        assert DCTAlgorithm.embed_bit_in_dct_coefficient(coeff, 0, quantization) == expected

    @pytest.mark.parametrize(
        ("coeff", "expected"),
        [
            (10.5, 1),  # Quantizes to 1, which is odd
            (15.3, 0),  # Quantizes to 2, which is even
            (20.7, 0),  # Quantizes to 2, which is even
            (25.1, 1),  # Quantizes to 3, which is odd
        ],
    )
    def test_extract_bit_from_dct_coefficient(self, coeff: float, expected: int) -> None:
        """Test extracting bit from quantized coefficient."""
        result = DCTAlgorithm.extract_bit_from_dct_coefficient(coeff, 10)
        assert result == expected

    def test_embedding_extraction_roundtrip(self) -> None:
        """Test that embedding and extraction work together."""
        test_coeff = 17.3
        quantization = 10

        # Test both bits
        for bit in [0, 1]:
            embedded = DCTAlgorithm.embed_bit_in_dct_coefficient(test_coeff, bit, quantization)
            extracted = DCTAlgorithm.extract_bit_from_dct_coefficient(embedded, quantization)
            assert extracted == bit


class TestDCTAlgorithm:
    """Test the DCTAlgorithm class."""

    def test_initialization_invalid_block_size(
        self, mock_steganographer_server_config: SteganographerServerConfig
    ) -> None:
        """Test that invalid block size raises ValueError."""
        # Block size must be positive power of 2
        with pytest.raises(ValueError, match="block_size must be a positive power of 2"):
            DCTAlgorithm(
                block_size=0,
                dct_coefficient=mock_steganographer_server_config.steganography.dct_coefficient,
                quantization_factor=mock_steganographer_server_config.steganography.dct_quantization_factor,
            )

        with pytest.raises(ValueError, match="block_size must be a positive power of 2"):
            DCTAlgorithm(
                block_size=7,
                dct_coefficient=mock_steganographer_server_config.steganography.dct_coefficient,
                quantization_factor=mock_steganographer_server_config.steganography.dct_quantization_factor,
            )  # Not power of 2

        with pytest.raises(ValueError, match="block_size must be a positive power of 2"):
            DCTAlgorithm(
                block_size=-8,
                dct_coefficient=mock_steganographer_server_config.steganography.dct_coefficient,
                quantization_factor=mock_steganographer_server_config.steganography.dct_quantization_factor,
            )

    def test_initialization_invalid_dct_coefficient(
        self, mock_steganographer_server_config: SteganographerServerConfig
    ) -> None:
        """Test that invalid DCT coefficient raises ValueError."""
        # DCT coefficient must be in valid range
        with pytest.raises(ValueError, match="dct_coefficient must be between"):
            DCTAlgorithm(
                dct_coefficient=0,
                block_size=mock_steganographer_server_config.steganography.dct_block_size,
                quantization_factor=mock_steganographer_server_config.steganography.dct_quantization_factor,
            )  # Too low

        with pytest.raises(ValueError, match="dct_coefficient must be between"):
            DCTAlgorithm(
                dct_coefficient=64,
                block_size=mock_steganographer_server_config.steganography.dct_block_size,
                quantization_factor=mock_steganographer_server_config.steganography.dct_quantization_factor,
            )  # Too high for 8x8 blocks

    def test_initialization_invalid_quantization_factor(
        self, mock_steganographer_server_config: SteganographerServerConfig
    ) -> None:
        """Test that invalid quantization factor raises ValueError."""
        with pytest.raises(ValueError, match="quantization_factor must be positive"):
            DCTAlgorithm(
                quantization_factor=0,
                block_size=mock_steganographer_server_config.steganography.dct_block_size,
                dct_coefficient=mock_steganographer_server_config.steganography.dct_coefficient,
            )

        with pytest.raises(ValueError, match="quantization_factor must be positive"):
            DCTAlgorithm(
                quantization_factor=-5,
                block_size=mock_steganographer_server_config.steganography.dct_block_size,
                dct_coefficient=mock_steganographer_server_config.steganography.dct_coefficient,
            )

    def test_embed_data_basic(self, dct_algorithm: DCTAlgorithm, mock_image_channel: np.ndarray[np.uint8]) -> None:
        """Test basic data embedding."""
        test_message = "Hi"

        # Embed message
        modified_channel = dct_algorithm.embed_data(mock_image_channel, test_message)

        # Should return same shape and dtype
        assert modified_channel.shape == mock_image_channel.shape
        assert modified_channel.dtype == mock_image_channel.dtype

        # Should be different from original (unless extremely unlikely)
        assert not np.array_equal(modified_channel, mock_image_channel)

    def test_embed_data_empty_message(
        self, dct_algorithm: DCTAlgorithm, mock_image_channel: np.ndarray[np.uint8]
    ) -> None:
        """Test embedding empty message."""
        # Should work without error
        modified_channel = dct_algorithm.embed_data(mock_image_channel, "")

        # Should return same shape
        assert modified_channel.shape == mock_image_channel.shape

    def test_embed_data_message_too_large(
        self, dct_algorithm: DCTAlgorithm, mock_image_channel: np.ndarray[np.uint8]
    ) -> None:
        """Test that embedding too large message raises error."""
        large_message = "A" * 1000

        with pytest.raises(ValueError, match="Message too large for image"):
            dct_algorithm.embed_data(mock_image_channel, large_message)

    def test_extract_data_basic(self, dct_algorithm: DCTAlgorithm, mock_image_channel: np.ndarray[np.uint8]) -> None:
        """Test basic data extraction."""
        # Should be able to extract from any channel without error
        result = dct_algorithm.extract_data(mock_image_channel)

        # Should return a string
        assert isinstance(result, str)

    @pytest.mark.parametrize(
        "message",
        [
            "Hello",
            "123",
            "!@#$% ",
            "A",
        ],
    )
    def test_embed_extract_roundtrip(
        self, dct_algorithm: DCTAlgorithm, mock_image_channel: np.ndarray[np.uint8], message: str
    ) -> None:
        """Test roundtrip with various message types."""
        modified_channel = dct_algorithm.embed_data(mock_image_channel, message)
        extracted = dct_algorithm.extract_data(modified_channel)
        assert message in extracted

    def test_embed_extract_roundtrip_non_square_image(self, dct_algorithm: DCTAlgorithm) -> None:
        """Test with non-square image."""
        # Create rectangular image
        rect_image = np.full((32, 64), 128, dtype=np.uint8)
        message = "Hi"  # Shorter message to fit in 32 blocks (4 chars + null = 35 bits > 32)

        # Should work fine
        modified = dct_algorithm.embed_data(rect_image, message)
        extracted = dct_algorithm.extract_data(modified)
        assert message in extracted

    @pytest.mark.parametrize(
        ("shape", "expected_capacity"),
        [
            ((16, 16), max(0, (16 // 8) * (16 // 8) - 7) // 7),  # (4-7)//7 = 0
            ((32, 32), max(0, (32 // 8) * (32 // 8) - 7) // 7),  # (16-7)//7 = 1
            ((128, 128), max(0, (128 // 8) * (128 // 8) - 7) // 7),  # (256-7)//7 = 35
        ],
    )
    def test_calculate_capacity(
        self, dct_algorithm: DCTAlgorithm, shape: tuple[int, int], expected_capacity: int
    ) -> None:
        """Test capacity calculation for different image sizes."""
        capacity = dct_algorithm.calculate_capacity(shape)
        assert capacity == expected_capacity

    def test_calculate_capacity_invalid_dimensions(self, dct_algorithm: DCTAlgorithm) -> None:
        """Test that invalid dimensions raise ValueError."""
        with pytest.raises(ValueError, match="DCT algorithm requires 2D channel shape"):
            dct_algorithm.calculate_capacity((64,))  # 1D

        with pytest.raises(ValueError, match="DCT algorithm requires 2D channel shape"):
            dct_algorithm.calculate_capacity((64, 64, 3))  # 3D
