[![python](https://img.shields.io/badge/Python-3.13-3776AB.svg?style=flat&logo=python&logoColor=ffd343)](https://docs.python.org/3.13/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![CI](https://img.shields.io/github/actions/workflow/status/javidahmed64592/python-steganographer/ci.yml?branch=main&style=flat-square&label=CI&logo=github)](https://github.com/javidahmed64592/python-steganographer/actions/workflows/ci.yml)
[![Build](https://img.shields.io/github/actions/workflow/status/javidahmed64592/python-steganographer/build.yml?branch=main&style=flat-square&label=Build&logo=github)](https://github.com/javidahmed64592/python-steganographer/actions/workflows/build.yml)
[![Docker](https://img.shields.io/github/actions/workflow/status/javidahmed64592/python-steganographer/docker.yml?branch=main&style=flat-square&label=Docker&logo=github)](https://github.com/javidahmed64592/python-steganographer/actions/workflows/docker.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<!-- omit from toc -->
# Python Steganographer

A production-ready FastAPI steganography server which uses [python-template-server](https://github.com/javidahmed64592/python-template-server).

<!-- omit from toc -->
## Table of Contents
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Generate API Token](#generate-api-token)
  - [Run the Server](#run-the-server)
- [Documentation](#documentation)
- [License](#license)

## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```sh
# Clone the repository
git clone https://github.com/javidahmed64592/python-steganographer.git
cd python-steganographer

# Install dependencies
uv sync --extra dev
```

### Generate API Token

```sh
uv run generate-new-token
# ⚠️ Save the displayed token - you'll need it for API requests!
```

### Run the Server

```sh
# Start the server
uv run python-steganographer

# Server runs at https://localhost:443/api
# Swagger UI: https://localhost:443/api/docs
# Redoc: https://localhost:443/api/redoc
# Health check: curl -k https://localhost:443/api/health
# Login (requires authentication): curl -k -H "X-API-Key: your-token-here" https://localhost:443/api/login
```

## Documentation

- **[API Documentation](./docs/API.md)**: API architecture and endpoints
- **[Software Maintenance Guide](./docs/SMG.md)**: Development setup, configuration
- **[Workflows](./docs/WORKFLOWS.md)**: CI/CD pipeline details

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
