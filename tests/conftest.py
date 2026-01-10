"""Pytest fixtures for the application's unit tests."""

import numpy as np
import pytest

from python_steganographer.algorithms import DCTAlgorithm, LSBAlgorithm
from python_steganographer.models import SteganographerServerConfig

rng = np.random.default_rng(42)


# Steganographer Server Configuration Models
@pytest.fixture
def mock_steganographer_server_config() -> SteganographerServerConfig:
    """Provide a mock SteganographerServerConfig instance."""
    return SteganographerServerConfig.model_validate({})  # type: ignore[no-any-return]


# Algorithm Fixtures
@pytest.fixture
def mock_image_channel() -> np.ndarray[np.uint8]:
    """Create a sample 64x64 image channel for testing."""
    return rng.integers(0, 256, size=(64, 64), dtype=np.uint8)


@pytest.fixture
def lsb_algorithm() -> LSBAlgorithm:
    """Create LSB algorithm instance."""
    return LSBAlgorithm()


@pytest.fixture
def dct_algorithm() -> DCTAlgorithm:
    """Create DCT algorithm instance."""
    return DCTAlgorithm()
