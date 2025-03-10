import pandas as pd
import os

def import_data(years):
    """
    Function that imports the yearly combined dataset for the specified years

    Inputs: 
    - years: a list of 4 digit YYYY integers representing years (possible values are from 2018 to 2023)

    Returns:
    - a dictionary with key-value pairs where keys are years and the values are pandas dataframes
    """
    data_dict = {} # initialize empty dictionary

    for year in years:
        path = f"{os.getcwd()}/0_Datasets/1.7Master_Files/Individual Year Files/yearly_data_{year}.csv" # pathname

        data = pd.read_csv(path)

        data_dict[year] = data # add to dictionary

    return data_dict

def add_district_type(data_dict):
    """
    Function joins District Type dataset to a dictionary where the keys are the year and the values are Pandas dataframes.

    Inputs: 
    - data_dict: a dictionary with the combined yearly datasets

    Returns:
    - a dictionary with years as the keys and the values are dataframes with the yearly data and the district type data
    """
    combined_dict = {}
    years_dict = {2018: 1, 2019: 2, 2020: 3, 2021: 4, 2022: 5, 2023: 6}
    for year in data_dict.keys(): # for each year
        path = f"{os.getcwd()}/0_Datasets/1.{years_dict[year]}Data{year}/District/clean_data/district_type{year}_clean.csv" # year-dependent path

        df = pd.read_csv(path) # load in csv file

        print(f"Loaded in District Type for {year}")

        df['District Number'] = df['District Number'].astype(str).str.replace("[^0-9]"," ", regex = True).astype(int)

        data_dict[year]['district_id'] = data_dict[year]['district_id'].astype(str).str.replace("[^0-9]"," ", regex = True).astype(int)

        # prevent problems with any NAs in the district ID columns
        if sum(data_dict[year]['district_id'].isna()) != 0 and sum(df[year]['District Number'].isna()) != 0:
            raise("NAs in identification columns. Ensure all rows have an ID.")

        # join the dataframes together
        joined_df = data_dict[year].merge(df, left_on = ['district_id','distname'], right_on = ['District Number', 'District'], how = 'inner')
        combined_dict[year] = joined_df

    return combined_dict

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
        new_name = f"District {year} {col}".lower() # new name for column with District YYYY

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
                        'Student Membership: All Students Count']
        
        
        colnames = year_dependent_colnames_generator(year, year_dep_cols) # use helper function

        selected_col_dict[year] = dist_prof_type_dict[year][colnames] # select columns of interest and assign to new dictionary
        
    return selected_col_dict

def filter_out_charters(data_dict):
    """
    Takes a joined DISTPROF and District Type dataset and returns only non-charter school district data. 

    Inputs:
    - a dictionary where the keys are years (YYYY) and the values are dataframes which contain joined DISTPROF and District Type data.

    Returns:
    - a dictionary where each dataframe is subsetted to only include non-charter districts. 
    """
    no_charters = {}

    for year in data_dict.keys():
       
       no_charters[year] = data_dict[year][
    (data_dict[year]['TEA Description'] != 'Charter School Districts') & 
    (data_dict[year]['TEA Description'] != 'Charter Schools')] # remove charters
       
    return no_charters 

from sklearn.manifold import TSNE
import plotly.express as px
import re

def visualize_tnse(year, components, data_dict, selected_columns = None, y_var = 'TEA Description'):
    """
    Runs t-SNE based on two specified columns, to visualize the relationship between the two. 

    Inputs:
    - year: a 4 digit integer representing a year, YYYY, such as 2020
    - components: the number of components you want t-SNE to use
    - data_dict: a dictionary with key-value pairs where the key is a year, and the value is a DISTPROF dataset as a dataframe
    - column1: a string representing the first demographic you want plotted
    - column2: a string representing the second demographic you want plotted
    - y_var: a string representing a column that you want to classify the data with. Default is TEA Description
    """
    data = data_dict[year].dropna()
    if y_var == 'TEA Description' or y_var == 'NCES Description':
        if selected_columns != None:
            X = data[selected_columns]
        else:
            X = data.drop(['District Number', 'District', 'TEA Description', 'NCES Description'], axis = 1)
    else:
        if selected_columns != None:
            X = data[selected_columns].drop(y_var, axis=1)
        else:
            X = data.drop(['District Number', 'District', 'TEA Description', 'NCES Description', y_var], axis = 1)

    y = data[y_var]

    label = re.sub(f"District {year} ", "", y_var)

    tsne = TSNE(n_components=components, random_state=42)

    X_tsne = tsne.fit_transform(X)

    tsne.kl_divergence_

    fig = px.scatter(x=X_tsne[:, 0], y=X_tsne[:, 1], color = y)
    fig.update_layout(
    title=f"t-SNE visualization of DISTPROF by {label}, {year}",
    xaxis_title="First t-SNE",
    yaxis_title="Second t-SNE",
    legend_title=label
    )
    fig.show()