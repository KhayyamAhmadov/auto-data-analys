class DataFindings:

    def __init__(self, df, profile, cleaning, eda):
        self.df = df
        self.profile = profile
        self.cleaning = cleaning
        self.eda = eda

    def generate(self):
        findings = []

        findings.append(f"Dataset {self.profile['rows']} sətir və {self.profile['columns']} sütundan ibarətdir.")

        missing = self.cleaning["missing"]
        if missing:
            for column, count in missing.items():
                findings.append(f"{column} sütununda {count} çatışmayan dəyər mövcuddur.")
        else:
            findings.append("Datasetdə çatışmayan dəyər aşkar edilməmişdir")


        duplicates = self.cleaning["duplicates"]
        if duplicates > 0:
            findings.append(f"Datasetdə {duplicates} təkrarlanan sətir aşkar edilmişdir.")
        else:
            findings.append("Datasetdə təkrarlanan sətir aşkar edilməmişdir.")


        for column, count in self.cleaning["outliers"].items():
            if count > 0:
                findings.append(f"{column} sütununda {count} potensial outlier aşkar edilmişdir")


        corr = self.eda["correlation"]
        if not corr.empty:
            columns = corr.columns
            st_pair = None
            st_value = -1

            for i in range(len(columns)):
                for j in range(i + 1, len(columns)):
                    value = abs(corr.iloc[i, j])
                    if value > st_value:
                        st_value = value
                        st_pair = (columns[i], columns[j], corr.iloc[i, j])

            if st_pair:
                findings.append(
                    f"Ən güclü xətti əlaqə "
                    f"{st_pair[0]} və "
                    f"{st_pair[1]} "
                    f"arasında müşahidə edilmişdir "
                    f"(r = {st_pair[2]:.2f}).")

        return findings
