# Decision Matrix

A desktop application for comparing options with weighted criteria. The included sample matrix uses fictional law schools, but the engine is generic: it can compare any options such as jobs, apartments, or cars.

## Install and run (development)

```powershell
cd law_school_matrix
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m app.main
```

The app opens with no project and no sample data. Create a project from the **Projects** menu or import a CSV. Projects are saved automatically in your Windows app-data folder and the last project reopens on your next launch.

## Projects

Use the **Projects** menu to create, switch, rename, or delete separate decision matrices. **Save** (`Ctrl+S`) saves the current project selection and window layout; edits to categories, options, and values are already saved as you make them.

## Share a clean Windows app

On a Windows machine with Python 3.12 installed, run this from PowerShell:

```powershell
cd law_school_matrix
.\tools\build_release.ps1
```

It creates `DecisionMatrix-Windows.zip`. Send that ZIP to someone else; they only need to extract it and double-click `DecisionMatrix.exe`. Their projects are stored in their own Windows app-data location, so your data is never bundled. To share a particular matrix, use **File → Export / link CSV…** and send the exported CSV separately.

For the one-command workflow that rebuilds and replaces the copy in your desktop's `DM Application` folder, see [DEVELOPMENT.md](DEVELOPMENT.md).

Run tests with:

```powershell
$env:PYTHONPATH = "src"
pytest
```

## Import a CSV

Use **Import CSV** in the sidebar or File menu. A simple wide CSV creates numeric, higher-is-better categories with equal importance:

```csv
School / Option,Employment Outcomes,Cost
Atlas Law,91,60000
Beacon Law,84,48000
```

For full control, add these optional rows directly below the header. Values may be blank where the default is wanted.

```csv
School / Option,Employment Outcomes,Cost of Attendance,Location
#weight,8,7,5
#type,rating,numeric,rating
#direction,higher_is_better,lower_is_better,higher_is_better
Atlas Law,91,60000,82
Beacon Law,84,48000,90
```

Allowed types are `numeric` and `rating`; allowed directions are `higher_is_better` and `lower_is_better`. `#weight` is an optional whole-number importance rating from 1 to 10; if omitted, every category starts at 5. Blank option values remain `N/A`, and the imported matrix is created as a new saved matrix so existing work is not overwritten.

Imported matrices stay linked to their CSV: subsequent edits to options, category importance, directions, or values automatically update that same file. To link an existing manually created matrix, choose **File → Export / link CSV…** once.

## Scoring

Numeric values are normalized across the current options. Higher-is-better uses `100 * (x-min)/(max-min)`; lower-is-better reverses it. Equal numeric values receive 100. Ratings are entered directly from 0 to 100. Rate each category's importance from 1 (least important) to 10 (most important); the application normalizes those ratings internally. Missing values yield `N/A` rather than a misleading score.

## Structure

- `domain`: typed entities and enums.
- `calculations`: PySide-independent normalization, scoring, and ranking.
- `persistence`: SQLite schema and repository.
- `services`: validation and application use cases.
- `gui`: PySide6 dialogs and views.

See [ARCHITECTURE.md](ARCHITECTURE.md) for data flow, schema, and extension guidance.
