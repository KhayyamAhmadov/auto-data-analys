import pandas as pd
class DataEDA:
    def __init__(self, df, column_types):
        self.df = df
        self.column_types = column_types

    def valid_columns(self, key):
        columns = self.column_types.get(key, [])
        return [c for c in columns if c in self.df.columns]

    def numeric_statistic(self):
        columns = self.valid_columns("numeric")
        if not columns:
            return pd.DataFrame()
        return self.df[columns].describe().round(2)

    def categorical_statistics(self):
        result = {}
        for column in self.valid_columns("categorical"):
            result[column] = (self.df[column].value_counts().head(10).to_dict())
        return result

    def correlation(self):
        columns = self.valid_columns("numeric")
        if len(columns) < 2:
            return pd.DataFrame()
        return self.df[columns].corr().round(2)

    def datetime_analysis(self):
        result = {}
        for column in self.valid_columns("datetime"):
            dates = pd.to_datetime(self.df[column], errors="coerce")
            result[column] = {
                "min": None if dates.isna().all() else str(dates.min()),
                "max": None if dates.isna().all() else str(dates.max()),
                "unique_dates": int(dates.nunique()),}
        return result

    def run(self):
        return {
            "numeric_statistic": self.numeric_statistic(),
            "categorical_statistics": self.categorical_statistics(),
            "correlation": self.correlation(),
            "datetime": self.datetime_analysis(),}