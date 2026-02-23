"""
© Ocado Group
Created on 28/01/2026 at 16:52:19(+00:00).
"""

import typing as t

from .base import BaseCache

V = t.TypeVar("V")


class BaseFixedKeyCache(BaseCache[V], t.Generic[V]):
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

    @classmethod
    def delete(  # type: ignore[override]
        cls,
        version: t.Optional[int] = None,
    ):
        super().delete(
            key=cls.key,
            version=version,
        )

    # pylint: enable=arguments-differ
