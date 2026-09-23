from __future__ import annotations
import io
import pandas as pd
from datetime import datetime
import base64
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer


class NamedBytesIO(io.BytesIO):
    def __init__(self, data: bytes, name: str):
        super().__init__(data)
        self.name = name


def quality_summary(df: pd.DataFrame) -> dict:
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "memory_bytes": float(df.memory_usage(deep=True).sum() / 1024**2)}


def format_bytes(size: int) -> str:
    units = ("B", "KB", "MB", "GB")
    value = float(size)
    index = 0

    while value >= 1024 and index < len(units) - 1:
        value /= 1024
        index += 1

    if index == 0:
        return f"{int(value)} B"
    return f"{value:.1f} {units[index]}"


def greeting() -> str:
    try:
        from zoneinfo import ZoneInfo
        hour = datetime.now(ZoneInfo("Asia/Baku")).hour
    except Exception: 
        hour = datetime.now().hour

    if 5 <= hour < 12:
        return "Sabahınız xeyir ☀️"
    if 12 <= hour < 18:
        return "Gününüz xeyir 🌤️"
    if 18 <= hour < 23:
        return "Axşamınız xeyir 🌆"
    return "Gecəniz xeyir 🌙"


def show_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        pdf_bytes = file.read()
    pdf_viewer(pdf_path, width=800, height=1000, zoom_level=1.25)