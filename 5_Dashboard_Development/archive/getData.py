
### DATA DEPENDENCIES ###

# =============================================================================
# 1. Imports and Settings
# =============================================================================
# Standard Imports
import pandas as pd
import numpy as np
import warnings
import urllib.error

# Set Warning Settings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl.worksheet.header_footer")


# =============================================================================
# 2. Load GitHub Data Function
# =============================================================================
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
    base_url = f"https://raw.githubusercontent.com/mm175rice/HERC-DISTRICT-MATCH-FILES/main/data/{year}"
    csv_url = f"{base_url}/merged_{year}.csv"
    xlsx_url = f"{base_url}/TAPR_district_adv_{year}.xlsx"

    try:
        df = pd.read_csv(csv_url)
        column_key = pd.read_excel(xlsx_url, sheet_name='distprof')
    except (urllib.error.URLError, urllib.error.HTTPError, FileNotFoundError):
        raise ValueError("This year of data does not exist yet. Check the year or the GitHub repository.")

    if 'Charter School (Y/N)' in df.columns:
        df = df[df['Charter School (Y/N)'] == 'N']

    numeric_cols = df.select_dtypes(include='number').columns
    df[numeric_cols] = df[numeric_cols].mask(df[numeric_cols] < 0, pd.NA)

    return df, column_key

# =============================================================================
# 3. Outcome Data Functions
# =============================================================================
# --- Clean STAAR Data To Be Mutually Exclusive By Grade Level and Subject ---
def get_subject_level_exclusive_scores(df, subject):
    """
    Returns mutually exclusive STAAR scores (Approaches only, Meets only, Masters, Did Not Meet) by grade level
    for a given subject.

    Args:
        df (pd.DataFrame): Raw district-level STAAR dataset.
        subject (str): One of ['Mathematics', 'Reading/ELA', 'Writing', 'Science', 'Social Studies'].

    Returns:
        pd.DataFrame: Long-format dataframe with DISTNAME, DISTRICT_id, Grade, and exclusive performance levels.
    """
    # Step 1: Build level mapping dynamically
    level_mapping = {
        'Approaches': [col for col in df.columns if subject in col and 'Approaches Grade Level' in col and "Rate" in col and "All Students" in col],
        'Meets': [col for col in df.columns if subject in col and 'Meets Grade Level' in col and "Rate" in col and "All Students" in col],
        'Masters': [col for col in df.columns if subject in col and 'Masters Grade Level' in col and "Rate" in col and "All Students" in col],
    }

    if not any(level_mapping.values()):
        print(f"Warning: No data available for subject '{subject}'.")
        return None

    # Step 2: Create long DataFrames per level
    def melt_level(level):
        cols = level_mapping[level]
        df_level = df[['DISTNAME', 'DISTRICT_id'] + cols].copy()
        df_long = df_level.melt(id_vars=['DISTNAME', 'DISTRICT_id'], value_vars=cols,
                                var_name='raw_column', value_name=level)
        df_long['Grade'] = df_long['raw_column'].str.extract(r'Grade (\d+)')
        return df_long.drop(columns='raw_column')

    df_approaches = melt_level('Approaches')
    df_meets = melt_level('Meets')
    df_masters = melt_level('Masters')

    # Step 3: Merge the levels on DISTRICT, DISTNAME, and Grade
    merged = df_approaches.merge(df_meets, on=['DISTNAME', 'DISTRICT_id', 'Grade'], how='inner')
    merged = merged.merge(df_masters, on=['DISTNAME', 'DISTRICT_id', 'Grade'], how='inner')

    # Step 4: Compute mutually exclusive performance levels
    merged['Masters Grade Level'] = merged['Masters']
    merged['Meets Grade Level'] = merged['Meets'] - merged['Masters']
    merged['Approaches Grade Level'] = merged['Approaches'] - merged['Meets']
    merged['Did Not Meet Grade Level'] = 100 - merged['Approaches']

    # Round values and reorder
    result = merged[['DISTNAME', 'DISTRICT_id', 'Grade', 'Approaches Grade Level', 'Meets Grade Level', 'Masters Grade Level', 'Did Not Meet Grade Level']]
    return result.round(2)


