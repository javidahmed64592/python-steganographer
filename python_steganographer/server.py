"""Steganographer server module."""

import logging
from typing import Any

from python_template_server.template_server import TemplateServer

from python_steganographer.models import SteganographerServerConfig

logger = logging.getLogger(__name__)


class SteganographerServer(TemplateServer):
    """FastAPI steganographer server."""

    def __init__(self, config: SteganographerServerConfig | None = None) -> None:
        """Initialize the SteganographerServer.

        :param SteganographerServerConfig | None config: Optional pre-loaded configuration
        """
        super().__init__(
            package_name="python_steganographer",
            config=config,
        )

    def validate_config(self, config_data: dict[str, Any]) -> SteganographerServerConfig:
        """Validate configuration data against the SteganographerServerConfig model.

        :param dict config_data: The configuration data to validate
        :return SteganographerServerConfig: The validated configuration model
        :raise ValidationError: If the configuration data is invalid
        """
        return SteganographerServerConfig.model_validate(config_data)  # type: ignore[no-any-return]

    def setup_routes(self) -> None:
        """Set up API routes."""
        super().setup_routes()
