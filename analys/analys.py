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
        if self.df is None:
            raise ValueError("Dataset boşdur (None). Zəhmət olmasa keçərli bir DataFrame verin.")

        if self.df.shape[1] == 0:
            raise ValueError("Datasetdə heç bir sütun tapılmadı.")

        if self.df.shape[0] == 0:
            print("Xəbərdarlıq: dataset 0 sətirdən ibarətdir, analiz məhdud olacaq.")

        print("1. Bismillah. Datasetin analizinə başladım...")
        try:
            profiler = DataProfiler(self.df)
            self.profile = profiler.profile()
        except Exception as e:
            raise RuntimeError(f"Dataset profil edilərkən xəta baş verdi: {e}") from e

        print("2. Çalışıramki data təmiz olsun...")
        try:
            clean = DataCleaning(self.df, self.profile["column_types"])
            self.cleaning = clean.run()
        except Exception as e:
            print(f"Xəbərdarlıq: cleaning mərhələsində xəta baş verdi, boş nəticə ilə davam edilir: {e}")
            self.cleaning = {
                "missing": {},
                "missing_percentage": {},
                "duplicates": 0,
                "duplicate_percentage": 0.0,
                "outliers": {},
                "constant_columns": [],
                "duplicate_columns": [],
                "high_cardinality": {},
                "type_mismatches": [],
                "rare_categories": {},
                "quality_score": None,
            }

        print("3. EDA prosesi başladım uje. İnan uje indidən başım xarab oldu...")
        try:
            eda = DataEDA(self.df, self.profile["column_types"])
            self.eda = eda.run()
        except Exception as e:
            print(f"Xəbərdarlıq: EDA mərhələsində xəta baş verdi, boş nəticə ilə davam edilir: {e}")
            self.eda = {
                "numeric_statistic": None,
                "skewness_kurtosis": {},
                "categorical_statistics": {},
                "correlation": None,
                "categorical_association": None,
                "numeric_by_category": {},
                "multicollinearity": {},
                "datetime": {},
            }

        print("4. Vizuallar hazırlayıram. Səbrli ol...")
        try:
            vizual = DataVisualization(self.df, self.profile["column_types"])
            self.charts = vizual.run()
        except Exception as e:
            print(f"Xəbərdarlıq: vizuallaşdırma mərhələsində xəta baş verdi, qrafiksiz davam edilir: {e}")
            self.charts = []

        print("5. Nəticə çıxarıram. Uje birtəhər olmuşam...")
        try:
            finding = DataFindings(self.df, self.profile, self.cleaning, self.eda)
            self.findings = finding.generate()
        except Exception as e:
            print(f"Xəbərdarlıq: tapıntılar hazırlanarkən xəta baş verdi: {e}")
            self.findings = {"summary": [], "recommendations": []}

        print("6. Mənkidə iş döyüle...")
        report = ReportGenerator()
        pdf_path = report.create_report(self.profile, self.cleaning, self.eda, self.charts, self.findings)

        print(f"Çox Şükür Allaha. Gələ pdf-ün hazırdı. Burda: {pdf_path}")

        return {
            "profile": self.profile,
            "cleaning": self.cleaning,
            "eda": self.eda,
            "charts": self.charts,
            "findings": self.findings,
            "report": pdf_path
        }