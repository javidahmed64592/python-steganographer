"""Pydantic models for the server."""

from enum import StrEnum, auto

from pydantic import BaseModel, Field
from python_template_server.models import BaseResponse, TemplateServerConfig

from python_steganographer.constants import (
    DEFAULT_AES_KEY_SIZE,
    DEFAULT_DCT_BLOCK_SIZE,
    DEFAULT_DCT_COEFFICIENT,
    DEFAULT_DCT_QUANTIZATION_FACTOR,
    DEFAULT_IV_SIZE,
    DEFAULT_PRIVATE_KEY_SIZE,
)


# Steganographer Server Configuration Models
class SteganographyConfig(BaseModel):
    """Configuration model for steganography settings."""

    dct_block_size: int = Field(default=DEFAULT_DCT_BLOCK_SIZE, description="DCT block size", ge=4)
    dct_coefficient: int = Field(
        default=DEFAULT_DCT_COEFFICIENT, description="DCT coefficient to modify (1-indexed, avoid DC component)", ge=1
    )
    dct_quantization_factor: int = Field(
        default=DEFAULT_DCT_QUANTIZATION_FACTOR, description="Quantization factor for DCT coefficients", ge=1
    )
    private_key_size: int = Field(
        default=DEFAULT_PRIVATE_KEY_SIZE, description="Size of the RSA private key in bits", ge=1024
    )
    iv_size: int = Field(default=DEFAULT_IV_SIZE, description="Size of the AES initialization vector in bytes", ge=8)
    aes_key_size: int = Field(default=DEFAULT_AES_KEY_SIZE, description="Size of the AES key in bytes", ge=16)


class SteganographerServerConfig(TemplateServerConfig):
    """Configuration model for the Steganographer Server."""

    steganography: SteganographyConfig = Field(
        default_factory=SteganographyConfig, description="Steganography-related configuration settings"
    )


# Steganography Models
class AlgorithmType(StrEnum):
    """Enumeration of supported steganography algorithms."""

    LSB = auto()
    DCT = auto()


# API Response Models
class PostEncodeResponse(BaseResponse):
    """Response model for encoding data into an image."""

    image_data: str = Field(..., description="Base64-encoded image bytes")


class PostDecodeResponse(BaseResponse):
    """Response model for decoding data from an image."""

    decoded_message: str = Field(..., description="The decoded message from the image")


class PostCapacityResponse(BaseResponse):
    """Response model for checking image capacity for steganography."""

    capacity_characters: int = Field(..., description="The capacity in characters for hiding data in a single channel")


# API Request Models
class PostEncodeRequest(BaseModel):
    """Request model for encoding data into an image."""

    image_data: str = Field(..., description="Base64-encoded image bytes")
    output_format: str = Field(..., description="Output image format")
    message: str = Field(..., description="The message to encode")
    algorithm: AlgorithmType = Field(..., description="The steganography algorithm to use")


class PostDecodeRequest(BaseModel):
    """Request model for decoding data from an image."""

    image_data: str = Field(..., description="Base64-encoded image bytes")
    algorithm: AlgorithmType = Field(..., description="The steganography algorithm to use")


class PostCapacityRequest(BaseModel):
    """Request model for checking image capacity for steganography."""

    image_data: str = Field(..., description="Base64-encoded image bytes")
    algorithm: AlgorithmType = Field(..., description="The steganography algorithm to use")
