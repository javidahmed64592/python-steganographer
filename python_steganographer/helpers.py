"""Helper methods for the steganography application."""

import base64

import numpy as np

from python_steganographer.constants import BIT_MAP, NUM_BITS


def bytes_to_str(msg: bytes) -> str:
    """Convert bytes to a base64 encoded string.

    :param bytes msg: Bytes to convert
    :return str: Base64 encoded string representation of the bytes
    """
    return base64.b64encode(msg).decode("utf-8")


def str_to_bytes(msg: str) -> bytes:
    """Convert a base64 encoded string to bytes.

    :param str msg: Base64 encoded string to convert
    :return bytes: Bytes representation of the base64 encoded string
    """
    padded_msg = msg + "=" * (-len(msg) % 4)
    return base64.b64decode(padded_msg.encode("utf-8"))


def char_to_byte_list(char: str) -> list[int]:
    """Convert an ASCII character to a list of bits of length 7.

    ```
    char_to_byte_list("a") # [1, 1, 0, 0, 0, 0, 1]
    ```

    :param str char:
        Single ASCII character to convert to a list of bits
    :return list[int]:
        List of bits representing the ASCII character, padded to length 7
    """
    char_bin = bin(ord(char))
    char_bytes = char_bin[2:]
    padding = [0] * (NUM_BITS - len(char_bytes))
    return padding + [int(b) for b in char_bytes]


def msg_to_bytes_list(msg: str) -> list[int]:
    """Convert an ASCII message to a list of bytes of length (7 * length of message).

    :param str msg:
        Sequence of ASCII characters
    :return list[int]:
        List of bytes representing the ASCII message
    """
    byte_list = []
    for char in msg:
        byte_list += char_to_byte_list(char)
    return byte_list


def byte_list_to_char(byte_list: list[int]) -> str:
    """Convert a list of bits to a character.

    ```
    byte_list_to_char([1, 1, 0, 0, 0, 0, 1]) # "a"
    ```

    :param list[int] byte_list:
        Character represented as a list of bits (up to 7 bits)
    :return str:
        Single ASCII character
    """
    if len(byte_list) < NUM_BITS:
        byte_list = [0] * (NUM_BITS - len(byte_list)) + byte_list
    elif len(byte_list) > NUM_BITS:
        byte_list = byte_list[:NUM_BITS]

    return chr(int(np.sum(BIT_MAP * byte_list)))


def bytes_list_to_msg(bytes_list: list[int]) -> str:
    """Convert a list of bytes to a message.

    :param list[int] bytes_list:
        Characters represented as a list of bits
    :return str:
        Message in bytes_list
    """
    char_list = []
    i = 0
    while i < len(bytes_list):
        char_byte = bytes_list[i : i + NUM_BITS]
        if not char_byte:
            break

        char = byte_list_to_char(char_byte)
        if ord(char) == 0:
            break

        char_list.append(char)
        i += NUM_BITS

    return "".join(char_list)