# --- Calculate Average Dropout Rates ---
def compute_dropout_rates(df, year):
    """
    Calculate average dropout rates for grade 07-08 and 09-12 by student group.

    Args:
        df (pd.DataFrame): Raw district-level dataframe with dropout columns.
        year (int): The current reporting year. Dropout rates are based on year - 1.

    Returns:
        pd.DataFrame: DataFrame with combined dropout rates by identity and district.
    """
    identities = ['All Students', 'Male', 'Female', 'African American', 'American Indian', 'Asian',
                  'Hispanic', 'Pacific Islander', 'Two or More Races', 'White', 'Econ Disadv', 
                  'Special Ed', 'At Risk', 'EB/EL']

    dropout_columns = [
        f'District {year - 1} Annual Dropout for Grades 07-08: {id_} Rate'
        for id_ in identities
    ] + [
        f'District {year - 1} Annual Dropout for Grades 09-12: {id_} Rate'
        for id_ in identities
    ]

    existing_columns = ['DISTNAME', 'DISTRICT_id'] + [col for col in dropout_columns if col in df.columns]
    df_dropout = df[existing_columns].copy()

    for identity in identities:
        col1 = f'District {year - 1} Annual Dropout for Grades 07-08: {identity} Rate'
        col2 = f'District {year - 1} Annual Dropout for Grades 09-12: {identity} Rate'

        cols_to_avg = [col for col in [col1, col2] if col in df_dropout.columns]
        if cols_to_avg:
            df_dropout.loc[:, f'{identity} Dropout Rate'] = df_dropout[cols_to_avg].mean(axis=1)

    df_dropout.drop(columns=dropout_columns, inplace=True, errors='ignore')
    return df_dropout


