"""Smoke tests — verify the package imports cleanly.

These tests exist so CI is green from day one, before real tests land in
Phases 2-10. Remove or expand as real tests are written.
"""


def test_package_imports():
    """`import bot` works and exposes __version__."""
    import bot

    assert bot.__version__ == "0.1.0"


def test_all_stub_modules_import():
    """Every stub module is importable (no ImportError)."""
    from bot import ai, config, main, reads, store, writes

    assert all(m is not None for m in (ai, config, main, reads, store, writes))
