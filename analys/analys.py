from .profiler import DataProfiler
from .cleaning import DataCleaning
from .report import ReportGenerator

class DataAnalys:
    def __init__(self, df):
        self.df = df
        self.profile = None
        self.cleaning = None
        self.report = None

    def run(self):

        print("1. Dataset analiz edilir...")
        profiler = DataProfiler(self.df)
        self.profile = profiler.profile()


        print("2. Data təmizlənir...")
        clean = DataCleaning(self.df, self.profile["column_types"])
        self.cleaning = clean.run()

        report = ReportGenerator()
        pdf_path = report.create_report(self.profile, self.cleaning)

        return {
            "profile": self.profile,
            "cleaning": self.cleaning,
            "report": pdf_path}