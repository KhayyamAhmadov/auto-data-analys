import os
from datetime import datetime
from xml.sax.saxutils import escape
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def safe_text(value):
    if value is None:
        return "-"
    try:
        if isinstance(value, float) and pd.isna(value):
            return "-"
    except Exception:
        pass
    return escape(str(value))


def register_unicode_font():
    candidates = [
        # Linux
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        # Windows
        ("C:\\Windows\\Fonts\\arial.ttf", "C:\\Windows\\Fonts\\arialbd.ttf"),
        ("C:\\Windows\\Fonts\\calibri.ttf", "C:\\Windows\\Fonts\\calibrib.ttf"),
        # macOS
        ("/System/Library/Fonts/Supplemental/Arial.ttf",
         "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        # Layihə qovluğunda bundle edilmiş font (tövsiyə olunan yol)
        ("fonts/DejaVuSans.ttf", "fonts/DejaVuSans-Bold.ttf"),]

    for regular_path, bold_path in candidates:
        if os.path.exists(regular_path):
            try:
                pdfmetrics.registerFont(TTFont("MainFont", regular_path))
                if os.path.exists(bold_path):
                    pdfmetrics.registerFont(TTFont("MainFont-Bold", bold_path))
                    return "MainFont", "MainFont-Bold"
                return "MainFont", "MainFont"
            except Exception:
                continue

    return None, None


def quality_label(score):
    if score is None:
        return "N/A"
    if score >= 85:
        return "Əla"
    if score >= 70:
        return "Yaxşı"
    if score >= 50:
        return "Orta"
    return "Zəif"


class ReportGenerator:

    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Köməkçi metodlar
    # ------------------------------------------------------------------
    def _dataframe_table(self, df, page_width, table_font, index_label="", max_col_width=None):
        """Ümumi DataFrame -> reportlab Table çevirməsi (korrelyasiya, Cramér's V və s. üçün)."""
        columns = [index_label] + [safe_text(c) for c in df.columns]
        table_data = [columns]
        for idx in df.index:
            row = [safe_text(idx)] + [safe_text(df.loc[idx, c]) for c in df.columns]
            table_data.append(row)

        n_cols = len(columns)
        col_width = page_width / n_cols
        table = Table(table_data, repeatRows=1, colWidths=[col_width] * n_cols)
        table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ("FONTNAME", (0, 0), (-1, -1), table_font),
                ]
            )
        )
        return table

    def create_report(self, profile, cleaning, eda, charts, findings):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(self.output_dir, f"data_report_{timestamp}.pdf")

        pdf = SimpleDocTemplate(path, pagesize=A4)
        styles = getSampleStyleSheet()

        font_name, font_name_bold = register_unicode_font()
        if font_name:
            for style_name in ("Normal", "BodyText", "Title", "Heading2"):
                styles[style_name].fontName = font_name
            table_font = font_name
            footer_font = font_name
        else:
            # Font tapılmadı - standart font Azərbaycan hərflərini göstərməyəcək
            print(
                "Error: Unicode font tapılmadı. "
                "Azərbaycan hərfləri (ə, ğ, ı, ş, ç, ö, ü) PDF-də düzgün "
                "görünməyə bilər. 'fonts/DejaVuSans.ttf' faylını əlavə edin.")
            table_font = "Helvetica"
            footer_font = "Helvetica"

        # findings həm köhnə (list) həm də yeni (dict: summary/recommendations) formatı dəstəkləsin
        if isinstance(findings, dict):
            findings_summary = findings.get("summary", [])
            findings_recommendations = findings.get("recommendations", [])
        else:
            findings_summary = findings or []
            findings_recommendations = []

        content = []

        page_width = A4[0] - 2 * 20 * mm

        # -------------------------
        # TITLE
        # -------------------------
        content.append(Paragraph("DATA ANALYSIS REPORT", styles["Title"]))
        content.append(Spacer(1, 20))

        # -------------------------
        # EXECUTIVE SUMMARY
        # -------------------------
        content.append(Paragraph("İcra Xülasəsi (Executive Summary)", styles["Heading2"]))

        quality_score = cleaning.get("quality_score")
        label = quality_label(quality_score)
        score_text = f"{quality_score}/100 ({label})" if quality_score is not None else "N/A"

        summary_data = [
            ["Göstərici", "Dəyər"],
            ["Sətir sayı", safe_text(profile["rows"])],
            ["Sütun sayı", safe_text(profile["columns"])],
            ["Data keyfiyyət balı", score_text],
            ["Çatışmayan dəyər olan sütun sayı", safe_text(len(cleaning.get("missing", {})))],
            ["Təkrarlanan sətir sayı", safe_text(cleaning.get("duplicates", 0))],
            ["Sabit (faydasız) sütun sayı", safe_text(len(cleaning.get("constant_columns", [])))],
        ]
        table = Table(summary_data, colWidths=[page_width * 0.6, page_width * 0.4])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTNAME", (0, 0), (-1, -1), table_font),
                ]
            )
        )
        content.append(table)
        content.append(Spacer(1, 20))

        # -------------------------
        # 1. DATASET INFO
        # -------------------------
        content.append(Paragraph("1. Dataset haqqında ümumi məlumat", styles["Heading2"]))

        data = [
            ["Göstərici", "Dəyər"],
            ["Sətir sayı", safe_text(profile["rows"])],
            ["Sütun sayı", safe_text(profile["columns"])],
        ]

        table = Table(data, colWidths=[page_width * 0.5, page_width * 0.5])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTNAME", (0, 0), (-1, -1), table_font),]))
        content.append(table)
        content.append(Spacer(1, 20))

        # -------------------------
        # 2. COLUMN TYPES
        # -------------------------
        content.append(Paragraph("2. Sütun tipləri", styles["Heading2"]))

        for category, columns in profile["column_types"].items():
            cols_text = safe_text(", ".join(columns)) if columns else "Yoxdur"
            content.append(
                Paragraph(f"<b>{safe_text(category.upper())}</b>: {cols_text}", styles["BodyText"],))
            content.append(Spacer(1, 5))

        # -------------------------
        # 3. CLEANING
        # -------------------------
        content.append(Spacer(1, 15))
        content.append(Paragraph("3. Data Cleaning nəticələri", styles["Heading2"]))

        dup_pct = cleaning.get("duplicate_percentage")
        dup_text = f" ({dup_pct}%)" if dup_pct is not None else ""
        content.append(
            Paragraph(f"Təkrarlanan sətirlər: {safe_text(cleaning['duplicates'])}{dup_text}", styles["BodyText"],))
        content.append(Spacer(1, 8))
        content.append(Paragraph("Çatışmayan dəyərlər:", styles["BodyText"]))

        if cleaning["missing"]:
            percentages = cleaning.get("missing_percentage", {})
            for column, count in cleaning["missing"].items():
                pct = percentages.get(column)
                pct_text = f" ({pct}%)" if pct is not None else ""
                content.append(
                    Paragraph(f"{safe_text(column)}: {safe_text(count)}{safe_text(pct_text)}", styles["BodyText"],))
        else:
            content.append(Paragraph("Çatışmayan dəyər yoxdur.", styles["BodyText"]))

        if cleaning.get("outliers"):
            content.append(Spacer(1, 8))
            content.append(Paragraph("Kənar dəyərlər (outliers):", styles["BodyText"]))
            for column, count in cleaning["outliers"].items():
                if count > 0:
                    content.append(
                        Paragraph(f"{safe_text(column)}: {safe_text(count)}", styles["BodyText"],))

        constant_columns = cleaning.get("constant_columns", [])
        if constant_columns:
            content.append(Spacer(1, 8))
            content.append(Paragraph("Sabit (dəyişməyən) sütunlar:", styles["BodyText"]))
            content.append(Paragraph(safe_text(", ".join(constant_columns)), styles["BodyText"]))

        duplicate_columns = cleaning.get("duplicate_columns", [])
        if duplicate_columns:
            content.append(Spacer(1, 8))
            content.append(Paragraph("Təkrarlanan (eyni məzmunlu) sütun cütləri:", styles["BodyText"]))
            for col_a, col_b in duplicate_columns:
                content.append(Paragraph(f"{safe_text(col_a)} = {safe_text(col_b)}", styles["BodyText"]))

        type_mismatches = cleaning.get("type_mismatches", [])
        if type_mismatches:
            content.append(Spacer(1, 8))
            content.append(Paragraph("Tip uyğunsuzluğu olan sütunlar (əslində ədədi görünür):", styles["BodyText"]))
            content.append(Paragraph(safe_text(", ".join(type_mismatches)), styles["BodyText"]))

        high_cardinality = cleaning.get("high_cardinality", {})
        if high_cardinality:
            content.append(Spacer(1, 8))
            content.append(Paragraph("Yüksək kardinallıqlı sütunlar (unikal dəyər faizi):", styles["BodyText"]))
            for column, ratio in high_cardinality.items():
                content.append(Paragraph(f"{safe_text(column)}: {safe_text(ratio)}%", styles["BodyText"]))

        rare_categories = cleaning.get("rare_categories", {})
        if rare_categories:
            content.append(Spacer(1, 8))
            content.append(Paragraph("Nadir kateqoriyalar:", styles["BodyText"]))
            for column, values in rare_categories.items():
                values_text = ", ".join(f"{v} ({p}%)" for v, p in list(values.items())[:5])
                content.append(Paragraph(f"{safe_text(column)}: {safe_text(values_text)}", styles["BodyText"]))

        # -------------------------
        # 4. EDA - NUMERIC STATISTICS
        # -------------------------
        content.append(Spacer(1, 20))
        content.append(Paragraph("4. Exploratory Data Analysis - Ədədi sütunlar", styles["Heading2"]))

        statistics = eda.get("numeric_statistic")

        if statistics is not None and not statistics.empty:
            table_data = [["Column"] + [safe_text(i) for i in statistics.index]]

            for column in statistics.columns:
                row = [safe_text(column)] + [
                    safe_text(statistics.loc[index, column])
                    for index in statistics.index
                ]
                table_data.append(row)

            n_cols = len(table_data[0])
            col_width = page_width / n_cols

            table = Table(table_data, repeatRows=1, colWidths=[col_width] * n_cols)
            table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("FONTSIZE", (0, 0), (-1, -1), 7),
                        ("FONTNAME", (0, 0), (-1, -1), table_font),
                    ]
                )
            )
            content.append(table)

            skew_kurt = eda.get("skewness_kurtosis", {})
            if skew_kurt:
                content.append(Spacer(1, 10))
                content.append(Paragraph("Çəpəkilik (Skewness) və Sivrilik (Kurtosis):", styles["BodyText"]))
                sk_data = [["Sütun", "Skewness", "Kurtosis"]]
                for column, stats in skew_kurt.items():
                    sk_data.append([safe_text(column), safe_text(stats.get("skewness")), safe_text(stats.get("kurtosis"))])
                sk_table = Table(sk_data, colWidths=[page_width * 0.4, page_width * 0.3, page_width * 0.3])
                sk_table.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("FONTSIZE", (0, 0), (-1, -1), 8),
                            ("FONTNAME", (0, 0), (-1, -1), table_font),
                        ]
                    )
                )
                content.append(sk_table)
        else:
            content.append(Paragraph("Ədədi sütun tapılmadı.", styles["BodyText"]))

        # -------------------------
        # 5. EDA - CATEGORICAL STATISTICS
        # -------------------------
        content.append(Spacer(1, 20))
        content.append(Paragraph("5. Kateqorik sütunların analizi", styles["Heading2"]))

        categorical_stats = eda.get("categorical_statistics", {})
        if categorical_stats:
            for column, value_counts in categorical_stats.items():
                content.append(Paragraph(f"<b>{safe_text(column)}</b>", styles["BodyText"]))
                table_data = [["Dəyər", "Say"]] + [
                    [safe_text(value), safe_text(count)]
                    for value, count in value_counts.items()
                ]
                table = Table(table_data, colWidths=[page_width * 0.7, page_width * 0.3])
                table.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("FONTSIZE", (0, 0), (-1, -1), 8),
                            ("FONTNAME", (0, 0), (-1, -1), table_font),
                        ]
                    )
                )
                content.append(table)
                content.append(Spacer(1, 10))
        else:
            content.append(Paragraph("Kateqorik sütun tapılmadı.", styles["BodyText"]))

        # -------------------------
        # 6. DATETIME ANALYSIS
        # -------------------------
        content.append(Spacer(1, 20))
        content.append(Paragraph("6. Tarix sütunlarının analizi", styles["Heading2"]))

        datetime_stats = eda.get("datetime", {})
        if datetime_stats:
            table_data = [["Sütun", "Minimum", "Maksimum", "Unikal tarix sayı"]]
            for column, stats in datetime_stats.items():
                table_data.append(
                    [
                        safe_text(column),
                        safe_text(stats.get("min")),
                        safe_text(stats.get("max")),
                        safe_text(stats.get("unique_dates")),
                    ]
                )
            table = Table(table_data, colWidths=[page_width * 0.25] * 4)
            table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("FONTNAME", (0, 0), (-1, -1), table_font),
                    ]
                )
            )
            content.append(table)
        else:
            content.append(Paragraph("Tarix sütunu tapılmadı.", styles["BodyText"]))

        # -------------------------
        # 7. CATEGORICAL ASSOCIATION (Cramér's V)
        # -------------------------
        content.append(Spacer(1, 20))
        content.append(Paragraph("7. Kateqorik sütunlar arası əlaqə (Cramér's V)", styles["Heading2"]))

        association = eda.get("categorical_association")
        if association is not None and not association.empty:
            content.append(Paragraph(
                "Dəyər 0-dan 1-ə qədərdir; 0 - əlaqə yoxdur, 1 - tam əlaqə.", styles["BodyText"]))
            content.append(Spacer(1, 5))
            content.append(self._dataframe_table(association, page_width, table_font, index_label="Sütun"))
        else:
            content.append(Paragraph("Kifayət qədər kateqorik sütun tapılmadı.", styles["BodyText"]))

        # -------------------------
        # 8. NUMERIC BY CATEGORY (groupby)
        # -------------------------
        content.append(Spacer(1, 20))
        content.append(Paragraph("8. Kateqoriya üzrə ədədi ortalamalar", styles["Heading2"]))

        numeric_by_category = eda.get("numeric_by_category", {})
        if numeric_by_category:
            for cat_column, groups in numeric_by_category.items():
                if not groups:
                    continue
                content.append(Paragraph(f"<b>{safe_text(cat_column)}</b> üzrə orta dəyərlər", styles["BodyText"]))
                group_df = pd.DataFrame(groups).T
                content.append(self._dataframe_table(group_df, page_width, table_font, index_label=cat_column))
                content.append(Spacer(1, 10))
        else:
            content.append(Paragraph("Uyğun kateqorik/ədədi kombinasiya tapılmadı.", styles["BodyText"]))

        # -------------------------
        # 9. MULTICOLLINEARITY (VIF)
        # -------------------------
        content.append(Spacer(1, 20))
        content.append(Paragraph("9. Çoxxətli asılılıq (VIF)", styles["Heading2"]))

        vif = eda.get("multicollinearity", {})
        if vif:
            content.append(Paragraph(
                "VIF > 5 risk, VIF > 10 ciddi çoxxətli asılılıq deməkdir.", styles["BodyText"]))
            content.append(Spacer(1, 5))
            vif_data = [["Sütun", "VIF"]] + [[safe_text(c), safe_text(v)] for c, v in vif.items()]
            vif_table = Table(vif_data, colWidths=[page_width * 0.6, page_width * 0.4])
            vif_table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("FONTNAME", (0, 0), (-1, -1), table_font),
                    ]
                )
            )
            content.append(vif_table)
        else:
            content.append(Paragraph("VIF hesablamaq üçün kifayət qədər ədədi sütun tapılmadı.", styles["BodyText"]))

        # -------------------------
        # 10. FINDINGS
        # -------------------------
        content.append(Spacer(1, 20))
        content.append(Paragraph("10. Əsas tapıntılar", styles["Heading2"]))

        if findings_summary:
            for finding in findings_summary:
                content.append(Paragraph(f"• {safe_text(finding)}", styles["BodyText"]))
                content.append(Spacer(1, 5))
        else:
            content.append(Paragraph("Tapıntı yoxdur.", styles["BodyText"]))

        # -------------------------
        # 11. RECOMMENDATIONS
        # -------------------------
        content.append(Spacer(1, 20))
        content.append(Paragraph("11. Tövsiyələr", styles["Heading2"]))

        if findings_recommendations:
            for recommendation in findings_recommendations:
                content.append(Paragraph(f"• {safe_text(recommendation)}", styles["BodyText"]))
                content.append(Spacer(1, 5))
        else:
            content.append(Paragraph("Tövsiyə yoxdur.", styles["BodyText"]))

        # -------------------------
        # 12. CHARTS
        # -------------------------
        content.append(Spacer(1, 20))
        content.append(Paragraph("12. Vizual analiz", styles["Heading2"]))

        if not charts:
            content.append(Paragraph("Qrafik yaradıla bilmədi.", styles["BodyText"]))

        for chart in charts:
            # Həm ("Başlıq", "yol") tuple formatını, həm də köhnə düz yol formatını dəstəklə
            if isinstance(chart, (tuple, list)) and len(chart) == 2:
                title, chart_path = chart
            else:
                title, chart_path = None, chart

            if os.path.exists(chart_path):
                try:
                    if title:
                        content.append(Paragraph(safe_text(title), styles["BodyText"]))
                        content.append(Spacer(1, 4))

                    img = Image(chart_path)
                    max_width = page_width
                    max_height = 280

                    ratio = img.imageWidth / img.imageHeight
                    width = max_width
                    height = width / ratio

                    if height > max_height:
                        height = max_height
                        width = height * ratio

                    img.drawWidth = width
                    img.drawHeight = height

                    content.append(img)
                    content.append(Spacer(1, 15))
                except Exception:
                    content.append(
                        Paragraph(
                            f"Şəkil yüklənə bilmədi: {safe_text(chart_path)}",
                            styles["BodyText"],
                        )
                    )

        # -------------------------
        # PAGE NUMBERS (footer)
        # -------------------------
        def add_page_number(canvas, doc):
            canvas.saveState()
            try:
                canvas.setFont(footer_font, 8)
            except Exception:
                canvas.setFont("Helvetica", 8)
            canvas.drawRightString(A4[0] - 20 * mm, 10 * mm, f"Səhifə {doc.page}")
            canvas.restoreState()

        try:
            pdf.build(content, onFirstPage=add_page_number, onLaterPages=add_page_number)
        except Exception as e:
            raise RuntimeError(f"PDF yaradılarkən xəta baş verdi: {e}")

        return path