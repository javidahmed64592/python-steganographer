"""Classes for steganography algorithms."""

from abc import ABC, abstractmethod

import numpy as np
from scipy.fft import dct, idct

from python_steganographer.constants import (
    NUM_BITS,
)
from python_steganographer.helpers import bytes_list_to_msg, msg_to_bytes_list


class AlgorithmBase(ABC):
    """Abstract base class for steganography algorithms."""

    @abstractmethod
    def embed_data(self, channel: np.ndarray[np.uint8], data: str) -> np.ndarray[np.uint8]:
        """Embed data into image channel.

        :param np.ndarray[np.uint8] channel: Image channel to embed data into
        :param str data: Data to embed
        :return np.ndarray[np.uint8]: Modified channel with embedded data
        """
        # Check capacity
        max_capacity = self.calculate_capacity(channel.shape)
        if len(data) > max_capacity:
            msg = (
                f"Message too large for image. Message length: {len(data)}, Maximum capacity: {max_capacity} characters"
            )
            raise ValueError(msg)

    @abstractmethod
    def extract_data(self, channel: np.ndarray[np.uint8]) -> str:
        """Extract data from image channel.

        :param np.ndarray[np.uint8] channel: Image channel to extract data from
        :return str: Extracted data
        """
        pass

    @abstractmethod
    def calculate_capacity(self, channel_shape: tuple[int, ...]) -> int:
        """Calculate data capacity for this channel.

        :param tuple[int, ...] channel_shape: Shape of the image channel
        :return int: Maximum number of characters that can be embedded
        """
        pass


