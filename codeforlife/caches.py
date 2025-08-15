"""
© Ocado Group
Created on 11/08/2025 at 11:07:45(+01:00).
"""

import typing as t

from django.core.cache import cache

K = t.TypeVar("K")
V = t.TypeVar("V")


class BaseValueCache(t.Generic[V]):
    """Base class which helps to get and set cache values."""

    @classmethod
    def get(
        cls,
        key: str,
        default: t.Optional[V] = None,
        version: t.Optional[int] = None,
    ) -> t.Optional[V]:
        """
        Fetch a given key from the cache. If the key does not exist, return
        default, which itself defaults to None.
        """
        return cache.get(
            key=key,
            default=default,
            version=version,
        )

    @classmethod
    def set(
        cls,
        key: str,
        value: V,
        timeout: t.Optional[int] = None,
        version: t.Optional[int] = None,
    ):
        """
        Set a value in the cache. If timeout is given, use that timeout for the
        key; otherwise use the default cache timeout.
        """
        cache.set(
            key=key,
            value=value,
            timeout=timeout,
            version=version,
        )


class BaseFixedKeyValueCache(BaseValueCache[V], t.Generic[V]):
    """Base class which helps to get and set cache values with a fixed key."""

    key: str

    # pylint: disable=arguments-differ

    @classmethod
    def get(  # type: ignore[override]
        cls,
        default: t.Optional[V] = None,
        version: t.Optional[int] = None,
    ) -> t.Optional[V]:
        return super().get(
            key=cls.key,
            default=default,
            version=version,
        )

    @classmethod
    def set(  # type: ignore[override]
        cls,
        value: V,
        timeout: t.Optional[int] = None,
        version: t.Optional[int] = None,
    ):
        super().set(
            key=cls.key,
            value=value,
            timeout=timeout,
            version=version,
        )

    # pylint: enable=arguments-differ


class BaseDynamicKeyValueCache(BaseValueCache[V], t.Generic[K, V]):
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
