"""Unit tests for the python_steganographer.models module."""

from python_steganographer.models import SteganographerServerConfig


# Steganographer Server Configuration Models
class TestSteganographerServerConfig:
    """Unit tests for the SteganographerServerConfig class."""

    def test_model_dump(self, mock_steganographer_server_config: SteganographerServerConfig) -> None:
        """Test the model_dump method."""
        assert isinstance(mock_steganographer_server_config.model_dump(), dict)  # Temporary until more config is added
