"""
bioiga — BioIGA-2D Evolutionary IGA Suite
==========================================

Install the full suite from the project root::

    pip install -e .

Then import algorithms directly from their packages::

    from mpmbso import MPMBPSOAlgorithm, MPMBPSOConfig
    from mpga   import MPGAAlgorithm,   MPGAConfig
    from mpbfa  import MPBFAAlgorithm,  MPBFAConfig
    from mpbgwo import MPBGWOAlgorithm, MPBGWOConfig
    from mpbba  import MPBBAAlgorithm,  MPBBAConfig

Or via this meta-package::

    from bioiga import MPMBPSOAlgorithm, MPGAAlgorithm, ...

Shared utilities (used internally by all packages)::

    from bioiga.shared import apply_transfer_function, ring_migrate, calculate_auc
"""


def __getattr__(name: str):
    """
    Lazy attribute resolution so that ``from bioiga import MPGAAlgorithm``
    works without causing circular import issues at module load time.
    """
    _mpmbso = (
        "MPMBPSOConfig", "MPMBPSOAlgorithm", "Particle",
        "MPMBPSOMetricsEvaluator",
    )
    _mpga = (
        "MPGAConfig", "MPGAAlgorithm", "Individual", "MPGAMetricsEvaluator",
    )
    _mpbfa = (
        "MPBFAConfig", "MPBFAAlgorithm", "Firefly", "MPBFAMetricsEvaluator",
    )
    _mpbgwo = (
        "MPBGWOConfig", "MPBGWOAlgorithm", "Wolf", "MPBGWOMetricsEvaluator",
    )
    _mpbba = (
        "MPBBAConfig", "MPBBAAlgorithm", "Bat", "MPBBAMetricsEvaluator",
    )

    if name in _mpmbso:
        import mpmbso
        return getattr(mpmbso, name)
    if name in _mpga:
        import mpga
        return getattr(mpga, name)
    if name in _mpbfa:
        import mpbfa
        return getattr(mpbfa, name)
    if name in _mpbgwo:
        import mpbgwo
        return getattr(mpbgwo, name)
    if name in _mpbba:
        import mpbba
        return getattr(mpbba, name)

    raise AttributeError(f"module 'bioiga' has no attribute {name!r}")


try:
    from importlib.metadata import version as _version, PackageNotFoundError as _PNFError
    __version__ = _version("bioiga")
    del _version, _PNFError
except Exception:
    __version__ = "0.2.0"  # fallback during development before install
__author__ = "Rafael Inostroza"

__all__ = [
    # MPMBPSO
    "MPMBPSOConfig", "MPMBPSOAlgorithm", "Particle",
    # MPGA
    "MPGAConfig", "MPGAAlgorithm", "Individual",
    # MPBFA
    "MPBFAConfig", "MPBFAAlgorithm", "Firefly",
    # MPBGWO
    "MPBGWOConfig", "MPBGWOAlgorithm", "Wolf",
    # MPBBA
    "MPBBAConfig", "MPBBAAlgorithm", "Bat",
    # Shared utilities namespace
    "shared",
]
