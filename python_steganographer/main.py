"""FastAPI steganographer server using uvicorn."""

from python_steganographer.server import SteganographerServer


def run() -> None:
    """Serve the FastAPI application using uvicorn."""
    server = SteganographerServer()
    server.run()
