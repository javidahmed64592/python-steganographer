"""Constants for the steganographer server."""

import numpy as np

MAX_BITS_PER_PIXEL = 8
NUM_BITS = MAX_BITS_PER_PIXEL - 1
BIT_MAP = np.array([2 ** (NUM_BITS - 1 - i) for i in range(NUM_BITS)])
