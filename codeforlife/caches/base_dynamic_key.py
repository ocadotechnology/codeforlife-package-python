"""
© Ocado Group
Created on 28/01/2026 at 16:52:19(+00:00).
"""

import typing as t

from .base import BaseCache

V = t.TypeVar("V")
K = t.TypeVar("K")


class BaseDynamicKeyCache(BaseCache[V], t.Generic[K, V]):
    """Base class which helps to get and set cache values with a dynamic key."""

    @staticmethod
    def make_key(key: K) -> str:
        """Make the cache key from the key's data."""
        raise NotImplementedError()

    @classmethod
    def get(  # type: ignore[override]
        cls,
        key: K,
        default: t.Optional[V] = None,
        version: t.Optional[int] = None,
    ) -> t.Optional[V]:
        return super().get(
            key=cls.make_key(key),
            default=default,
            version=version,
        )

    @classmethod
    def set(  # type: ignore[override]
        cls,
        key: K,
        value: V,
        timeout: t.Optional[int] = None,
        version: t.Optional[int] = None,
    ):
        super().set(
            key=cls.make_key(key),
            value=value,
            timeout=timeout,
            version=version,
        )

    @classmethod
    def delete(  # type: ignore[override]
        cls,
        key: K,
        version: t.Optional[int] = None,
    ):
        super().delete(
            key=cls.make_key(key),
            version=version,
        )
