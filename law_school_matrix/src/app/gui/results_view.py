from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem
from app.domain.models import Matrix, MatrixResult


class ResultsView(QTableWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(0, 3, parent)
        self.setHorizontalHeaderLabels(["Rank", "School / Option", "Overall Score"])
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

    def show_results(self, matrix: Matrix, result: MatrixResult) -> None:
        rows = sorted(matrix.options, key=lambda option: ((result.option_results.get(option.id).rank if option.id in result.option_results else None) is None, result.option_results.get(option.id).rank or 9999, option.name))
        self.setRowCount(len(rows))
        for row, option in enumerate(rows):
            item = result.option_results.get(option.id)
            self.setItem(row, 0, QTableWidgetItem(str(item.rank) if item and item.rank else "N/A"))
            self.setItem(row, 1, QTableWidgetItem(option.name))
            score = QTableWidgetItem(f"{item.overall_score:.2f}" if item and item.overall_score is not None else "N/A")
            score.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.setItem(row, 2, score)
