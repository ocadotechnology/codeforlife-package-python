"""
© Ocado Group
Created on 11/03/2026 at 14:42:45(+00:00).

Pretty-printing utilities for terminal output.
"""

import os
import typing as t

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

if t.TYPE_CHECKING:
    from typing_extensions import Protocol

    # pylint: disable-next=too-few-public-methods
    class StyleProtocol(Protocol):
        """A callable that applies a style to a message."""

        @t.overload
        def __call__(
            self, message: str, write: t.Literal[True] = True, **kwargs
        ) -> str: ...

        @t.overload
        def __call__(self, message: str, write: t.Literal[False]) -> str: ...


# pylint: disable-next=too-many-instance-attributes
class PrettyPrinter:
    """A utility class for pretty-printing styled messages to the terminal."""

    Write: t.TypeAlias = t.Callable[..., None]
    Style: t.TypeAlias = "StyleProtocol"

    def __init__(self, write: Write):
        self.write = write

        self.black = self.make_ansi_style(BLACK)
        self.white = self.make_ansi_style(WHITE)

        self.red = self.make_ansi_style(RED)
        self.green = self.make_ansi_style(GREEN)
        self.blue = self.make_ansi_style(BLUE)

        self.yellow = self.make_ansi_style(YELLOW)
        self.magenta = self.make_ansi_style(MAGENTA)
        self.cyan = self.make_ansi_style(CYAN)

        self.bold = self.make_ansi_style(BOLD)
        self.underline = self.make_ansi_style(UNDERLINE)
        self.overline = self.make_ansi_style(OVERLINE)

        self.success = self.combine_styles(self.green, self.bold)
        self.error = self.combine_styles(self.red, self.bold)
        self.warn = self.warning = self.combine_styles(self.yellow, self.bold)
        self.info = self.notice = self.combine_styles(self.blue, self.bold)

    def make_style(self, stylize: t.Callable[[str], str]) -> Style:
        # pylint: disable=line-too-long
        """Make a style that applies the given stylization function to messages.

        Args:
            stylize: A function that takes a message and returns a stylized version of it.

        Returns:
            A style that applies the given stylization function to messages and writes them if a write function is set.
        """
        # pylint: enable=line-too-long

        def style(message: str, write: bool = True, **kwargs):
            styled_message = stylize(message)

            if write:
                self.write(styled_message, **kwargs)

            return styled_message

        return style

    def make_ansi_style(self, ansi_code: str):
        """Make a style that applies the given ANSI code to messages.

        Args:
            ansi_code: The ANSI code to apply.

        Returns:
            A style that applies the given ANSI code to messages.
        """
        return self.make_style(lambda message: ansi_code + message + RESET)

    def combine_styles(self, *styles: Style):
        """Combine multiple styles into a single style.

        Args:
            *styles: The styles to combine.

        Returns:
            A function that takes a message and applies all the styles to it.
        """

        def combined_style(message: str):
            for style in styles:
                message = style(message, write=False)

            return message

        return self.make_style(combined_style)

    def divider(
        self,
        default_columns=80,
        char="-",
        style: t.Optional[Style] = None,
        **kwargs
    ):
        # pylint: disable=line-too-long
        """Write a divider line with the specified character.

        Args:
            default_columns: The default number of columns to use if the terminal width cannot be determined.
            char: The character to use for the divider.
            style: An optional style to apply to the divider line.
        """
        # pylint: enable=line-too-long
        message = int(os.getenv("COLUMNS", default_columns)) * char

        if style:
            message = style(message, write=False)

        self.write(message, **kwargs)

    def indent(self, count: int, spaces=2, char=" ", **kwargs):
        """Write an indentation of the specified number of spaces.

        Args:
            count: The number of indentation levels.
            spaces: The number of spaces per indentation level.
            char: The character to use for indentation.
        """
        self.write(char * count * spaces, **kwargs)


pprint = PrettyPrinter(write=print)
