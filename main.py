from analys.analys import DataAnalys
from gui import load_dataset

def main():
    df = load_dataset()
    analyzer = DataAnalys(df)
    result = analyzer.run()


if __name__ == "__main__":
    main()