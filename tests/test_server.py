"""Unit tests for the python_steganographer.server module."""

import asyncio
from collections.abc import Generator
from importlib.metadata import PackageMetadata
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, Request, Security
from fastapi.routing import APIRoute
from fastapi.security import APIKeyHeader
from fastapi.testclient import TestClient
from python_template_server.models import ResponseCode

from python_steganographer.image import Image
from python_steganographer.models import (
    PostCapacityRequest,
    PostDecodeRequest,
    PostEncodeRequest,
    SteganographerServerConfig,
)
from python_steganographer.server import SteganographerServer


@pytest.fixture(autouse=True)
def mock_package_metadata() -> Generator[MagicMock]:
    """Mock importlib.metadata.metadata to return a mock PackageMetadata."""
    with patch("python_template_server.template_server.metadata") as mock_metadata:
        mock_pkg_metadata = MagicMock(spec=PackageMetadata)
        metadata_dict = {
            "Name": "python-steganographer",
            "Version": "0.1.0",
            "Summary": "A FastAPI application for steganography.",
        }
        mock_pkg_metadata.__getitem__.side_effect = lambda key: metadata_dict[key]
        mock_metadata.return_value = mock_pkg_metadata
        yield mock_metadata


@pytest.fixture
def mock_image_instance(mock_image_instance_lsb: Image) -> Generator[Image]:
    """Provide a mock Image instance."""
    with (
        patch(
            "python_steganographer.server.SteganographerServer._get_image_instance_from_algorithm",
            return_value=mock_image_instance_lsb,
        ),
        patch.object(mock_image_instance_lsb, "encode"),
        patch.object(mock_image_instance_lsb, "decode", return_value="Decoded message"),
    ):
        yield mock_image_instance_lsb


@pytest.fixture
def mock_server(
    mock_steganographer_server_config: SteganographerServerConfig,
    mock_image_instance: Image,
) -> Generator[SteganographerServer]:
    """Provide a SteganographerServer instance for testing."""

    async def fake_verify_api_key(
        api_key: str | None = Security(APIKeyHeader(name="X-API-Key", auto_error=False)),
    ) -> None:
        """Fake verify API key that accepts the security header and always succeeds in tests."""
        return

    with (
        patch.object(SteganographerServer, "_verify_api_key", new=fake_verify_api_key),
        patch("python_steganographer.server.SteganographerServerConfig.save_to_file"),
    ):
        server = SteganographerServer(mock_steganographer_server_config)
        yield server


class TestSteganographerServer:
    """Unit tests for the SteganographerServer class."""

    def test_init(self, mock_server: SteganographerServer) -> None:
        """Test SteganographerServer initialization."""
        assert isinstance(mock_server.config, SteganographerServerConfig)

    def test_validate_config(
        self, mock_server: SteganographerServer, mock_steganographer_server_config: SteganographerServerConfig
    ) -> None:
        """Test configuration validation."""
        config_dict = mock_steganographer_server_config.model_dump()
        validated_config = mock_server.validate_config(config_dict)
        assert validated_config == mock_steganographer_server_config

    def test_validate_config_invalid_returns_default(self, mock_server: SteganographerServer) -> None:
        """Test invalid configuration returns default configuration."""
        invalid_config = {"model": None}
        validated_config = mock_server.validate_config(invalid_config)
        assert isinstance(validated_config, SteganographerServerConfig)


class TestSteganographerServerRoutes:
    """Integration tests for the routes in SteganographerServer."""

    def test_setup_routes(self, mock_server: SteganographerServer) -> None:
        """Test that routes are set up correctly."""
        api_routes = [route for route in mock_server.app.routes if isinstance(route, APIRoute)]
        routes = [route.path for route in api_routes]
        expected_endpoints = [
            "/health",
            "/login",
            "/image/encode",
            "/image/decode",
            "/image/capacity",
        ]
        for endpoint in expected_endpoints:
            assert endpoint in routes, f"Expected endpoint {endpoint} not found in routes"


