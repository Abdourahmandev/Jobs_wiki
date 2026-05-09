from importlib import import_module
from ingestion.un import __all__ as exported_names


def test_un_package_exports_reliefweb_modules():
    assert "reliefweb_client" in exported_names

    # verify the module is actually importable
    module = import_module("ingestion.un.reliefweb_client")
    assert module is not None
