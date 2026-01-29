[![python](https://img.shields.io/badge/Python-3.13-3776AB.svg?style=flat&logo=python&logoColor=ffd343)](https://docs.python.org/3.13/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![CI](https://img.shields.io/github/actions/workflow/status/javidahmed64592/python-steganographer/ci.yml?branch=main&style=flat-square&label=CI&logo=github)](https://github.com/javidahmed64592/python-steganographer/actions/workflows/ci.yml)
[![Build](https://img.shields.io/github/actions/workflow/status/javidahmed64592/python-steganographer/build.yml?branch=main&style=flat-square&label=Build&logo=github)](https://github.com/javidahmed64592/python-steganographer/actions/workflows/build.yml)
[![Docker](https://img.shields.io/github/actions/workflow/status/javidahmed64592/python-steganographer/docker.yml?branch=main&style=flat-square&label=Docker&logo=github)](https://github.com/javidahmed64592/python-steganographer/actions/workflows/docker.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<!-- omit from toc -->
# Python Steganographer

A production-ready FastAPI steganography server with hybrid encryption built on [python-template-server](https://github.com/javidahmed64592/python-template-server).
Hide encrypted messages in images using LSB or DCT algorithms with comprehensive API security.

<!-- omit from toc -->
## Table of Contents
- [Features](#features)
  - [Steganography Capabilities](#steganography-capabilities)
  - [Security Features](#security-features)
- [Quick Start](#quick-start)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Managing the Container](#managing-the-container)
- [Links](#links)
- [Documentation](#documentation)
- [License](#license)

## Features

### Steganography Capabilities

**Dual Algorithm Support**:
- **LSB (Least Significant Bit)**: High capacity, fast encoding/decoding, ideal for lossless formats (PNG)
- **DCT (Discrete Cosine Transform)**: JPEG-compression resistant, robust to image transformations

**Operations**:
- **Encode**: Hide encrypted messages in images with base64 input/output
- **Decode**: Extract and decrypt hidden messages from images
- **Capacity Check**: Calculate maximum message size for any image

**Flexible Image Handling**:
- Supports multiple formats
- Base64 encoding for API transmission
- Configurable output formats
- Maintains image dimensions and quality

### Security Features

**Hybrid Encryption Architecture**:
- **RSA-2048**: Asymmetric encryption for secure key exchange
- **AES-256-CFB**: Symmetric encryption for message data
- **Random IV**: Unique initialization vector for each operation
- **Multi-Channel Embedding**: Data distributed across RGB channels

## Quick Start

### Installation

Download the latest release from [GitHub Releases](https://github.com/javidahmed64592/python-steganographer/releases).

### Configuration

Rename `.env.example` to `.env` and edit it to configure the server.

- `HOST`: Server host address (default: localhost)
- `PORT`: Server port (default: 443)
- `API_TOKEN_HASH`: Leave blank to auto-generate on first run, or provide your own token hash

### Managing the Container

```sh
# Start the container
docker compose up -d

# Stop the container
docker compose down

# Update to the latest version
docker compose pull && docker compose up -d

# View the logs
docker compose logs -f pi-dashboard
```

**Note:** You may need to add your user to the Docker group and log out/in for permission changes to take effect:
```sh
sudo usermod -aG docker ${USER}
```

## Links

- Access the web application: https://localhost:443
- Server runs at: https://localhost:443/api
- Swagger UI: https://localhost:443/api/docs
- Redoc: https://localhost:443/api/redoc

## Documentation

- **[API Documentation](./docs/API.md)**: API architecture and endpoints
- **[Software Maintenance Guide](./docs/SMG.md)**: Development setup, configuration
- **[Workflows](./docs/WORKFLOWS.md)**: CI/CD pipeline details

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
