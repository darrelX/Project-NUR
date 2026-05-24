file = r"breakdown automation\dataset\COMPILATION BREAK.xlsx"

print("Converting to csv...")

import pandas as pd

df = pd.read_excel(file, sheet_name="Sheet1")

print(df["SUB RCA"].head(500))