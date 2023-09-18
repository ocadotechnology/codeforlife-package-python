import os


def test_import():
    """Basic test to ensure importing the package does not raise an error."""
    import codeforlife


def test_import_settings():
    os.environ["SERVICE_NAME"] = "example"
    from codeforlife import settings
