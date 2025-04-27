"""
Data Wrangling File (2020-2023). The capabilities of this file are the following: 
* Read in data from the github repository in python
* Perform preliminary data cleaning steps (Converting columns to numeric, renaming '.', '-1', '-3' values to NA)
* Mapping column IDs with real column names from refrence files 
* Combining level refrence file with datasets
Note: This should work for 2020 - 2023 data. 
"""

#Importing necessary packages
import pandas as pd
import os 
import numpy as np
import warnings
import re
warnings.simplefilter("ignore")

# Helper Function 1: Loading in downloaded data to begin cleaning process 
def load_data(directory, year):
    """
    Reads all CSV files in the specified directory into a dictionary (RAWDATA) 
    and loads all sheets from an Excel file into another dictionary (REF).
    
    Args:
        directory (str): The path to the directory containing the raw data files.
        year (int or str): The year to append to dictionary keys.
    
    Returns:
        tuple: (RAWDATA, REF)
        RAWDATA: Dictionary containing all raw data files 
        REF: Dictionary containing column IDs for each 
    """
    
    # Change to the specified directory
    os.chdir(directory)

    # Store all raw CSV data in a dictionary with dynamic year
    csv_files = [f for f in os.listdir() if f.endswith('.csv')]
    RAWDATA = {file.split('.')[0].lower(): pd.read_csv(file) for file in csv_files}

    # Look for an Excel file (assuming there's only one Excel file in the directory)
    excel_files = [f for f in os.listdir() if f.endswith('.xlsx') or f.endswith('.xls')]
    
    REF = {}
    if excel_files:
        file_path = excel_files[0]  # Taking the first Excel file found
        sheetname_ref = pd.ExcelFile(file_path).sheet_names
        REF = {f"{sheet}_ref{year}": pd.read_excel(file_path, sheet_name=sheet) for sheet in sheetname_ref}

    # Return both dictionaries
    return RAWDATA, REF

# Helper Function 2: Performing primary datacleaning of datasets including remove nas 
def primary_data_cleaning(df_dict, level):
    """
    Converts all columns in each DataFrame (except the one containing the specified level) to numeric.
    Replaces '.', '-1', and '-3' values with NaN.
    
    Additionally, searches the DataFrame's columns for a column that contains the specified level's long form
    and renames it to '{original_name}_id' if found.
    
    Args:
        df_dict (dict): Dictionary of pandas DataFrames.
        level (str): Level of granularity ('C', 'D', 'R', 'S') corresponding to Campus, District, Region, State.
    
    Returns:
        dict: Dictionary of DataFrames with processed data.
    """
    level_map = {
        "C": ["Campus", "District"],  # Campus level should include both Campus and District columns
        "D": ["District"],
        "R": ["Region"],
        "S": ["State"]
    }
    
    level_names = level_map.get(level)
    if not level_names:
        raise ValueError("Invalid level input. Must be one of 'C', 'D', 'R', 'S'.")
    
    processed_dict = {}
    
    for key, df in df_dict.items():
        # Skip processing for DataFrames whose key contains 'ref' or 'type' because they are different files 
        if 'ref' in key.lower() or 'type' in key.lower():
            processed_dict[key] = df.copy()
            continue
        
        df = df.copy()
        
        # Identify columns that match the specified level names
        matching_columns = [col for col in df.columns if any(name.lower() in col.lower() for name in level_names)]
        
        # Rename matching columns by appending '_id'
        for col in matching_columns:
            df.rename(columns={col: f"{col}_id"}, inplace=True)
        
        # Convert all columns except the identified level columns to numeric
        #id_columns = [f"{col}_id" for col in matching_columns]
        #id_columns.append("DISTNAME")
        for col in df.columns:
            if col not in [f"{col}_id" for col in matching_columns] and "DISTNAME" not in col.upper():
                df[col] = df[col].replace({'.': np.nan, '-1': np.nan, '-3': np.nan})  # Replace invalid values with NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert to numeric
            else:
                df[col] = df[col].astype(str)  # Ensure ID columns remain as strings
        
        processed_dict[key] = df
    
    return processed_dict

