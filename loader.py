# import pandas as pd

# def load_dataset(file_path):
    
#     if file_path.endswith(".csv"):
#        return pd.read_csv(file_path)

#     elif file_path.endswith((".xlsx", ".xls")):
#         return pd.read_excel(file_path)

#     elif file_path.endswith(".json"):
#         return pd.read_json(file_path)

#     else:
#         raise ValueError ("Dəstəklənməyən fayl formatı. Sadəcə CSV , EXCEL , JSON fromatı dəstəklənir.")



from gui import open_file
import pandas as pd

def load_dataset(file_path):

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)

    elif file_path.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path)

    elif file_path.endswith(".json"):
        df = pd.read_json(file_path)

    return df