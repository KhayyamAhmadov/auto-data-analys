import numpy as np
import pandas as pd


class DataCleaning:
    def __init__(self, df, column_types):
        self.df = df
        self.column_types = column_types

    # ------------------------------------------------------------------
    # Əsas keyfiyyət yoxlamaları
    # ------------------------------------------------------------------
    def missing_values(self):
        missing = self.df.isnull().sum()
        missing = missing[missing > 0]
        return missing.to_dict()

    def missing_percentage(self):
        percentage = self.df.isnull().mean() * 100
        percentage = percentage[percentage > 0]
        return percentage.round(2).to_dict()

    def duplicates(self):
        return int(self.df.duplicated().sum())

    def duplicate_percentage(self):
        n = len(self.df)
        if n == 0:
            return 0.0
        return round(self.duplicates() / n * 100, 2)

    def outliers(self):
        result = {}
        for i in self.column_types.get("numeric", []):
            if i not in self.df.columns:
                continue

            series = self.df[i].dropna()
            if len(series) < 5:
                continue

            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1

            if IQR == 0:
                # Bütün dəyərlər demək olar eynidir (Q1 == Q3).
                # Bu halda "outlier" - əksəriyyətdən fərqli olan dəyərlərdir.
                mode_value = Q1
                result[i] = int((series != mode_value).sum())
                continue

            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            count = ((series < lower) | (series > upper)).sum()
            result[i] = int(count)

        return result

    # ------------------------------------------------------------------
    # Əlavə keyfiyyət yoxlamaları
    # ------------------------------------------------------------------
    def constant_columns(self):
        """Bütün (qeyri-boş) sətirlərdə eyni dəyəri olan sütunlar - faydasızdır."""
        result = []
        for column in self.df.columns:
            non_null = self.df[column].dropna()
            if non_null.empty:
                continue
            if non_null.nunique() == 1:
                result.append(column)
        return result

    def duplicate_columns(self):
        """Bir-birinin tam eyni olan sütun cütləri."""
        result = []
        columns = list(self.df.columns)
        for i in range(len(columns)):
            for j in range(i + 1, len(columns)):
                col_a, col_b = columns[i], columns[j]
                try:
                    if self.df[col_a].equals(self.df[col_b]):
                        result.append((col_a, col_b))
                except Exception:
                    continue
        return result

    def high_cardinality_columns(self, threshold=0.9):
        """Kateqorik sütunlarda unikal dəyər nisbəti çox yüksəkdirsə (mətn ola bilər)."""
        result = {}
        n = len(self.df)
        if n == 0:
            return result
        for column in self.column_types.get("categorical", []):
            if column not in self.df.columns:
                continue
            ratio = self.df[column].nunique(dropna=True) / n
            if ratio > threshold:
                result[column] = round(ratio * 100, 2)
        return result

    def type_mismatches(self):
        """Kateqorik/mətn kimi saxlanan, amma əslində ədədi olan sütunlar."""
        result = []
        candidates = self.column_types.get("categorical", []) + self.column_types.get("text", [])
        for column in candidates:
            if column not in self.df.columns:
                continue
            series = self.df[column].dropna()
            if series.empty:
                continue
            converted = pd.to_numeric(series, errors="coerce")
            valid_ratio = converted.notna().mean()
            if valid_ratio > 0.9:
                result.append(column)
        return result

    def rare_categories(self, threshold=0.02, max_unique=30):
        """Tezliyi çox aşağı olan kateqoriyalar (yazı səhvi, nadir hal ola bilər).
        Unikal dəyər sayı çox yüksək olan sütunlar (demək olar hər dəyər fərqlidir)
        bu yoxlamadan çıxarılır, çünki nəticə mənasız və çox böyük olardı - belə
        sütunlar artıq `high_cardinality_columns` vasitəsilə ayrıca işarələnir.
        """
        result = {}
        n = len(self.df)
        if n == 0:
            return result
        for column in self.column_types.get("categorical", []):
            if column not in self.df.columns:
                continue
            if self.df[column].nunique(dropna=True) > max_unique:
                continue
            counts = self.df[column].value_counts(normalize=True, dropna=True)
            rare = counts[counts < threshold]
            if not rare.empty:
                result[column] = (rare * 100).round(2).to_dict()
        return result

    def quality_score(self):
        """
        0-100 aralığında ümumi data keyfiyyət balı.
        100-dən başlayır, hər problem növünə görə məhdud (capped) cəza tətbiq olunur ki,
        tək bir problem balı sıfıra endirməsin.
        """
        score = 100.0
        n_rows = len(self.df)
        n_cols = len(self.df.columns) or 1

        missing_pct = self.missing_percentage()
        if missing_pct:
            avg_missing = sum(missing_pct.values()) / n_cols
            score -= min(avg_missing * 0.5, 25)

        score -= min(self.duplicate_percentage() * 0.5, 15)

        outliers = self.outliers()
        if outliers and n_rows > 0:
            total_outliers = sum(outliers.values())
            outlier_ratio = total_outliers / (n_rows * max(len(outliers), 1))
            score -= min(outlier_ratio * 100 * 0.3, 15)

        score -= min(len(self.constant_columns()) * 3, 15)
        score -= min(len(self.duplicate_columns()) * 3, 10)
        score -= min(len(self.type_mismatches()) * 3, 10)
        score -= min(len(self.high_cardinality_columns()) * 2, 10)

        return max(0.0, round(score, 1))

    def run(self):
        return {
            "missing": self.missing_values(),
            "missing_percentage": self.missing_percentage(),
            "duplicates": self.duplicates(),
            "duplicate_percentage": self.duplicate_percentage(),
            "outliers": self.outliers(),
            "constant_columns": self.constant_columns(),
            "duplicate_columns": self.duplicate_columns(),
            "high_cardinality": self.high_cardinality_columns(),
            "type_mismatches": self.type_mismatches(),
            "rare_categories": self.rare_categories(),
            "quality_score": self.quality_score(),
        }