from .profiler import DataProfiler
from .cleaning import DataCleaning
from .eda import DataEDA
from .findings import DataFindings
from .vizualization import DataVisualization
from .report import ReportGenerator


class DataAnalys:
    def __init__(self, df):
        self.df = df
        self.profile = None
        self.cleaning = None
        self.charts = None
        self.eda = None
        self.findings = None
        self.report = None

    def run(self):

        print("1. Bismillah. Datasetin analizinə başladım...")
        profiler = DataProfiler(self.df)
        self.profile = profiler.profile()


        print("2. Çalışıramki data təmiz olsun...")
        clean = DataCleaning(self.df, self.profile["column_types"])
        self.cleaning = clean.run()


        print("3. EDA prosesi başladım uje. İnan uje indidən başım xarab oldu...")
        eda = DataEDA(self.df, self.profile["column_types"])
        self.eda = eda.run()


        print("4. Vizuallar hazırlayıram. Səbrli ol...")
        vizual = DataVisualization(self.df, self.profile["column_types"])
        self.charts = vizual.run()


        print("5. Nəticə çıxarıram. Uje birtəhər olmuşam...")
        finding = DataFindings(self.df, self.profile, self.cleaning, self.eda)
        self.findings = finding.generate()

        print("6. Mənkidə iş döyüle...")
        report = ReportGenerator()
        pdf_path = report.create_report(self.profile, self.cleaning, self.eda, self.charts, self.findings )

        print(f"Çox Şükür Allaha. Gələ pdf-ün hazırdı. Burda: {pdf_path}")


        return {
            "profile": self.profile,
            "cleaning": self.cleaning,
            "eda": self.eda,
            "charts": self.charts,
            "findings": self.findings,
            "report": pdf_path
        }


