import os
import pandas as pd

ROOT_DIR = os.path.abspath("")
EXCELS_DIR = os.path.join(ROOT_DIR, "auction_results")

files = next(os.walk(EXCELS_DIR))[2]
files_dir = [os.path.join(EXCELS_DIR, f) for f in files]

df = pd.concat([pd.read_excel(f) for f in files_dir], ignore_index=True)

df.to_csv("output\\combined_auction_results.csv")