# Helper Function 3: Using column refrence files to rename encoded files 
def rename_columns_using_ref(rawdata, ref):
    """
    Renames columns in each DataFrame in rawdata using the corresponding mapping found in ref.
    If a filename contains 'ref' or 'type', it is copied unchanged.

    Args:
        rawdata (dict): Dictionary containing raw DataFrames with keys as filenames.
        ref (dict): Dictionary containing reference DataFrames with keys as filenames.

    Returns:
        dict: Dictionary containing renamed DataFrames.
    """
    
    updated_data = {}  # Dictionary to store updated DataFrames

    for raw_key, raw_df in rawdata.items():
        # Skip processing if key contains 'ref' or 'type'
        if 'ref' in raw_key.lower() or 'type' in raw_key.lower():
            updated_data[raw_key] = raw_df.copy()
            continue
        
        # Extract base name before the first underscore (_)
        base_name = raw_key.split("_")[0]
        
        # Find the matching key in REF (case-insensitive)
        matching_key = next((key for key in ref if key.lower().startswith(base_name.lower())), None)
        
        if matching_key:
            # Extract mapping from REF (second column = column ID, third column = actual column name)
            ref_df = ref[matching_key]
            column_mapping = dict(zip(ref_df.iloc[:, 0], ref_df.iloc[:, 1]))  # Map column ID → Actual name
            
            # Rename columns in RAWDATA DataFrame
            renamed_df = raw_df.rename(columns=column_mapping)
        else:
            # If no match is found, keep the DataFrame unchanged
            renamed_df = raw_df.copy()

        # Store in updated_data with the original key
        updated_data[raw_key] = renamed_df

    # Print confirmation
    print(f"Processed {len(updated_data)} DataFrames (Renamed: {len([k for k in updated_data if k not in rawdata or ('ref' not in k.lower() and 'type' not in k.lower())])}, Unchanged: {len([k for k in updated_data if 'ref' in k.lower() or 'type' in k.lower()])}).")

    return updated_data

# Helper Function 4: Using level refrence files to join on datasets. Understand what value level_id corresponds to 
def join_with_reference(df_dict, level):
    """
    Identifies the DataFrame with 'ref' in its key and left joins it with all other DataFrames 
    (except those containing '_type' in their key). The join is performed using {LEVEL} in the 
    reference DataFrame and f"{LEVEL}_id" in the other DataFrames.

    Ensures that the merged columns are converted to strings before merging.

    Args:
        df_dict (dict): Dictionary of pandas DataFrames.
        level (str): Level of granularity ('C', 'D', 'R', 'S') corresponding to Campus, District, Region, State.

    Returns:
        dict: Updated dictionary with joined data.
    """
    level_full_name = {
        "C": "CAMPUS",  
        "D": "DISTRICT",
        "R": "REGION",
        "S": "STATE"
    }[level]

    ref_df = None
    ref_key = None

    # Locate the reference DataFrame
    for key in df_dict.keys():
        if 'ref' in key.lower():
            ref_df = df_dict[key]
            ref_key = key
            break  # Only one reference DataFrame is assumed

    if ref_df is None:
        raise ValueError("No reference DataFrame found in the dictionary keys.")

    join_col_ref = level_full_name  # Column name in the reference DataFrame
    join_col_main = f"{level_full_name}_id"  # Column name in other DataFrames

    print(f"Joining on: ref[{join_col_ref}] with main[{join_col_main}]")

    # Convert the reference column to string
    ref_df[join_col_ref] = ref_df[join_col_ref].astype(str)

    updated_dict = {}

    for key, df in df_dict.items():
        if key == ref_key or '_type' in key.lower():  
            # Keep the reference and '_type' DataFrames unchanged
            updated_dict[key] = df
        elif join_col_main in df.columns:  
            # Convert the main DataFrame's join column to string before merging
            df[join_col_main] = df[join_col_main].astype(str)

            # Perform the left join
            updated_dict[key] = df.merge(ref_df, how='left', left_on=join_col_main, right_on=join_col_ref)
        else:
            # If no matching column, keep the DataFrame unchanged
            updated_dict[key] = df

    return updated_dict

