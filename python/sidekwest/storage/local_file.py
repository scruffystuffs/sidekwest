import json
from pathlib import Path
from typing import Optional

import aiofiles

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

    async def load_state(self, storage_key: str) -> dict:
        try:
            async with aiofiles.open(
                self._resolve_filepath(storage_key), "r", encoding=ENCODING
            ) as jfp:
                str_data = await jfp.read()
            state: dict = json.loads(str_data)
        except FileNotFoundError:
            state = {}
        return state

    async def save_state(self, storage_key: str, data: dict):
        str_data = json.dumps(data, sort_keys=True)
        async with aiofiles.open(
            self._resolve_filepath(storage_key), "w", encoding=ENCODING
        ) as jfp:
            await jfp.write(str_data)

    def _resolve_filepath(self, storage_key: str) -> Path:
        return self._storage_dir / f"{storage_key}.json"
