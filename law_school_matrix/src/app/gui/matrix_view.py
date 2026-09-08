from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from app.domain.models import Matrix, MatrixResult


class MatrixView(QTableWidget):
    value_edited = Signal(int, int, str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.cellChanged.connect(self._emit_edit)
        self._matrix: Matrix | None = None

    def display(self, matrix: Matrix, result: MatrixResult) -> None:
        self._matrix = matrix
        self.blockSignals(True)
        self.setColumnCount(1 + len(matrix.categories) + 2)
        self.setHorizontalHeaderLabels(["School / Option", *[category.name for category in matrix.categories], "Overall Score", "Rank"])
        self.setRowCount(len(matrix.options))
        for row, option in enumerate(matrix.options):
            name_item = QTableWidgetItem(option.name); name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable); self.setItem(row, 0, name_item)
            for col, category in enumerate(matrix.categories, 1):
                raw = option.values.get(category.id)
                self.setItem(row, col, QTableWidgetItem("" if raw is None else str(raw)))
            entry = result.option_results.get(option.id)
            self.setItem(row, len(matrix.categories) + 1, QTableWidgetItem(f"{entry.overall_score:.2f}" if entry and entry.overall_score is not None else "N/A"))
            self.setItem(row, len(matrix.categories) + 2, QTableWidgetItem(str(entry.rank) if entry and entry.rank else "N/A"))
        self.blockSignals(False)
        self.resizeColumnsToContents()

    def selected_option_id(self) -> int | None:
        if self._matrix is None or self.currentRow() < 0:
            return None
        return self._matrix.options[self.currentRow()].id

    def _emit_edit(self, row: int, column: int) -> None:
        if self._matrix and 1 <= column <= len(self._matrix.categories):
            option = self._matrix.options[row]; category = self._matrix.categories[column - 1]
            self.value_edited.emit(option.id or 0, category.id or 0, self.item(row, column).text())
