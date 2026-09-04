import tkinter as tk
from tkinter import filedialog, messagebox
from main import *
import pandas as pd


def open_file():
    file_path = filedialog.askopenfilename(title = "faylı seç", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("Json files", "*.json")])
    if file_path:
        file_input.delete(0, tk.END)
        file_input.insert(0, file_path)


def load_dataset(file_path):

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)

    elif file_path.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path)

    elif file_path.endswith(".json"):
        df = pd.read_json(file_path)

    return df


def start_analys():
    file_path = file_input.get()

    if not file_path:
        messagebox.showwarning("Xəta" , "Əvvəlcə fayl seçin!")
        return

    df = load_dataset(file_path)
    analyzer = DataAnalys(df)
    analyzer.run()
    messagebox.showinfo("Uğurlu" , "Data analiz edilir...")


root = tk.Tk()
root.title("AVTOMATİK MƏLUMAT ANALİZ SİSTEMİ")
root.geometry("600x300")

frame = tk.Frame(root)
frame.place(relx=0.5, rely=0.5, anchor="center")

file_input = tk.Entry(frame, width = 50)
file_input.pack(side = "left", padx=5)

button = tk.Button(root, text = "Faylı seç", command = open_file)
button.pack()

button = tk.Button(root, text = "Analizə başla", command = start_analys)
button.pack() 

root.mainloop()