# Helper Function 5: Merging multiple dataframes into 1 
def merge_data_frames(dfs, level):
    """
    Merges multiple pandas DataFrames stored in a dictionary, based on the given level.

    - Uses the first DataFrame as the base for left joins.
    - Drops shared columns (except for {level}_id) before merging.
    - Merges any '_type' file (like 'district_type') last.
    - Skips merging any DataFrame whose key contains "ref".
    - Returns the original dictionary with the final merged DataFrame stored under the key "merged".

    Parameters:
        dfs (dict): A dictionary where keys are dataset names and values are pandas DataFrames.
        level (str): One of 'C', 'D', or 'R' indicating Campus, District, or Region.

    Returns:
        dict: Updated dictionary with final merged DataFrame added under key "merged".
    """
    level_full_name = {
        "C": "CAMPUS",
        "D": "DISTRICT",
        "R": "REGION"
    }[level]

    id_col = f"{level_full_name}_id"

    shared_columns = [
        'DISTRICT', 'DISTNAME', 'COUNTY', 'CNTYNAME', 'REGION',
        'DFLCHART', 'DFLALTED', 'D_RATING', 'OUTCOME', 'ASVAB_STATUS',
        'asvab_status', 'DAD_POST', 'District Name'
    ]

    updated_dfs = {k: v.copy() for k, v in dfs.items()}
    merge_df = list(updated_dfs.values())[0]
    merged_keys = []

    # Separate merge keys
    all_keys = list(updated_dfs.keys())[1:]
    regular_keys = [k for k in all_keys if "ref" not in k.lower() and "district_type" not in k.lower()]
    type_key = next((k for k in all_keys if "district_type" in k.lower()), None)

    # Merge regular files first
    for key in regular_keys:
        df_to_be_merged = updated_dfs[key].drop(columns=shared_columns, errors='ignore')
        print(f"\nMerging {key}:")
        print(f"  - Shape of merge_df before merge: {merge_df.shape}")
        print(f"  - Shape of df_to_be_merged: {df_to_be_merged.shape}")

        merge_df = merge_df.merge(df_to_be_merged, on=id_col, how="left")
        print(f"  - Merged with LEFT join on '{id_col}'. New shape: {merge_df.shape}")
        merged_keys.append(key)

    # Merge the _type file last (only for District level)
    if type_key and level == "D":
        df_to_be_merged = updated_dfs[type_key].drop(columns=shared_columns, errors='ignore')
        print(f"\nMerging {type_key} (merged last):")
        print(f"  - Shape of merge_df before merge: {merge_df.shape}")
        print(f"  - Shape of df_to_be_merged: {df_to_be_merged.shape}")

        merge_df[id_col] = merge_df[id_col].astype(str).str.replace(r"[^\d]", "", regex=True).astype(int)
        df_to_be_merged["District Number"] = df_to_be_merged["District Number"].astype(int)
        merge_df = merge_df.merge(df_to_be_merged, left_on=id_col, right_on="District Number", how="left")
        print(f"  - Merged with LEFT join on '{id_col}' and 'District Number'. New shape: {merge_df.shape}")
        merged_keys.append(type_key)

    # Store final result
    if merged_keys:
        updated_dfs["merged"] = merge_df
    else:
        print("No merges were performed.")

    return updated_dfs


# Helper Function 6: Combining the previous 5 functions in 1 to fully process the data in python environment 
def processing(directory, year, level):
    """
    Processes raw data by loading, cleaning, renaming columns, and joining level refrence.

    Args:
        directory (str): Path to the directory containing the data.
        year (int): Year of the data to be processed.
        level (str): Cleaning level or category for data processing.

    Returns:
        DataFrame: The cleaned and processed data with renamed columns.
    """
    rawdata, ref = load_data(directory, year)
    cleaned_data = primary_data_cleaning(rawdata, level)
    column_data = rename_columns_using_ref(cleaned_data, ref)
    if level != 'S':
        ref_data = join_with_reference(column_data, level)
        final_data = merge_data_frames(ref_data, level)
        return final_data
    else:
        return column_data

# Master Function: Process data and store it into a specified directory. 
def process_and_save_all_data(base_directory, level):
    """
    Loops through all Data{year} folders, processes the data, and saves the output
    as multiple Excel files in the corresponding clean_data folder within each level.
    
    Parameters:
    base_directory (str): Path to the folder containing Data{year} folders.
    level (str): Level parameter required for data processing.
    """
    # Get the full level name 
    valid_levels = {
        'C': 'Campus',
        'D': 'District',
        'R': 'Region',
        'S': 'State'
    }

    # Get all folder names and extract years
    year_folders = [f for f in os.listdir(base_directory) if f.startswith('Data')]
    years = sorted([int(f.replace('Data', '')) for f in year_folders if f.replace('Data', '').isdigit() and int(f.replace('Data', '')) >= 2020])
    
    for year in years:
        data_year_folder = os.path.join(base_directory, f'Data{year}')
        raw_data_folder = os.path.join(data_year_folder, f'{valid_levels[level]}', 'raw_data')
        clean_data_folder = os.path.join(data_year_folder, f'{valid_levels[level]}', 'clean_data')
        os.makedirs(clean_data_folder, exist_ok=True)
        
        if os.path.exists(raw_data_folder):
            # Check if all output files already exist before processing
            processed_data_needed = False
            
            for file_name in os.listdir(raw_data_folder):
                clean_file_name = f"{os.path.splitext(file_name)[0]}_clean.csv"
                output_file = os.path.join(clean_data_folder, clean_file_name)
                if not os.path.exists(output_file):
                    processed_data_needed = True
                    break
            
            if not processed_data_needed:
                print(f"Skipping processing for year {year} at level {level} as all files already exist.")
                continue
            
            print(f"Processing data for year {year} at level {level}...")
            
            # Run the processing function, which returns a dictionary of DataFrames
            processed_data = processing(raw_data_folder, year, level)
            
            # Save each DataFrame in the dictionary as a separate Excel file
            for file_name, df in processed_data.items():
                clean_file_name = f"{file_name}_clean.csv"
                output_file = os.path.join(clean_data_folder, clean_file_name)
                
                if os.path.exists(output_file):
                    print(f"Skipping {clean_file_name} as it already exists.")
                else:
                    df.to_csv(output_file, index=False)
                    print(f"Saved cleaned data for {year}, level {level}: {clean_file_name}")
        else:
            print(f"Warning: Raw data folder for {year} at level {level} does not exist, skipping...")

