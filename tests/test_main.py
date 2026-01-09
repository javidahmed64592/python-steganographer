"""Unit tests for the python_steganographer.main module."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from python_steganographer.main import run
from python_steganographer.models import SteganographerServerConfig


@pytest.fixture
def mock_steganographer_server_class(
    mock_steganographer_server_config: SteganographerServerConfig,
) -> Generator[MagicMock]:
    """Mock SteganographerServer class."""
    with patch("python_steganographer.main.SteganographerServer") as mock_server:
        mock_server.load_config.return_value = mock_steganographer_server_config
        yield mock_server


class TestRun:
    """Unit tests for the run function."""

    def test_run(self, mock_steganographer_server_class: MagicMock) -> None:
        """Test successful server run."""
        run()

        mock_steganographer_server_class.return_value.run.assert_called_once()
