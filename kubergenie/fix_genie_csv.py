import pandas as pd

file_path = "results/genie_signals.csv"
df = pd.read_csv(file_path)

# 🔍 Show raw columns to check hidden characters
print("🧪 Raw columns detected:", list(df.columns))

# 🧼 Strip spaces and hidden characters from column names
df.columns = df.columns.str.strip()

# ✅ Show cleaned columns
print("✅ Cleaned columns:", list(df.columns))

# ✅ Re-save cleaned version
df.to_csv(file_path, index=False)
print("✅ Fixed and saved:", file_path)
