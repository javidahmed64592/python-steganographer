"""Pytest fixtures for the application's unit tests."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from python_steganographer.algorithms import DCTAlgorithm, LSBAlgorithm
from python_steganographer.image import Image
from python_steganographer.models import SteganographerServerConfig, SteganographyConfig

rng = np.random.default_rng(42)


# Steganographer Server Configuration Models
@pytest.fixture
def mock_steganography_config() -> SteganographyConfig:
    """Provide a mock SteganographyConfig instance."""
    return SteganographyConfig(private_key_size=1024, iv_size=16, aes_key_size=32)


@pytest.fixture
def mock_steganographer_server_config(mock_steganography_config: SteganographyConfig) -> SteganographerServerConfig:
    """Provide a mock SteganographerServerConfig instance."""
    return SteganographerServerConfig(steganography=mock_steganography_config)


# Algorithm fixtures
@pytest.fixture
def lsb_algorithm() -> LSBAlgorithm:
    """Create LSB algorithm instance."""
    return LSBAlgorithm()


@pytest.fixture
def dct_algorithm() -> DCTAlgorithm:
    """Create DCT algorithm instance."""
    return DCTAlgorithm()


# Image fixtures
@pytest.fixture
def mock_image() -> np.ndarray[np.uint8]:
    """Create a sample 64x64x3 image for testing."""
    return rng.integers(0, 256, size=(64, 64, 3), dtype=np.uint8)


@pytest.fixture
def mock_big_image() -> np.ndarray[np.uint8]:
    """Create a sample 640x640x3 image for testing."""
    return rng.integers(0, 256, size=(640, 640, 3), dtype=np.uint8)


@pytest.fixture
def mock_image_channel(mock_image: np.ndarray[np.uint8]) -> np.ndarray[np.uint8]:
    """Create a sample 64x64 image channel for testing."""
    return mock_image[:, :, 0]


@pytest.fixture
def mock_load_image(mock_big_image: np.ndarray[np.uint8]) -> Generator[MagicMock]:
    """Fixture to mock image loading from file."""
    with patch("python_steganographer.image.skimage.io.imread", return_value=mock_big_image) as mock_imread:
        yield mock_imread


@pytest.fixture
def mock_image_instance_lsb(mock_load_image: MagicMock) -> Image:
    """Create an Image instance with LSB algorithm."""
    mock_image_instance = Image.lsb()
    mock_image_instance.load_image(image_bytes=b"dummy_bytes")
    return mock_image_instance


@pytest.fixture
def mock_image_instance_dct(mock_load_image: MagicMock) -> Image:
    """Create an Image instance with DCT algorithm."""
    mock_image_instance = Image.dct(block_size=8, dct_coefficient=3, quantization_factor=10)
    mock_image_instance.load_image(image_bytes=b"dummy_bytes")
    return mock_image_instance
