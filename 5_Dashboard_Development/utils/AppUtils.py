### APP GENERAL DEPENDENCIES ###

# =============================================================================
# 1. Imports and Settings
# =============================================================================
from pathlib import Path
import re
import pandas as pd

# =============================================================================
# 2. Loading Data
# =============================================================================
# --- Get District ID Key ---
current_dir = Path(__file__).resolve().parent
data_dir = current_dir.parent / "data"
ids_path = data_dir / "ids.csv"
ids = pd.read_csv(ids_path)

# =============================================================================
# 3. District Name Formatting Helper Function
# =============================================================================
def title_case_with_spaces(text):
    """
    Function that converts all text in a string to title case except if it's one
    of the common school district acronyms, CISD, ISD, or MSD. 

    Inputs: 
        text (str): A string of a district name

    Returns:
        the same string in title case, except where it CISD, ISD, MSD
    """
    if 'CISD' in text:
        words = text.split()
        words = [word.title() if word != 'CISD' else word for word in words]
        return ' '.join(words)
    if 'ISD' in text:
        words = text.split()
        words = [word.title() if word != 'ISD' else word for word in words]
        return ' '.join(words)
    if 'MSD' in text:
        words = text.split()
        words = [word.title() if word != 'MSD' else word for word in words]
        return ' '.join(words)
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', text).title()

# =============================================================================
# 4. Demographic Buckets and Helper Functions
# =============================================================================
bucket_options = {"Student Teacher Ratio": 'student_teacher_ratio',
    "Student Count": 'student_count',
    "Staff Count": 'staff_count',
    "Race/Ethnicity Student %": 'race_ethnicity_percent',
    "Economically Disadvantaged Student %": 'economically_disadvantaged',
    "Special Education / 504 Student %": 'special_ed_504',
    "Language Education Student %": 'language_education_percent',
    "Special Populations Student %": 'special_populations_percent',
    "Gifted Student %": 'gifted_students'}

demographic_buckets = {'student_teacher_ratio': ['DPSTKIDR'],
 'student_count': ['DPNTALLC'],
 'staff_count': ['DPSATOFC'],
 'race_ethnicity_percent': ['DPNTBLAP',
  'DPNTINDP',
  'DPNTASIP',
  'DPNTHISP',
  'DPNTPCIP',
  'DPNTTWOP',
  'DPNTWHIP'],
 'economically_disadvantaged': ['DPNTECOP', 'DPNTTT1P'],
 'special_ed_504': ['DPNT504P', 'DPNTSPEP'],
 'language_education_percent': ['DPNTBILP', 'DPNTLEPP'],
 'special_populations_percent': ['DPNTFOSP',
  'DPNTHOMP',
  'DPNTIMMP',
  'DPNTMIGP',
  'DPNTMLCP'],
 'gifted_students': ['DPNTGIFP'],
 'district_identifiers': ['DISTRICT_id',
  'TEA District Type',
  'TEA Description',
  'NCES District Type',
  'NCES Description',
  'Charter School (Y/N)',
  'COUNTY',
  'REGION',
  'DISTRICT',
  'DISTNAME',
  'CNTYNAME',
  'DFLCHART',
  'DFLALTED',
  'ASVAB_STATUS']}


def get_labels_from_variable_name_dict(name_dict, key_df):
    """
    Given a dictionary of COLUMN ID values, return a dictionary mapping each key to a list of COLUMN LABEL Values
    from the key DataFrame. For the 'district_identifiers' key, include its values without modification.

    Args:
        name_dict (dict): Dictionary with string keys and list of COLUMN IDs as values.
        key_df (pd.DataFrame): DataFrame with 'NAME' and 'LABEL' columns. The NAME LABEL mapping file

    Returns:
        dict: Dictionary with the same keys and list of corresponding LABELs as values.
    """
    result = {}
    for key, name_list in name_dict.items():
        if key == "district_identifiers":
            # Leave district identifiers untouched
            result[key] = name_list
        else:
            # Map NAMEs to LABELs using the key DataFrame
            result[key] = key_df[key_df['NAME'].isin(name_list)]['LABEL'].tolist()
    return result

def get_combined_values(data_dict, columns_wanted):
    return [item for col in columns_wanted for item in data_dict.get(col, [])]