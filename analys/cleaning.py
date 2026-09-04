import numpy as np


class DataCleaning:
    def __init__(self, df, column_types):
        self.df = df
        self.column_types = column_types

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
                result[i] = 0
                continue

            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            count = ((series < lower) | (series > upper)).sum()
            result[i] = int(count)

        return result

    def run(self):
        return {"missing": self.missing_values(), "missing_percentage": self.missing_percentage(), "duplicates": self.duplicates(), "outliers": self.outliers()}