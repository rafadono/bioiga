"""
mpbfa.transfer_functions
========================
Redirects to the canonical suite implementation in bioiga.shared.

All binary transfer function logic lives in a single place:
:mod:`bioiga.shared.transfer_functions`.
"""
from bioiga.shared.transfer_functions import apply_transfer_function, apply_position_update

__all__ = ["apply_transfer_function", "apply_position_update"]
