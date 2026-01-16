"""Unit tests for the python_steganographer.models module."""

from python_steganographer.models import SteganographerServerConfig, SteganographyConfig


# Steganographer Server Configuration Models
class TestSteganographerServerConfig:
    """Unit tests for the SteganographerServerConfig class."""

    def test_model_dump(
        self,
        mock_steganographer_server_config: SteganographerServerConfig,
        mock_steganography_config: SteganographyConfig,
    ) -> None:
        """Test the model_dump method."""
        assert mock_steganographer_server_config.steganography.model_dump() == mock_steganography_config.model_dump()
