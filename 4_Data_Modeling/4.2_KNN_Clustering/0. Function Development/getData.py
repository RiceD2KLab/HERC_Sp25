import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl.worksheet.header_footer")


def load_data_from_github(year):
    """
    Loads district-level education data and corresponding column key from the HERC GitHub repository.

    Parameters:
    -----------
    year : int or str
        The year for which to load the data (e.g., 2020).

    Returns:
    --------
    df : pandas.DataFrame
        The cleaned district-level dataset for the specified year. Charter schools are filtered out,
        and negative values in numeric columns are replaced with NaN.

    column_key : pandas.DataFrame
        The column key DataFrame from the 'distprof' sheet in the corresponding Excel file, 
        used for understanding column meanings in `df`.

    Notes:
    ------
    - The data is sourced from the mm175rice/HERC-DISTRICT-MATCH-FILES GitHub repository.
    - Assumes the structure of files follows the naming convention: 
      'merged_<year>.csv' and 'TAPR_district_adv_<year>.xlsx' located at:
      https://github.com/mm175rice/HERC-DISTRICT-MATCH-FILES/tree/main/data/<year>
    """
    # Base raw GitHub URL
    base_url = f"https://raw.githubusercontent.com/mm175rice/HERC-DISTRICT-MATCH-FILES/main/data/{year}"

    # Build expected filenames
    csv_filename = f"merged_{year}.csv"
    xlsx_filename = f"TAPR_district_adv_{year}.xlsx"

    # Build full URLs
    csv_url = f"{base_url}/{csv_filename}"
    xlsx_url = f"{base_url}/{xlsx_filename}"

    # Load CSV
    df = pd.read_csv(csv_url)
    column_key = pd.read_excel(xlsx_url, sheet_name='distprof')

    # Filter out charter schools if applicable
    if 'Charter School (Y/N)' in df.columns:
        df = df[df['Charter School (Y/N)'] == 'N']

    # Replace negative values with NaN in numeric columns
    numeric_cols = df.select_dtypes(include='number').columns
    df[numeric_cols] = df[numeric_cols].mask(df[numeric_cols] < 0, np.nan)

    return df, column_key


