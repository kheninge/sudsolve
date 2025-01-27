from PySide6.QtWidgets import QApplication


class FixedSizeControl:
    """A utility class for use with Qt Applications. It determines the available screen real states
    and creates a scaled height and width"""

    def __init__(
        self,
        app: QApplication,
        width_ratio: float,
        height_ratio: float = 1,
    ) -> None:
        self.app = app
        screens = self.app.screens()
        geometry = screens[0].availableGeometry()
        self._full_width = geometry.width()
        self._full_height = geometry.height()
        self._app_width = int(self._full_width * width_ratio)
        self._app_height = int(self._full_height * height_ratio)

    @property
    def full_width(self) -> int:
        return self._full_width

    @property
    def full_height(self) -> int:
        return self._full_height

    @property
    def app_width(self) -> int:
        return self._app_width

    @property
    def app_height(self) -> int:
        return self._app_height
