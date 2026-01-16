"""Pydantic models for the server."""

from enum import StrEnum, auto

from pydantic import BaseModel, Field
from python_template_server.models import BaseResponse, TemplateServerConfig


# Steganographer Server Configuration Models
class SteganographerServerConfig(TemplateServerConfig):
    """Configuration model for the Steganographer Server."""


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
