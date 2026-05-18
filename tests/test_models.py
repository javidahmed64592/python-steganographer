"""Unit tests for the python_steganographer.models module."""

from python_steganographer.models import EncryptionConfig, ImageConfig, SteganographerServerConfig


# Steganographer Server Configuration Models
class TestSteganographerServerConfig:
    """Unit tests for the SteganographerServerConfig class."""

    def test_model_dump(
        self,
        mock_image_config: ImageConfig,
        mock_encryption_config: EncryptionConfig,
        mock_steganographer_server_config: SteganographerServerConfig,
    ) -> None:
        """Test the model_dump method."""
        config_dict = mock_steganographer_server_config.model_dump()
        assert config_dict["image"] == mock_image_config.model_dump()
        assert config_dict["encryption"] == mock_encryption_config.model_dump()
