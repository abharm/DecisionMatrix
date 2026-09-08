from app.domain.models import CategoryDataType, Direction
from app.persistence.repositories import MatrixRepository
from app.services.matrix_service import MatrixService, ValidationError


def test_import_csv_with_scoring_metadata(tmp_path):
    source = tmp_path / "schools.csv"
    source.write_text("School,Employment,Cost\n#weight,8,6\n#type,rating,numeric\n#direction,higher_is_better,lower_is_better\nAlpha,90,70000\nBeta,80,50000\n", encoding="utf-8")
    repository = MatrixRepository(tmp_path / "test.db")
    service = MatrixService(repository)
    matrix = service.import_csv(source, "Imported")
    assert [category.weight for category in matrix.categories] == [8, 6]
    assert matrix.categories[0].data_type == CategoryDataType.RATING
    assert matrix.categories[1].direction == Direction.LOWER_IS_BETTER
    assert matrix.options[0].values
    assert service.calculate(matrix).option_results[matrix.options[0].id].overall_score is not None
    repository.close()


def test_import_simple_csv_uses_defaults(tmp_path):
    source = tmp_path / "options.csv"
    source.write_text("Option,Quality,Price\nA,2,5\nB,4,3\n", encoding="utf-8")
    repository = MatrixRepository(tmp_path / "test.db")
    matrix = MatrixService(repository).import_csv(source)
    assert [category.weight for category in matrix.categories] == [5, 5]
    assert all(category.data_type == CategoryDataType.NUMERIC for category in matrix.categories)
    repository.close()


def test_import_rejects_invalid_metadata(tmp_path):
    source = tmp_path / "bad.csv"
    source.write_text("Option,Score\n#type,letters\nA,50\n", encoding="utf-8")
    repository = MatrixRepository(tmp_path / "test.db")
    try:
        with __import__("pytest").raises(ValidationError):
            MatrixService(repository).import_csv(source)
    finally:
        repository.close()


def test_linked_csv_updates_after_editing_matrix(tmp_path):
    source = tmp_path / "linked.csv"
    source.write_text("School,Score\nAlpha,50\n", encoding="utf-8")
    repository = MatrixRepository(tmp_path / "test.db")
    service = MatrixService(repository)
    matrix = service.import_csv(source)
    category = matrix.categories[0]
    option = matrix.options[0]
    service.update_category(category.__class__(category.id, category.matrix_id, category.name, 9, category.data_type, category.direction))
    service.set_value(option.id, category, "75")
    written = source.read_text(encoding="utf-8")
    assert "#weight,9" in written
    assert "Alpha,75" in written
    repository.close()
