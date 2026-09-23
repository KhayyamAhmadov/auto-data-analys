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
        text = []

        for i in self.df.columns:
            series = self.df[i]
            n = len(series)

            unique_ratio = series.nunique(dropna=True) / n if n > 0 else 0
            col_lower = str(i).lower()

            # Aydın ID adlandırması: "id", "user_id", "id_number" və s.
            explicit_id_name = (
                col_lower == "id"
                or col_lower.endswith("_id")
                or col_lower.startswith("id_")
            )
            # "userid" kimi ayırıcısız adlar üçün daha ciddi meyar tələb olunur ki,
            # "grid", "valid", "solid" kimi sözlər səhvən ID sayılmasın.
            probable_id_name = (
                col_lower.endswith("id")
                and len(col_lower) > 2
                and unique_ratio > 0.95
            )

            is_id = explicit_id_name or probable_id_name
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
                # object/string sütun - sərbəst mətn yoxsa kateqoriyadır?
                non_null = series.dropna().astype(str)
                avg_len = non_null.str.len().mean() if not non_null.empty else 0
                if unique_ratio > 0.5 and avg_len > 30:
                    text.append(i)
                else:
                    categorical.append(i)

        return {
            "numeric": numeric,
            "categorical": categorical,
            "datetime": datetime,
            "id": id_columns,
            "text": text,
        }

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
                    "id": [],
                    "text": [],
                },
            }

        types = self.column_types()
        return {
            "rows": self.df.shape[0],
            "columns": self.df.shape[1],
            "column_names": list(self.df.columns),
            "column_types": types,
        }