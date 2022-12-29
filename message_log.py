from typing import Reversible, Iterable
from tcod import Console
from textwrap import wrap

import tcod
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

    def add_message(
        self, text: str, fg: tuple[int, int, int] = color.white, *, stack: bool = True
    ) -> None:
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

    def render(self, console: Console) -> None:
        """Render this log over the given area"""
        position = 64, 40
        size = 32, 24
        console.draw_frame(*position, *size)
        console.print_box(*position, size[0], 1, "┤ Logs ├", alignment=tcod.CENTER)
        self.render_messages(console, position, size, self.messages)

    @staticmethod
    def wrap(text: str, width: int) -> Iterable[str]:
        """Handle message text wrap"""
        for line in text.splitlines():
            yield from wrap(line, width, expand_tabs=True)

    @classmethod
    def render_messages(
        cls,
        console: Console,
        position: tuple[int, int],
        size: tuple[int, int],
        messages: Reversible[Message],
        gap: tuple[int, int] = (2, 2),
    ) -> None:
        """
        Render provided messages
        The `messages` are rendered starting at the last message and working backwords
        """
        x, y = position
        x += gap[0] // 2
        y += gap[1] // 2

        w, h = size
        w -= gap[0]
        h -= gap[1]

        y_offset = 0
        for message in reversed(messages):
            for line in cls.wrap(message.full_text, w):
                console.print(x, y + y_offset, line, message.fg)
                y_offset += 1
                if y_offset >= h:
                    return
