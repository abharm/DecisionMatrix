import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.gui.category_dialog import CategoryDialog


def test_typed_importance_is_committed_before_save():
    app = QApplication.instance() or QApplication([])
    dialog = CategoryDialog()
    dialog.weight.lineEdit().setText("9")

    assert dialog.values()[1] == 9
