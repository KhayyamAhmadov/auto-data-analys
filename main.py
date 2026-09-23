from data_load.load_file import load_file
from analys.analys import DataAnalys


def run_analysis(file_path):
    df = load_file(file_path)
    analyzer = DataAnalys(df)
    result = analyzer.run()
    return result