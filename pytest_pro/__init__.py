"""PyTest Pro - Python öğretimi için dinamik ölçme ve değerlendirme sistemi."""
__version__ = "3.1.0"


def create_app(*args, **kwargs):
    from .app import create_app as _create_app
    return _create_app(*args, **kwargs)
