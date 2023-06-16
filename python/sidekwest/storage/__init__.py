from __future__ import annotations

from .base import Storable, StorageEngine, MissingState
from .local_file import LocalStorage

DEFAULT_ENGINES = [
    LocalStorage()
]
