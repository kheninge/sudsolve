import sys
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QListWidgetItem,
    QTextEdit,
    QPushButton,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QSplitter,
    QLabel,
    QToolButton,
    QStyle,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal, QSize

from gui.fixed_size_control import FixedSizeControl
from sudoku.puzzleio import PuzzleList


class ItemWidget(QWidget):
    deleteClicked = Signal(QListWidgetItem)

    def __init__(self, text, parent=None):
        super().__init__(parent)

        # Create layout for the item widget
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Add label for the item text
        self.label = QLabel(text)
        layout.addWidget(self.label, 1)  # 1 for stretch factor - take available space

        # Create delete button
        self.delete_button = QToolButton()
        self.delete_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)
        )
        self.delete_button.setIconSize(QSize(16, 16))
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.setStyleSheet("QToolButton { border: none; padding: 0px; }")
        self.delete_button.clicked.connect(self.onDeleteClicked)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def onDeleteClicked(self):
        # Emit signal to parent when delete button is clicked
        self.deleteClicked.emit(self._list_item)

    def setListItem(self, item):
        # Store reference to list item
        self._list_item = item


class PuzzleListWidget(QDialog):
    """A popup window containing a list of puzzles which can be loaded, deleted or added to"""

    def __init__(self, parent, gui_top, puzzles: PuzzleList, sizes: FixedSizeControl):
        super().__init__(parent)
        self.puzzles = puzzles
        self.parent = parent
        self.gui_top = gui_top
        self.setFixedSize(int(sizes.app_width * 0.60), int(sizes.app_height * 0.60))
        self.setWindowTitle("Puzzles")
        self.setModal(True)
        self.verified_new_puzzle_name = None
        self.verified_new_puzzle_input = None
        self.new_puzzle_name_error = False

        # Create main layout
        main_layout = QVBoxLayout(self)

        # Create search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search puzzles...")
        self.search_bar.textChanged.connect(self.filter_items)
        main_layout.addWidget(self.search_bar)

        # Create horizontal splitter for list and preview
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(content_splitter, 1)  # 1 to make it expand

        # Create left panel with list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        list_label = QLabel("Puzzles:")
        left_layout.addWidget(list_label)

        self.item_list = QListWidget()
        self.item_list.currentItemChanged.connect(self.update_preview)
        self.item_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        # self.item_list.setFixedWidth(int(sizes.app_width * 0.15))
        left_layout.addWidget(self.item_list)

        for item in self.puzzles.puzzles.keys():
            self._add_item_with_delete(item)

        content_splitter.addWidget(left_panel)

        # Create right panel with preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        preview_label = QLabel("Preview:")
        right_layout.addWidget(preview_label)

        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        right_layout.addWidget(self.preview_area)

        content_splitter.addWidget(right_panel)

        # Set initial splitter sizes (25% left, 75% right)
        content_splitter.setSizes([200, 600])

        button_layout = QHBoxLayout()
        # Create cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        # self.cancel_button.setEnabled(False)  # Disabled until an item is selected
        button_layout.addWidget(self.cancel_button)
        # Create load button
        self.load_button = QPushButton("Load Selected Item")
        self.load_button.clicked.connect(self.load_selected_item)
        self.load_button.setEnabled(False)  # Disabled until an item is selected
        button_layout.addWidget(self.load_button)
        main_layout.addLayout(button_layout)

        # Add New Puzzle section
        add_new_layout = QHBoxLayout()
        add_label = QLabel()
        add_label.setText("Add a new puzzle:")
        main_layout.addWidget(add_label)
        ## Create field for inputting new puzzle name
        self.new_name = QLineEdit()
        self.new_name.setPlaceholderText("New Puzzle Name")
        self.new_name.textChanged.connect(self.check_new_puzzle_name)
        add_new_layout.addWidget(self.new_name)
        ## Create field for inputting new puzzles
        self.new_field = QLineEdit()
        self.new_field.setPlaceholderText("New Puzzle Values 0-9; 0 for blank")
        self.new_field.textChanged.connect(self.check_new_puzzle_input)
        add_new_layout.addWidget(self.new_field)
        ## Create save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_new_puzzle)
        self.save_button.setEnabled(False)  # Disabled until the full puzzle is input
        add_new_layout.addWidget(self.save_button)
        main_layout.addLayout(add_new_layout)

        # Apply the layout
        self.setLayout(main_layout)
        self._define_shortcuts()

        # Get the default text to display in the preview
        self.update_preview(None, None)

    def _define_shortcuts(self):
        # Define Shortcuts
        shortcuts = {
            "q": self.close,
        }
        for k, func in shortcuts.items():
            QShortcut(QKeySequence(k), self).activated.connect(func)

    def _add_item_with_delete(self, text):
        """Add an item to the list with a delete icon"""
        list_item = QListWidgetItem(self.item_list)
        item_widget = ItemWidget(text)
        item_widget.setListItem(list_item)
        item_widget.deleteClicked.connect(self.delete_item)

        # Store the text in the item's data for filtering
        list_item.setData(Qt.ItemDataRole.UserRole, text)

        # Set size hint to ensure proper display
        list_item.setSizeHint(item_widget.sizeHint())

        # Set the custom widget for this item
        self.item_list.setItemWidget(list_item, item_widget)

    def delete_item(self, item):
        """Delete the specified item from the list"""
        row = self.item_list.row(item)
        deleted_puzzle = self.item_list.item(row)
        item_text = deleted_puzzle.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Delete {item_text}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Delete the item
            self.puzzles.delete(item_text)
            self.puzzles.update()

            deleted_puzzle = self.item_list.takeItem(row)
            # Update preview if the currently selected item was deleted
            current = self.item_list.currentItem()
            if not current:
                self.preview_area.setText("No item selected")
                self.load_button.setEnabled(False)

    def filter_items(self, text):
        """Filter the items in the list based on search text"""
        for i in range(self.item_list.count()):
            item = self.item_list.item(i)
            item_text = item.data(Qt.ItemDataRole.UserRole)
            item.setHidden(text.lower() not in item_text.lower())

    def check_new_puzzle_name(self, name):
        """Check if the new puzzle name is valid and enable the save button"""
        self.new_puzzle_name_error = False
        if name:
            if name in self.puzzles.puzzles.keys():
                self.save_button.setEnabled(False)
                self.new_puzzle_name_error = True
                self.verified_new_puzzle_name = None
            else:
                self.verified_new_puzzle_name = name
            self.update_preview(None, None)
        else:
            self.verified_new_puzzle_name = None

    def check_new_puzzle_input(self, input):
        """Check if the new puzzle input is valid and enable the save button"""
        self.new_puzzle_input_error = False
        for c in input:
            if c not in {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}:
                self.new_puzzle_input_error = True
        if not self.new_puzzle_name_error and len(input) == 81:
            self.verified_new_puzzle_input = input
        if self.verified_new_puzzle_name and self.verified_new_puzzle_input:
            self.save_button.setEnabled(True)
            self.save_button.setDefault(True)
        else:
            self.save_button.setEnabled(False)

    def save_new_puzzle(self):
        """Save the new puzzle to the list"""
        puzzle_name = self.verified_new_puzzle_name
        puzzle_string = self.verified_new_puzzle_input
        self.puzzles.add(puzzle_name, puzzle_string)
        self.puzzles.update()
        self._load_puzzle_and_exit(self.verified_new_puzzle_name)

    def update_preview(self, current, previous):
        """Update the preview area when a new item is selected"""
        if self.new_puzzle_name_error:
            self.preview_area.setText("Give the new puzzle a unique name")
            self.load_button.setEnabled(False)
            self.cancel_button.setDefault(True)
        elif current:
            self.load_button.setEnabled(True)
            self.load_button.setDefault(True)
            file_name = current.text()
            file_ext = file_name.split(".")[-1].lower()

            # Generate a preview based on file type
            if file_ext in ["jpg", "png", "gif", "bmp"]:
                preview_text = f"[Image Preview for {file_name}]\n\nType: Image File\nFormat: {file_ext.upper()}"
            elif file_ext in ["pdf"]:
                preview_text = f"[PDF Document Preview for {file_name}]\n\nType: PDF Document\nPages: 12"
            elif file_ext in ["docx", "doc"]:
                preview_text = f"[Word Document Preview for {file_name}]\n\nType: Word Document\nPages: 8\nContains: Text, Tables"
            elif file_ext in ["xlsx", "xls"]:
                preview_text = f"[Spreadsheet Preview for {file_name}]\n\nType: Excel Spreadsheet\nSheets: 3\nContains: Data, Charts"
            elif file_ext in ["txt", "md"]:
                preview_text = f"[Text Preview for {file_name}]\n\nType: Text File\nSize: 2.4 KB\n\nThis is a sample text content that would be displayed in the preview area. Actual implementation would load the real content."
            else:
                preview_text = f"[Preview for {file_name}]\n\nType: {file_ext.upper()} File\nNo preview available."

            self.preview_area.setText(preview_text)
        else:
            self.load_button.setEnabled(False)
            self.cancel_button.setDefault(True)
            self.preview_area.setText("No item selected")

    def _load_puzzle_and_exit(self, puzzle_name):
        self.gui_top.load_puzzle(puzzle_name)
        self.accept()

    def load_selected_item(self):
        selected_puzzle = self.item_list.currentItem()
        if selected_puzzle:
            puzzle_text = selected_puzzle.data(Qt.ItemDataRole.UserRole)
            self._load_puzzle_and_exit(puzzle_text)
