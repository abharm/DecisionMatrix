# Architecture

The GUI calls `MatrixService`, never SQLite directly. The service validates changes through a repository and invokes the calculation engine to produce a derived `MatrixResult`. The calculation package depends only on domain models and is covered by unit tests without PySide6.

SQLite tables: `matrices(id, name)`, `categories(id, matrix_id, name, weight, data_type, direction)`, `schools(id, matrix_id, name)`, and `school_values(school_id, category_id, raw_value)`. Calculated values are intentionally not stored.

To add a criterion type, extend `CategoryDataType` and the normalizer dispatch. To add another normalization strategy, add a focused function in `calculations.normalization` and select it from `normalize_category`. Future views should continue calling service methods so validation and persistence remain consistent.