# --- Gather the Remaining Outcomes Data ---
def get_existing_columns(df, year):
    """
    Selects columns from a master DataFrame that exist and are relevant to performance indicators.

    Args:
        df (pd.DataFrame): The master district-level DataFrame.
        year (int): Reporting year to resolve dynamic column names.

    Returns:
        pd.DataFrame: Subset of the original DataFrame with only the relevant and existing columns.
    """
    additional_columns = [

    # DREF:

   'DFLCHART',
   'DFLALTED',
   'ASVAB_STATUS',

   # DTYPE:

   'TEA Description',
   'NCES Description',
   'Charter School (Y/N)',

    # Demography
   f'District {year} Student Membership: All Students Count',
   f'District {year} Student Membership: Male Percent',
   f'District {year} Student Membership: Female Percent',
   f'District {year} Student Membership: African American Percent',
   f'District {year} Student Membership: American Indian Percent',
   f'District {year} Student Membership: Asian Percent',
   f'District {year} Student Membership: Hispanic Percent',
   f'District {year} Student Membership: Pacific Islander Percent',
   f'District {year} Student Membership: Two or More Races Percent',
   f'District {year} Student Membership: White Percent',
   f'District {year} Student Membership: Econ Disadv Percent',
   f'District {year} Student Membership: Special Ed Percent',
   f'District {year} Student Membership: Gifted & Talented Percent',
   f'District {year} Student Membership: EB/EL Percent',
   f'District {year} Student Membership: At Risk Percent',
   f'District {year} Student Membership: Immigrant Percent',
   f'District {year} Student Membership: Gifted & Talented Percent',
   f'District {year} Staff: Teacher Student Ratio',

    # CCMR Rates
   f'District {year - 1} College, Career, & Military Ready Graduates: All Students Rate',
   f'District {year - 1} College, Career, & Military Ready Graduates: Male Rate',
   f'District {year - 1} College, Career, & Military Ready Graduates: Female Rate',
   f'District {year - 1} College, Career, & Military Ready Graduates: African American Rate',
   f'District {year - 1} College, Career, & Military Ready Graduates: Hispanic Rate',
   f'District {year - 1} College, Career, & Military Ready Graduates: White Rate',
   f'District {year - 1} College, Career, & Military Ready Graduates: American Indian Rate',
   f'District {year - 1} College, Career, & Military Ready Graduates: Asian Rate',
   f'District {year - 1} College, Career, & Military Ready Graduates: Pacific Islander Rate',
   f'District {year - 1} College, Career, & Military Ready Graduates: Two or More Races Rate',
   f'District {year - 1} College, Career, & Military Ready Graduates: Econ Disadv Rate',
   f'District {year - 1} College, Career, & Military Ready Graduates: Special Ed Rate',
   f'District {year - 1} College, Career, & Military Ready Graduates: EB/EL Rate',
   f'District {year - 1} College, Career, & Military Ready Graduates: At Risk Rate',


    # Attendence Rates
   f'District {year - 1} Attendance: All Students Rate',
   f'District {year - 1} Attendance: Two or More Races Rate',
   f'District {year - 1} Attendance: Asian Rate',
   f'District {year - 1} Attendance: Pacific Islander Rate',
   f'District {year - 1} Attendance: African American Rate',
   f'District {year - 1} Attendance: Hispanic Rate',
   f'District {year - 1} Attendance: White Rate',
   f'District {year - 1} Attendance: American Indian Rate',
   f'District {year - 1} Attendance: Econ Disadv Rate',
   f'District {year - 1} Attendance: Special Ed Rate',
   f'District {year - 1} Attendance: Female Rate',
   f'District {year - 1} Attendance: Male Rate',
   f'District {year - 1} Attendance: EB/EL Rate',
   f'District {year - 1} Attendance: At Risk Rate',

    # Chronic Absenteeism Rates
   f'{year - 1} district Chronic Absenteeism All Students Group: Rate',
   f'{year - 1} district Chronic Absenteeism African American Group: Rate',
   f'{year - 1} district Chronic Absenteeism Hispanic Group: Rate',
   f'{year - 1} district Chronic Absenteeism White Group: Rate',
   f'{year - 1} district Chronic Absenteeism American Indian Group: Rate',
   f'{year - 1} district Chronic Absenteeism Asian Group: Rate',
   f'{year - 1} district Chronic Absenteeism Pacific Islander Group: Rate',
   f'{year - 1} district Chronic Absenteeism Two or More Races Group: Rate',
   f'{year - 1} district Chronic Absenteeism Econ Disadv Group: Rate',
   f'{year - 1} district Chronic Absenteeism Special Ed Group: Rate',
   f'{year - 1} district Chronic Absenteeism EL Group: Rate',
   f'{year - 1} district Chronic Absenteeism At Risk Group: Rate',

    # 4-Year Longitudinal
   f'District {year - 1} 4-Year Longitudinal: [FHSP-DLA Graduates] for All Students Rate',
   f'District {year - 1} 4-Year Longitudinal: [FHSP-DLA Graduates] for Female Rate',
   f'District {year - 1} 4-Year Longitudinal: [FHSP-DLA Graduates] for Male Rate',
   f'District {year - 1} 4-Year Longitudinal: [FHSP-DLA Graduates] for African American Rate',
   f'District {year - 1} 4-Year Longitudinal: [FHSP-DLA Graduates] for American Indian Rate',
   f'District {year - 1} 4-Year Longitudinal: [FHSP-DLA Graduates] for Asian Rate',
   f'District {year - 1} 4-Year Longitudinal: [FHSP-DLA Graduates] for Hispanic Rate',
   f'District {year - 1} 4-Year Longitudinal: [FHSP-DLA Graduates] for Pacific Islander Rate',
   f'District {year - 1} 4-Year Longitudinal: [FHSP-DLA Graduates] for White Rate',
   f'District {year - 1} 4-Year Longitudinal: [FHSP-DLA Graduates] for Two or More Races Rate',
   f'District {year - 1} 4-Year Longitudinal: [FHSP-DLA Graduates] for Econ Disadv Rate',
   f'District {year - 1} 4-Year Longitudinal: [FHSP-DLA Graduates] for Special Ed Rate',
   f'District {year - 1} 4-Year Longitudinal: [FHSP-DLA Graduates] for EB/EL Rate',
   f'District {year - 1} 4-Year Longitudinal: [FHSP-DLA Graduates] for At Risk Rate',
   f'District {year - 1} 4-Year Longitudinal: [RHSP/DAP or FHSP-E/DLA Graduates] for All Students Rate',
   f'District {year - 1} 4-Year Longitudinal: [RHSP/DAP or FHSP-E/DLA Graduates] for Male Rate',
   f'District {year - 1} 4-Year Longitudinal: [RHSP/DAP or FHSP-E/DLA Graduates] for Female Rate',
   f'District {year - 1} 4-Year Longitudinal: [RHSP/DAP or FHSP-E/DLA Graduates] for African American Rate',
   f'District {year - 1} 4-Year Longitudinal: [RHSP/DAP or FHSP-E/DLA Graduates] for American Indian Rate',
   f'District {year - 1} 4-Year Longitudinal: [RHSP/DAP or FHSP-E/DLA Graduates] for Asian Rate',
   f'District {year - 1} 4-Year Longitudinal: [RHSP/DAP or FHSP-E/DLA Graduates] for Hispanic Rate',
   f'District {year - 1} 4-Year Longitudinal: [RHSP/DAP or FHSP-E/DLA Graduates] for Pacific Islander Rate',
   f'District {year - 1} 4-Year Longitudinal: [RHSP/DAP or FHSP-E/DLA Graduates] for White Rate',
   f'District {year - 1} 4-Year Longitudinal: [RHSP/DAP or FHSP-E/DLA Graduates] for Two or More Races Rate',
   f'District {year - 1} 4-Year Longitudinal: [RHSP/DAP or FHSP-E/DLA Graduates] for Econ Disadv Rate',
   f'District {year - 1} 4-Year Longitudinal: [RHSP/DAP or FHSP-E/DLA Graduates] for Special Ed Rate',
   f'District {year - 1} 4-Year Longitudinal: [RHSP/DAP or FHSP-E/DLA Graduates] for EB/EL Rate',
   f'District {year - 1} 4-Year Longitudinal: [RHSP/DAP or FHSP-E/DLA Graduates] for At Risk Rate',

    # AP/IB
   f'District {year - 1} AP/IB Course Completion Graduates: All Students Rate',
   f'District {year - 1} AP/IB Course Completion Graduates: African American Rate',
   f'District {year - 1} AP/IB Course Completion Graduates: Hispanic Rate',
   f'District {year - 1} AP/IB Course Completion Graduates: White Rate',
   f'District {year - 1} AP/IB Course Completion Graduates: American Indian Rate',
   f'District {year - 1} AP/IB Course Completion Graduates: Asian Rate',
   f'District {year - 1} AP/IB Course Completion Graduates: Pacific Islander Rate',
   f'District {year - 1} AP/IB Course Completion Graduates: Two or More Races Rate',
   f'District {year - 1} AP/IB Course Completion Graduates: Male Rate',
   f'District {year - 1} AP/IB Course Completion Graduates: Female Rate',
   f'District {year - 1} AP/IB Course Completion Graduates: Econ Disadv Rate',
   f'District {year - 1} AP/IB Course Completion Graduates: Special Ed Rate',
   f'District {year - 1} AP/IB Course Completion Graduates: EB/EL Rate',
   f'District {year - 1} AP/IB Course Completion Graduates: At Risk Rate',
   f'District {year - 1} AP/IB: All Students (All Subjects) % Taking',
   f'District {year - 1} AP/IB: Male (All Subjects) % Taking',
   f'District {year - 1} AP/IB: Female (All Subjects) % Taking',
   f'District {year - 1} AP/IB: African American (All Subjects) % Taking',
   f'District {year - 1} AP/IB: American Indian (All Subjects) % Taking',
   f'District {year - 1} AP/IB: Asian (All Subjects) % Taking',
   f'District {year - 1} AP/IB: Hispanic (All Subjects) % Taking',
   f'District {year - 1} AP/IB: Two or More Races (All Subjects) % Taking',
   f'District {year - 1} AP/IB: Pacific Islander (All Subjects) % Taking',
   f'District {year - 1} AP/IB: White (All Subjects) % Taking',
   f'District {year - 1} AP/IB: Special Ed (All Subjects) % Taking',
   f'District {year - 1} AP/IB: Econ Disadv (All Subjects) % Taking',
   f'District {year - 1} AP/IB: EB/EL (All Subjects) % Taking',
   f'District {year - 1} AP/IB: At Risk (All Subjects) % Taking',
   f'District {year - 1} AP/IB: All Students (All Subjects) % Students Above Criterion',
   f'District {year - 1} AP/IB: Female (All Subjects) % Students Above Criterion',
   f'District {year - 1} AP/IB: Male (All Subjects) % Students Above Criterion',
   f'District {year - 1} AP/IB: African American (All Subjects) % Students Above Criterion',
   f'District {year - 1} AP/IB: American Indian (All Subjects) % Students Above Criterion',
   f'District {year - 1} AP/IB: Asian (All Subjects) % Students Above Criterion',
   f'District {year - 1} AP/IB: Hispanic (All Subjects) % Students Above Criterion',
   f'District {year - 1} AP/IB: Two or More Races (All Subjects) % Students Above Criterion',
   f'District {year - 1} AP/IB: Pacific Islander (All Subjects) % Students Above Criterion',
   f'District {year - 1} AP/IB: White (All Subjects) % Students Above Criterion',
   f'District {year - 1} AP/IB: Special Ed (All Subjects) % Students Above Criterion',
   f'District {year - 1} AP/IB: Econ Disadv (All Subjects) % Students Above Criterion',
   f'District {year - 1} AP/IB: EB/EL (All Subjects) % Students Above Criterion',
   f'District {year - 1} AP/IB: At Risk (All Subjects) % Students Above Criterion',

    # SAT/ACT
   f'District {year - 1} SAT/ACT: All Students, % Above Criterion',
   f'District {year - 1} SAT/ACT: Female Students, % Above Criterion',
   f'District {year - 1} SAT/ACT: Male Students, % Above Criterion',
   f'District {year - 1} SAT/ACT: African American Students, % Above Criterion',
   f'District {year - 1} SAT/ACT: American Indian Students, % Above Criterion',
   f'District {year - 1} SAT/ACT: Asian Students, % Above Criterion',
   f'District {year - 1} SAT/ACT: Hispanic Students, % Above Criterion',
   f'District {year - 1} SAT/ACT: Two or More Races Students, % Above Criterion',
   f'District {year - 1} SAT/ACT: Pacific Islander Students, % Above Criterion',
   f'District {year - 1} SAT/ACT: White Students, % Above Criterion',
   f'District {year - 1} SAT/ACT: Special Ed Students, % Above Criterion',
   f'District {year - 1} SAT/ACT: Econ Disadv Students, % Above Criterion',
   f'District {year - 1} SAT/ACT: EL Students, % Above Criterion',
   f'District {year - 1} SAT/ACT: At Risk Students, % Above Criterion',
   f'District {year - 1} SAT/ACT: All Students, % Test-Taking',
   f'District {year - 1} SAT/ACT: Female Students, % Test-Taking',
   f'District {year - 1} SAT/ACT: Male Students, % Test-Taking',
   f'District {year - 1} SAT/ACT: African American Students, % Test-Taking',
   f'District {year - 1} SAT/ACT: American Indian Students, % Test-Taking',
   f'District {year - 1} SAT/ACT: Asian Students, % Test-Taking',
   f'District {year - 1} SAT/ACT: Hispanic Students, % Test-Taking',
   f'District {year - 1} SAT/ACT: Two or More Races Students, % Test-Taking',
   f'District {year - 1} SAT/ACT: Pacific Islander Students, % Test-Taking',
   f'District {year - 1} SAT/ACT: White Students, % Test-Taking',
   f'District {year - 1} SAT/ACT: Special Ed Students, % Test-Taking',
   f'District {year - 1} SAT/ACT: Econ Disadv Students, % Test-Taking',
   f'District {year - 1} SAT/ACT: EL Students, % Test-Taking',
   f'District {year - 1} SAT/ACT: At Risk Students, % Test-Taking',
   f'District {year - 1} SAT/ACT: All Students, % Graduates Above Criterion',
   f'District {year - 1} SAT/ACT: Male Students, % Graduates Above Criterion',
   f'District {year - 1} SAT/ACT: Female Students, % Graduates Above Criterion',
   f'District {year - 1} SAT/ACT: African American Students, % Graduates Above Criterion',
   f'District {year - 1} SAT/ACT: Hispanic Students, % Graduates Above Criterion',
   f'District {year - 1} SAT/ACT: White Students, % Graduates Above Criterion',
   f'District {year - 1} SAT/ACT: American Indian Students, % Graduates Above Criterion',
   f'District {year - 1} SAT/ACT: Asian Students, % Graduates Above Criterion',
   f'District {year - 1} SAT/ACT: Pacific Islander Students, % Graduates Above Criterion',
   f'District {year - 1} SAT/ACT: Two or More Races Students, % Graduates Above Criterion',
   f'District {year - 1} SAT/ACT: Econ Disadv Students, % Graduates Above Criterion',
   f'District {year - 1} SAT/ACT: At Risk Students, % Graduates Above Criterion',
   f'District {year - 1} SAT/ACT: EL Students, % Graduates Above Criterion',
   f'District {year - 1} SAT/ACT: Special Ed Students, % Graduates Above Criterion',
]
    existing_cols = ['DISTNAME', 'DISTRICT_id'] + [col for col in additional_columns if col in df.columns]
    return df[existing_cols].copy()


# --- Master Function for Outcome Data ---
def engineer_performance(year):
    """
    Engineer a comprehensive district-level performance DataFrame by aggregating academic performance,
    dropout rates, demographics, college readiness, SAT/ACT, and more.

    Args:
        parent_dir (str): Path to the base data directory.
        year (int): Target reporting year.
        additional_columns (list): List of additional column names to include in the final output.

    Returns:
        pd.DataFrame: Cleaned and combined DataFrame of engineered performance features by district.
    """
    # Base raw GitHub URL
    base_url = f"https://raw.githubusercontent.com/mm175rice/HERC-DISTRICT-MATCH-FILES/main/data/{year}"
    #Get CSV exact filename
    csv_filename = f"merged_{year}.csv"

    #Build csv url 
    csv_url = f"{base_url}/{csv_filename}"

    #Load CSV 
    df = pd.read_csv(csv_url)

    dropout_df = compute_dropout_rates(df, year)

    df_extra = get_existing_columns(df, year)

    return dropout_df.merge(df_extra, on=['DISTNAME', 'DISTRICT_id'], how='inner')