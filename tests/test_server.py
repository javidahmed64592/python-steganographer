"""Unit tests for the python_steganographer.server module."""

from collections.abc import Generator
from importlib.metadata import PackageMetadata
from unittest.mock import MagicMock, patch

import pytest

from python_steganographer.models import SteganographerServerConfig
from python_steganographer.routers import ImageRouter
from python_steganographer.server import SteganographerServer


@pytest.fixture(autouse=True)
def mock_package_metadata() -> Generator[MagicMock]:
    """Mock importlib.metadata.metadata to return a mock PackageMetadata."""
    with patch("python_template_server.template_server.metadata") as mock_metadata:
        mock_pkg_metadata = MagicMock(spec=PackageMetadata)
        metadata_dict = {
            "Name": "python-steganographer",
            "Version": "0.1.0",
            "Summary": "A FastAPI application for steganography.",
        }
        mock_pkg_metadata.__getitem__.side_effect = lambda key: metadata_dict[key]
        mock_metadata.return_value = mock_pkg_metadata
        yield mock_metadata


@pytest.fixture
def mock_server(
    mock_steganographer_server_config: SteganographerServerConfig, mock_image_router: ImageRouter
) -> Generator[SteganographerServer]:
    """Provide a SteganographerServer instance for testing."""
    with (
        patch("python_steganographer.server.ImageRouter", return_value=mock_image_router, autospec=True),
        patch("python_steganographer.server.SteganographerServerConfig.save_to_file"),
    ):
        server = SteganographerServer(config=mock_steganographer_server_config)
        yield server


class TestSteganographerServer:
    """Unit tests for the SteganographerServer class."""

    def test_init(self, mock_server: SteganographerServer) -> None:
        """Test SteganographerServer initialization."""
        assert isinstance(mock_server.config, SteganographerServerConfig)

    def test_validate_config(
        self, mock_server: SteganographerServer, mock_steganographer_server_config: SteganographerServerConfig
    ) -> None:
        """Test configuration validation."""
        config_dict = mock_steganographer_server_config.model_dump()
        validated_config = mock_server.validate_config(config_dict)
        assert validated_config == mock_steganographer_server_config

    def test_validate_config_invalid_returns_default(self, mock_server: SteganographerServer) -> None:
        """Test invalid configuration returns default configuration."""
        invalid_config = {"model": None}
        validated_config = mock_server.validate_config(invalid_config)
        assert isinstance(validated_config, SteganographerServerConfig)

    def test_routers_property(self, mock_server: SteganographerServer, mock_image_router: ImageRouter) -> None:
        """Test that the routers property returns the expected list of routers."""
        assert mock_image_router in mock_server._routers
