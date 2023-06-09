import json
from os import PathLike
from pathlib import Path
from typing import TypeAlias

from .base import StorageEngine

IntoPath: TypeAlias = str | PathLike[str]

class LocalStorage(StorageEngine):
    def __init__(self, storage_dir: IntoPath) -> None:
        self._storage_dir = Path(storage_dir)
        assert self._storage_dir.is_dir()

    def load_state(self, storage_key: str) -> dict:
        with self._resolve_filepath(storage_key).open("r", encoding="utf-8") as jfp:
            state: dict = json.load(jfp)
        return state

    def save_state(self, storage_key: str, data: dict):
        with self._resolve_filepath(storage_key).open("w", encoding="utf-8") as jfp:
            json.dump(data, jfp, sort_keys=True)

    def _resolve_filepath(self, storage_key: str) -> Path:
        return self._storage_dir / f"{storage_key}.json"
