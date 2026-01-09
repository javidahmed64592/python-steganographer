"""Pytest fixtures for the application's unit tests."""

import pytest

from python_steganographer.models import SteganographerServerConfig


# Steganographer Server Configuration Models
@pytest.fixture
def mock_steganographer_server_config() -> SteganographerServerConfig:
    """Provide a mock SteganographerServerConfig instance."""
    return SteganographerServerConfig.model_validate({})  # type: ignore[no-any-return]
