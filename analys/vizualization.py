import os
import re
import shutil
import matplotlib.pyplot as plt
import seaborn as sns


def sanitize_filename(name):
    name = str(name).strip()
    name = re.sub(r"[^\w\-]", "_", name, flags=re.UNICODE)
    return name or "unnamed"


class DataVisualization:
    def __init__(self, df, column_types, charts_dir="charts", clear_existing=True):
        self.df = df
        self.column_types = column_types
        self.charts_dir = charts_dir

        if clear_existing and os.path.exists(self.charts_dir):
            shutil.rmtree(self.charts_dir)

        os.makedirs(self.charts_dir, exist_ok=True)

    def valid_columns(self, key):
        columns = self.column_types.get(key, [])
        return [c for c in columns if c in self.df.columns]

    def numeric_charts(self):
        charts = []
        for column in self.valid_columns("numeric"):
            series = self.df[column].dropna()
            if series.empty:
                continue

            safe_name = sanitize_filename(column)

            plt.figure(figsize=(8, 5))
            plt.hist(series, bins=30)
            plt.title(f"{column} Distribution")
            plt.xlabel(column)
            plt.ylabel("Frequency")
            path = os.path.join(self.charts_dir, f"{safe_name}_histogram.png")
            plt.savefig(path, bbox_inches="tight")
            plt.close()
            charts.append(path)

            plt.figure(figsize=(8, 4))
            sns.boxplot(x=series)
            plt.title(f"{column} Boxplot")
            path = os.path.join(self.charts_dir, f"{safe_name}_boxplot.png")
            plt.savefig(path, bbox_inches="tight")
            plt.close()
            charts.append(path)

        return charts

    def categorical_charts(self):
        charts = []
        for column in self.valid_columns("categorical"):
            series = self.df[column].dropna()
            if series.empty or series.nunique() > 20:
                continue

            safe_name = sanitize_filename(column)

            plt.figure(figsize=(8, 5))
            series.value_counts().head(10).plot(kind="bar")
            plt.title(f"{column} Distribution")
            plt.xlabel(column)
            plt.ylabel("Count")
            path = os.path.join(self.charts_dir, f"{safe_name}_bar.png")
            plt.savefig(path, bbox_inches="tight")
            plt.close()
            charts.append(path)

        return charts

    def correlation_chart(self):
        columns = self.valid_columns("numeric")
        if len(columns) < 2:
            return None

        corr = self.df[columns].corr()
        if corr.isna().all().all():
            return None

        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True, fmt=".2f")
        plt.title("Correlation Matrix")
        path = os.path.join(self.charts_dir, "correlation.png")
        plt.savefig(path, bbox_inches="tight")
        plt.close()
        return path

    def run(self):
        charts = []
        charts.extend(self.numeric_charts())
        charts.extend(self.categorical_charts())

        correlation = self.correlation_chart()
        if correlation:
            charts.append(correlation)

        return charts