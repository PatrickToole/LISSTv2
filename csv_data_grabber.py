import os
import shutil
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

data_path = filedialog.askdirectory()
destination_path = filedialog.askdirectory()


for root, dirs, files in os.walk(data_path):
    for f in files:
        if f.endswith('.csv'):
            shutil.copy(os.path.join(root,f), destination_path)