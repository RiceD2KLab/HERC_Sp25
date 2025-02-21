#Importing necessary packages
import pandas as pd
import os 
import numpy as np
import warnings
import re
warnings.simplefilter("ignore")

def load_data(directory, year):
    """
    Reads all CSV files in the specified directory into a dictionary (RAWDATA) 
    and loads all sheets from an Excel file into another dictionary (REF).

    
    
    Args:
        directory (str): The path to the directory containing the raw data files.
        year (int or str): The year to append to dictionary keys.
    
    Returns:
        tuple: (RAWDATA, REF)
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


def primary_data_cleaning(df_dict, level):
    """
    Converts all columns in each DataFrame (except the one containing the specified level) to numeric.
    Replaces '.', '-1', and '-3' values with NaN.
    Drops columns containing 'rate' or 'percent' in their name if any values exceed 100,
    except for DataFrames with 'ref' in their title.
    
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
        id_columns = [f"{col}_id" for col in matching_columns]
        for col in df.columns:
            if col not in id_columns:
                df[col] = df[col].replace({'.': np.nan, '-1': np.nan, '-3': np.nan})  # Replace invalid values with NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert to numeric
            else:
                df[col] = df[col].astype(str)  # Ensure ID columns remain as strings
        
        processed_dict[key] = df
    
    return processed_dict



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
            column_mapping = dict(zip(ref_df.iloc[:, 1], ref_df.iloc[:, 2]))  # Map column ID → Actual name
            
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


def processing(directory, year, level):
    """
    Processes raw data by loading, cleaning, and renaming columns.

    Args:
        directory (str): Path to the directory containing the data.
        year (int): Year of the data to be processed.
        level (str): Cleaning level or category for data processing.

    Returns:
        DataFrame: The cleaned and processed data with renamed columns.
    """
    rawdata, ref = load_data(directory, year)
    cleaned_data = primary_data_cleaning(rawdata, level)
    final_data = rename_columns_using_ref(cleaned_data, ref)
    return final_data


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
    years = sorted([int(f.replace('Data', '')) for f in year_folders if f.replace('Data', '').isdigit()])
    
    for year in years:
        data_year_folder = os.path.join(base_directory, f'Data{year}')
        raw_data_folder = os.path.join(data_year_folder, f'{valid_levels[level]}', 'raw_data')
        clean_data_folder = os.path.join(data_year_folder, f'{valid_levels[level]}', 'clean_data')
        os.makedirs(clean_data_folder, exist_ok=True)
        
        if os.path.exists(raw_data_folder):
            print(f"Processing data for year {year} at level {level}...")
            
            # Run the processing function, which returns a dictionary of DataFrames
            processed_data = processing(raw_data_folder, year, level)
            
            # Save each DataFrame in the dictionary as a separate Excel file
            for file_name, df in processed_data.items():
                clean_file_name = f"{file_name}_clean.xlsx"
                output_file = os.path.join(clean_data_folder, clean_file_name)
                df.to_excel(output_file, index=False)
                print(f"Saved cleaned data for {year}, level {level}: {clean_file_name}")
        else:
            print(f"Warning: Raw data folder for {year} at level {level} does not exist, skipping...")


