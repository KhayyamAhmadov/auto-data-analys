# import tkinter as tk
# from tkinter import filedialog, messagebox
# from main import *
# import pandas as pd
# from playsound3 import playsound


# def open_file():
#     file_path = filedialog.askopenfilename(title = "faylı seç", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("Json files", "*.json")])
#     if file_path:
#         file_input.delete(0, tk.END)
#         file_input.insert(0, file_path)


# def load_dataset(file_path):

#     if file_path.endswith(".csv"):
#         df = pd.read_csv(file_path)

#     elif file_path.endswith((".xlsx", ".xls")):
#         df = pd.read_excel(file_path)

#     elif file_path.endswith(".json"):
#         df = pd.read_json(file_path)

#     return df


# def start_analys():
#     file_path = file_input.get()

#     if not file_path:
#         messagebox.showwarning("Xəta" , "Əvvəlcə fayl seçin!")
#         return

#     df = load_dataset(file_path)
#     analyzer = DataAnalys(df)
#     analyzer.run()
#     messagebox.showinfo("Uğurlu" , "Data analiz edildi.")


# root = tk.Tk()
# root.title("AVTOMATİK MƏLUMAT ANALİZ SİSTEMİ")
# root.geometry("600x300")

# frame = tk.Frame(root)
# frame.place(relx=0.5, rely=0.5, anchor="center")

# file_input = tk.Entry(frame, width = 50)
# file_input.pack(side = "left", padx=5)

# button = tk.Button(root, text = "Faylı seç", command = open_file)
# button.pack()

# button = tk.Button(root, text = "Analizə başla", command = start_analys)
# button.pack() 

# root.mainloop()


import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from main import *
import pandas as pd


def load_dataset(file_path):

    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)

    elif file_path.endswith((".xlsx", ".xls")):
        return pd.read_excel(file_path)

    elif file_path.endswith(".json"):
        return pd.read_json(file_path)

    else:
        raise ValueError("Dəstəklənməyən fayl formatı")


def open_file():

    file_path = filedialog.askopenfilename(
        title="Dataset seçin",
        filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx *.xls"), ("JSON files", "*.json"), ("Bütün fayllar", "*.*")])

    if file_path:

        file_input.delete(0, tk.END)
        file_input.insert(0, file_path)

        status_label.config(text="✓ Fayl seçildi", foreground="#2e7d32")


def start_analysis():

    file_path = file_input.get().strip()

    if not file_path:
        messagebox.showwarning("Xəbərdarlıq", "Əvvəlcə analiz etmək üçün fayl seçin!")
        return

    try:

        status_label.config(
            text="⏳ Data analiz edilir...",
            foreground="#1565c0"
        )

        root.update()

        df = load_dataset(file_path)

        analyzer = DataAnalys(df)
        analyzer.run()

        status_label.config(
            text="✓ Analiz uğurla tamamlandı",
            foreground="#2e7d32"
        )

        messagebox.showinfo(
            "Uğurlu",
            "Data analizi uğurla tamamlandı."
        )

    except Exception as e:

        status_label.config(
            text="✕ Analiz zamanı xəta baş verdi",
            foreground="#c62828"
        )

        messagebox.showerror(
            "Xəta",
            f"Analiz zamanı xəta baş verdi:\n\n{e}"
        )


# =========================================================
# ƏSAS PƏNCƏRƏ
# =========================================================

root = tk.Tk()

root.title("Data Analysis Pro")
root.geometry("750x500")
root.minsize(650, 450)

# Arxa fon
root.configure(bg="#f4f6f8")


# =========================================================
# STYLE
# =========================================================

style = ttk.Style()

style.theme_use("clam")

style.configure(
    "Title.TLabel",
    background="#f4f6f8",
    foreground="#1f2937",
    font=("Segoe UI", 24, "bold")
)

style.configure(
    "Subtitle.TLabel",
    background="#f4f6f8",
    foreground="#6b7280",
    font=("Segoe UI", 11)
)

style.configure(
    "Card.TFrame",
    background="white"
)

style.configure(
    "File.TEntry",
    font=("Segoe UI", 11),
    padding=10
)

style.configure(
    "Select.TButton",
    font=("Segoe UI", 10, "bold"),
    padding=(18, 10)
)

style.configure(
    "Analyze.TButton",
    font=("Segoe UI", 12, "bold"),
    padding=(25, 13)
)

style.configure(
    "Status.TLabel",
    background="#f4f6f8",
    font=("Segoe UI", 10)
)


# =========================================================
# MAIN CONTAINER
# =========================================================

main_frame = ttk.Frame(
    root,
    padding=40
)

main_frame.pack(
    fill="both",
    expand=True
)


# =========================================================
# BAŞLIQ
# =========================================================

title_label = ttk.Label(
    main_frame,
    text="Data Analysis Pro",
    style="Title.TLabel"
)

title_label.pack(
    pady=(20, 5)
)


subtitle_label = ttk.Label(
    main_frame,
    text="Datasetinizi seçin və avtomatik data analizini başladın",
    style="Subtitle.TLabel"
)

subtitle_label.pack(
    pady=(0, 30)
)


# =========================================================
# FILE CARD
# =========================================================

file_card = ttk.Frame(
    main_frame,
    style="Card.TFrame",
    padding=25
)

file_card.pack(
    fill="x",
    padx=30
)


# Fayl başlığı

file_title = tk.Label(
    file_card,
    text="Dataset faylı",
    bg="white",
    fg="#1f2937",
    font=("Segoe UI", 12, "bold")
)

file_title.pack(
    anchor="w",
    pady=(0, 10)
)


# Entry + Button

file_row = ttk.Frame(
    file_card,
    style="Card.TFrame"
)

file_row.pack(
    fill="x"
)


file_input = ttk.Entry(
    file_row,
    style="File.TEntry"
)

file_input.pack(
    side="left",
    fill="x",
    expand=True,
    padx=(0, 10)
)


select_button = ttk.Button(
    file_row,
    text="📁  Faylı seç",
    style="Select.TButton",
    command=open_file
)

select_button.pack(
    side="right"
)


# Dəstəklənən formatlar

format_label = tk.Label(
    file_card,
    text="Dəstəklənən formatlar: CSV  •  Excel  •  JSON",
    bg="white",
    fg="#9ca3af",
    font=("Segoe UI", 9)
)

format_label.pack(
    anchor="w",
    pady=(10, 0)
)


# =========================================================
# ANALİZ BUTTON
# =========================================================

analyze_button = ttk.Button(
    main_frame,
    text="▶  Analizə başla",
    style="Analyze.TButton",
    command=start_analysis
)

analyze_button.pack(
    pady=30
)


status_label = ttk.Label(main_frame, text="Hazırdır — analiz üçün dataset seçin", style="Status.TLabel")
status_label.pack(pady = (5, 15))

footer = tk.Label(root, text="DataPro  •  Automated Data Analysis System", bg="#f4f6f8", fg="#9ca3af", font=("Segoe UI", 9))
footer.pack(side = "bottom", pady=12)

root.mainloop()