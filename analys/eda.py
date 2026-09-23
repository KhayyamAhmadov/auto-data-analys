import numpy as np
import pandas as pd


class DataEDA:
    def __init__(self, df, column_types):
        self.df = df
        self.column_types = column_types

    def valid_columns(self, key):
        columns = self.column_types.get(key, [])
        return [c for c in columns if c in self.df.columns]

    # ------------------------------------------------------------------
    # Ədədi statistikalar
    # ------------------------------------------------------------------
    def numeric_statistic(self):
        columns = self.valid_columns("numeric")
        if not columns:
            return pd.DataFrame()
        return self.df[columns].describe().round(2)

    def skewness_kurtosis(self):
        """Paylanmanın çəpəkiliyi (skewness) və sivriliyi (kurtosis)."""
        result = {}
        for column in self.valid_columns("numeric"):
            series = self.df[column].dropna()
            if len(series) < 3:
                continue
            try:
                result[column] = {
                    "skewness": round(float(series.skew()), 2),
                    "kurtosis": round(float(series.kurt()), 2),
                }
            except Exception:
                continue
        return result

    def correlation(self):
        columns = self.valid_columns("numeric")
        if len(columns) < 2:
            return pd.DataFrame()
        return self.df[columns].corr().round(2)

    def multicollinearity(self):
        """
        VIF (Variance Inflation Factor) - standartlaşdırılmış korrelyasiya matrisinin
        tərsinin diaqonalı vasitəsilə hesablanır (statsmodels asılılığı olmadan).
        VIF > 5 çoxxətli asılılıq (multicollinearity) riskinə işarədir, VIF > 10 ciddi risk deməkdir.
        """
        columns = self.valid_columns("numeric")
        result = {}
        if len(columns) < 2:
            return result

        data = self.df[columns].dropna()
        if len(data) < len(columns) + 1 or data.shape[0] < 3:
            return result

        std = data.std(ddof=0)
        if (std == 0).any():
            # Sabit sütun varsa korrelyasiya matrisi tərslənə bilməz
            columns = [c for c, s in zip(columns, std) if s > 0]
            data = data[columns]
            if len(columns) < 2:
                return result

        corr = data.corr().values
        try:
            inv_corr = np.linalg.inv(corr)
        except np.linalg.LinAlgError:
            try:
                inv_corr = np.linalg.pinv(corr)
            except Exception:
                return result

        for idx, column in enumerate(columns):
            vif = float(inv_corr[idx, idx])
            result[column] = round(vif, 2)
        return result

    # ------------------------------------------------------------------
    # Kateqorik statistikalar
    # ------------------------------------------------------------------
    def categorical_statistics(self):
        result = {}
        for column in self.valid_columns("categorical"):
            result[column] = (self.df[column].value_counts().head(10).to_dict())
        return result

    @staticmethod
    def _chi2(table):
        observed = table.values.astype(float)
        row_sums = observed.sum(axis=1, keepdims=True)
        col_sums = observed.sum(axis=0, keepdims=True)
        total = observed.sum()
        if total == 0:
            return 0.0
        expected = row_sums @ col_sums / total
        with np.errstate(divide="ignore", invalid="ignore"):
            terms = np.where(expected > 0, (observed - expected) ** 2 / expected, 0)
        return float(terms.sum())

    def _cramers_v(self, col_a, col_b):
        """İki kateqorik sütun arasındakı əlaqə gücü (0 = əlaqə yoxdur, 1 = tam əlaqə)."""
        try:
            table = pd.crosstab(self.df[col_a], self.df[col_b])
            if table.size == 0:
                return None
            chi2 = self._chi2(table)
            n = table.values.sum()
            if n <= 1:
                return None
            phi2 = chi2 / n
            r, k = table.shape
            phi2_corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
            r_corr = r - ((r - 1) ** 2) / (n - 1)
            k_corr = k - ((k - 1) ** 2) / (n - 1)
            denom = min((k_corr - 1), (r_corr - 1))
            if denom <= 0:
                return None
            return round(float(np.sqrt(phi2_corr / denom)), 2)
        except Exception:
            return None

    def categorical_association(self, max_columns=8, max_unique=30):
        """Cramér's V matrisi - kateqorik sütunlar arasında əlaqə gücü."""
        columns = self.valid_columns("categorical")
        # Çox yüksək kardinallı sütunları çıxarırıq (hesablama mənasız/ağır olar)
        columns = [c for c in columns if self.df[c].nunique(dropna=True) <= max_unique][:max_columns]

        if len(columns) < 2:
            return pd.DataFrame()

        matrix = pd.DataFrame(index=columns, columns=columns, dtype=float)
        for col_a in columns:
            for col_b in columns:
                if col_a == col_b:
                    matrix.loc[col_a, col_b] = 1.0
                else:
                    value = self._cramers_v(col_a, col_b)
                    matrix.loc[col_a, col_b] = value if value is not None else np.nan
        return matrix.round(2)

    def numeric_by_category(self, max_categories=8):
        """Hər kateqorik sütun üzrə, hər ədədi sütunun kateqoriyalar üzrə orta dəyəri."""
        result = {}
        numeric_columns = self.valid_columns("numeric")
        if not numeric_columns:
            return result

        for cat_column in self.valid_columns("categorical"):
            try:
                if self.df[cat_column].nunique(dropna=True) > max_categories:
                    continue
                grouped = self.df.groupby(cat_column)[numeric_columns].mean().round(2)
                result[cat_column] = grouped.to_dict(orient="index")
            except Exception:
                continue
        return result

    # ------------------------------------------------------------------
    # Tarix statistikaları
    # ------------------------------------------------------------------
    def datetime_analysis(self):
        result = {}
        for column in self.valid_columns("datetime"):
            dates = pd.to_datetime(self.df[column], errors="coerce")
            result[column] = {
                "min": None if dates.isna().all() else str(dates.min()),
                "max": None if dates.isna().all() else str(dates.max()),
                "unique_dates": int(dates.nunique()),
            }
        return result

    def run(self):
        return {
            "numeric_statistic": self.numeric_statistic(),
            "skewness_kurtosis": self.skewness_kurtosis(),
            "categorical_statistics": self.categorical_statistics(),
            "correlation": self.correlation(),
            "categorical_association": self.categorical_association(),
            "numeric_by_category": self.numeric_by_category(),
            "multicollinearity": self.multicollinearity(),
            "datetime": self.datetime_analysis(),
        }