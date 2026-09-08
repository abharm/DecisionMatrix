import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.domain.models import CategoryDataType, Direction
from app.gui.main_window import MainWindow
from app.persistence.repositories import MatrixRepository
from app.services.matrix_service import MatrixService


def test_category_table_weighting_saves_immediately(tmp_path):
    app = QApplication.instance() or QApplication([])
    repository = MatrixRepository(tmp_path / "matrix.db")
    service = MatrixService(repository)
    matrix = service.create_matrix("Test project")
    category = service.add_category(matrix.id, "Cost", 4, CategoryDataType.NUMERIC, Direction.LOWER_IS_BETTER)
    window = MainWindow(service, matrix.id)

    weighting = window.categories.cellWidget(0, 1)
    weighting.setValue(9)

    assert service.load(matrix.id).categories[0].weight == 9
    window.close()
    repository.close()
