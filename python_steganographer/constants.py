"""Constants for the steganographer application."""

import numpy as np

MAX_BITS_PER_PIXEL = 8
NUM_BITS = MAX_BITS_PER_PIXEL - 1
BIT_MAP = np.array([2 ** (NUM_BITS - 1 - i) for i in range(NUM_BITS)])

DEFAULT_BLOCK_SIZE = 8
DEFAULT_DCT_COEFFICIENT = 3  # Which DCT coefficient to modify (1-indexed, avoid DC component)
DEFAULT_QUANTIZATION_FACTOR = 10  # Quantization factor for DCT coefficients

DEFAULT_PRIVATE_KEY_SIZE = 2048  # RSA key size in bits
DEFAULT_IV_SIZE = 16  # AES block size in bytes
DEFAULT_AES_KEY_SIZE = 32  # AES-256 key size in bytes
