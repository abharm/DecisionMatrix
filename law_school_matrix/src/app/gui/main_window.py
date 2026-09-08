"""Navigation-driven primary desktop interface."""
from collections.abc import Callable
from PySide6.QtCore import QByteArray
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QAbstractItemView, QFileDialog, QFrame, QHBoxLayout, QHeaderView, QInputDialog, QLabel, QMainWindow, QMessageBox, QPushButton, QSpinBox, QStackedWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from app.domain.models import Category, Matrix, Option
from app.gui.category_dialog import CategoryDialog
from app.gui.matrix_view import MatrixView
from app.gui.ranking_chart import RankingChart
from app.gui.results_view import ResultsView
from app.gui.school_dialog import SchoolDialog
from app.services.matrix_service import MatrixService, ValidationError

APP_STYLE = """
QMainWindow, QDialog { background: #1E1E1E; color: #D4D4D4; }
QMenuBar { background: #181818; color: #D4D4D4; border-bottom: 1px solid #3E3E42; }
QMenuBar::item:selected, QMenu::item:selected { background: #094771; color: #FFFFFF; }
QMenu { background: #252526; color: #D4D4D4; border: 1px solid #3E3E42; }
QFrame#sidebar { background: #252526; border-right: 1px solid #3E3E42; }
QLabel#brand { color: #FFFFFF; font-size: 22px; font-weight: 700; padding: 18px 18px 4px; }
QLabel#subtitle { color: #A0A0A0; padding: 0 18px 18px; }
QPushButton#nav { color: #CCCCCC; text-align: left; padding: 11px 18px; border: none; font-size: 14px; }
QPushButton#nav:hover { background: #37373D; }
QPushButton#nav:checked { background: #094771; color: #FFFFFF; font-weight: 600; border-left: 3px solid #007ACC; }
QWidget#page { background: #1E1E1E; }
QLabel#pageTitle { font-size: 25px; font-weight: 700; color: #FFFFFF; }
QLabel#pageHint { color: #A0A0A0; font-size: 13px; }
QFrame#surface { background: #252526; border: 1px solid #3E3E42; border-radius: 8px; }
QPushButton { background: #3E3E42; color: #FFFFFF; border: 1px solid #555555; border-radius: 4px; padding: 8px 12px; font-weight: 600; }
QPushButton:hover { background: #505055; }
QPushButton#primary { background: #007ACC; color: #FFFFFF; border-color: #007ACC; }
QPushButton#primary:hover { background: #0E639C; }
QTableWidget { border: none; background: #1E1E1E; color: #D4D4D4; gridline-color: #3E3E42; selection-background-color: #094771; selection-color: #FFFFFF; alternate-background-color: #252526; }
QTableWidget::item { color: #D4D4D4; padding: 3px; }
QTableWidget::item:selected { background: #094771; color: #FFFFFF; }
QHeaderView::section { background: #333333; color: #FFFFFF; border: none; border-bottom: 1px solid #555555; padding: 9px; font-weight: 700; }
QLineEdit, QComboBox, QDoubleSpinBox { background: #3C3C3C; color: #FFFFFF; border: 1px solid #555555; border-radius: 3px; padding: 5px; }
QComboBox QAbstractItemView { background: #252526; color: #FFFFFF; selection-background-color: #094771; }
QStatusBar { background: #007ACC; color: #FFFFFF; border-top: 1px solid #3E3E42; }
"""