class TestPostEncodeEndpoint:
    """Integration and unit tests for the /image/encode endpoint."""

    @pytest.fixture
    def mock_request_object(self, mock_post_encode_request: PostEncodeRequest) -> MagicMock:
        """Provide a mock Request object with JSON data."""
        request = MagicMock(spec=Request)
        request.json = AsyncMock(return_value=mock_post_encode_request.model_dump())
        return request

    def test_post_encode(
        self,
        mock_server: SteganographerServer,
        mock_request_object: MagicMock,
    ) -> None:
        """Test the /image/encode method handles valid JSON and returns a model reply."""
        response = asyncio.run(mock_server.post_encode(mock_request_object))

        assert response.message == "Image encoded successfully"
        assert isinstance(response.timestamp, str)
        assert isinstance(response.image_data, str)

    def test_post_encode_error(
        self,
        mock_server: SteganographerServer,
        mock_request_object: MagicMock,
        mock_image_instance: Image,
    ) -> None:
        """Test /image/encode handles errors gracefully."""
        with (
            pytest.raises(HTTPException, match=r"Failed to encode image"),
            patch.object(mock_image_instance, "encode", side_effect=Exception("Encoding failed")),
        ):
            asyncio.run(mock_server.post_encode(mock_request_object))

    def test_post_encode_endpoint(
        self,
        mock_server: SteganographerServer,
        mock_post_encode_request: PostEncodeRequest,
    ) -> None:
        """Test /image/encode endpoint returns 200 and includes image data."""
        app = mock_server.app
        client = TestClient(app)

        response = client.post(
            "/image/encode",
            json=mock_post_encode_request.model_dump(),
        )
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert response_body["message"] == "Image encoded successfully"
        assert isinstance(response_body["timestamp"], str)
        assert isinstance(response_body["image_data"], str)


class TestPostDecodeEndpoint:
    """Integration and unit tests for the /image/decode endpoint."""

    @pytest.fixture
    def mock_request_object(self, mock_post_decode_request: PostDecodeRequest) -> MagicMock:
        """Provide a mock Request object with JSON data."""
        request = MagicMock(spec=Request)
        request.json = AsyncMock(return_value=mock_post_decode_request.model_dump())
        return request

    def test_post_decode(
        self,
        mock_server: SteganographerServer,
        mock_request_object: MagicMock,
    ) -> None:
        """Test the /image/decode method handles valid JSON and returns a model reply."""
        response = asyncio.run(mock_server.post_decode(mock_request_object))

        assert response.message == "Image decoded successfully"
        assert isinstance(response.timestamp, str)
        assert isinstance(response.decoded_message, str)

    def test_post_decode_error(
        self,
        mock_server: SteganographerServer,
        mock_request_object: MagicMock,
        mock_image_instance: Image,
    ) -> None:
        """Test /image/decode handles errors gracefully."""
        with (
            pytest.raises(HTTPException, match=r"Failed to decode image"),
            patch.object(mock_image_instance, "decode", side_effect=Exception("Decoding failed")),
        ):
            asyncio.run(mock_server.post_decode(mock_request_object))

    def test_post_decode_endpoint(
        self,
        mock_server: SteganographerServer,
        mock_post_decode_request: PostDecodeRequest,
    ) -> None:
        """Test /image/decode endpoint returns 200 and includes decoded message."""
        app = mock_server.app
        client = TestClient(app)

        response = client.post(
            "/image/decode",
            json=mock_post_decode_request.model_dump(),
        )
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert response_body["message"] == "Image decoded successfully"
        assert isinstance(response_body["timestamp"], str)
        assert isinstance(response_body["decoded_message"], str)


class TestPostCapacityEndpoint:
    """Integration and unit tests for the /image/capacity endpoint."""

    @pytest.fixture
    def mock_request_object(self, mock_post_capacity_request: PostCapacityRequest) -> MagicMock:
        """Provide a mock Request object with JSON data."""
        request = MagicMock(spec=Request)
        request.json = AsyncMock(return_value=mock_post_capacity_request.model_dump())
        return request

    def test_post_capacity(
        self,
        mock_server: SteganographerServer,
        mock_request_object: MagicMock,
    ) -> None:
        """Test the /image/capacity method handles valid JSON and returns a model reply."""
        response = asyncio.run(mock_server.post_capacity(mock_request_object))

        assert response.message == "Capacity calculated successfully"
        assert isinstance(response.timestamp, str)
        assert isinstance(response.capacity_characters, int)

    def test_post_capacity_error(
        self,
        mock_server: SteganographerServer,
        mock_request_object: MagicMock,
        mock_image_instance: Image,
    ) -> None:
        """Test /image/capacity handles errors gracefully."""
        with (
            pytest.raises(HTTPException, match=r"Failed to calculate capacity"),
            patch.object(mock_image_instance, "get_capacity", side_effect=Exception("Capacity calculation failed")),
        ):
            asyncio.run(mock_server.post_capacity(mock_request_object))

    def test_post_capacity_endpoint(
        self,
        mock_server: SteganographerServer,
        mock_post_capacity_request: PostCapacityRequest,
    ) -> None:
        """Test /image/capacity endpoint returns 200 and includes capacity information."""
        app = mock_server.app
        client = TestClient(app)

        response = client.post(
            "/image/capacity",
            json=mock_post_capacity_request.model_dump(),
        )
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert response_body["message"] == "Capacity calculated successfully"
        assert isinstance(response_body["timestamp"], str)
        assert isinstance(response_body["capacity_characters"], int)
