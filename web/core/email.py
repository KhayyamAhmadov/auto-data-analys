import smtplib
from email.message import EmailMessage
from pathlib import Path


def send_analysis_email(receiver_email, pdf_path, dataset_name):
    sender_email = "səninmail@gmail.com"
    sender_password = "GMAIL_APP_PASSWORD"

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError("PDF faylı tapılmadı.")

    message = EmailMessage()

    message["Subject"] = f"Data Analysis Report - {dataset_name}"
    message["From"] = sender_email
    message["To"] = receiver_email

    message.set_content(
        f"""Salam! 👋

Dataset analizi uğurla tamamlandı.

📊 Dataset məlumatları

Dataset: {dataset_name}

📈 Analiz nəticələri

Analiz nəticələri PDF formatında bu emailə əlavə edilmişdir.

Təşəkkürlər,
maybeData?
Data Analysis Tool
""")

    with open(pdf_path, "rb") as file:
        pdf_data = file.read()

    message.add_attachment(pdf_data, maintype="application", subtype="pdf", filename=pdf_path.name)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(message)