import pandas as pd
import numpy as np


class DataProfiler:
    def __init__(self, df):
        self.df = df

    def column_types(self):
        numeric = []
        categorical = []
        datetime = []
        id_columns = []

        for i in self.df.columns:
            series = self.df[i]
            n = len(series)

            unique_ratio = series.nunique(dropna=True) / n if n > 0 else 0
            col_lower = i.lower()

            is_id = (col_lower.endswith("_id") or col_lower == "id" or (col_lower.endswith("id") and unique_ratio > 0.8))
            if is_id:
                id_columns.append(i)
                continue

            if pd.api.types.is_datetime64_any_dtype(series):
                datetime.append(i)
                continue

            if series.dtype == "object":
                converted = pd.to_datetime(series, errors="coerce")
                valid_ratio = converted.notna().mean() if n > 0 else 0
                if valid_ratio > 0.8:
                    datetime.append(i)
                    continue

            if pd.api.types.is_bool_dtype(series):
                categorical.append(i)
            elif pd.api.types.is_numeric_dtype(series):
                numeric.append(i)
            else:
                categorical.append(i)

        return {"numeric": numeric, "categorical": categorical, "datetime": datetime, "id": id_columns}
    
    def profile(self):
        if self.df.shape[0] == 0:
            return {
                "rows": 0,
                "columns": self.df.shape[1],
                "column_names": list(self.df.columns),
                "column_types": {
                    "numeric": [],
                    "categorical": [],
                    "datetime": [],
                    "id": []}}

        types = self.column_types()
        return {"rows": self.df.shape[0], "columns": self.df.shape[1], "column_names": list(self.df.columns), "column_types": types}