"""
© Ocado Group
Created on 18/03/2024 at 14:06:07(+00:00).
"""

import re
import typing as t

from rest_framework.decorators import action as _action


def action(**kwargs):
    """
    Wraps DRF's @action decorator to support converting an action's name to a
    kebab-cased url-path. Furthermore, names can also be converted to
    url-sub-paths. The url-path will only be set if not specified.

    Action names are converted to url-paths using the following convention:

    - 1 underscore is converted to a dash. For example:
        name: "a_b" -> url-path: "a-b"
    - 2 underscores are converted to a forward slash. For example:
        name: "a__b" -> url-path: "a/b"
    - 3+ underscores are not supported and will raise an assertion error.
    """

    def wrapper(handler: t.Callable):
        # Set handler name as url-path if url-path is not specified.
        if "url_path" not in kwargs:
            url_path = handler.__name__
            assert not re.match(
                r"_{3,}", url_path
            ), "Cannot have 3+ underscores in action's name."

            # Replace double underscores with sub-path. For example:
            #   name: "messages__replies" -> url-path: "messages/replies"
            url_path = re.sub(r"_{2}", "/", url_path)

            # Replace single underscore with dash. For example:
            #   name: "messages__replies" -> url-path: "messages/replies"
            url_path = re.sub(r"_", "-", url_path)

            kwargs["url_path"] = url_path

        return _action(**kwargs)(handler)

    return wrapper
