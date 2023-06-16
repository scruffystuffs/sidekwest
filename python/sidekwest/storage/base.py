from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Self, TypeVar

# pylint: disable=invalid-name
TStorable_co = TypeVar("TStorable_co", bound="Storable", covariant=True)


class EngineSaveError(IOError):
    pass


class MissingState(KeyError):
    pass


class Storable(ABC):
    @classmethod
    @abstractmethod
    def storage_key(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def from_json(cls, data: dict) -> Self:
        pass

    @classmethod
    def default(cls) -> Self:
        raise MissingState(KeyError)

    @classmethod
    def load_json(cls, engine: StorageEngine) -> Self:
        key = cls.storage_key()
        state = engine.load_state(key)
        if state is None:
            return cls.default()
        return cls.from_json(state)

    @abstractmethod
    def to_json(self) -> dict:
        pass

    @classmethod
    def fetch(cls, engines: list[StorageEngine]) -> Self:
        if not engines:
            raise ValueError("No engines enabled")
        last_err: Optional[MissingState] = None
        for engine in engines:
            try:
                return cls.load_json(engine)
            except MissingState as exc:
                last_err = exc
        if last_err is None:
            assert (
                False
            ), "Insanity: no error was recorded, but no engine succeeded in loading state"
        raise last_err

    def save(self, engines: list[StorageEngine]):
        errs: list[Exception] = []
        for engine in engines:
            try:
                data = self.to_json()
                engine.save_state(self.storage_key(), data)
            except EngineSaveError as exc:
                errs.append(exc)
        if errs:
            raise errs[0]


class StorageEngine(ABC):
    @abstractmethod
    def load_state(self, storage_key: str) -> dict:
        pass

    @abstractmethod
    def save_state(self, storage_key: str, data: dict):
        pass
