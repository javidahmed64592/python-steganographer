<!-- omit from toc -->
# API

This document summarizes the API endpoints specific to the Python Steganographer.

## Base Server Infrastructure

The Python Steganographer is built from [python-template-server](https://github.com/javidahmed64592/python-template-server), which provides production-ready infrastructure including:

- **API Key Authentication**: All authenticated endpoints require the `X-API-Key` header with a SHA-256 hashed token
- **Rate Limiting**: Configurable request throttling (default: 100 requests/minute per IP)
- **Security Headers**: Automatic HSTS, CSP, and X-Frame-Options enforcement
- **Request Logging**: Comprehensive logging of all requests/responses with client IP tracking
- **Health Checks**: Standard `/api/health` endpoint for availability monitoring
- **HTTPS Support**: Built-in SSL certificate generation and management

For detailed information about these features, authentication token generation, server middleware, and base configuration, see the [python-template-server README](https://github.com/javidahmed64592/python-template-server/blob/main/README.md) and [python-template-server API documentation](https://github.com/javidahmed64592/python-template-server/blob/main/docs/API.md).

## Frontend Client

The project includes a Next.js frontend (`python-steganographer-frontend/`) with a TypeScript API client (`src/lib/api.ts`) that handles:

- **Authentication**: Automatic API key injection via Axios interceptors
- **Error Handling**: Extracts FastAPI error details from response messages
- **Type Safety**: Full TypeScript support with Pydantic-aligned models (`src/lib/types.ts`)
- **Functions**: `encodeImage()`, `decodeImage()`, `getImageCapacity()`, `getHealth()`, `login()`

<!-- omit from toc -->
## Table of Contents
- [Base Server Infrastructure](#base-server-infrastructure)
- [Frontend Client](#frontend-client)
- [Steganography Endpoints](#steganography-endpoints)
  - [POST /api/image/encode](#post-apiimageencode)
  - [POST /api/image/decode](#post-apiimagedecode)
  - [POST /api/image/capacity](#post-apiimagecapacity)
- [Steganography Algorithms](#steganography-algorithms)
  - [LSB (Least Significant Bit)](#lsb-least-significant-bit)
  - [DCT (Discrete Cosine Transform)](#dct-discrete-cosine-transform)
- [Request and Response Models (Pydantic)](#request-and-response-models-pydantic)
- [API Documentation](#api-documentation)
  - [Swagger UI (/api/docs)](#swagger-ui-apidocs)
  - [ReDoc (/api/redoc)](#redoc-apiredoc)

## Steganography Endpoints

All steganography endpoints require authentication via the `X-API-Key` header.

### POST /api/image/encode

**Purpose**: Encode a message into an image using steganography.

**Request Model**: `PostEncodeRequest`

- `image_data` (string): Base64-encoded image bytes
- `output_format` (string): Output image format (e.g., "png", "jpeg")
- `message` (string): The message to encode into the image
- `algorithm` (string): The steganography algorithm to use ("lsb" or "dct")

**Response Model**: `PostEncodeResponse`

- `message` (string): Status message ("Image encoded successfully" or error message)
- `timestamp` (string): ISO 8601 timestamp
- `image_data` (string): Base64-encoded image bytes with embedded message

**Encryption Details**: The message is encrypted using hybrid encryption

### POST /api/image/decode

**Purpose**: Decode a hidden message from an image.

**Request Model**: `PostDecodeRequest`

- `image_data` (string): Base64-encoded image bytes containing hidden message
- `algorithm` (string): The steganography algorithm used for encoding ("lsb" or "dct")

**Response Model**: `PostDecodeResponse`

- `message` (string): Status message ("Image decoded successfully" or error message)
- `timestamp` (string): ISO 8601 timestamp
- `decoded_message` (string): The extracted and decrypted message

### POST /api/image/capacity

**Purpose**: Calculate the steganography capacity of an image (how many characters can be hidden).

**Request Model**: `PostCapacityRequest`

- `image_data` (string): Base64-encoded image bytes
- `algorithm` (string): The steganography algorithm to check capacity for ("lsb" or "dct")

**Response Model**: `PostCapacityResponse`

- `message` (string): Status message ("Capacity calculated successfully" or error message)
- `timestamp` (string): ISO 8601 timestamp
- `capacity_characters` (int): Maximum number of characters that can be hidden in a single channel

## Steganography Algorithms

The server supports two steganography algorithms, each with different characteristics:

### LSB (Least Significant Bit)

**Description**: Hides data by modifying the least significant bit of each pixel in the image.

**Characteristics**:
- **High Capacity**: Can store approximately (image width × height) / 7 characters per channel
- **Fast Performance**: Simple bit manipulation operations
- **Low Robustness**: Sensitive to image compression and transformations
- **Use Case**: Best for lossless formats (PNG) when images won't be modified

**How It Works**:
1. Converts message to binary representation (7 bits per character)
2. Modifies the LSB of each pixel to store message bits
3. Distributes data across RGB channels (R: encrypted data, G: encrypted key, B: private key)

### DCT (Discrete Cosine Transform)

**Description**: Hides data by modifying DCT coefficients in image blocks, similar to JPEG compression.

**Characteristics**:
- **Compression Resistant**: More robust to JPEG compression and image processing
- **Lower Capacity**: Stores 1 bit per block (default 8×8 blocks)
- **Moderate Performance**: Requires DCT/IDCT transformations
- **Use Case**: Best when images may undergo compression or transformations

**How It Works**:
1. Divides image into blocks (default 8×8 pixels)
2. Applies Discrete Cosine Transform to each block
3. Modifies specific DCT coefficients (default: coefficient 3) to embed message bits
4. Uses quantization (default factor: 10) to control embedding strength
5. Applies inverse DCT to reconstruct the image

**Configuration**: DCT parameters can be adjusted in `configuration/config.json`:
```json
{
  "steganography": {
    "dct_block_size": 8,
    "dct_coefficient": 3,
    "dct_quantization_factor": 10
  }
}
```

## Request and Response Models (Pydantic)

All Pydantic models are defined in `python_steganographer/models.py`.

## API Documentation

FastAPI automatically generates interactive API documentation.

### Swagger UI (/api/docs)

**URL**: `https://localhost:443/api/docs`

**Purpose**: Interactive API documentation with "Try it out" functionality

**Features**:
- Execute API calls directly from the browser
- Upload images and test steganography operations
- View request/response schemas for all endpoints
- Test authentication with API keys
- Explore algorithm options and parameters

### ReDoc (/api/redoc)

**URL**: `https://localhost:443/api/redoc`

**Purpose**: Alternative API documentation with a clean, three-panel layout

**Features**:
- Read-only documentation interface
- Clean, responsive design
- Detailed schema information for all models
- Search functionality across all endpoints
- Markdown support in descriptions
