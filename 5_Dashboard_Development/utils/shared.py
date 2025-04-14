from pathlib import Path
import pandas as pd

# Get the directory of the current file (i.e., utils/)
current_dir = Path(__file__).resolve().parent

# Go one level up to 5_Dash_dev/, then into data/
data_dir = current_dir.parent / "data"

# Define file paths
demographics_path = data_dir / "demographic2023.csv"
performance_path = data_dir / "combined_years_performance.csv"
ids_path = data_dir / "ids.csv"

# Load the data
demographics = pd.read_csv(demographics_path)
performance = pd.read_csv(performance_path)
ids = pd.read_csv(ids_path)