import os 
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
#from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import NearestNeighbors
import seaborn as sns
from sklearn.manifold import MDS
from scipy.cluster.hierarchy import linkage, dendrogram
import geopandas as gpd


def calculate_missing_percentage(df):
    """
    Function to calculate the percentage of missing values in each column of a given dataset.
    
    Parameters:
        df (pd.DataFrame): The dataset as a pandas DataFrame.
    
    Returns:
        pd.Series: A Series with column names as index and percentage of missing values as values.
    """
    missing_percentage = (df.isna().sum() / len(df)) * 100
    missing_percentage = missing_percentage[missing_percentage > 0]  # Only keep columns with missing values
    
    return missing_percentage.sort_values(ascending=False)  # Sort in descending order


def drop_columns(df, threshold=50):
    """
    Function to drop columns with missing values exceeding a specified threshold
    and columns containing 'numerator' or 'denominator' in their names. These columsn are going to be fairly useless for analysis 
    
    Parameters:
        df (pd.DataFrame): The dataset as a pandas DataFrame.
        threshold (float): The percentage threshold for dropping columns.
    
    Returns:
        pd.DataFrame: The dataframe with columns dropped.
    """
    print(f"Original Dataset Shape: {df.shape}")
    missing_percentage = calculate_missing_percentage(df)
    cols_to_drop = set(missing_percentage[missing_percentage >= threshold].index)
    
    # Drop columns containing 'numerator' or 'denominator' (case-insensitive)
    cols_to_drop.update([col for col in df.columns if 'numerator' in col.lower() or 'denominator' in col.lower()])
    
    resulting_df = df.drop(columns=cols_to_drop)

    print(f"Dropped Dataset Shape: {resulting_df.shape}")
    return resulting_df

def find_nearest_districts(df, district_id, feature_buckets, n_neighbors=5, impute_strategy="median"):
    """
    Finds the nearest neighboring districts using K-Nearest Neighbors (KNN) based on selected demographic features.

    Parameters:
        df (pd.DataFrame): The dataset containing school district data.
        district_id (int or str): The ID of the district for which to find similar districts.
        feature_buckets (list): List of feature columns to be used for similarity comparison.
        n_neighbors (int, optional): Number of nearest neighbors to find (default is 5).
        impute_strategy (str, optional): Strategy for handling missing values, options include 
                                         'mean', 'median', 'most_frequent', or 'constant' (default is "median").

    Returns:
        list: A list of district IDs corresponding to the nearest neighboring districts.

    Raises:
        ValueError: If the specified district_id is not found in the dataset.

    Process:
        1. Filters the dataset to include only the relevant feature columns.
        2. Handles missing values in the selected feature columns using the specified imputation strategy.
        3. Standardizes (normalizes) the feature values to ensure consistent distance calculations.
        4. Fits a K-Nearest Neighbors (KNN) model using Euclidean distance as the similarity metric.
        5. Identifies the closest districts to the specified district_id based on the trained KNN model.
        6. Returns the list of nearest district IDs.

    Example Usage:
        ```python
        nearest_districts = find_nearest_districts(df, district_id=1023, 
                                                   feature_buckets=["Student_Teacher_Ratio", "Econ_Disadv_Percent"],
                                                   n_neighbors=5, impute_strategy="mean")
        print(nearest_districts)
        ```
    """
    # Step 1: Filter dataset for selected features
    existing_columns = [col for col in feature_buckets if col in df.columns]
    
    # Select only available columns
    knn_df = df[["DISTRICT_id"] + existing_columns].copy()
    
    # Step 2: Handle missing values
    imputer = SimpleImputer(strategy=impute_strategy)
    knn_df[existing_columns] = imputer.fit_transform(knn_df[existing_columns])
    
    # Step 3: Normalize the feature set
    scaler = StandardScaler()
    knn_df[existing_columns] = scaler.fit_transform(knn_df[existing_columns])
    
    # Step 4: Fit KNN model (excluding DISTRICT_id)
    knn_model = NearestNeighbors(n_neighbors=n_neighbors, metric="euclidean")
    knn_model.fit(knn_df[existing_columns])
    
    # Step 5: Find the nearest neighbors for the specified district
    query_point = knn_df[knn_df["DISTRICT_id"] == district_id][existing_columns]
    if query_point.empty:
        raise ValueError(f"District ID {district_id} not found in dataset.")
    
    distances, indices = knn_model.kneighbors(query_point)
    
    # Step 6: Get the closest districts
    nearest_districts = knn_df.iloc[indices[0]]["DISTRICT_id"].tolist()

    return nearest_districts


