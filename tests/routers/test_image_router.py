"""Unit tests for the python_steganographer.routers.image_router module."""

import asyncio
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, Request
from fastapi.routing import APIRoute

from python_steganographer.image import Image
from python_steganographer.models import (
    PostCapacityRequest,
    PostDecodeRequest,
    PostEncodeRequest,
)
from python_steganographer.routers import ImageRouter


@pytest.fixture(autouse=True)
def mock_image_instance(mock_image_instance_lsb: Image) -> Generator[Image]:
    """Provide a mock Image instance."""
    with (
        patch(
            "python_steganographer.routers.image_router.ImageRouter._get_image_instance_from_algorithm",
            return_value=mock_image_instance_lsb,
        ),
        patch.object(mock_image_instance_lsb, "encode"),
        patch.object(mock_image_instance_lsb, "decode", return_value="Decoded message"),
    ):
        yield mock_image_instance_lsb


class TestRoutes:
    """Unit tests for route setup in ImageRouter."""

    def test_setup_routes(self, mock_image_router: ImageRouter) -> None:
        """Test that routes are set up correctly."""
        api_routes = [route for route in mock_image_router.router.routes if isinstance(route, APIRoute)]
        routes = [route.path for route in api_routes]
        expected_endpoints = [
            "/image/encode",
            "/image/decode",
            "/image/capacity",
        ]
        for endpoint in expected_endpoints:
            assert endpoint in routes, f"Expected endpoint {endpoint} not found in routes"


class TestPostEncodeEndpoint:
    """Integration and unit tests for the /image/encode endpoint."""

    @pytest.fixture
    def mock_request_object(self, mock_post_encode_request: PostEncodeRequest) -> Request:
        """Provide a mock Request object with JSON data."""
        request = MagicMock(spec=Request)
        request.json = AsyncMock(return_value=mock_post_encode_request.model_dump())
        return request

    def test_post_encode(self, mock_image_router: ImageRouter, mock_request_object: Request) -> None:
        """Test the /image/encode method handles valid JSON and returns a model reply."""
        response = asyncio.run(mock_image_router.post_encode(mock_request_object))

        assert response.message == "Image encoded successfully"
        assert isinstance(response.image_data, str)

    def test_post_encode_error(
        self, mock_image_router: ImageRouter, mock_request_object: Request, mock_image_instance: Image
    ) -> None:
        """Test /image/encode handles errors gracefully."""
        with (
            patch.object(mock_image_instance, "encode", side_effect=Exception("Encoding failed")),
            pytest.raises(HTTPException, match=r"Failed to encode image"),
        ):
            asyncio.run(mock_image_router.post_encode(mock_request_object))


class TestPostDecodeEndpoint:
    """Integration and unit tests for the /image/decode endpoint."""

    @pytest.fixture
    def mock_request_object(self, mock_post_decode_request: PostDecodeRequest) -> Request:
        """Provide a mock Request object with JSON data."""
        request = MagicMock(spec=Request)
        request.json = AsyncMock(return_value=mock_post_decode_request.model_dump())
        return request

    def test_post_decode(self, mock_image_router: ImageRouter, mock_request_object: Request) -> None:
        """Test the /image/decode method handles valid JSON and returns a model reply."""
        response = asyncio.run(mock_image_router.post_decode(mock_request_object))

        assert response.message == "Image decoded successfully"
        assert isinstance(response.decoded_message, str)

    def test_post_decode_error(
        self, mock_image_router: ImageRouter, mock_request_object: Request, mock_image_instance: Image
    ) -> None:
        """Test /image/decode handles errors gracefully."""
        with (
            patch.object(mock_image_instance, "decode", side_effect=Exception("Decoding failed")),
            pytest.raises(HTTPException, match=r"Failed to decode image"),
        ):
            asyncio.run(mock_image_router.post_decode(mock_request_object))


class TestPostCapacityEndpoint:
    """Integration and unit tests for the /image/capacity endpoint."""

    @pytest.fixture
    def mock_request_object(self, mock_post_capacity_request: PostCapacityRequest) -> Request:
        """Provide a mock Request object with JSON data."""
        request = MagicMock(spec=Request)
        request.json = AsyncMock(return_value=mock_post_capacity_request.model_dump())
        return request

    def test_post_capacity(self, mock_image_router: ImageRouter, mock_request_object: Request) -> None:
        """Test the /image/capacity method handles valid JSON and returns a model reply."""
        response = asyncio.run(mock_image_router.post_capacity(mock_request_object))

        assert response.message == "Capacity calculated successfully"
        assert isinstance(response.capacity_characters, int)

    def test_post_capacity_error(
        self, mock_image_router: ImageRouter, mock_request_object: Request, mock_image_instance: Image
    ) -> None:
        """Test /image/capacity handles errors gracefully."""
        with (
            patch.object(mock_image_instance, "get_capacity", side_effect=Exception("Capacity calculation failed")),
            pytest.raises(HTTPException, match=r"Failed to calculate capacity"),
        ):
            asyncio.run(mock_image_router.post_capacity(mock_request_object))
