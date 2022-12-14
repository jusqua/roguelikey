from typing import Reversible
from tcod import Console
from textwrap import wrap
import color


class Message:
    def __init__(self, text: str, fg: tuple[int, int, int]) -> None:
        self.plain_text = text
        self.fg = fg
        self.count = 1

    @property
    def full_text(self) -> str:
        """The full text of this message, including count if necessary"""
        return self.plain_text + f" (x{self.count})" * (self.count != 1)


class MessageLog:
    def __init__(self) -> None:
        self.messages: list[Message] = []

    def add_message(self, text: str, fg: tuple[int, int, int] = color.white, *, stack: bool = True) -> None:
        """
        Add message to this log
        `text` is the plain text
        `fg` is the text color
        If `stack` is True, then message can stack with previous ones
        """
        if stack and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count += 1
        else:
            self.messages.append(Message(text, fg))

    def render(self, console: Console, position: tuple[int, int], size: tuple[int, int]) -> None:
        """Render this log over the given area"""
        self.render_messages(console, position, size, self.messages)

    @staticmethod
    def render_messages(
            console: Console,
            position: tuple[int, int],
            size: tuple[int, int],
            messages: Reversible[Message]
        ) -> None:
        """
        Render provided messages
        The `messages` are rendered starting at the last message and working backwords
        """
        x, y = position
        w, h = size
        y_offset = h - 1

        for message in reversed(messages):
            for line in reversed(wrap(message.full_text, w)):
                console.print(x, y + y_offset, line, message.fg)
                y_offset -= 1
                if y_offset < 0:
                    return

