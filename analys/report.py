import os
from datetime import datetime
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def safe_text(value):
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


class ReportGenerator:

    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

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
            table_font_bold = font_name_bold
        else:
            # Font tapılmadı - standart font Azərbaycan hərflərini göstərməyəcək
            print(
                "Error: Unicode font tapılmadı. "
                "Azərbaycan hərfləri (ə, ğ, ı, ş, ç, ö, ü) PDF-də düzgün "
                "görünməyə bilər. 'fonts/DejaVuSans.ttf' faylını əlavə edin.")
            table_font = "Helvetica"
            table_font_bold = "Helvetica-Bold"

        content = []

        page_width = A4[0] - 2 * 20 * mm




        # TITLE
        content.append(Paragraph("DATA ANALYSIS REPORT", styles["Title"]))
        content.append(Spacer(1, 20))




        # DATASET INFO
        content.append(Paragraph("1. Dataset haqqında ümumi məlumat", styles["Heading2"]))

        data = [
            ["Göstərici", "Dəyər"],
            ["Sətir sayı", safe_text(profile["rows"])],
            ["Sütun sayı", safe_text(profile["columns"])],]

        table = Table(data, colWidths=[page_width * 0.5, page_width * 0.5])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTNAME", (0, 0), (-1, -1), table_font),]))
        content.append(table)
        content.append(Spacer(1, 20))



        # COLUMN TYPES
        content.append(Paragraph("2. Sütun tipləri", styles["Heading2"]))

        for category, columns in profile["column_types"].items():
            cols_text = safe_text(", ".join(columns)) if columns else "Yoxdur"
            content.append(
                Paragraph(f"<b>{safe_text(category.upper())}</b>: {cols_text}", styles["BodyText"],))
            content.append(Spacer(1, 5))



        # CLEANING
        content.append(Spacer(1, 15))
        content.append(Paragraph("3. Data Cleaning nəticələri", styles["Heading2"]))

        content.append(
            Paragraph(f"Təkrarlanan sətirlər: {safe_text(cleaning['duplicates'])}",styles["BodyText"],))
        content.append(Spacer(1, 8))
        content.append(Paragraph("Çatışmayan dəyərlər:", styles["BodyText"]))

        if cleaning["missing"]:
            for column, count in cleaning["missing"].items():
                content.append(
                    Paragraph(f"{safe_text(column)}: {safe_text(count)}",styles["BodyText"],))
        else:
            content.append(Paragraph("Çatışmayan dəyər yoxdur.", styles["BodyText"]))


        if cleaning.get("outliers"):
            content.append(Spacer(1, 8))
            content.append(Paragraph("Kənar dəyərlər (outliers):", styles["BodyText"]))
            for column, count in cleaning["outliers"].items():
                if count > 0:
                    content.append(
                        Paragraph(
                            f"{safe_text(column)}: {safe_text(count)}",
                            styles["BodyText"],
                        )
                    )

        # EDA - NUMERIC STATISTICS
        content.append(Spacer(1, 20))
        content.append(Paragraph("4. Exploratory Data Analysis", styles["Heading2"]))

        statistics = eda["numeric_statistics"]

        if not statistics.empty:
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
        else:
            content.append(Paragraph("Ədədi sütun tapılmadı.", styles["BodyText"]))

        # -------------------------
        # FINDINGS
        # -------------------------
        content.append(Spacer(1, 20))
        content.append(Paragraph("5. Əsas tapıntılar", styles["Heading2"]))

        if findings:
            for finding in findings:
                content.append(
                    Paragraph(f"• {safe_text(finding)}", styles["BodyText"])
                )
                content.append(Spacer(1, 5))
        else:
            content.append(Paragraph("Tapıntı yoxdur.", styles["BodyText"]))

        # -------------------------
        # CHARTS
        # -------------------------
        content.append(Spacer(1, 20))
        content.append(Paragraph("6. Vizual analiz", styles["Heading2"]))

        for chart in charts:
            if os.path.exists(chart):
                try:
                    img = Image(chart)
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
                            f"Şəkil yüklənə bilmədi: {safe_text(chart)}",
                            styles["BodyText"],
                        )
                    )

        try:
            pdf.build(content)
        except Exception as e:
            raise RuntimeError(f"PDF yaradılarkən xəta baş verdi: {e}")

        return path