"""Classes for steganography algorithms."""

from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray


class AlgorithmBase(ABC):
    """Abstract base class for steganography algorithms."""

    @abstractmethod
    def embed_data(self, channel: NDArray[np.uint8], data: str) -> NDArray[np.uint8]:
        """Embed data into image channel.

        :param NDArray[np.uint8] channel: Image channel to embed data into
        :param str data: Data to embed
        :return NDArray[np.uint8]: Modified channel with embedded data
        """
        # Check capacity
        max_capacity = self.calculate_capacity(channel.shape)
        if len(data) > max_capacity:
            msg = (
                f"Message too large for image. Message length: {len(data)}, Maximum capacity: {max_capacity} characters"
            )
            raise ValueError(msg)

        return channel

    @abstractmethod
    def extract_data(self, channel: NDArray[np.uint8]) -> str:
        """Extract data from image channel.

        :param NDArray[np.uint8] channel: Image channel to extract data from
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
