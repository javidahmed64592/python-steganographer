"""Unit tests for the python_steganographer.helpers module."""

from python_steganographer.helpers import (
    byte_list_to_char,
    bytes_list_to_msg,
    bytes_to_str,
    char_to_byte_list,
    msg_to_bytes_list,
    str_to_bytes,
)


def test_bytes_to_str_and_str_to_bytes() -> None:
    """Test conversion between bytes and string representations."""
    original_bytes = b"Sample bytes for testing"
    encoded_str = bytes_to_str(original_bytes)
    decoded_bytes = str_to_bytes(encoded_str)
    assert original_bytes == decoded_bytes


def test_char_to_byte_list_and_byte_list_to_char() -> None:
    """Test conversion between a character and its byte list representation."""
    original_char = "z"
    byte_list = char_to_byte_list(original_char)
    restored_char = byte_list_to_char(byte_list)
    assert original_char == restored_char


def test_msg_to_bytes_list_and_bytes_list_to_msg() -> None:
    """Test conversion between a message and its byte list representation."""
    original_msg = "hello"
    byte_list = msg_to_bytes_list(original_msg)
    restored_msg = bytes_list_to_msg(byte_list)
    assert original_msg == restored_msg
