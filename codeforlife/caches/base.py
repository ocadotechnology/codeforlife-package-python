"""
© Ocado Group
Created on 28/01/2026 at 16:52:19(+00:00).
"""

import typing as t

from django.core.cache import cache

V = t.TypeVar("V")


class BaseCache(t.Generic[V]):
    """Base class which helps to get and set cache values."""

    timeout: int | None = None

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
            timeout=timeout or cls.timeout,
            version=version,
        )

    @classmethod
    def delete(
        cls,
        key: str,
        version: t.Optional[int] = None,
    ):
        """
        Delete a key from the cache and return whether it succeeded, failing
        silently.
        """
        cache.delete(
            key=key,
            version=version,
        )
