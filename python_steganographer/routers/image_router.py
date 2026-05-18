"""Image router with encoding and decoding endpoints."""

import base64
import logging

from fastapi import HTTPException, Request
from python_template_server.models import ResponseCode
from python_template_server.routers import BaseRouter

from python_steganographer.image import Image
from python_steganographer.models import (
    AlgorithmType,
    EncryptionConfig,
    ImageConfig,
    PostCapacityRequest,
    PostCapacityResponse,
    PostDecodeRequest,
    PostDecodeResponse,
    PostEncodeRequest,
    PostEncodeResponse,
)

logger = logging.getLogger(__name__)


class ImageRouter(BaseRouter):
    """Router for image encoding and decoding endpoints."""

    def configure_router(self, image_config: ImageConfig, encryption_config: EncryptionConfig) -> None:
        """Configure the router with necessary dependencies."""
        self.image_config = image_config
        self.encryption_config = encryption_config

    def setup_routes(self) -> None:
        """Set up the API routes for image operations."""
        self.add_route(
            endpoint="/encode",
            handler_function=self.post_encode,
            response_model=PostEncodeResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/decode",
            handler_function=self.post_decode,
            response_model=PostDecodeResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/capacity",
            handler_function=self.post_capacity,
            response_model=PostCapacityResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )

    def _get_image_instance_from_algorithm(self, algorithm: AlgorithmType) -> Image:
        """Get an Image instance based on the specified algorithm.

        :param AlgorithmType algorithm: The steganography algorithm
        :return Image: The corresponding Image instance
        """
        match algorithm:
            case AlgorithmType.LSB:
                return Image.lsb()
            case AlgorithmType.DCT:
                return Image.dct(
                    block_size=self.image_config.dct_block_size,
                    dct_coefficient=self.image_config.dct_coefficient,
                    quantization_factor=self.image_config.dct_quantization_factor,
                )

    async def post_encode(self, request: Request) -> PostEncodeResponse:
        """Handle image encode requests - encode a message into an image.

        :param Request request: The request object
        :return PostEncodeResponse: Server response with encoded image data
        """
        try:
            encode_request = PostEncodeRequest.model_validate(await request.json())

            image_bytes = base64.b64decode(encode_request.image_data)
            image = self._get_image_instance_from_algorithm(algorithm=encode_request.algorithm)
            image.load_image(image_bytes=image_bytes)

            image.encode(
                msg=encode_request.message,
                private_key_size=self.encryption_config.private_key_size,
                iv_size=self.encryption_config.iv_size,
                aes_key_size=self.encryption_config.aes_key_size,
            )

            encoded_image_bytes = image.save_image_to_bytes(format_str=encode_request.output_format)
            encoded_image_b64 = base64.b64encode(encoded_image_bytes).decode("utf-8")

            return PostEncodeResponse(
                message="Image encoded successfully",
                image_data=encoded_image_b64,
            )
        except Exception as e:
            error_msg = "Failed to encode image"
            logger.exception(error_msg)
            raise HTTPException(status_code=ResponseCode.INTERNAL_SERVER_ERROR, detail=error_msg) from e

    async def post_decode(self, request: Request) -> PostDecodeResponse:
        """Handle image decode requests - extract a message from an image.

        :param Request request: The request object
        :return PostDecodeResponse: Server response with decoded message
        """
        try:
            decode_request = PostDecodeRequest.model_validate(await request.json())

            image_bytes = base64.b64decode(decode_request.image_data)
            image = self._get_image_instance_from_algorithm(algorithm=decode_request.algorithm)
            image.load_image(image_bytes=image_bytes)

            decoded_message = image.decode(iv_size=self.encryption_config.iv_size)

            return PostDecodeResponse(
                message="Image decoded successfully",
                decoded_message=decoded_message,
            )
        except Exception as e:
            error_msg = "Failed to decode image"
            logger.exception(error_msg)
            raise HTTPException(status_code=ResponseCode.INTERNAL_SERVER_ERROR, detail=error_msg) from e

    async def post_capacity(self, request: Request) -> PostCapacityResponse:
        """Handle capacity check requests - calculate steganography capacity of an image.

        :param Request request: The request object
        :return PostCapacityResponse: Server response with capacity information
        """
        try:
            capacity_request = PostCapacityRequest.model_validate(await request.json())

            image_bytes = base64.b64decode(capacity_request.image_data)
            image = self._get_image_instance_from_algorithm(algorithm=capacity_request.algorithm)
            image.load_image(image_bytes=image_bytes)

            capacity_characters = image.get_capacity()

            return PostCapacityResponse(
                message="Capacity calculated successfully",
                capacity_characters=capacity_characters,
            )
        except Exception as e:
            error_msg = "Failed to calculate capacity"
            logger.exception(error_msg)
            raise HTTPException(status_code=ResponseCode.INTERNAL_SERVER_ERROR, detail=error_msg) from e
