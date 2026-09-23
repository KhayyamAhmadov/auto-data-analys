import os
import re
import shutil
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # server/headless mühitdə GUI backend xətasının qarşısını alır
import matplotlib.pyplot as plt
import seaborn as sns


def sanitize_filename(name):
    name = str(name).strip()
    name = re.sub(r"[^\w\-]", "_", name, flags=re.UNICODE)
    return name or "unnamed"


class DataVisualization:
    def __init__(self, df, column_types, charts_dir="charts", clear_existing=True, max_sample=5000):
        self.df = df
        self.column_types = column_types
        self.charts_dir = charts_dir
        self.max_sample = max_sample

        if clear_existing and os.path.exists(self.charts_dir):
            shutil.rmtree(self.charts_dir)

        os.makedirs(self.charts_dir, exist_ok=True)

    def valid_columns(self, key):
        columns = self.column_types.get(key, [])
        return [c for c in columns if c in self.df.columns]

    def _sampled_df(self):
        """Böyük datasetlərdə qrafik performansı üçün seçmə (sample) aparır."""
        if len(self.df) > self.max_sample:
            return self.df.sample(self.max_sample, random_state=42)
        return self.df

    # ------------------------------------------------------------------
    # Əsas qrafiklər
    # ------------------------------------------------------------------
    def numeric_charts(self):
        charts = []
        for column in self.valid_columns("numeric"):
            series = self.df[column].dropna()
            if series.empty:
                continue

            safe_name = sanitize_filename(column)

            try:
                plt.figure(figsize=(8, 5))
                plt.hist(series, bins=30)
                plt.title(f"{column} Distribution")
                plt.xlabel(column)
                plt.ylabel("Frequency")
                path = os.path.join(self.charts_dir, f"{safe_name}_histogram.png")
                plt.savefig(path, bbox_inches="tight")
                plt.close()
                charts.append((f"{column} - Paylanma (Histogram)", path))

                plt.figure(figsize=(8, 4))
                sns.boxplot(x=series)
                plt.title(f"{column} Boxplot")
                path = os.path.join(self.charts_dir, f"{safe_name}_boxplot.png")
                plt.savefig(path, bbox_inches="tight")
                plt.close()
                charts.append((f"{column} - Kənar dəyərlər (Boxplot)", path))
            except Exception as e:
                plt.close()
                print(f"Xəbərdarlıq: '{column}' üçün qrafik yaradıla bilmədi: {e}")

        return charts

    def categorical_charts(self):
        charts = []
        for column in self.valid_columns("categorical"):
            series = self.df[column].dropna()
            if series.empty or series.nunique() <= 1 or series.nunique() > 20:
                continue

            safe_name = sanitize_filename(column)

            try:
                plt.figure(figsize=(8, 5))
                series.value_counts().head(10).plot(kind="bar")
                plt.title(f"{column} Distribution")
                plt.xlabel(column)
                plt.ylabel("Count")
                plt.xticks(rotation=45, ha="right")
                path = os.path.join(self.charts_dir, f"{safe_name}_bar.png")
                plt.savefig(path, bbox_inches="tight")
                plt.close()
                charts.append((f"{column} - Ən çox rast gəlinən dəyərlər", path))
            except Exception as e:
                plt.close()
                print(f"Xəbərdarlıq: '{column}' üçün qrafik yaradıla bilmədi: {e}")

        return charts

    def correlation_chart(self):
        columns = self.valid_columns("numeric")
        if len(columns) < 2:
            return None

        corr = self.df[columns].corr()
        if corr.isna().all().all():
            return None

        try:
            size = max(6, min(1.1 * len(columns), 20))
            plt.figure(figsize=(size, size * 0.8))
            sns.heatmap(corr, annot=len(columns) <= 20, fmt=".2f", cmap="coolwarm", center=0)
            plt.title("Correlation Matrix")
            path = os.path.join(self.charts_dir, "correlation.png")
            plt.savefig(path, bbox_inches="tight")
            plt.close()
            return ("Korrelyasiya Matrisi", path)
        except Exception as e:
            plt.close()
            print(f"Xəbərdarlıq: korrelyasiya qrafiki yaradıla bilmədi: {e}")
            return None

    # ------------------------------------------------------------------
    # Əlavə qrafiklər
    # ------------------------------------------------------------------
    def missing_values_chart(self):
        """Boşluqların (missing values) datasetdə necə yerləşdiyini göstərən xəritə."""
        if not self.df.isnull().values.any():
            return None
        try:
            plt.figure(figsize=(10, 6))
            sns.heatmap(self.df.isnull(), cbar=False, yticklabels=False, cmap="viridis")
            plt.title("Çatışmayan Dəyərlərin Xəritəsi")
            path = os.path.join(self.charts_dir, "missing_values_heatmap.png")
            plt.savefig(path, bbox_inches="tight")
            plt.close()
            return ("Çatışmayan Dəyərlərin Xəritəsi", path)
        except Exception as e:
            plt.close()
            print(f"Xəbərdarlıq: missing-value xəritəsi yaradıla bilmədi: {e}")
            return None

    def pairplot_chart(self, max_columns=5):
        """Ədədi sütunlar arasındakı əlaqəni göstərən scatter matrix (pairplot)."""
        columns = self.valid_columns("numeric")[:max_columns]
        if len(columns) < 2:
            return None
        try:
            data = self._sampled_df()[columns].dropna()
            if len(data) < 5:
                return None
            grid = sns.pairplot(data)
            path = os.path.join(self.charts_dir, "pairplot.png")
            grid.savefig(path, bbox_inches="tight")
            plt.close("all")
            return ("Ədədi Sütunlar Arası Əlaqə (Pairplot)", path)
        except Exception as e:
            plt.close("all")
            print(f"Xəbərdarlıq: pairplot yaradıla bilmədi: {e}")
            return None

    def time_series_charts(self, max_combinations=4):
        """Datetime + ədədi sütun kombinasiyaları üçün zaman sırası qrafiki."""
        charts = []
        datetime_columns = self.valid_columns("datetime")
        numeric_columns = self.valid_columns("numeric")
        if not datetime_columns or not numeric_columns:
            return charts

        combos = 0
        for date_column in datetime_columns:
            dates = pd.to_datetime(self.df[date_column], errors="coerce")
            for num_column in numeric_columns:
                if combos >= max_combinations:
                    return charts
                try:
                    temp = pd.DataFrame({date_column: dates, num_column: self.df[num_column]}).dropna()
                    if len(temp) < 5:
                        continue
                    temp = temp.sort_values(date_column)

                    # Çox nöqtə varsa, günlük ortalamaya endiririk ki, qrafik oxunaqlı qalsın
                    if len(temp) > 500:
                        temp = temp.set_index(date_column).resample("D").mean().dropna().reset_index()

                    safe_name = sanitize_filename(f"{date_column}_{num_column}")
                    plt.figure(figsize=(9, 4))
                    plt.plot(temp[date_column], temp[num_column])
                    plt.title(f"{num_column} zamanla dəyişməsi ({date_column})")
                    plt.xlabel(date_column)
                    plt.ylabel(num_column)
                    plt.xticks(rotation=30, ha="right")
                    path = os.path.join(self.charts_dir, f"timeseries_{safe_name}.png")
                    plt.savefig(path, bbox_inches="tight")
                    plt.close()
                    charts.append((f"{num_column} - Zaman sırası ({date_column})", path))
                    combos += 1
                except Exception as e:
                    plt.close()
                    print(f"Xəbərdarlıq: zaman sırası qrafiki yaradıla bilmədi ({date_column}, {num_column}): {e}")

        return charts

    def grouped_boxplot_charts(self, max_combinations=4, max_categories=8):
        """Kateqorik sütun üzrə qruplaşdırılmış ədədi dəyər boxplot-ları (məs. maaş - şəhər üzrə)."""
        charts = []
        categorical_columns = self.valid_columns("categorical")
        numeric_columns = self.valid_columns("numeric")
        if not categorical_columns or not numeric_columns:
            return charts

        combos = 0
        for cat_column in categorical_columns:
            if self.df[cat_column].nunique(dropna=True) > max_categories:
                continue
            for num_column in numeric_columns:
                if combos >= max_combinations:
                    return charts
                try:
                    data = self.df[[cat_column, num_column]].dropna()
                    if data.empty:
                        continue
                    safe_name = sanitize_filename(f"{cat_column}_{num_column}")
                    plt.figure(figsize=(8, 5))
                    sns.boxplot(data=data, x=cat_column, y=num_column)
                    plt.title(f"{num_column} - {cat_column} üzrə")
                    plt.xticks(rotation=30, ha="right")
                    path = os.path.join(self.charts_dir, f"grouped_{safe_name}_boxplot.png")
                    plt.savefig(path, bbox_inches="tight")
                    plt.close()
                    charts.append((f"{num_column} sütununun {cat_column} üzrə paylanması", path))
                    combos += 1
                except Exception as e:
                    plt.close()
                    print(f"Xəbərdarlıq: qruplaşdırılmış boxplot yaradıla bilmədi ({cat_column}, {num_column}): {e}")

        return charts

    def run(self):
        charts = []
        charts.extend(self.numeric_charts())
        charts.extend(self.categorical_charts())

        missing_chart = self.missing_values_chart()
        if missing_chart:
            charts.append(missing_chart)

        correlation = self.correlation_chart()
        if correlation:
            charts.append(correlation)

        pairplot = self.pairplot_chart()
        if pairplot:
            charts.append(pairplot)

        charts.extend(self.time_series_charts())
        charts.extend(self.grouped_boxplot_charts())

        return charts