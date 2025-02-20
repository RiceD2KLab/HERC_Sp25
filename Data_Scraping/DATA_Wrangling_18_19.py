
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import traceback
import urllib3
import glob
import os
import io

raw_data_dir = "/Users/treymccray/Kinder_HERC_F24/00_Datasets/Raw_Download_Data"
merge_data_dir = "/Users/treymccray/Kinder_HERC_F24/00_Datasets/Final_Merged_Data"

import pandas as pd

def combine_district_data_2017_2023(year):
    """
    This function merges multiple data sources related to school districts from the specified school year and the following year (e.g., 2017-2018).
    
    Parameters:
    ----------
    year : int
        The starting year of the school year to be processed (e.g., 2017 for the 2017-2018 school year).

    Returns:
    --------
    df_final_combined : DataFrame
        A Pandas DataFrame containing the merged data from multiple sources for the specified year and next year.
    """
    next_year = year + 1
    year_str = str(year)[-2:]  
    next_year_str = str(next_year)[-2:]  

    # Load the District Type file
    file_path = f'{raw_data_dir}/district_type/district-type{year}-{next_year}.xlsx'
    sheets = pd.read_excel(file_path, sheet_name=['Overview', 'Data Dictionary', f'{year_str}{next_year_str}_Data'])
    district_type = sheets[f'{year_str}{next_year_str}_Data']

    df_district_type = district_type.rename(columns={
        'TEA Description': 'District Type',
        'NCES Description': 'Location of District'
    })
    df_district_type['District Number'] = df_district_type['District Number'].astype(str).str.strip("'").astype(int)

    # Load the District Rating file
    df_dref = pd.read_csv(f'{raw_data_dir}/DREF/DREF_{year}-{next_year}.csv', low_memory=False)
    df_dref_filtered = df_dref.rename(columns={
        'DISTRICT': 'District Number',
        'DISTNAME': 'District',
        'CNTYNAME': 'County'
    })
    df_dref_filtered['District Number'] = df_dref_filtered['District Number'].astype(str).str.strip("'").astype(int)

    df_merged = pd.merge(df_district_type, df_dref_filtered, on='District Number', how='inner')

    # Load Student Information file and Reference file
    df_stu = pd.read_csv(f'{raw_data_dir}/DISTPROF/DISTPROF_{year}-{next_year}.csv', low_memory=False)
    df_stu_ref = pd.read_csv(f'{raw_data_dir}/REF/ref_stu{year_str}.csv', low_memory=False)

    mapping_dict = dict(zip(df_stu_ref['NAME'], df_stu_ref['LABEL']))
    df_stu.rename(columns=mapping_dict, inplace=True)
    df_stu['District Number'] = df_stu['District Number'].astype(str).str.strip("'").astype(int)

    df_final_merged = pd.merge(df_merged, df_stu, on='District Number', how='inner')

    # Load Attendance and Dropout Rate file and Reference file
    df_attend_drop_grad = pd.read_csv(f'{raw_data_dir}/DISTGRAD/DISTGRAD_{year}-{next_year}.csv', low_memory=False)
    df_attend_drop_grad_ref = pd.read_csv(f'{raw_data_dir}/REF/ref_attend_drop{year_str}.csv', low_memory=False)

    mapping_dict = dict(zip(df_attend_drop_grad_ref['NAME'], df_attend_drop_grad_ref['LABEL']))
    df_attend_drop_grad.rename(columns=mapping_dict, inplace=True)
    df_attend_drop_grad['District Number'] = df_attend_drop_grad['District Number'].astype(str).str.strip("'").astype(int)

    df_final_combined = pd.merge(df_final_merged, df_attend_drop_grad, on='District Number', how='inner')

    # Load STAAR Assessment Data and Reference file
    df_staar = pd.read_csv(f'{raw_data_dir}/DISTSTAAR1/DISTSTAAR1_{year}-{next_year}.csv', low_memory=False)
    df_staar_ref = pd.read_csv(f'{raw_data_dir}/REF/ref_staar{next_year_str}.csv', low_memory=False)

    mapping_dict = dict(zip(df_staar_ref['NAME'], df_staar_ref['LABEL']))
    df_staar.rename(columns=mapping_dict, inplace=True)
    df_staar['District Number'] = df_staar['District Number'].astype(str).str.strip("'").astype(int)

    df_final_combined = pd.merge(df_final_combined, df_staar, on='District Number', how='inner')

    # Load CCMR data and Reference file
    df_ccmr = pd.read_csv(f'{raw_data_dir}/DISTPERF/DISTPERF_{year}-{next_year}.csv', low_memory=False)
    df_ccmr_ref = pd.read_csv(f'{raw_data_dir}/REF/ref_attend_drop{year_str}.csv', low_memory=False)

    mapping_dict = dict(zip(df_ccmr_ref['NAME'], df_ccmr_ref['LABEL']))
    df_ccmr.rename(columns=mapping_dict, inplace=True)
    df_ccmr['District Number'] = df_ccmr['District Number'].astype(str).str.strip("'").astype(int)

    if 'District Name' in df_ccmr.columns:
        df_ccmr.drop(columns=['District Name'], inplace=True)

    df_final_combined = pd.merge(df_final_combined, df_ccmr, on='District Number', how='inner')

    # Add Year column
    df_final_combined['Year'] = f"{year}-{next_year}"

    return df_final_combined


df_2017_2018 = combine_district_data_2017_2023(2017)
df_2018_2019 = combine_district_data_2017_2023(2018)

