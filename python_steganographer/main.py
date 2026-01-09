"""FastAPI steganographer server using uvicorn."""

from python_steganographer.server import SteganographerServer


def run() -> None:
    """Serve the FastAPI application using uvicorn.

    :raise SystemExit: If configuration fails to load or SSL certificate files are missing
    """
    server = SteganographerServer()
    server.run()
