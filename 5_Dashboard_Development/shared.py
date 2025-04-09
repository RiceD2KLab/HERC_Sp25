from pathlib import Path

import pandas as pd

app_dir = Path(__file__).parent
demographics = pd.read_csv(app_dir / "demographic2023.csv")
performance = pd.read_csv(app_dir / "combined_years_performance.csv")
