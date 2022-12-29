class Impossible(Exception):
    """
    Raised when an action cannot be performed,
    The reason is given has the exception message.
    """


class QuitWithoutSave(SystemExit):
    """Can be raised to exit the game without automatically saving."""
