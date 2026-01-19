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
- [Security Features](#security-features)
- [API Documentation](#api-documentation)
  - [Swagger UI (/api/docs)](#swagger-ui-apidocs)
  - [ReDoc (/api/redoc)](#redoc-apiredoc)

## Steganography Endpoints

All steganography endpoints require authentication via the `X-API-Key` header.

### POST /api/image/encode

**Purpose**: Encode a message into an image using steganography.

**Authentication**: Required (API key must be provided)

**Rate Limiting**: Subject to rate limits (default: 100/minute)

**Request Model**: `PostEncodeRequest`

- `image_data` (string): Base64-encoded image bytes
- `output_format` (string): Output image format (e.g., "png", "jpeg")
- `message` (string): The message to encode into the image
- `algorithm` (string): The steganography algorithm to use ("lsb" or "dct")

**Response Model**: `PostEncodeResponse`

- `code` (int): HTTP status code (200 for success, 500 for error)
- `message` (string): Status message ("Image encoded successfully" or error message)
- `timestamp` (string): ISO 8601 timestamp
- `image_data` (string): Base64-encoded image bytes with embedded message

**Example Request**:
```bash
curl -k https://localhost:443/api/image/encode \
  -H "X-API-Key: your-api-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "base64_encoded_image_data_here",
    "output_format": "png",
    "message": "Secret message",
    "algorithm": "lsb"
  }'
```

**Example Response (200 OK)**:
```json
{
  "code": 200,
  "message": "Image encoded successfully",
  "timestamp": "2026-01-17T12:00:00.000000Z",
  "image_data": "base64_encoded_result_image_here"
}
```

**Example Response (500 Internal Server Error)**:
```json
{
  "code": 500,
  "message": "Failed to encode image",
  "timestamp": "2026-01-17T12:00:00.000000Z",
  "image_data": ""
}
```

**Encryption Details**: The message is encrypted using hybrid RSA + AES encryption:
- RSA-2048 key pair is generated for each encoding operation
- AES-256 is used to encrypt the message with a randomly generated key and IV
- The RSA public key encrypts the AES key
- The encrypted message, encrypted AES key, and RSA private key are embedded in separate RGB channels

### POST /api/image/decode

**Purpose**: Decode a hidden message from an image.

**Authentication**: Required (API key must be provided)

**Rate Limiting**: Subject to rate limits (default: 100/minute)

**Request Model**: `PostDecodeRequest`

- `image_data` (string): Base64-encoded image bytes containing hidden message
- `algorithm` (string): The steganography algorithm used for encoding ("lsb" or "dct")

**Response Model**: `PostDecodeResponse`

- `code` (int): HTTP status code (200 for success, 500 for error)
- `message` (string): Status message ("Image decoded successfully" or error message)
- `timestamp` (string): ISO 8601 timestamp
- `decoded_message` (string): The extracted and decrypted message

**Example Request**:
```bash
curl -k https://localhost:443/api/image/decode \
  -H "X-API-Key: your-api-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "base64_encoded_image_with_hidden_message",
    "algorithm": "lsb"
  }'
```

**Example Response (200 OK)**:
```json
{
  "code": 200,
  "message": "Image decoded successfully",
  "timestamp": "2026-01-17T12:00:00.000000Z",
  "decoded_message": "Secret message"
}
```

**Example Response (500 Internal Server Error)**:
```json
{
  "code": 500,
  "message": "Failed to decode image",
  "timestamp": "2026-01-17T12:00:00.000000Z",
  "decoded_message": ""
}
```

### POST /api/image/capacity

**Purpose**: Calculate the steganography capacity of an image (how many characters can be hidden).

**Authentication**: Required (API key must be provided)

**Rate Limiting**: Subject to rate limits (default: 100/minute)

**Request Model**: `PostCapacityRequest`

- `image_data` (string): Base64-encoded image bytes
- `algorithm` (string): The steganography algorithm to check capacity for ("lsb" or "dct")

**Response Model**: `PostCapacityResponse`

- `code` (int): HTTP status code (200 for success, 500 for error)
- `message` (string): Status message ("Capacity calculated successfully" or error message)
- `timestamp` (string): ISO 8601 timestamp
- `capacity_characters` (int): Maximum number of characters that can be hidden in a single channel

**Example Request**:
```bash
curl -k https://localhost:443/api/image/capacity \
  -H "X-API-Key: your-api-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "base64_encoded_image_data_here",
    "algorithm": "lsb"
  }'
```

**Example Response (200 OK)**:
```json
{
  "code": 200,
  "message": "Capacity calculated successfully",
  "timestamp": "2026-01-17T12:00:00.000000Z",
  "capacity_characters": 262144
}
```

**Example Response (500 Internal Server Error)**:
```json
{
  "code": 500,
  "message": "Failed to calculate capacity",
  "timestamp": "2026-01-17T12:00:00.000000Z",
  "capacity_characters": 0
}
```

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

All Pydantic models are defined in `python_steganographer/models.py`:

**Base Models** (inherited from python-template-server):
- `BaseResponse`: Base model with code, message, and timestamp fields
- `TemplateServerConfig`: Base configuration for server settings

**Steganographer-Specific Models**:

**Configuration Models**:
- `SteganographyConfig`: Steganography algorithm parameters (DCT settings, key sizes, IV size)
- `SteganographerServerConfig`: Extends TemplateServerConfig with steganography settings

**Request Models**:
- `PostEncodeRequest`: Fields for encoding data into images
- `PostDecodeRequest`: Fields for decoding data from images
- `PostCapacityRequest`: Fields for calculating image capacity

**Response Models**:
- `PostEncodeResponse`: Extends BaseResponse with image_data field
- `PostDecodeResponse`: Extends BaseResponse with decoded_message field
- `PostCapacityResponse`: Extends BaseResponse with capacity_characters field

**Enumerations**:
- `AlgorithmType`: Supported algorithms (LSB, DCT)

## Security Features

The steganography server implements multiple layers of security:

**1. Hybrid Encryption**:
- **RSA-2048**: Asymmetric encryption for secure key exchange
- **AES-256-CFB**: Symmetric encryption for message data
- **Random IV**: Unique initialization vector for each encoding

**2. Multi-Channel Embedding**:
- **Red Channel**: Encrypted message data
- **Green Channel**: Encrypted AES key (encrypted with RSA public key)
- **Blue Channel**: RSA private key for decryption

**3. API Security** (inherited from python-template-server):
- **Token Authentication**: SHA-256 hashed API keys
- **HTTPS Only**: Self-signed SSL certificates (production should use trusted certificates)
- **Security Headers**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options
- **Rate Limiting**: Protection against abuse

**4. Configuration Security**:
- API tokens stored as hashes in `.env` (never committed to version control)
- Configurable key sizes and encryption parameters
- Separate configuration files for different environments

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
