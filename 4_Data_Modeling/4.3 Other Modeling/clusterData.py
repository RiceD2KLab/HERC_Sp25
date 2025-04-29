import pandas as pd
import os

def import_data(years, directory):
    """
    Function that imports the yearly combined dataset for the specified years

    Inputs: 
    - years: a list of 4 digit YYYY integers representing years (possible values are from 2018 to 2023)
    - directory: a string specifying your local directory where the Github is cloned

    Returns:
    - a dictionary with key-value pairs where keys are years and the values are pandas dataframes
    """

    data_dict = {} # initialize empty dictionary

    for year in years:
        path = f"{directory}/0_Datasets/1.7Master_Files/Individual Year Files_Take2/merged_{year}.csv" # pathname

        data = pd.read_csv(path)

        data_dict[year] = data # add to dictionary

    return data_dict

def year_dependent_colnames_generator(year, base_names):
    """
    Helper function that creates a list of column names based on the year inputted. 
    Some columns in the data have "District 2020" in the column names, so this helps select for each year the columns necessary.

    Inputs:
    - year: a 4 digit integer representing a year (YYYY), such as 2020
    - base_names: the base names of the columns, excluding "District YYYY", such as "Student Membership: All Students Count"

    Returns:
    - a list of strings representing column names that should exist in a joined District Type and DISTPROF dataframe, depending on input year
    """
    # names that are not dependent on year
    new_names = ['District Number', 'District', 'TEA Description', 'NCES Description']

    for col in base_names: # create new names for year-dependent columns
        new_name = f"District {year} {col}" # new name for column with District YYYY

        new_names.append(new_name)
        
    return new_names

def select_columns(dist_prof_type_dict):
    """
    Function that selects the identifiers for distircts and the features specified as most important by our sponsor, 
    such as racial/ethnic percentages and the count of students. 

    Inputs:
    - a dictionary where the keys are years (YYYY) and the values are dataframes which contain joined DISTPROF and District Type data

    Returns:
    - a dictionary where each dataframe is subsetted to only include the columns specified by our sponsor
    """
    selected_col_dict = {} # initialize empty dictionary

    for year in dist_prof_type_dict.keys():

        # columns of interest
        year_dep_cols = ['Student Membership: White Percent', 'Student Membership: Hispanic Percent', 
                        'Student Membership: African American Percent', 'Student Membership: American Indian Percent',
                        'Student Membership: Asian Percent', 'Student Membership: Pacific Islander Percent',
                        'Student Membership: Two or More Races Percent', 'Student Membership: Econ Disadv Percent',
                        'Student Membership: Special Ed Percent', 'Student Membership: Bilingual/ESL Percent',
                        'Student Membership: Gifted & Talented Percent', 'Student Membership: Immigrant Percent',
                        'Student Membership: All Students Count', 'Staff: Teacher Student Ratio', 'Student Membership: At Risk Percent']
        
        
        colnames = year_dependent_colnames_generator(year, year_dep_cols) # use helper function

        selected_col_dict[year] = dist_prof_type_dict[year][colnames] # select columns of interest and assign to new dictionary
        
    return selected_col_dict

def filter_out_charters(data_dict):
    """
    Takes a joined TAPR dataset and returns only non-charter school district data. 

    Inputs:
    - a dictionary where the keys are years (YYYY) and the values are dataframes with the column "TEA Description"

    Returns:
    - a dictionary where each dataframe is subsetted to only include non-charter districts. 
    """
    no_charters = {}

    for year in data_dict.keys():
       
       no_charters[year] = data_dict[year][
    (data_dict[year]['TEA Description'] != 'Charter School Districts') & 
    (data_dict[year]['TEA Description'] != 'Charter Schools')] # remove charters
       
    return no_charters 

def master_cluster_data(data_dict):
    by_year = []
    data_dict2 = select_columns(filter_out_charters(data_dict))
    for year in data_dict2.keys():
        df = data_dict2[year].copy()
        df.columns = df.columns.str.replace(f'District {year} ', '')
        df.loc[:,"Year"] = year
        by_year.append(df)

    combined_data = pd.concat(by_year)
    return(combined_data)