class MainWindow(QMainWindow):
    def __init__(self, service: MatrixService, matrix_id: int | None = None) -> None:
        super().__init__()
        self.service: MatrixService = service
        self.matrix: Matrix | None = None
        self.setWindowTitle("Decision Matrix")
        self.resize(1200, 780)
        geometry = self._state_value("window_geometry")
        if geometry: self.restoreGeometry(QByteArray.fromBase64(geometry.encode("ascii")))
        self.setStyleSheet(APP_STYLE)
        self._build_shell()
        self._build_menu()
        if matrix_id is not None: self.load(matrix_id)
        elif not self._restore_last_matrix(): self._show_empty_project()
        self.show_page(int(self._state_value("active_page") or 0))

    def _build_shell(self) -> None:
        root = QWidget(); layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        sidebar = QFrame(objectName="sidebar"); sidebar.setFixedWidth(205)
        side = QVBoxLayout(sidebar); side.setContentsMargins(0, 0, 0, 16); side.setSpacing(3)
        side.addWidget(QLabel("Decision\nMatrix", objectName="brand")); side.addWidget(QLabel("Compare what matters.", objectName="subtitle"))
        self.nav_buttons: list[QPushButton] = []
        for title in ("Matrix", "Categories", "Rankings"):
            button = QPushButton(title, objectName="nav"); button.setCheckable(True)
            button.clicked.connect(lambda checked, index=len(self.nav_buttons): self.show_page(index))
            side.addWidget(button); self.nav_buttons.append(button)
        side.addStretch()
        importer = QPushButton("Import CSV", objectName="nav"); importer.clicked.connect(self.import_csv); side.addWidget(importer)
        layout.addWidget(sidebar)
        self.pages = QStackedWidget()
        self.pages.addWidget(self._matrix_page()); self.pages.addWidget(self._categories_page()); self.pages.addWidget(self._rankings_page())
        layout.addWidget(self.pages, 1); self.setCentralWidget(root)
        self.pages.setCurrentIndex(0)
        self.nav_buttons[0].setChecked(True)

    def _page(self, title: str, hint: str) -> tuple[QWidget, QVBoxLayout, QFrame]:
        page = QWidget(objectName="page"); layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 25, 30, 25); layout.setSpacing(12)
        layout.addWidget(QLabel(title, objectName="pageTitle")); layout.addWidget(QLabel(hint, objectName="pageHint"))
        surface = QFrame(objectName="surface"); layout.addWidget(surface, 1)
        return page, layout, surface

    def _buttons(self, options: list[tuple[str, Callable, bool]]) -> QHBoxLayout:
        actions = QHBoxLayout()
        for label, callback, primary in options:
            button = QPushButton(label)
            if primary: button.setObjectName("primary")
            button.clicked.connect(callback); actions.addWidget(button)
        actions.addStretch(); return actions

    def _matrix_page(self) -> QWidget:
        page, _, surface = self._page("Matrix", "Enter raw values directly. Rankings update automatically when each option is complete.")
        content = QVBoxLayout(surface); content.setContentsMargins(14, 14, 14, 14)
        content.addLayout(self._buttons([("Add school / option", self.add_school, True), ("Edit selected", self.edit_school, False), ("Delete selected", self.delete_school, False), ("Recalculate", self.refresh, False)]))
        self.matrix_view = MatrixView(); self.matrix_view.value_edited.connect(self.set_value); content.addWidget(self.matrix_view)
        return page

    def _categories_page(self) -> QWidget:
        page, _, surface = self._page("Categories & importance", "Set each category's importance from 1 (least) to 10 (most) directly in the table, or use Edit selected.")
        content = QVBoxLayout(surface); content.setContentsMargins(14, 14, 14, 14)
        content.addLayout(self._buttons([("Add category", self.add_category, True), ("Edit selected", self.edit_category, False), ("Delete selected", self.delete_category, False)]))
        self.categories = QTableWidget(0, 4); self.categories.setHorizontalHeaderLabels(["Category", "Importance", "Data type", "Direction"])
        self.categories.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows); self.categories.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); self.categories.verticalHeader().setVisible(False)
        self.categories.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in (1, 2, 3): self.categories.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        content.addWidget(self.categories); return page

    def _rankings_page(self) -> QWidget:
        page, _, surface = self._page("Rankings", "Overall scores combine your importance ratings with each normalized category score.")
        content = QVBoxLayout(surface); content.setContentsMargins(18, 16, 18, 18)
        self.ranking_chart = RankingChart(); self.results = ResultsView()
        content.addWidget(self.ranking_chart, 2); content.addWidget(QLabel("Detailed results", objectName="pageHint")); content.addWidget(self.results, 1)
        return page

    def _build_menu(self) -> None:
        project_menu = self.menuBar().addMenu("Projects")
        for label, callback in (("New project…", self.new_matrix), ("Switch project…", self.choose_load), ("Rename current project…", self.rename_project), ("Delete current project…", self.delete_project)): self._action(project_menu, label, callback)
        file_menu = self.menuBar().addMenu("File")
        for label, callback in (("Save", self.save), ("Import CSV…", self.import_csv), ("Export / link CSV…", self.export_csv), ("Refresh", self.refresh)): self._action(file_menu, label, callback)
        options_menu = self.menuBar().addMenu("Options")
        for label, callback in (("Add school / option", self.add_school), ("Edit selected", self.edit_school), ("Delete selected", self.delete_school)): self._action(options_menu, label, callback)
        categories_menu = self.menuBar().addMenu("Categories")
        for label, callback in (("Add category", self.add_category), ("Edit selected", self.edit_category), ("Delete selected", self.delete_category)): self._action(categories_menu, label, callback)

    def _action(self, menu, label: str, callback: Callable) -> None:
        action = QAction(label, self)
        if label == "Save": action.setShortcut("Ctrl+S")
        action.triggered.connect(callback); menu.addAction(action)

    def show_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        for position, button in enumerate(self.nav_buttons): button.setChecked(position == index)
        self.service.repository.set_app_setting("active_page", str(index))

    def new_matrix(self) -> None:
        name, ok = QInputDialog.getText(self, "New Project", "Project name:", text="My Decision Matrix")
        if ok: self._run(lambda: self.service.create_matrix(name), lambda matrix: self.load(matrix.id or 0))

    def choose_load(self) -> None:
        matrices = self.service.repository.list_matrices()
        if not matrices: return
        selected, ok = QInputDialog.getItem(self, "Switch Project", "Project:", [matrix.name for matrix in matrices], editable=False)
        if ok: self.load(next(matrix.id for matrix in matrices if matrix.name == selected) or 0)

    def rename_project(self) -> None:
        if not self.matrix: return
        name, ok = QInputDialog.getText(self, "Rename Project", "Project name:", text=self.matrix.name)
        if ok:
            self._run(lambda: self.service.rename_matrix(self.matrix.id or 0, name), lambda _: self.load(self.matrix.id or 0))

    def delete_project(self) -> None:
        if not self.matrix or not self._confirm(f"Delete project '{self.matrix.name}' and all of its categories and options?"):
            return
        deleted_id = self.matrix.id or 0
        self._run(lambda: self.service.delete_matrix(deleted_id), lambda _: self._load_next_project())

    def _load_next_project(self) -> None:
        projects = self.service.repository.list_matrices()
        if projects: self.load(projects[0].id or 0)
        else: self._show_empty_project()

    def _show_empty_project(self) -> None:
        self.matrix = None
        self.setWindowTitle("Decision Matrix — No project open")
        self.matrix_view.clear(); self.categories.setRowCount(0); self.results.clearContents(); self.results.setRowCount(0); self.ranking_chart.clear_chart()
        self.statusBar().showMessage("Create a project or import a CSV to get started.")

    def import_csv(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import Decision Matrix CSV", "", "CSV files (*.csv);;All files (*)")
        if path: self._run(lambda: self.service.import_csv(path), lambda matrix: self.load(matrix.id or 0))

    def export_csv(self) -> None:
        if not self.matrix: return
        suggested = self.matrix.source_csv_path or f"{self.matrix.name}.csv"
        path, _ = QFileDialog.getSaveFileName(self, "Export and Link Matrix CSV", suggested, "CSV files (*.csv)")
        if path:
            self._run(lambda: self.service.export_and_link_csv(self.matrix.id or 0, path), lambda _: self.refresh())

    def load(self, matrix_id: int) -> None:
        self.matrix = self.service.load(matrix_id); self.refresh()
        self.service.repository.set_app_setting("last_matrix_id", str(matrix_id))
        self.setWindowTitle(f"Decision Matrix — {self.matrix.name}")

    def save(self) -> None:
        """Persist the current workspace selection and window layout."""
        self._persist_ui_state()
        self.statusBar().showMessage("Saved. This project will reopen here next time.", 4000)

    def _restore_last_matrix(self) -> bool:
        matrix_id = int(self._state_value("last_matrix_id") or 0)
        if not matrix_id: return False
        try:
            self.load(matrix_id)
            return True
        except KeyError:
            self.service.repository.set_app_setting("last_matrix_id", "0")
            return False

    def _persist_ui_state(self) -> None:
        if self.matrix: self.service.repository.set_app_setting("last_matrix_id", str(self.matrix.id))
        geometry = bytes(self.saveGeometry().toBase64()).decode("ascii")
        self.service.repository.set_app_setting("window_geometry", geometry)
        self.service.repository.set_app_setting("active_page", str(self.pages.currentIndex()))

    def _state_value(self, key: str) -> str | None:
        return self.service.repository.get_app_setting(key)

    def closeEvent(self, event) -> None:
        self._persist_ui_state()
        event.accept()

    def refresh(self) -> None:
        if not self.matrix: return
        self.matrix = self.service.load(self.matrix.id or 0); result = self.service.calculate(self.matrix)
        self.matrix_view.display(self.matrix, result); self.results.show_results(self.matrix, result); self.ranking_chart.show_results(self.matrix, result)
        self.categories.setRowCount(len(self.matrix.categories))
        for row, category in enumerate(self.matrix.categories):
            values = (category.name, category.data_type.value.replace("_", " ").title(), category.direction.value.replace("_", " ").title())
            self.categories.setItem(row, 0, QTableWidgetItem(values[0]))
            importance = QSpinBox()
            importance.setRange(1, 10); importance.setValue(round(category.weight)); importance.setToolTip("Change importance (1–10). The project saves automatically.")
            importance.valueChanged.connect(lambda value, category_id=category.id: self.set_category_weight(category_id or 0, value))
            self.categories.setCellWidget(row, 1, importance)
            self.categories.setItem(row, 2, QTableWidgetItem(values[1]))
            self.categories.setItem(row, 3, QTableWidgetItem(values[2]))
        self.statusBar().showMessage(result.error or "Scores are live. Importance ratings are normalized automatically; blank values stay N/A.")

    def add_school(self) -> None:
        if not self.matrix: return
        dialog = SchoolDialog(parent=self)
        if dialog.exec(): self._run(lambda: self.service.add_option(self.matrix.id or 0, dialog.name), lambda _: self.refresh())

    def edit_school(self) -> None:
        option = self._selected_option()
        if option:
            dialog = SchoolDialog(option.name, self)
            if dialog.exec(): self._run(lambda: self.service.update_option(Option(option.id, option.matrix_id, dialog.name, option.values)), lambda _: self.refresh())

    def delete_school(self) -> None:
        option = self._selected_option()
        if option and self._confirm(f"Delete {option.name}?"): self.service.delete_option(option.id or 0); self.refresh()

    def add_category(self) -> None:
        if not self.matrix: return
        dialog = CategoryDialog(parent=self)
        if dialog.exec():
            name, weight, kind, direction = dialog.values(); self._run(lambda: self.service.add_category(self.matrix.id or 0, name, weight, kind, direction), lambda _: self.refresh())

    def edit_category(self) -> None:
        if not self.matrix or self.categories.currentRow() < 0: return
        category = self.matrix.categories[self.categories.currentRow()]; dialog = CategoryDialog(category, self)
        if dialog.exec():
            name, weight, kind, direction = dialog.values(); self._run(lambda: self.service.update_category(Category(category.id, category.matrix_id, name, weight, kind, direction)), lambda _: self.refresh())

    def set_category_weight(self, category_id: int, weight: int) -> None:
        """Persist a table-based importance edit immediately and refresh scores."""
        if not self.matrix:
            return
        category = next((item for item in self.matrix.categories if item.id == category_id), None)
        if category and category.weight != weight:
            updated = Category(category.id, category.matrix_id, category.name, weight, category.data_type, category.direction)
            self._run(lambda: self.service.update_category(updated), lambda _: self.refresh())

    def delete_category(self) -> None:
        if self.matrix and self.categories.currentRow() >= 0:
            category = self.matrix.categories[self.categories.currentRow()]
            if self._confirm(f"Delete {category.name}?"): self.service.delete_category(category.id or 0); self.refresh()

    def set_value(self, option_id: int, category_id: int, raw: str) -> None:
        category = next((item for item in self.matrix.categories if item.id == category_id), None) if self.matrix else None
        if category: self._run(lambda: self.service.set_value(option_id, category, raw), lambda _: self.refresh())

    def _selected_option(self) -> Option | None:
        return next((option for option in self.matrix.options if option.id == self.matrix_view.selected_option_id()), None) if self.matrix else None

    def _run(self, operation: Callable, success: Callable) -> None:
        try: success(operation())
        except ValidationError as error: QMessageBox.warning(self, "Validation", str(error)); self.refresh()

    def _confirm(self, question: str) -> bool:
        return QMessageBox.question(self, "Confirm", question) == QMessageBox.StandardButton.Yes
