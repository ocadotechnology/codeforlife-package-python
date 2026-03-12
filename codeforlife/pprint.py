"""
© Ocado Group
Created on 11/03/2026 at 14:42:45(+00:00).

Pretty-printing utilities for terminal output.
"""

import os
import typing as t
from enum import Enum

Write: t.TypeAlias = t.Callable[[str], None]


class ANSI(Enum):
    """ANSI escape codes for styling terminal output."""

    RESET = "\033[0m"

    BLACK = "\033[30m"
    WHITE = "\033[37m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"

    YELLOW = "\033[33m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"

    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    OVERLINE = "\033[53m"


class Style:
    """A callable class that applies styles to messages."""

    def __init__(self, apply: t.Callable[[str], str], write: Write = print):
        self.apply = apply
        self.write = write

    def __call__(self, message: str, *args, **kwargs):
        styled_message = self.apply(message)
        self.write(styled_message, *args, **kwargs)

    @classmethod
    def ansi(cls, code: ANSI, write: Write = print):
        """Create a style that applies the given ANSI code to messages.

        Args:
            code: The ANSI code to apply.
            write: The function to use for writing the styled message.

        Returns:
            A style that applies the given ANSI code to messages.
        """

        def apply(message: str):
            return code.value + message + ANSI.RESET.value

        return cls(apply, write)

    @classmethod
    def combine(cls, styles: t.List["Style"], write: Write = print):
        """Combine multiple styles into a single style.

        Args:
            styles: The styles to combine.
            write: The function to use for writing the styled message.

        Returns:
            A style that applies all the given styles to messages.
        """

        def apply(message: str):
            for style in styles:
                message = style.apply(message)

            return message

        return cls(apply, write)


# pylint: disable-next=too-many-instance-attributes
class PrettyPrinter:
    """A utility class for pretty-printing styled messages to the terminal."""

    def __init__(self, write: Write):
        self.write = write

        # Black and white.
        self.black = Style.ansi(ANSI.BLACK, write)
        self.white = Style.ansi(ANSI.WHITE, write)

        # Red, green, and blue.
        self.red = Style.ansi(ANSI.RED, write)
        self.green = Style.ansi(ANSI.GREEN, write)
        self.blue = Style.ansi(ANSI.BLUE, write)

        # Cyan, magenta, and yellow.
        self.cyan = Style.ansi(ANSI.CYAN, write)
        self.magenta = Style.ansi(ANSI.MAGENTA, write)
        self.yellow = Style.ansi(ANSI.YELLOW, write)

        # Common text styles.
        self.bold = Style.ansi(ANSI.BOLD, write)
        self.underline = Style.ansi(ANSI.UNDERLINE, write)
        self.overline = Style.ansi(ANSI.OVERLINE, write)

        # Status styles.
        self.success = Style.combine([self.green, self.bold], write)
        self.error = Style.combine([self.red, self.bold], write)
        self.warn = self.warning = Style.combine(
            [self.yellow, self.bold], write
        )
        self.info = self.notice = Style.combine([self.blue, self.bold], write)

        # Heading styles.
        h1 = Style(
            lambda message: "\n".join(
                [self.divider("="), message, self.divider("=")]
            ),
            write,
        )
        self.h1 = Style.combine([h1, self.bold], write)
        h2 = Style(
            lambda message: "\n".join(
                [self.divider("-"), message, self.divider("-")]
            ),
            write,
        )
        self.h2 = Style.combine([h2, self.bold], write)
        self.h3 = Style.combine(
            [self.overline, self.underline, self.bold], write
        )

    def divider(self, char="-", default_columns=80):
        # pylint: disable=line-too-long
        """Write a divider line with the specified character.

        Args:
            default_columns: The default number of columns to use if the terminal width cannot be determined.
            char: The character to use for the divider.
        """
        # pylint: enable=line-too-long
        try:
            columns = os.get_terminal_size().columns
        except OSError:
            columns = default_columns

        return char * columns

    def indent(self, count: int, spaces=2, char=" "):
        """Write an indentation of the specified number of spaces.

        Args:
            count: The number of indentation levels.
            spaces: The number of spaces per indentation level.
            char: The character to use for indentation.
        """
        return char * count * spaces


pprint = PrettyPrinter(write=print)
