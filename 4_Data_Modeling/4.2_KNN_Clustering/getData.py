from Demographic_Buckets import student_teacher_ratio
from Demographic_Buckets import student_count
from Demographic_Buckets import staff_count
from Demographic_Buckets import race_ethnicity_percent
from Demographic_Buckets import economically_disadvantaged
from Demographic_Buckets import special_ed_504
from Demographic_Buckets import language_education_percent
from Demographic_Buckets import special_populations_percent
from Demographic_Buckets import gifted_students
from Demographic_Buckets import district_identifiers

import pandas as pd
import numpy as np

def get_data(root_directory, year):
    df = pd.read_csv(f"{root_directory}/HERC_Sp25/0_Datasets/1.7Master_Files/Individual Year Files_Take2/merged_{year}.csv")   
    df = df[df['Charter School (Y/N)'] == 'N']
    demographic_df = df[student_teacher_ratio + student_count + staff_count + race_ethnicity_percent + economically_disadvantaged +
                    special_ed_504 + language_education_percent + special_populations_percent + gifted_students +
                    district_identifiers]

    # Select only numeric columns
    numeric_cols = df.select_dtypes(include='number').columns

    # Replace negative values with NaN only in numeric columns
    df[numeric_cols] = df[numeric_cols].mask(df[numeric_cols] < 0, np.nan)
    return(df)