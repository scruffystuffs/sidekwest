import json
from pathlib import Path
from typing import Optional

from sidekwest import IntoPath

from .base import StorageEngine

DEFAULT_LOCATION = ".storage"
ENCODING = "utf-8"


class LocalStorage(StorageEngine):
    def __init__(self, storage_dir: Optional[IntoPath] = None) -> None:
        if storage_dir is None:
            storage_dir = DEFAULT_LOCATION
        self._storage_dir = Path(storage_dir)
        if not self._storage_dir.is_dir():
            self._storage_dir.mkdir(0o755, parents=True, exist_ok=True)

    def load_state(self, storage_key: str) -> dict:
        try:
            with self._resolve_filepath(storage_key).open(
                "r", encoding=ENCODING
            ) as jfp:
                state: dict = json.load(jfp)
        except FileNotFoundError:
            state = {}
        return state

    def save_state(self, storage_key: str, data: dict):
        with self._resolve_filepath(storage_key).open("w", encoding=ENCODING) as jfp:
            json.dump(data, jfp, sort_keys=True)

    def _resolve_filepath(self, storage_key: str) -> Path:
        return self._storage_dir / f"{storage_key}.json"
