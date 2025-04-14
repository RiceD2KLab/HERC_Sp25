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

def engineer_performance(parent_dir, year):
    df = pd.read_csv(f"{parent_dir}/HERC_Sp25/0_Datasets/1.7Master_Files/Individual Year Files_Take2/merged_{year}.csv")
    level_mapping = {
        'Approaches Grade Level': {
            'Mathematics': [col for col in df.columns if 'Mathematics' in col and 'Approaches Grade Level' in col],
            'Reading/ELA': [col for col in df.columns if 'Reading/ELA' in col and 'Approaches Grade Level' in col],
            #'Writing': [col for col in df.columns if 'Writing' in col and 'Approaches Grade Level' in col],
            'Science': [col for col in df.columns if 'Science' in col and 'Approaches Grade Level' in col],
            'Social Studies': [col for col in df.columns if 'Social Studies' in col and 'Approaches Grade Level' in col],
        },
        'Meets Grade Level': {
            'Mathematics': [col for col in df.columns if 'Mathematics' in col and 'Meets Grade Level' in col],
            'Reading/ELA': [col for col in df.columns if 'Reading/ELA' in col and 'Meets Grade Level' in col],
            #'Writing': [col for col in df.columns if 'Writing' in col and 'Meets Grade Level' in col],
            'Science': [col for col in df.columns if 'Science' in col and 'Meets Grade Level' in col],
            'Social Studies': [col for col in df.columns if 'Social Studies' in col and 'Meets Grade Level' in col],
        },
        'Masters Grade Level': {
            'Mathematics': [col for col in df.columns if 'Mathematics' in col and 'Masters Grade Level' in col],
            'Reading/ELA': [col for col in df.columns if 'Reading/ELA' in col and 'Masters Grade Level' in col],
            #'Writing': [col for col in df.columns if 'Writing' in col and 'Masters Grade Level' in col],
            'Science': [col for col in df.columns if 'Science' in col and 'Masters Grade Level' in col],
            'Social Studies': [col for col in df.columns if 'Social Studies' in col and 'Masters Grade Level' in col],
        }
    }

    # Create a new DataFrame for aggregating performance levels by subject
    # Include 'distname', 'district_id', 'county' for context
    df_agg_levels_subject = df[['DISTNAME', 'DISTRICT_id']].copy()

    # Iterate over each performance level and each subject to calculate the average scores
    for level, subjects in level_mapping.items():
        for subject, columns in subjects.items():
            # Create a new column in the aggregation DataFrame for each subject-performance level combination
            # Calculate the mean score for each subject-performance level across the specified columns
            df_agg_levels_subject[f'{subject} ({level})'] = df[columns].mean(axis=1)

    dropout_columns = [
   f'District {year - 1} Annual Dropout for Grades 07-08: All Students Rate',
   f'District {year - 1} Annual Dropout for Grades 07-08: Male Rate',
   f'District {year - 1} Annual Dropout for Grades 07-08: Female Rate',
   f'District {year - 1} Annual Dropout for Grades 07-08: African American Rate',
   f'District {year - 1} Annual Dropout for Grades 07-08: American Indian Rate',
   f'District {year - 1} Annual Dropout for Grades 07-08: Asian Rate',
   f'District {year - 1} Annual Dropout for Grades 07-08: Hispanic Rate',
   f'District {year - 1} Annual Dropout for Grades 07-08: Pacific Islander Rate',
   f'District {year - 1} Annual Dropout for Grades 07-08: Two or More Races Rate',
   f'District {year - 1} Annual Dropout for Grades 07-08: White Rate',
   f'District {year - 1} Annual Dropout for Grades 07-08: Econ Disadv Rate',
   f'District {year - 1} Annual Dropout for Grades 07-08: Special Ed Rate',
   f'District {year - 1} Annual Dropout for Grades 07-08: At Risk Rate',
   f'District {year - 1} Annual Dropout for Grades 07-08: EB/EL Rate',
   f'District {year - 1} Annual Dropout for Grades 09-12: All Students Rate',
   f'District {year - 1} Annual Dropout for Grades 09-12: Male Rate',
   f'District {year - 1} Annual Dropout for Grades 09-12: Female Rate',
   f'District {year - 1} Annual Dropout for Grades 09-12: African American Rate',
   f'District {year - 1} Annual Dropout for Grades 09-12: American Indian Rate',
   f'District {year - 1} Annual Dropout for Grades 09-12: Asian Rate',
   f'District {year - 1} Annual Dropout for Grades 09-12: Hispanic Rate',
   f'District {year - 1} Annual Dropout for Grades 09-12: Pacific Islander Rate',
   f'District {year - 1} Annual Dropout for Grades 09-12: Two or More Races Rate',
   f'District {year - 1} Annual Dropout for Grades 09-12: White Rate',
   f'District {year - 1} Annual Dropout for Grades 09-12: Econ Disadv Rate',
   f'District {year - 1} Annual Dropout for Grades 09-12: Special Ed Rate',
   f'District {year - 1} Annual Dropout for Grades 09-12: At Risk Rate',
   f'District {year - 1} Annual Dropout for Grades 09-12: EB/EL Rate'
    ]

    # Create a DataFrame with the selected dropout columns, ensuring DistrictName is included
    existing_columns = ['DISTNAME', 'DISTRICT_id'] + [col for col in dropout_columns if col in df.columns]
    df_dropout = df[existing_columns].copy()

    # Aggregate dropout rates into new columns, and convert identity labels to lowercase (to match column name case)
    for identity in ['All Students', 'Male', 'Female', 'African American', 'American Indian', 'Asian',
                    'Hispanic', 'Pacific Islander', 'Two or More Races', 'White', 'Econ Disadv', 
                    'Special Ed', 'At Risk', 'EB/EL']:
        
        # Convert the column names to lowercase to match dataset column names
        col1 = f'District {year - 1} Annual Dropout for Grades 07-08: {identity} Rate'
        col2 = f'District {year - 1} Annual Dropout for Grades 09-12: {identity} Rate'

        # Ensure columns exist before trying to compute mean
        cols_to_avg = [col for col in [col1, col2] if col in df_dropout.columns]
        
        if cols_to_avg:  # Only compute if at least one column exists
            df_dropout.loc[:, f'{identity} Dropout Rate'] = df_dropout[cols_to_avg].mean(axis=1, skipna=True)

    df_dropout.drop(columns=dropout_columns, inplace=True, errors='ignore')

    df_combined = df_agg_levels_subject.merge(df_dropout, on=['DISTNAME', 'DISTRICT_id'], how='inner')

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
    existing_columns2 = ['DISTNAME', 'DISTRICT_id'] + [col for col in additional_columns if col in df.columns]
    df_combined2 = df_combined.merge(df[existing_columns2], on=['DISTNAME', 'DISTRICT_id'], how='inner')
    return df_combined2