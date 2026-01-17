# Python Steganographer - AI Agent Instructions

## Project Overview

FastAPI-based steganography server for hiding encrypted messages in images using LSB or DCT algorithms.
Built on [python-template-server](https://github.com/javidahmed64592/python-template-server) for authentication, rate limiting, and security.
Implements hybrid encryption (RSA-2048 + AES-256) with multi-channel embedding across RGB color channels.

## Architecture & Key Components

### Application Structure

- Entry: `main.py:run()` → instantiates `SteganographerServer` (extends `TemplateServer`) → calls `.run()`
- `SteganographerServer.__init__()` inherits middleware/auth setup, calls `setup_routes()` to add steganography endpoints
- **Endpoints**: Three authenticated routes for encode, decode, and capacity operations
- **Algorithms**: Factory pattern via `Image.lsb()` and `Image.dct()` for algorithm selection

### Steganography System

- **Image Class**: Central abstraction in `image.py` with factory methods for algorithm instantiation
- **Algorithm Base**: Abstract class `AlgorithmBase` defines interface for `embed_data()`, `extract_data()`, `calculate_capacity()`
- **LSB Algorithm**: Modifies least significant bit of pixels, high capacity (~width×height/7 chars per channel), fast but compression-sensitive
- **DCT Algorithm**: Modifies DCT coefficients in blocks, compression-resistant but lower capacity (1 bit per block)
- **Multi-Channel Embedding**: R=encrypted message data, G=encrypted AES key, B=RSA private key

### Encryption Architecture

- **Hybrid System**: RSA-2048 for key exchange + AES-256-CFB for message encryption
- **EncryptionHandler**: Generates RSA key pair, random AES key/IV, encrypts message, encrypts AES key with RSA public key
- **Key Embedding**: Private key stripped of PEM headers, embedded in blue channel for decryption
- **Security**: Each encode operation generates new RSA keys and random IV for forward secrecy

### Configuration System

- `config.json` loaded via inherited `TemplateServer.load_config()` method
- Validated using `SteganographerServerConfig` (extends `TemplateServerConfig`)
- **Steganography Config**: `dct_block_size`, `dct_coefficient`, `dct_quantization_factor`, `private_key_size`, `iv_size`, `aes_key_size`
- Environment variables in `.env` (API_TOKEN_HASH only, never commit)
- Default values defined in `constants.py`

### API Endpoints

All endpoints require `X-API-Key` authentication and return JSON with code/message/timestamp:

- **POST /api/image/encode**: Takes `image_data` (base64), `output_format`, `message`, `algorithm` → returns encoded `image_data`
- **POST /api/image/decode**: Takes `image_data` (base64), `algorithm` → returns `decoded_message`
- **POST /api/image/capacity**: Takes `image_data` (base64), `algorithm` → returns `capacity_characters`

## Developer Workflows

### Essential Commands

```powershell
# Setup (first time)
uv sync                          # Install dependencies
uv run generate-new-token        # Generate API key, save hash to .env

# Development
uv run python-steganographer     # Start server (https://localhost:443/api)
uv run -m pytest                 # Run tests with coverage
uv run -m mypy .                 # Type checking
uv run -m ruff check .           # Linting

# Docker Development
docker compose up --build -d     # Build + start all services
docker compose logs -f python-steganographer  # View logs
docker compose down              # Stop and remove containers
```

### Testing Patterns

- **Fixtures**: All tests use `conftest.py` fixtures, auto-mock `pyhere.here()` to tmp_path
- **Algorithm Testing**: Tests for both LSB and DCT algorithms with various image sizes
- **Encryption Testing**: Verify RSA+AES encryption/decryption roundtrip
- **Integration Tests**: Test API endpoints via FastAPI TestClient with auth headers
- **Coverage Target**: 99%+ (currently achieved)
- **Pattern**: Unit tests per module (test_algorithms.py, test_encryption.py, etc.) + integration tests (test_server.py)

### Docker Multi-Stage Build

- **Stage 1 (builder)**: Uses Python 3.13-slim base, installs Git and `uv`, copies source files, builds wheel with `uv build --wheel`
- **Stage 2 (runtime)**: Python 3.13-slim base, installs Git and `uv`, installs wheel with `uv pip install --system`, copies configuration files
- **Runtime Files**: Copies `.here`, `LICENSE`, `README.md` from installed wheel site-packages to `/app` directory
- **Startup Script**: `/app/start.sh` generates API token if `API_TOKEN_HASH` env var is missing, then starts server with `--port $PORT`
- **Directories**: Creates `/app/logs` for log storage, `/app/configuration` for config files
- **Volumes**: Uses named volumes for `certs` and `logs` persistence across container restarts
- **Environment Variables**: `API_TOKEN_HASH` (optional, generated if missing), `PORT` (defaults to 443)
- **Health Check**: Python script curls `/api/health` with unverified SSL context, 30s interval, 10s timeout, 3 retries, 10s start period
- **Container**: Runs as root user (no user switching implemented)

## Project-Specific Conventions

### Code Organization

- **Core Modules**: `server.py` (SteganographerServer), `image.py` (Image operations), `algorithms.py` (LSB/DCT)
- **Encryption**: `encryption.py` (EncryptionHandler for RSA+AES), `helpers.py` (byte/string conversions)
- **Constants**: All magic numbers in `constants.py` (DCT defaults, key sizes, bit mappings)
- **Models**: Pydantic models for config + API requests/responses in `models.py`

### Steganography Patterns

- **Algorithm Selection**: Use factory methods `Image.lsb()` and `Image.dct(...)` for algorithm instantiation
- **Channel Operations**: R=message data, G=AES key, B=private key (consistent across encode/decode)
- **Capacity Checks**: Always validate message length against channel capacity before embedding
- **Null Termination**: DCT algorithm uses null terminator to mark end of message

### Security Patterns

- **Never log secrets**: Print tokens via `print()`, not `logger` (inherited from python-template-server)
- **Key Generation**: New RSA keys and random IV for each encode operation
- **PEM Headers**: Strip headers before embedding, add back during decoding
- **Base64 Encoding**: All byte data converted to/from base64 for API transmission

### API Design

- **Prefix**: All routes under `/api` (inherited from TemplateServer)
- **Authentication**: Applied via `add_authenticated_route()` method (includes rate limiting)
- **Response Models**: All endpoints return `BaseResponse` subclasses with code/message/timestamp
- **Error Handling**: Try/except blocks in endpoints return 500 with empty data on failure
- **Base64 I/O**: All image data transmitted as base64 strings in JSON

### CI/CD Validation

All PRs must pass:

**CI Workflow (ci.yml):**

1. `validate-pyproject` - pyproject.toml schema validation
2. `ruff` - linting (120 char line length, strict rules in pyproject.toml)
3. `mypy` - 100% type coverage (strict mode)
4. `pytest` - 99% code coverage, HTML report uploaded
5. `bandit` - security check for Python code
6. `pip-audit` - audit dependencies for known vulnerabilities
7. `version-check` - pyproject.toml vs uv.lock version consistency

**Build Workflow (build.yml):**

1. `build-wheel` - Create and upload Python wheel package
2. `verify-structure` - Verify installed package structure and required files

**Docker Workflow (docker.yml):**

1. `build` - Build and test development image with docker compose

## Quick Reference

### Key Files

- `server.py` - SteganographerServer class (extends TemplateServer) with encode/decode/capacity endpoints
- `main.py` - Application entry point, instantiates SteganographerServer
- `image.py` - Image class with factory methods for LSB/DCT algorithms
- `algorithms.py` - AlgorithmBase, LSBAlgorithm, DCTAlgorithm classes
- `encryption.py` - EncryptionHandler for hybrid RSA+AES encryption
- `helpers.py` - Utility functions for byte/string/bit conversions
- `models.py` - All Pydantic models (SteganographerServerConfig, API request/response models)
- `constants.py` - DCT defaults, key sizes, bit mappings
- `docker-compose.yml` - Container stack

### Key Algorithms

**LSB (Least Significant Bit)**:

- Capacity: `(width × height) / 7` characters per channel
- Method: Modify LSB of each pixel (7 bits per character)
- Best for: PNG and other lossless formats
- Vulnerable to: JPEG compression, image transformations

**DCT (Discrete Cosine Transform)**:

- Capacity: 1 bit per block (default 8×8 blocks)
- Method: Modify DCT coefficient (default: coefficient 3) in each block
- Best for: JPEG and scenarios with compression
- Config: `dct_block_size`, `dct_coefficient`, `dct_quantization_factor`

### Environment Variables

- `API_TOKEN_HASH` - SHA-256 hash of API token (only var required, inherited from python-template-server)

### Configuration Files

- `configuration/config.json` - Server and steganography configuration
- `.env` - API token hash (auto-created by generate-new-token)
- **Steganography Settings**: DCT parameters, RSA key size (2048), IV size (16), AES key size (32)
