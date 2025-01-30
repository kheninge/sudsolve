from PySide6.QtCore import QObject, Signal


class UpdateController(QObject):
    """Allow for explicit control of when views get updated. Provides a way to register an update function. The main
    update function then just goes through the list of update functions registered and calls them"""

    updated = Signal()

    def __init__(self) -> None:
        super().__init__()
