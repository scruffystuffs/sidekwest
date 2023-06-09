from __future__ import annotations

from .base import fetch_state, Storable, StorageEngine, MissingState
from .local_file import LocalStorage

DEFAULT_ENGINES = [
    LocalStorage('.')
]
