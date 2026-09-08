from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QSpinBox
from app.domain.models import Category, CategoryDataType, Direction


class CategoryDialog(QDialog):
    def __init__(self, category: Category | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Category")
        self.name_edit = QLineEdit(category.name if category else "")
        # Importance is intentionally an integer.  QSpinBox commits a typed
        # value reliably before the dialog closes, unlike the prior decimal
        # spin box in this interaction.
        self.weight = QSpinBox(); self.weight.setRange(1, 10); self.weight.setSingleStep(1); self.weight.setValue(int(category.weight) if category else 5)
        self.data_type = QComboBox(); self.data_type.addItem("Numeric", CategoryDataType.NUMERIC); self.data_type.addItem("Rating (0–100)", CategoryDataType.RATING)
        self.direction = QComboBox(); self.direction.addItem("Higher is better", Direction.HIGHER_IS_BETTER); self.direction.addItem("Lower is better", Direction.LOWER_IS_BETTER)
        if category:
            self.data_type.setCurrentIndex(self.data_type.findData(category.data_type)); self.direction.setCurrentIndex(self.direction.findData(category.direction))
        layout = QFormLayout(self); layout.addRow("Name:", self.name_edit); layout.addRow("Importance (1–10):", self.weight); layout.addRow("Data type:", self.data_type); layout.addRow("Direction:", self.direction)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Save category")
        buttons.accepted.connect(self._save); buttons.rejected.connect(self.reject); layout.addRow(buttons)

    def _save(self) -> None:
        """Commit the editor's current text before reporting an accepted edit."""
        self.weight.interpretText()
        self.accept()

    def values(self) -> tuple[str, float, CategoryDataType, Direction]:
        # Also commit here for callers that accept the dialog programmatically.
        self.weight.interpretText()
        return self.name_edit.text(), self.weight.value(), self.data_type.currentData(), self.direction.currentData()
