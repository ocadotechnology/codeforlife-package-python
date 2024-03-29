"""
© Ocado Group
Created on 15/01/2024 at 15:32:54(+00:00).

Reusable type hints.
"""

import typing as t

Args = t.Tuple[t.Any, ...]
KwArgs = t.Dict[str, t.Any]

JsonList = t.List["JsonValue"]
JsonDict = t.Dict[str, "JsonValue"]
JsonValue = t.Union[None, int, str, bool, JsonList, JsonDict]

DataDict = t.Dict[str, t.Any]
OrderedDataDict = t.OrderedDict[str, t.Any]
