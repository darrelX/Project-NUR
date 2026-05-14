file = r"breakdown automation\dataset\COMPILATION BREAK.xlsx"

print("Converting to csv...")

import pandas as pd

df = pd.read_excel(file, sheet_name="Sheet1")

output = r"breakdown automation\dataset\COMPILATION BREAK.csv"

df.to_csv(output, index=False)

print("Done")