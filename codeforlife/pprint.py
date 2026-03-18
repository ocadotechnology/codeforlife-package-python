"""
© Ocado Group
Created on 11/03/2026 at 14:42:45(+00:00).

Pretty-printing utilities for terminal output.
"""

import os
import typing as t
from enum import Enum
from timeit import default_timer

if t.TYPE_CHECKING:
    from typing_extensions import Protocol

    # pylint: disable-next=too-few-public-methods
    class Apply(Protocol):
        """A protocol for a callable that applies a style to a message."""

        def __call__(self, message: str, **kwargs) -> str: ...


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

    def __init__(self, apply: "Apply", write: Write = print):
        self.apply = apply
        self.write = write

    def __call__(self, message: str, *args, **kwargs):
        styled_message = self.apply(message)
        self.write(styled_message, *args, **kwargs)

    @classmethod
    def ansi(cls, code: ANSI):
        """Create a style that applies the given ANSI code to messages.

        Args:
            code: The ANSI code to apply.

        Returns:
            A style that applies the given ANSI code to messages.
        """

        def apply(message: str, **kwargs):
            if kwargs.get("reset", True):
                message += ANSI.RESET.value

            return code.value + message

        return cls(apply)

    @classmethod
    def combine(cls, *styles: "Style"):
        """Combine multiple styles into a single style.

        Args:
            *styles: The styles to combine.

        Returns:
            A style that applies all the given styles to messages.
        """

        def apply(message: str, **kwargs):
            for style in styles:
                message = style.apply(message, **kwargs)

            return message

        return cls(apply)

    @classmethod
    def with_write(cls, write: Write):
        """Create a style class that uses the given write function.

        Args:
            write: The function to use for writing the styled message.

        Returns:
            A style class that uses the given write function.
        """

        class StyleWithWrite(cls):  # type: ignore[valid-type,misc]
            """A style class that uses the given write function."""

            def __init__(self, apply: "Apply"):
                super().__init__(apply, write)

        return StyleWithWrite


# pylint: disable-next=too-many-instance-attributes
class PrettyPrinter:
    """A utility class for pretty-printing styled messages to the terminal."""

    def __init__(self, write: Write, name: str, indent_level=0):
        self.write = write
        self.name = name
        self.indent_level = indent_level
        self.start_time: t.Optional[float] = None
        self.end_time: t.Optional[float] = None

        StyleWithWrite = Style.with_write(self.__call__)

        # Black and white.
        self.black = StyleWithWrite.ansi(ANSI.BLACK)
        self.white = StyleWithWrite.ansi(ANSI.WHITE)

        # Red, green, and blue.
        self.red = StyleWithWrite.ansi(ANSI.RED)
        self.green = StyleWithWrite.ansi(ANSI.GREEN)
        self.blue = StyleWithWrite.ansi(ANSI.BLUE)

        # Cyan, magenta, and yellow.
        self.cyan = StyleWithWrite.ansi(ANSI.CYAN)
        self.magenta = StyleWithWrite.ansi(ANSI.MAGENTA)
        self.yellow = StyleWithWrite.ansi(ANSI.YELLOW)

        # Common text styles.
        self.bold = StyleWithWrite.ansi(ANSI.BOLD)
        self.underline = StyleWithWrite.ansi(ANSI.UNDERLINE)
        self.overline = StyleWithWrite.ansi(ANSI.OVERLINE)

        # Status styles.
        self.success = StyleWithWrite.combine(self.green, self.bold)
        self.error = StyleWithWrite.combine(self.red, self.bold)
        self.warn = self.warning = StyleWithWrite.combine(
            self.yellow, self.bold
        )
        self.info = self.notice = StyleWithWrite.combine(self.blue, self.bold)

        # Heading styles.
        self.h1 = StyleWithWrite(
            lambda message, **kwargs: "\n".join(
                [
                    self.bold.apply(self.divider("="), **kwargs),
                    self.bold.apply(message, **kwargs),
                    self.bold.apply(self.divider("="), **kwargs),
                ]
            )
        )
        self.h2 = StyleWithWrite(
            lambda message, **kwargs: "\n".join(
                [
                    self.bold.apply(self.divider("-"), **kwargs),
                    self.bold.apply(message, **kwargs),
                    self.bold.apply(self.divider("-"), **kwargs),
                ]
            )
        )
        self.h3 = StyleWithWrite.combine(
            self.overline, self.underline, self.bold
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
        self(
            self.bold.apply(f"{self.name} ")
            + (self.error.apply("✘") if exc_type else self.success.apply("✔"))
            + self.bold.apply(f" ({elapsed_time:.2f}s elapsed)")
        )

    def style(self, apply: "Apply"):
        """Create a new style based on the given apply function.

        Args:
            apply: The function to use for applying the style.

        Returns:
            A new style based on the given apply function.
        """
        return Style(apply, self.__call__)

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
