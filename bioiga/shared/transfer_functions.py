"""
bioiga.shared.transfer_functions
=================================
Transfer function library for binary optimization.

Converts continuous velocity vectors into per-bit flip probabilities and
applies the resulting stochastic position update.  Four shapes are
supported (S, V, U, Z), each with an optional time-varying schedule.

This is the single canonical implementation used by all binary
algorithm packages in the BioIGA-2D suite (mpmbso, mpbfa, mpbgwo, mpbba).
"""

import numpy as np


def apply_transfer_function(
    velocity: np.ndarray,
    tf_type: str,
    is_time_varying: bool,
    gen: int,
    max_gens: int,
) -> tuple:
    """
    Apply a transfer function to a continuous velocity vector.

    Parameters
    ----------
    velocity : np.ndarray
        Continuous velocity array of shape (D,).
    tf_type : str
        Transfer function identifier. One of:
        ``"s_shape"``, ``"v_shape"``, ``"u_shape"``, ``"z_shape"``
        (case-insensitive; only the first letter is checked).
    is_time_varying : bool
        If True, scale velocity by a linearly decaying factor alpha(t)
        that decreases from 2.0 (exploration) to 0.1 (exploitation).
    gen : int
        Current generation index (0-indexed).
    max_gens : int
        Total number of generations in the run.

    Returns
    -------
    T : np.ndarray
        Array of flip probabilities in [0, 1], shape (D,).
    is_absolute : bool
        True  → S-shape "absolute" position update rule.
        False → V/U/Z "bit-inversion" position update rule.

    Raises
    ------
    ValueError
        If ``tf_type`` is not one of the four supported options.

    Transfer function formulas
    --------------------------
    +----------+------------------------------+------------------+
    | Name     | Formula                      | Update rule      |
    +----------+------------------------------+------------------+
    | s_shape  | T(v) = 1/(1+e^-v)            | absolute set     |
    | v_shape  | T(v) = |tanh(v)|             | bit inversion    |
    | u_shape  | T(v) = min(1, v^2)           | bit inversion    |
    | z_shape  | T(v) = sqrt(1 - 20^-|v|)    | bit inversion    |
    +----------+------------------------------+------------------+
    """
    if is_time_varying:
        alpha = 2.0 - 1.9 * (gen / float(max(max_gens - 1, 1)))
    else:
        alpha = 1.0

    scaled_v = alpha * velocity
    tf = tf_type.lower().strip()

    if tf.startswith("s"):
        T = 1.0 / (1.0 + np.exp(-np.clip(scaled_v, -500, 500)))
        return T, True

    elif tf.startswith("v"):
        T = np.abs(np.tanh(scaled_v))
        return T, False

    elif tf.startswith("u"):
        T = np.minimum(1.0, scaled_v**2)
        return T, False

    elif tf.startswith("z"):
        val = np.clip(20.0 ** (-np.abs(scaled_v)), 1e-12, 1.0)
        T = np.sqrt(1.0 - val)
        return T, False

    else:
        raise ValueError(
            f"Unknown transfer function '{tf_type}'. "
            "Valid options: 's_shape', 'v_shape', 'u_shape', 'z_shape'."
        )


def apply_position_update(
    position: np.ndarray,
    T: np.ndarray,
    is_absolute: bool,
) -> np.ndarray:
    """
    Update a binary position vector using a probability array from a
    transfer function.

    Parameters
    ----------
    position : np.ndarray
        Current binary position of shape (D,) with values in {0, 1}.
    T : np.ndarray
        Flip (or set-to-1) probability array of shape (D,), from
        :func:`apply_transfer_function`.
    is_absolute : bool
        If True  → S-shape rule: ``x[d] = 1`` if ``U < T[d]``, else 0.
        If False → Inversion rule: flip ``x[d]`` if ``U < T[d]``.

    Returns
    -------
    new_position : np.ndarray
        Updated binary position of shape (D,).
    """
    u = np.random.rand(len(position))
    new_position = position.copy()

    if is_absolute:
        new_position = (u < T).astype(int)
    else:
        flip_mask = u < T
        new_position[flip_mask] = 1 - new_position[flip_mask]

    return new_position
