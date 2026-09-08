from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit


class SchoolDialog(QDialog):
    def __init__(self, name: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("School / Option")
        self.name_edit = QLineEdit(name)
        layout = QFormLayout(self)
        layout.addRow("Name:", self.name_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    @property
    def name(self) -> str:
        return self.name_edit.text()
