class DataFindings:

    def __init__(self, df, profile, cleaning, eda):
        self.df = df
        self.profile = profile
        self.cleaning = cleaning
        self.eda = eda

    # ------------------------------------------------------------------
    # Təsviri tapıntılar
    # ------------------------------------------------------------------
    def _summary(self):
        findings = []

        findings.append(f"Dataset {self.profile['rows']} sətir və {self.profile['columns']} sütundan ibarətdir.")

        missing = self.cleaning["missing"]
        if missing:
            percentages = self.cleaning.get("missing_percentage", {})
            for column, count in missing.items():
                pct = percentages.get(column)
                pct_text = f" ({pct}%)" if pct is not None else ""
                findings.append(f"{column} sütununda {count} çatışmayan dəyər mövcuddur{pct_text}.")
        else:
            findings.append("Datasetdə çatışmayan dəyər aşkar edilməmişdir")

        duplicates = self.cleaning["duplicates"]
        if duplicates > 0:
            dup_pct = self.cleaning.get("duplicate_percentage")
            pct_text = f" ({dup_pct}%)" if dup_pct is not None else ""
            findings.append(f"Datasetdə {duplicates} təkrarlanan sətir aşkar edilmişdir{pct_text}.")
        else:
            findings.append("Datasetdə təkrarlanan sətir aşkar edilməmişdir.")

        for column, count in self.cleaning["outliers"].items():
            if count > 0:
                findings.append(f"{column} sütununda {count} potensial outlier aşkar edilmişdir.")

        constant_columns = self.cleaning.get("constant_columns", [])
        if constant_columns:
            findings.append(f"Sabit (dəyişməyən) sütunlar aşkar edilmişdir: {', '.join(constant_columns)}.")

        for col_a, col_b in self.cleaning.get("duplicate_columns", []):
            findings.append(f'"{col_a}" və "{col_b}" sütunları tam eynidir.')

        type_mismatches = self.cleaning.get("type_mismatches", [])
        if type_mismatches:
            findings.append(
                f"Bu sütunlar mətn/kateqorik kimi saxlanılıb, amma əslində ədədi görünür: "
                f"{', '.join(type_mismatches)}.")

        high_cardinality = self.cleaning.get("high_cardinality", {})
        for column, ratio in high_cardinality.items():
            findings.append(f"{column} sütununda unikal dəyər nisbəti çox yüksəkdir ({ratio}%).")

        rare_categories = self.cleaning.get("rare_categories", {})
        for column, rare_values in rare_categories.items():
            values_text = ", ".join(f'"{v}" ({p}%)' for v, p in list(rare_values.items())[:5])
            findings.append(f"{column} sütununda nadir rast gəlinən kateqoriyalar var: {values_text}.")

        skew_kurt = self.eda.get("skewness_kurtosis", {})
        for column, stats in skew_kurt.items():
            skew = stats.get("skewness")
            if skew is not None and abs(skew) > 1:
                direction = "sağa" if skew > 0 else "sola"
                findings.append(f"{column} sütununun paylanması {direction} çəpdir (skewness = {skew}).")

        categorical_stats = self.eda.get("categorical_statistics", {})
        for column, value_counts in categorical_stats.items():
            if not value_counts:
                continue
            top_value, top_count = next(iter(value_counts.items()))
            findings.append(
                f'{column} sütununda ən çox rast gəlinən dəyər "{top_value}" ({top_count} dəfə) olmuşdur.')

        datetime_stats = self.eda.get("datetime", {})
        for column, stats in datetime_stats.items():
            if stats.get("min") and stats.get("max"):
                findings.append(
                    f"{column} sütunu {stats['min']} ilə {stats['max']} arasındakı dövrü əhatə edir "
                    f"({stats.get('unique_dates', 0)} unikal tarix).")

        corr = self.eda.get("correlation")
        if corr is not None and not corr.empty:
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

        vif = self.eda.get("multicollinearity", {})
        high_vif = {c: v for c, v in vif.items() if v is not None and v > 5}
        if high_vif:
            cols_text = ", ".join(f"{c} (VIF={v})" for c, v in high_vif.items())
            findings.append(f"Çoxxətli asılılıq (multicollinearity) riski aşkar edilmişdir: {cols_text}.")

        quality_score = self.cleaning.get("quality_score")
        if quality_score is not None:
            findings.append(f"Ümumi data keyfiyyət balı: {quality_score}/100.")

        return findings

    # ------------------------------------------------------------------
    # Əməli tövsiyələr
    # ------------------------------------------------------------------
    def _recommendations(self):
        recommendations = []

        missing_pct = self.cleaning.get("missing_percentage", {})
        for column, pct in missing_pct.items():
            if pct > 30:
                recommendations.append(
                    f"{column} sütununda çatışmayan dəyərlərin faizi çox yüksəkdir ({pct}%) — "
                    f"sütunu silmək və ya diqqətlə qiymətləndirmək tövsiyə olunur.")
            elif pct > 0:
                recommendations.append(
                    f"{column} sütunundakı çatışmayan dəyərlər üçün median/mode ilə doldurma "
                    f"(imputation) tövsiyə olunur.")

        if self.cleaning.get("duplicates", 0) > 0:
            recommendations.append("Təkrarlanan sətirlərin silinməsi (drop_duplicates) tövsiyə olunur.")

        for column, count in self.cleaning.get("outliers", {}).items():
            if count > 0:
                recommendations.append(
                    f"{column} sütunundakı outlier-lər üçün winsorization və ya IQR əsaslı "
                    f"filtrasiya nəzərdən keçirilə bilər.")

        for column in self.cleaning.get("constant_columns", []):
            recommendations.append(f"{column} sütunu sabitdir və heç bir məlumat daşımır — silinməsi tövsiyə olunur.")

        for col_a, col_b in self.cleaning.get("duplicate_columns", []):
            recommendations.append(f'"{col_a}" və "{col_b}" sütunlarından biri artıqdır — birini silmək olar.')

        for column in self.cleaning.get("type_mismatches", []):
            recommendations.append(f"{column} sütununu ədədi tipə çevirmək (pd.to_numeric) tövsiyə olunur.")

        for column in self.cleaning.get("rare_categories", {}):
            recommendations.append(
                f"{column} sütunundakı nadir kateqoriyaların yazı səhvi olub-olmadığını yoxlamaq faydalı olar.")

        vif = self.eda.get("multicollinearity", {})
        for column, value in vif.items():
            if value is not None and value > 10:
                recommendations.append(
                    f"{column} sütunu çox yüksək VIF dəyərinə malikdir ({value}) — model qurarkən "
                    f"silinməsi və ya PCA tətbiqi düşünülə bilər.")

        quality_score = self.cleaning.get("quality_score")
        if quality_score is not None and quality_score < 60:
            recommendations.append(
                f"Ümumi data keyfiyyət balı aşağıdır ({quality_score}/100) — analiz və ya "
                f"modelləşdirmədən əvvəl əlavə təmizlik mərhələsi tövsiyə olunur.")

        if not recommendations:
            recommendations.append("Əhəmiyyətli keyfiyyət problemi aşkar edilmədi — dataset analiz üçün hazırdır.")

        return recommendations

    def generate(self):
        return {
            "summary": self._summary(),
            "recommendations": self._recommendations(),
        }