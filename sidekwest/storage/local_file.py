import json
from os import PathLike
from pathlib import Path
from typing import Optional

from .base import StorageEngine


class LocalStorage(StorageEngine):
    def __init__(self, filepath: PathLike) -> None:
        self._filepath = Path(filepath)
        assert self._filepath.is_dir()
        self._cache: Optional[dict] = None

    def load_state(self, storage_key: str) -> dict:
        if self._cache is not None:
            return self._cache
        with self._filepath.joinpath(f"{storage_key}.json").open(
            "r", encoding="utf-8"
        ) as jfp:
            state = json.load(jfp)
        self._cache = state
        return state
