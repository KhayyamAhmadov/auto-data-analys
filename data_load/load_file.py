import pandas as pd
from pathlib import Path


def load_file(file_path):

    if hasattr(file_path, "name"):
        filename = file_path.name
    else:
        filename = str(file_path)

    extension = Path(filename).suffix.lower()

    if extension == ".csv":
        return pd.read_csv(file_path)

    elif extension == ".xlsx":
        return pd.read_excel(file_path, engine="openpyxl")

    elif extension == ".xls":
        return pd.read_excel(file_path, engine="xlrd")

    elif extension == ".json":
        return pd.read_json(file_path)

    else:
        raise ValueError(f"Dəstəklənməyən fayl formatı: {extension}")