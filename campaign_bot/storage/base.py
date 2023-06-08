from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Self, Type, TypeVar

# pylint: disable=invalid-name
TStorable_co = TypeVar("TStorable_co", bound="Storable", covariant=True)


def fetch_state(
    klass: Type[TStorable_co], engines: list[StorageEngine]
) -> TStorable_co:
    last_err: Optional[MissingState] = None
    for engine in engines:
        try:
            return klass.load_json(engine)
        except MissingState as exc:
            last_err = exc
    if last_err is None:
        assert (
            False
        ), "Insanity: no error was recorded, but no engine succeeded in loading state"
    raise last_err


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
    @abstractmethod
    def default(cls) -> Self:
        raise MissingState(KeyError)

    @classmethod
    def load_json(cls, engine: StorageEngine) -> Self:
        key = cls.storage_key()
        state = engine.load_state(key)
        substate = state
        if state is None:
            return cls.default()
        return cls.from_json(substate)


class StorageEngine(ABC):
    @abstractmethod
    def load_state(self, storage_key: str) -> dict:
        pass

    @abstractmethod
    def save_state(self, data: dict):
        pass
