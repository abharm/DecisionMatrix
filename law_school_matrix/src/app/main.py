"""Application entry point."""
import sys
from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QApplication
from app.gui.main_window import MainWindow
from app.persistence.repositories import MatrixRepository
from app.services.matrix_service import MatrixService


def database_path() -> Path:
    """Return a per-user data location that also works from a packaged app."""
    folder = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "decision_matrix.db"


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Decision Matrix")
    app.setOrganizationName("Decision Matrix")
    repository = MatrixRepository(database_path())
    service = MatrixService(repository)
    window = MainWindow(service)
    window.show()
    exit_code = app.exec()
    repository.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
