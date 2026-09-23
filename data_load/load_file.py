# import pandas as pd

# def load_file(file_path):

#     if file_path.endswith(".csv"):
#         return pd.read_csv(file_path)

#     elif file_path.endswith((".xlsx", ".xls")):
#         return pd.read_excel(file_path)

#     elif file_path.endswith(".json"):
#         return pd.read_json(file_path)

#     else:
#         raise ValueError("Dəstəklənməyən fayl formatı")



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

    elif extension in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)

    elif extension == ".json":
        return pd.read_json(file_path)

    else:
        raise ValueError(f"Dəstəklənməyən fayl formatı: {extension}")