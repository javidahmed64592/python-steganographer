"""Steganographer server module."""

import base64
import logging
from typing import Any

from fastapi import HTTPException, Request
from python_template_server.models import ResponseCode
from python_template_server.template_server import TemplateServer

from python_steganographer.image import Image
from python_steganographer.models import (
    AlgorithmType,
    PostCapacityRequest,
    PostCapacityResponse,
    PostDecodeRequest,
    PostDecodeResponse,
    PostEncodeRequest,
    PostEncodeResponse,
    SteganographerServerConfig,
)

logger = logging.getLogger(__name__)


class SteganographerServer(TemplateServer):
    """FastAPI steganographer server."""

    def __init__(self, config: SteganographerServerConfig | None = None) -> None:
        """Initialize the SteganographerServer.

        :param SteganographerServerConfig | None config: Optional pre-loaded configuration
        """
        self.config: SteganographerServerConfig
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
        self.add_authenticated_route(
            endpoint="/image/encode",
            handler_function=self.post_encode,
            response_model=PostEncodeResponse,
            methods=["POST"],
        )
        self.add_authenticated_route(
            endpoint="/image/decode",
            handler_function=self.post_decode,
            response_model=PostDecodeResponse,
            methods=["POST"],
        )
        self.add_authenticated_route(
            endpoint="/image/capacity",
            handler_function=self.post_capacity,
            response_model=PostCapacityResponse,
            methods=["POST"],
        )

    def _get_image_instance_from_algorithm(self, algorithm: AlgorithmType) -> Image:
        """Get an Image instance based on the specified algorithm.

        :param AlgorithmType algorithm: The steganography algorithm
        :return Image: The corresponding Image instance
        :raise HTTPException: If the algorithm is unsupported
        """
        match algorithm:
            case AlgorithmType.LSB:
                logger.info("Using LSB algorithm")
                return Image.lsb()
            case AlgorithmType.DCT:
                logger.info("Using DCT algorithm")
                return Image.dct(
                    block_size=self.config.steganography.dct_block_size,
                    dct_coefficient=self.config.steganography.dct_coefficient,
                    quantization_factor=self.config.steganography.dct_quantization_factor,
                )
            case _:
                logger.error("Unsupported algorithm: %s", algorithm)
                raise HTTPException(status_code=ResponseCode.BAD_REQUEST, detail="Unsupported algorithm")

    async def post_encode(self, request: Request) -> PostEncodeResponse:
        """Handle image encode requests - encode a message into an image.

        :param Request request: The request object
        :return PostEncodeResponse: Server response with encoded image data
        """
        encode_request = PostEncodeRequest.model_validate(await request.json())
        logger.info("Received encode request for '%s' file type", encode_request.output_format)

        image_bytes = base64.b64decode(encode_request.image_data)

        image = self._get_image_instance_from_algorithm(encode_request.algorithm)
        image.load_image(image_bytes)

        logger.info("Encoding message of length %d into image", len(encode_request.message))
        image.encode(
            msg=encode_request.message,
            private_key_size=self.config.steganography.private_key_size,
            iv_size=self.config.steganography.iv_size,
            aes_key_size=self.config.steganography.aes_key_size,
        )

        encoded_image_bytes = image.save_image_to_bytes(format_str=encode_request.output_format)
        encoded_image_b64 = base64.b64encode(encoded_image_bytes).decode("utf-8")

        return PostEncodeResponse(
            code=ResponseCode.OK,
            message="Image encoded successfully",
            timestamp=PostEncodeResponse.current_timestamp(),
            image_data=encoded_image_b64,
        )

    async def post_decode(self, request: Request) -> PostDecodeResponse:
        """Handle image decode requests - extract a message from an image.

        :param Request request: The request object
        :return PostDecodeResponse: Server response with decoded message
        """
        logger.info("Received decode request")
        decode_request = PostDecodeRequest.model_validate(await request.json())

        image_bytes = base64.b64decode(decode_request.image_data)

        image = self._get_image_instance_from_algorithm(decode_request.algorithm)
        image.load_image(image_bytes)

        decoded_message = image.decode(iv_size=self.config.steganography.iv_size)

        return PostDecodeResponse(
            code=ResponseCode.OK,
            message="Image decoded successfully",
            timestamp=PostDecodeResponse.current_timestamp(),
            decoded_message=decoded_message,
        )

    async def post_capacity(self, request: Request) -> PostCapacityResponse:
        """Handle capacity check requests - calculate steganography capacity of an image.

        :param Request request: The request object
        :return PostCapacityResponse: Server response with capacity information
        """
        logger.info("Received capacity check request")
        capacity_request = PostCapacityRequest.model_validate(await request.json())

        image_bytes = base64.b64decode(capacity_request.image_data)

        image = self._get_image_instance_from_algorithm(capacity_request.algorithm)
        image.load_image(image_bytes)

        capacity_characters = image.get_capacity()

        return PostCapacityResponse(
            code=ResponseCode.OK,
            message="Capacity calculated successfully",
            timestamp=PostCapacityResponse.current_timestamp(),
            capacity_characters=capacity_characters,
        )
