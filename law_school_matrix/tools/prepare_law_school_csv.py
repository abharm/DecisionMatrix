"""Create an import-ready numeric decision-matrix CSV from the supplied file."""
import csv
import re
from pathlib import Path

SOURCE = Path(r"C:\Users\bharm\Downloads\law_school_comparison - law_school.csv")
OUTPUT = Path(__file__).resolve().parents[1] / "law_school_comparison_import_ready.csv"

COLUMNS = [
    (3, "US News Rank", "lower_is_better"), (4, "Overall Prestige", "higher_is_better"),
    (5, "Public Defender Fit", "higher_is_better"), (6, "Public Interest Strength", "higher_is_better"),
    (7, "Median LSAT", "higher_is_better"), (8, "Median GPA", "higher_is_better"),
    (9, "Acceptance Rate", "higher_is_better"), (10, "Admission Chance (160 LSAT)", "higher_is_better"),
    (11, "Admission Chance (165 LSAT)", "higher_is_better"), (12, "Selectivity Tier", "lower_is_better"),
    (14, "Government Employment", "higher_is_better"), (15, "Public Interest Employment", "higher_is_better"),
    (18, "Annual Tuition", "lower_is_better"), (19, "Annual Cost of Attendance", "lower_is_better"),
    (20, "Three-Year Cost", "lower_is_better"), (21, "Scholarship Potential", "higher_is_better"),
    (23, "LRAP Rating", "higher_is_better"),
]


def numeric(value: str) -> str:
    """Remove display formatting; conservatively map '<5%' to 4 for import."""
    cleaned = value.strip().replace(",", "").replace("$", "").replace("%", "")
    if cleaned.startswith("<"):
        return str(float(re.sub(r"[^0-9.]", "", cleaned)) - 1)
    return cleaned


with SOURCE.open(encoding="utf-8-sig", newline="") as source, OUTPUT.open("w", encoding="utf-8", newline="") as target:
    reader = csv.reader(source)
    writer = csv.writer(target)
    next(reader)
    writer.writerow(["School / Option", *[name for _, name, _ in COLUMNS]])
    writer.writerow(["#weight", *([5] * len(COLUMNS))])
    writer.writerow(["#type", *(["numeric"] * len(COLUMNS))])
    writer.writerow(["#direction", *[direction for _, _, direction in COLUMNS]])
    for row in reader:
        writer.writerow([row[0], *[numeric(row[index]) for index, _, _ in COLUMNS]])

print(OUTPUT)
