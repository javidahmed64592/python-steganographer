"""Pydantic models for the server."""

from enum import StrEnum, auto

from pydantic import BaseModel
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

    image_data: str  # Base64-encoded image bytes


class PostDecodeResponse(BaseResponse):
    """Response model for decoding data from an image."""

    decoded_message: str


class PostCapacityResponse(BaseResponse):
    """Response model for checking image capacity for steganography."""

    capacity_bytes: int


# API Request Models
class PostEncodeRequest(BaseModel):
    """Request model for encoding data into an image."""

    image_data: str  # Base64-encoded image bytes
    output_format: str  # Output image format
    message: str
    algorithm: AlgorithmType


class PostDecodeRequest(BaseModel):
    """Request model for decoding data from an image."""

    image_data: str  # Base64-encoded image bytes
    algorithm: AlgorithmType


class PostCapacityRequest(BaseModel):
    """Request model for checking image capacity for steganography."""

    image_data: str  # Base64-encoded image bytes
    algorithm: AlgorithmType
