class UpdateController:
    """Allow for explicit control of when views get updated. Provides a way to register an update function. The main
    update function then just goes through the list of update functions registered and calls them"""

    def __init__(self) -> None:
        self._update_functions = []

    def add_update(self, update_function):
        self._update_functions.append(update_function)

    def call_updates(self):
        for update in self._update_functions:
            update()
