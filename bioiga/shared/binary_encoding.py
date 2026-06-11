"""
bioiga.shared.binary_encoding
==============================
Standard 10-bit-per-variable binary decoding for the BioIGA-2D suite.

All binary agent classes (Particle, Firefly, Wolf, Bat) delegate their
``decode_position`` logic to :func:`decode_binary_10bit` so there is
exactly one canonical implementation in the suite.
"""

import numpy as np


def decode_binary_10bit(position: np.ndarray, bounds: tuple) -> np.ndarray:
    """
    Decode a binary chromosome into a real-valued vector.

    Each continuous variable is encoded with **10 bits**, so a chromosome
    of length D encodes ``D // 10`` real variables.  The bit-string for
    each variable is converted to a non-negative integer, then linearly
    mapped to ``[low, high]``.

    Parameters
    ----------
    position : np.ndarray
        Binary array of shape (D,) with values in {0, 1}.
    bounds : tuple
        ``(low, high)`` — the continuous decoding range.

    Returns
    -------
    real_vector : np.ndarray
        Decoded continuous values of shape ``(D // 10,)`` in
        ``[low, high]``.

    Example
    -------
    >>> import numpy as np
    >>> from bioiga.shared.binary_encoding import decode_binary_10bit
    >>> pos = np.random.randint(0, 2, 100)
    >>> vals = decode_binary_10bit(pos, (-5.12, 5.12))
    >>> vals.shape
    (10,)
    """
    bits_per_var = 10
    num_vars = len(position) // bits_per_var
    real_vector = np.zeros(num_vars)

    low, high = bounds
    max_int = (1 << bits_per_var) - 1  # 1023

    for i in range(num_vars):
        start = i * bits_per_var
        end = start + bits_per_var
        bits = position[start:end]

        val_int = 0
        for bit in bits:
            val_int = (val_int << 1) | int(bit)

        real_vector[i] = low + (val_int / max_int) * (high - low)

    return real_vector