class LSBAlgorithm(AlgorithmBase):
    """LSB (Least Significant Bit) steganography algorithm.

    This algorithm hides data by modifying the least significant bit of each
    pixel in the image. It provides good capacity but may be detectable by
    statistical analysis.
    """

    def embed_data(self, channel: np.ndarray[np.uint8], data: str) -> np.ndarray[np.uint8]:
        """Embed data into image channel using LSB steganography.

        :param np.ndarray[np.uint8] channel: Image channel to embed data into
        :param str data: Data to embed
        :return np.ndarray[np.uint8]: Modified channel with embedded data
        """
        super().embed_data(channel, data)

        # Flatten the channel for processing
        original_shape = channel.shape
        flattened = channel.flatten()

        # Insert message using LSB
        modified_flattened = self.insert_msg(flattened, data)

        # Reshape back to original dimensions
        return modified_flattened.reshape(original_shape)

    def extract_data(self, channel: np.ndarray[np.uint8]) -> str:
        """Extract data from image channel using LSB steganography.

        :param np.ndarray[np.uint8] channel: Image channel to extract data from
        :return str: Extracted data
        """
        # Flatten the channel for processing
        flattened = channel.flatten()

        # Extract message using LSB
        return self.extract_msg(flattened)

    def calculate_capacity(self, channel_shape: tuple[int, ...]) -> int:
        """Calculate data capacity for this channel using LSB.

        :param tuple[int, ...] channel_shape: Shape of the image channel
        :return int: Maximum number of characters that can be embedded
        """
        total_pixels = np.prod(channel_shape)
        return int(total_pixels // NUM_BITS)

    @staticmethod
    def even_img(img: np.ndarray[np.uint8]) -> np.ndarray[np.uint8]:
        """Round down all values in image array to be even numbers.

        This is LSB-specific: we need even values so that adding 1 (for bit '1')
        or 0 (for bit '0') will set the LSB correctly.

        :param np.ndarray[np.uint8] img: Array of pixel values
        :return np.ndarray[np.uint8]: Array of even pixel values with same shape as `img`
        """
        return np.array(img - (img % 2), dtype=img.dtype)

    @staticmethod
    def insert_msg(flattened_img: np.ndarray[np.uint8], msg: str) -> np.ndarray[np.uint8]:
        """Insert a message into image using LSB steganography.

        This function modifies the least significant bit of each pixel to store
        message bits. The image must be flattened first.

        :param np.ndarray[np.uint8] flattened_img: Flattened image array
        :param str msg: Message to insert into image
        :return np.ndarray[np.uint8]: Flattened image array with message embedded in LSB
        """
        # Make all pixel values even (LSB = 0)
        flattened_img = LSBAlgorithm.even_img(flattened_img)

        # Convert message to bits
        msg_bytes = np.array(msg_to_bytes_list(msg), dtype=np.uint8)

        # Check if message fits
        if len(msg_bytes) > len(flattened_img):
            msg = f"Message too large for image. Need {len(msg_bytes)} pixels, have {len(flattened_img)}"
            raise ValueError(msg)

        # Add message bits to LSB of pixels
        flattened_img[: len(msg_bytes)] += msg_bytes

        return flattened_img

    @staticmethod
    def extract_msg(flattened_img: np.ndarray[np.uint8]) -> str:
        """Extract a message from an image using LSB steganography.

        This function reads the least significant bit of each pixel to reconstruct
        the hidden message.

        :param np.ndarray[np.uint8] flattened_img: Flattened image array with embedded message
        :return str: Extracted message from image LSBs
        """
        # Extract LSBs (remainder when divided by 2)
        msg_bytes = (flattened_img % 2).tolist()

        # Convert bits back to message
        return bytes_list_to_msg(msg_bytes)


class DCTAlgorithm(AlgorithmBase):
    """DCT (Discrete Cosine Transform) steganography algorithm.

    This algorithm hides data by modifying DCT coefficients in image blocks.
    It provides better resistance to compression and some image processing
    operations compared to LSB methods.
    """

    def __init__(
        self,
        block_size: int,
        dct_coefficient: int,
        quantization_factor: int,
    ) -> None:
        """Initialize DCT algorithm.

        :param int block_size: Size of DCT blocks (typically 8x8)
        :param int dct_coefficient: Which DCT coefficient to modify (1-based indexing, avoid DC component)
        :param int quantization_factor: Quantization factor for embedding
        """
        if block_size <= 0 or (block_size & (block_size - 1)) != 0:
            msg = "block_size must be a positive power of 2"
            raise ValueError(msg)

        if not 1 <= dct_coefficient < block_size * block_size:
            msg = f"dct_coefficient must be between 1 and {block_size * block_size - 1}"
            raise ValueError(msg)

        if quantization_factor <= 0:
            msg = "quantization_factor must be positive"
            raise ValueError(msg)

        self.block_size = block_size
        self.dct_coefficient = dct_coefficient
        self.quantization_factor = quantization_factor

    def embed_data(self, channel: np.ndarray[np.uint8], data: str) -> np.ndarray[np.uint8]:
        """Embed data into image channel using DCT steganography.

        :param np.ndarray[np.uint8] channel: Image channel to embed data into
        :param str data: Data to embed
        :return np.ndarray[np.uint8]: Modified channel with embedded data
        """
        super().embed_data(channel, data)

        # Convert message to bits and add termination marker
        msg_bits = msg_to_bytes_list(data + "\0")  # Add null terminator

        # Split image into blocks
        blocks = DCTAlgorithm.split_into_blocks(channel, self.block_size)

        # Process each block
        modified_blocks = []
        for i, block in enumerate(blocks):
            # Apply DCT
            dct_block = DCTAlgorithm.apply_dct_2d(block)

            # Embed bit if we have more bits to embed
            if i < len(msg_bits):
                coeff_pos = DCTAlgorithm.get_dct_coefficient_position(self.dct_coefficient, self.block_size)
                coeff_row, coeff_col = coeff_pos

                # Embed bit in the specified coefficient
                original_coeff = dct_block[coeff_row, coeff_col]
                modified_coeff = DCTAlgorithm.embed_bit_in_dct_coefficient(
                    original_coeff, msg_bits[i], self.quantization_factor
                )
                dct_block[coeff_row, coeff_col] = modified_coeff

            # Apply inverse DCT
            reconstructed_block = DCTAlgorithm.apply_idct_2d(dct_block)
            modified_blocks.append(reconstructed_block)

        # Reconstruct the image
        return DCTAlgorithm.reconstruct_from_blocks(modified_blocks, channel.shape, self.block_size)

    def extract_data(self, channel: np.ndarray[np.uint8]) -> str:
        """Extract data from image channel using DCT steganography.

        :param np.ndarray[np.uint8] channel: Image channel to extract data from
        :return str: Extracted data
        """
        # Split image into blocks
        blocks = DCTAlgorithm.split_into_blocks(channel, self.block_size)

        # Extract bits from each block
        extracted_bits = []
        for block in blocks:
            # Apply DCT
            dct_block = DCTAlgorithm.apply_dct_2d(block)

            # Extract bit from the specified coefficient
            coeff_pos = DCTAlgorithm.get_dct_coefficient_position(self.dct_coefficient, self.block_size)
            coeff_row, coeff_col = coeff_pos
            coeff_value = dct_block[coeff_row, coeff_col]

            bit = DCTAlgorithm.extract_bit_from_dct_coefficient(coeff_value, self.quantization_factor)
            extracted_bits.append(bit)

        # Convert bits back to message
        return bytes_list_to_msg(extracted_bits)

    def calculate_capacity(self, channel_shape: tuple[int, ...]) -> int:
        """Calculate data capacity for this channel using DCT.

        Capacity depends on the number of complete blocks that fit in the image.
        Each block can store 1 bit, so capacity = (num_blocks - null_terminator_bits) / 7 characters.

        :param tuple[int, ...] channel_shape: Shape of the image channel
        :return int: Maximum number of characters that can be embedded
        """
        if len(channel_shape) != 2:  # noqa: PLR2004
            msg = "DCT algorithm requires 2D channel shape"
            raise ValueError(msg)

        h, w = channel_shape
        # Calculate number of complete blocks
        num_blocks_h = h // self.block_size
        num_blocks_w = w // self.block_size
        total_blocks = num_blocks_h * num_blocks_w

        # Reserve space for null terminator (7 bits for '\0')
        available_bits = max(0, total_blocks - NUM_BITS)

        # Each character needs 7 bits
        return available_bits // NUM_BITS

    @staticmethod
    def get_dct_coefficient_position(coeff_index: int, block_size: int) -> tuple[int, int]:
        """Get the (row, col) position for a given DCT coefficient index.

        Uses a simple row-major ordering but skips the DC component at (0,0).
        For a 1-based coefficient index, maps to appropriate 2D coordinates.

        :param int coeff_index: 1-based coefficient index (1 means first AC coefficient)
        :param int block_size: Size of the DCT block
        :return tuple[int, int]: (row, col) position in the DCT block
        """
        if coeff_index < 1:
            msg = "DCT coefficient index must be >= 1 to avoid DC component"
            raise ValueError(msg)

        # Convert to 0-based and add 1 to skip DC component at (0,0)
        linear_index = coeff_index  # This skips (0,0) since we start from 1

        # Simple row-major ordering
        row = linear_index // block_size
        col = linear_index % block_size

        # If we're at the first position (0,0), move to (0,1) to avoid DC
        if row == 0 and col == 0:
            col = 1

        return (row, col)

    @staticmethod
    def apply_dct_2d(block: np.ndarray[np.float64]) -> np.ndarray[np.float64]:
        """Apply 2D DCT to an image block.

        :param np.ndarray[np.float64] block: 8x8 image block to transform
        :return np.ndarray[np.float64]: DCT coefficients
        """
        return dct(dct(block.T, norm="ortho").T, norm="ortho")  # type: ignore[no-any-return]

    @staticmethod
    def apply_idct_2d(dct_block: np.ndarray[np.float64]) -> np.ndarray[np.float64]:
        """Apply 2D inverse DCT to DCT coefficients.

        :param np.ndarray[np.float64] dct_block: DCT coefficients to transform back
        :return np.ndarray[np.float64]: Reconstructed image block
        """
        return idct(idct(dct_block.T, norm="ortho").T, norm="ortho")  # type: ignore[no-any-return]

    @staticmethod
    def split_into_blocks(channel: np.ndarray[np.uint8], block_size: int) -> list[np.ndarray[np.float64]]:
        """Split image channel into blocks for DCT processing.

        :param np.ndarray[np.uint8] channel: Image channel to split
        :param int block_size: Size of blocks (typically 8x8)
        :return list[np.ndarray[np.float64]]: List of image blocks as float arrays
        """
        h, w = channel.shape
        blocks = []

        # Process image in block_size x block_size blocks
        for i in range(0, h - h % block_size, block_size):
            for j in range(0, w - w % block_size, block_size):
                block = channel[i : i + block_size, j : j + block_size].astype(np.float64)
                blocks.append(block)

        return blocks

    @staticmethod
    def reconstruct_from_blocks(
        blocks: list[np.ndarray[np.float64]], original_shape: tuple[int, int], block_size: int
    ) -> np.ndarray[np.uint8]:
        """Reconstruct image channel from processed blocks.

        :param list[np.ndarray[np.float64]] blocks: List of processed image blocks
        :param tuple[int, int] original_shape: Original shape of the image channel
        :param int block_size: Size of blocks used
        :return np.ndarray[np.uint8]: Reconstructed image channel
        """
        h, w = original_shape
        reconstructed = np.zeros((h, w), dtype=np.float64)
        block_idx = 0

        # Reconstruct image from blocks
        for i in range(0, h - h % block_size, block_size):
            for j in range(0, w - w % block_size, block_size):
                if block_idx < len(blocks):
                    reconstructed[i : i + block_size, j : j + block_size] = blocks[block_idx]
                    block_idx += 1

        # Clip values to valid range and convert back to uint8
        reconstructed = np.clip(reconstructed, 0, 255)
        return reconstructed.astype(np.uint8)

    @staticmethod
    def embed_bit_in_dct_coefficient(dct_coeff: float, bit: int, quantization: int) -> float:
        """Embed a bit in a DCT coefficient using quantization.

        :param float dct_coeff: Original DCT coefficient
        :param int bit: Bit to embed (0 or 1)
        :param int quantization: Quantization factor
        :return float: Modified DCT coefficient
        """
        # Quantize the coefficient
        quantized = round(dct_coeff / quantization)

        # Embed bit by making coefficient even (bit=0) or odd (bit=1)
        if bit == 0:
            # Make even
            if quantized % 2 == 1:
                quantized -= 1
        elif bit == 1:
            # Make odd
            if quantized % 2 == 0:
                quantized += 1

        # Scale back
        return quantized * quantization

    @staticmethod
    def extract_bit_from_dct_coefficient(dct_coeff: float, quantization: int) -> int:
        """Extract a bit from a DCT coefficient.

        :param float dct_coeff: DCT coefficient to extract bit from
        :param int quantization: Quantization factor used during embedding
        :return int: Extracted bit (0 or 1)
        """
        # Quantize the coefficient
        quantized = round(dct_coeff / quantization)

        # Extract bit from parity (even=0, odd=1)
        return quantized % 2
