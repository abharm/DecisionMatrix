import pytest

from app.domain.models import Category, CategoryDataType, Direction
from app.persistence.repositories import MatrixRepository
from app.services.matrix_service import MatrixService, ValidationError


@pytest.fixture
def service(tmp_path):
    repository = MatrixRepository(tmp_path / "test.db")
    yield MatrixService(repository)
    repository.close()


def test_add_and_remove_schools_and_categories(service):
    matrix = service.create_matrix("Choices")
    category = service.add_category(matrix.id, "Cost", 7, CategoryDataType.NUMERIC, Direction.LOWER_IS_BETTER)
    option = service.add_option(matrix.id, "One")
    service.set_value(option.id, category, "300")
    assert service.load(matrix.id).options[0].values[category.id] == 300
    service.delete_option(option.id)
    service.delete_category(category.id)
    loaded = service.load(matrix.id)
    assert not loaded.options and not loaded.categories


def test_service_validation(service):
    matrix = service.create_matrix("Choices")
    with pytest.raises(ValidationError):
        service.add_category(matrix.id, "", 1, CategoryDataType.NUMERIC, Direction.HIGHER_IS_BETTER)
    with pytest.raises(ValidationError):
        service.add_category(matrix.id, "X", 0, CategoryDataType.NUMERIC, Direction.HIGHER_IS_BETTER)
    category = service.add_category(matrix.id, "Rating", 1, CategoryDataType.RATING, Direction.HIGHER_IS_BETTER)
    option = service.add_option(matrix.id, "One")
    with pytest.raises(ValidationError):
        service.set_value(option.id, category, "101")


def test_projects_and_category_importance_persist(service):
    first = service.create_matrix("First")
    second = service.create_matrix("Second")
    category = service.add_category(first.id, "Cost", 3, CategoryDataType.NUMERIC, Direction.LOWER_IS_BETTER)
    service.update_category(Category(category.id, category.matrix_id, category.name, 9, category.data_type, category.direction))
    service.rename_matrix(second.id, "Renamed")

    assert service.load(first.id).categories[0].weight == 9
    assert [matrix.name for matrix in service.repository.list_matrices()] == ["First", "Renamed"]
    service.delete_matrix(first.id)
    assert [matrix.name for matrix in service.repository.list_matrices()] == ["Renamed"]
