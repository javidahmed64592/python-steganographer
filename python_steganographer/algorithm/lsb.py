"""Classes for steganography algorithms."""

import numpy as np
from numpy.typing import NDArray

from python_steganographer.algorithm import AlgorithmBase
from python_steganographer.constants import NUM_BITS
from python_steganographer.helpers import bytes_list_to_msg, msg_to_bytes_list


class LSBAlgorithm(AlgorithmBase):
    """LSB (Least Significant Bit) steganography algorithm.

    This algorithm hides data by modifying the least significant bit of each
    pixel in the image. It provides good capacity but may be detectable by
    statistical analysis.
    """

    def embed_data(self, channel: NDArray[np.uint8], data: str) -> NDArray[np.uint8]:
        """Embed data into image channel using LSB steganography.

        :param NDArray[np.uint8] channel: Image channel to embed data into
        :param str data: Data to embed
        :return NDArray[np.uint8]: Modified channel with embedded data
        """
        super().embed_data(channel, data)

        # Flatten the channel for processing
        original_shape = channel.shape
        flattened = channel.flatten()

        # Insert message using LSB
        modified_flattened = self.insert_msg(flattened, data)

        # Reshape back to original dimensions
        return modified_flattened.reshape(original_shape)

    def extract_data(self, channel: NDArray[np.uint8]) -> str:
        """Extract data from image channel using LSB steganography.

        :param NDArray[np.uint8] channel: Image channel to extract data from
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
    def even_img(img: NDArray[np.uint8]) -> NDArray[np.uint8]:
        """Round down all values in image array to be even numbers.

        This is LSB-specific: we need even values so that adding 1 (for bit '1')
        or 0 (for bit '0') will set the LSB correctly.

        :param NDArray[np.uint8] img: Array of pixel values
        :return NDArray[np.uint8]: Array of even pixel values with same shape as `img`
        """
        # Cast to int to perform operations, then back to uint8
        img_int = img.astype(np.int32)
        return np.array(img_int - (img_int % 2), dtype=np.uint8)

    @staticmethod
    def insert_msg(flattened_img: NDArray[np.uint8], msg: str) -> NDArray[np.uint8]:
        """Insert a message into image using LSB steganography.

        This function modifies the least significant bit of each pixel to store
        message bits. The image must be flattened first.

        :param NDArray[np.uint8] flattened_img: Flattened image array
        :param str msg: Message to insert into image
        :return NDArray[np.uint8]: Flattened image array with message embedded in LSB
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
    def extract_msg(flattened_img: NDArray[np.uint8]) -> str:
        """Extract a message from an image using LSB steganography.

        This function reads the least significant bit of each pixel to reconstruct
        the hidden message.

        :param NDArray[np.uint8] flattened_img: Flattened image array with embedded message
        :return str: Extracted message from image LSBs
        """
        # Extract LSBs (remainder when divided by 2)
        msg_bytes_array: NDArray[np.uint8] = flattened_img % 2
        msg_bytes = msg_bytes_array.tolist()

        # Convert bits back to message
        return bytes_list_to_msg(msg_bytes)
