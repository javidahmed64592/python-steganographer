"""Pytest fixtures for the application's unit tests."""

import base64
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from numpy.typing import NDArray
from slowapi import Limiter

from python_steganographer.algorithms import DCTAlgorithm, LSBAlgorithm
from python_steganographer.image import Image
from python_steganographer.models import (
    AlgorithmType,
    EncryptionConfig,
    ImageConfig,
    PostCapacityRequest,
    PostDecodeRequest,
    PostEncodeRequest,
    SteganographerServerConfig,
)
from python_steganographer.routers import ImageRouter
from python_steganographer.server import IMAGE_ROUTER

rng = np.random.default_rng(42)


# Steganographer Server Configuration fixtures
@pytest.fixture
def mock_image_config() -> ImageConfig:
    """Provide a mock ImageConfig instance."""
    return ImageConfig(dct_block_size=8, dct_coefficient=3, dct_quantization_factor=10)


@pytest.fixture
def mock_encryption_config() -> EncryptionConfig:
    """Provide a mock EncryptionConfig instance."""
    return EncryptionConfig(private_key_size=1024, iv_size=16, aes_key_size=32)


@pytest.fixture
def mock_steganographer_server_config(
    mock_image_config: ImageConfig, mock_encryption_config: EncryptionConfig
) -> SteganographerServerConfig:
    """Provide a mock SteganographerServerConfig instance."""
    return SteganographerServerConfig(image=mock_image_config, encryption=mock_encryption_config)


# API Request fixtures
@pytest.fixture
def mock_post_encode_request(mock_big_image_bytes: bytes) -> PostEncodeRequest:
    """Provide a mock PostEncodeRequest instance."""
    image_data = base64.b64encode(mock_big_image_bytes).decode("utf-8")
    return PostEncodeRequest(
        image_data=image_data,
        output_format="png",
        message="Test message",
        algorithm=AlgorithmType.LSB,
    )


@pytest.fixture
def mock_post_decode_request(mock_big_image_bytes: bytes) -> PostDecodeRequest:
    """Provide a mock PostDecodeRequest instance."""
    image_data = base64.b64encode(mock_big_image_bytes).decode("utf-8")
    return PostDecodeRequest(
        image_data=image_data,
        algorithm=AlgorithmType.LSB,
    )


@pytest.fixture
def mock_post_capacity_request(mock_big_image_bytes: bytes) -> PostCapacityRequest:
    """Provide a mock PostCapacityRequest instance."""
    image_data = base64.b64encode(mock_big_image_bytes).decode("utf-8")
    return PostCapacityRequest(
        image_data=image_data,
        algorithm=AlgorithmType.LSB,
    )


# Algorithm fixtures
@pytest.fixture
def lsb_algorithm() -> LSBAlgorithm:
    """Create LSB algorithm instance."""
    return LSBAlgorithm()


@pytest.fixture
def dct_algorithm(mock_image_config: ImageConfig) -> DCTAlgorithm:
    """Create DCT algorithm instance."""
    return DCTAlgorithm(
        block_size=mock_image_config.dct_block_size,
        dct_coefficient=mock_image_config.dct_coefficient,
        quantization_factor=mock_image_config.dct_quantization_factor,
    )


# Image fixtures
@pytest.fixture
def mock_image() -> NDArray[np.uint8]:
    """Create a sample 64x64x3 image for testing."""
    return rng.integers(0, 256, size=(64, 64, 3), dtype=np.uint8)


@pytest.fixture
def mock_big_image() -> NDArray[np.uint8]:
    """Create a sample 640x640x3 image for testing."""
    return rng.integers(0, 256, size=(640, 640, 3), dtype=np.uint8)


@pytest.fixture
def mock_image_channel(mock_image: NDArray[np.uint8]) -> NDArray[np.uint8]:
    """Create a sample 64x64 image channel for testing."""
    return mock_image[:, :, 0]


@pytest.fixture
def mock_load_image(mock_big_image: NDArray[np.uint8]) -> Generator[MagicMock]:
    """Fixture to mock image loading from file."""
    with patch("python_steganographer.image.skimage.io.imread", return_value=mock_big_image) as mock_imread:
        yield mock_imread


@pytest.fixture
def mock_big_image_bytes(mock_big_image: NDArray[np.uint8]) -> bytes:
    """Provide bytes of a mock big image."""
    return mock_big_image.tobytes()


@pytest.fixture
def mock_image_instance_lsb(mock_load_image: MagicMock, mock_big_image_bytes: bytes) -> Image:
    """Create an Image instance with LSB algorithm."""
    mock_image_instance = Image.lsb()
    mock_image_instance.load_image(image_bytes=mock_big_image_bytes)
    return mock_image_instance


@pytest.fixture
def mock_image_instance_dct(mock_load_image: MagicMock, mock_big_image_bytes: bytes) -> Image:
    """Create an Image instance with DCT algorithm."""
    mock_image_instance = Image.dct(block_size=8, dct_coefficient=3, quantization_factor=10)
    mock_image_instance.load_image(image_bytes=mock_big_image_bytes)
    return mock_image_instance


# Server fixtures
@pytest.fixture(autouse=True)
def mock_limiter() -> Limiter:
    """Provide a mock Limiter instance for testing."""
    mock_limiter = MagicMock(spec=Limiter)
    mock_limiter.limit.return_value = MagicMock(return_value=MagicMock())
    return mock_limiter


@pytest.fixture
def mock_image_router(
    mock_limiter: Limiter, mock_image_config: ImageConfig, mock_encryption_config: EncryptionConfig
) -> ImageRouter:
    """Provide an ImageRouter instance for testing."""
    IMAGE_ROUTER.configure(
        hashed_token="hashed_value",  # noqa: S106
        limiter=mock_limiter,
        rate_limit="10/minute",
    )
    IMAGE_ROUTER.setup_routes()
    IMAGE_ROUTER.configure_router(image_config=mock_image_config, encryption_config=mock_encryption_config)
    return IMAGE_ROUTER
