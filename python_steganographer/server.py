"""Steganographer server module."""

import logging
from typing import Any

from python_template_server.routers import BaseRouter
from python_template_server.template_server import TemplateServer

from python_steganographer.models import SteganographerServerConfig
from python_steganographer.routers import ImageRouter

logger = logging.getLogger(__name__)

IMAGE_ROUTER = ImageRouter(prefix="/image")


class SteganographerServer(TemplateServer):
    """FastAPI steganographer server."""

    def __init__(self, config: SteganographerServerConfig | None = None) -> None:
        """Initialize the SteganographerServer.

        :param SteganographerServerConfig | None config: Optional pre-loaded configuration
        """
        self.config: SteganographerServerConfig
        super().__init__(
            package_name="python-steganographer",
            config=config,
        )

    @property
    def routers(self) -> list[BaseRouter]:
        """Define the API routers for the server.

        :return list[BaseRouter]: List of API routers
        """
        IMAGE_ROUTER.configure_router(image_config=self.config.image, encryption_config=self.config.encryption)
        return [IMAGE_ROUTER]

    def validate_config(self, config_data: dict[str, Any]) -> SteganographerServerConfig:
        """Validate configuration data against the SteganographerServerConfig model.

        :param dict config_data: The configuration data to validate
        :return SteganographerServerConfig: The validated configuration model
        """
        return SteganographerServerConfig.model_validate(config_data)  # type: ignore[no-any-return]
