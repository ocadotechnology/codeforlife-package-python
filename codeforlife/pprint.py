"""
© Ocado Group
Created on 11/03/2026 at 14:42:45(+00:00).

Pretty-printing utilities for terminal output.
"""

import os
import typing as t
from enum import Enum
from timeit import default_timer

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

    def __init__(self, write: Write, name: str, indent_level=0):
        self.write = write
        self.name = name
        self.indent_level = indent_level
        self.start_time: t.Optional[float] = None
        self.end_time: t.Optional[float] = None

        # Black and white.
        self.black = Style.ansi(ANSI.BLACK, self.__call__)
        self.white = Style.ansi(ANSI.WHITE, self.__call__)

        # Red, green, and blue.
        self.red = Style.ansi(ANSI.RED, self.__call__)
        self.green = Style.ansi(ANSI.GREEN, self.__call__)
        self.blue = Style.ansi(ANSI.BLUE, self.__call__)

        # Cyan, magenta, and yellow.
        self.cyan = Style.ansi(ANSI.CYAN, self.__call__)
        self.magenta = Style.ansi(ANSI.MAGENTA, self.__call__)
        self.yellow = Style.ansi(ANSI.YELLOW, self.__call__)

        # Common text styles.
        self.bold = Style.ansi(ANSI.BOLD, self.__call__)
        self.underline = Style.ansi(ANSI.UNDERLINE, self.__call__)
        self.overline = Style.ansi(ANSI.OVERLINE, self.__call__)

        # Status styles.
        self.success = Style.combine([self.green, self.bold], self.__call__)
        self.error = Style.combine([self.red, self.bold], self.__call__)
        self.warn = self.warning = Style.combine(
            [self.yellow, self.bold], self.__call__
        )
        self.info = self.notice = Style.combine(
            [self.blue, self.bold], self.__call__
        )

        # Heading styles.
        h1 = Style(
            lambda message: "\n".join(
                [self.divider("="), message, self.divider("=")]
            ),
            self.__call__,
        )
        self.h1 = Style.combine([h1, self.bold], self.__call__)
        h2 = Style(
            lambda message: "\n".join(
                [self.divider("-"), message, self.divider("-")]
            ),
            self.__call__,
        )
        self.h2 = Style.combine([h2, self.bold], self.__call__)
        self.h3 = Style.combine(
            [self.overline, self.underline, self.bold], self.__call__
        )

    def __call__(self, message: str, *args, **kwargs):
        # pylint: disable=line-too-long
        """Write a message to the terminal.

        Args:
            message: The message to write.
            *args: Additional positional arguments to pass to the write function.
            **kwargs: Additional keyword arguments to pass to the write function.
        """
        # pylint: enable=line-too-long
        indented_message = self.indent(self.indent_level) + message
        self.write(indented_message, *args, **kwargs)

    def __enter__(self):
        self.bold(self.name)
        self.indent_level = max(0, self.indent_level + 1)

        self.start_time = default_timer()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = default_timer()
        elapsed_time = self.end_time - (self.start_time or self.end_time)

        self.indent_level = max(0, self.indent_level - 1)
        (self.error if exc_type else self.success)(
            f"{self.name} ({elapsed_time:.2f}s elapsed)"
        )

    def process(self, name: str, indent_level: t.Optional[int] = None):
        """
        A context manager for processing a message with automatic success or
        error handling. If an exception is raised within the context, the
        message is marked as an error; otherwise, it is marked as a success.

        Any messages written within the context are indented by the specified
        level and written when the context is entered.
        """
        return self.__class__(
            write=self.write,
            name=name,
            indent_level=(
                self.indent_level if indent_level is None else indent_level
            ),
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

    def indent(self, count: int, spaces=4, char=" "):
        """Write an indentation of the specified number of spaces.

        Args:
            count: The number of indentation levels.
            spaces: The number of spaces per indentation level.
            char: The character to use for indentation.
        """
        return char * count * spaces


pprint = PrettyPrinter(write=print, name="main")
