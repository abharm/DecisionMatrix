"""A compact visual summary of the current ranking."""
from PySide6.QtCore import Qt
from PySide6.QtCharts import QBarCategoryAxis, QBarSet, QChart, QChartView, QHorizontalBarSeries, QValueAxis
from PySide6.QtGui import QBrush, QColor, QPainter

from app.domain.models import Matrix, MatrixResult


class RankingChart(QChartView):
    """Horizontal bar chart rendered from calculated, not persisted, scores."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMinimumHeight(300)
        self.setStyleSheet("background: transparent; border: 0;")

    def show_results(self, matrix: Matrix, result: MatrixResult) -> None:
        chart = QChart()
        chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        chart.setTitle("Top 10 overall scores")
        chart.setTitleBrush(QBrush(QColor("#FFFFFF")))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.legend().hide()
        scored = [(option, result.option_results.get(option.id)) for option in matrix.options]
        scored = [(option, item) for option, item in scored if item and item.overall_score is not None]
        scored.sort(key=lambda entry: (entry[1].rank or 9999, entry[0].name))
        if not scored:
            chart.setTitle("Overall score comparison — add complete values to see the chart")
            self.setChart(chart)
            return
        scored = scored[:10]
        bars = QBarSet("Overall score")
        bars.setColor(QColor("#2563EB"))
        bars.setLabelColor(QColor("#FFFFFF"))
        bars.append([item.overall_score for _, item in scored])
        series = QHorizontalBarSeries()
        series.append(bars)
        series.setLabelsVisible(True)
        series.setLabelsFormat("@value")
        categories = QBarCategoryAxis()
        categories.append([f"#{item.rank}  {option.name}" for option, item in scored])
        values = QValueAxis()
        values.setRange(0, 100)
        values.setLabelFormat("%.0f")
        values.setTitleText("Score (0–100)")
        for axis in (categories, values):
            axis.setLabelsBrush(QBrush(QColor("#FFFFFF")))
            axis.setTitleBrush(QBrush(QColor("#FFFFFF")))
        chart.addSeries(series)
        chart.addAxis(categories, Qt.AlignmentFlag.AlignLeft)
        chart.addAxis(values, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(categories)
        series.attachAxis(values)
        chart.setBackgroundVisible(False)
        chart.setPlotAreaBackgroundVisible(False)
        self.setChart(chart)

    def clear_chart(self) -> None:
        """Remove results when no project is open."""
        chart = QChart()
        chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        chart.setTitle("Create a project to see rankings")
        chart.setTitleBrush(QBrush(QColor("#FFFFFF")))
        chart.setBackgroundVisible(False)
        self.setChart(chart)
