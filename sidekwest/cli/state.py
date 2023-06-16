
from typing import Optional

from sidekwest import IntoPath
from sidekwest.storage.base import StorageEngine
from sidekwest.storage.local_file import LocalStorage


class CommandState:
    def __init__(self) -> None:
        self.enable_local: Optional[bool] = None
        self.local_opts: LocalStorageOptions = LocalStorageOptions()

    def to_engines(self) -> list[StorageEngine]:
        engines: list[StorageEngine] = []
        if self.enable_local:
            engines.append(self.local_opts.to_engine())
        return engines


class LocalStorageOptions:
    def __init__(self) -> None:
        self.storage_dir: Optional[IntoPath] = None

    def to_engine(self) -> LocalStorage:
        return LocalStorage(self.storage_dir)
