import os 
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import seaborn as sns
from sklearn.manifold import MDS
from scipy.cluster.hierarchy import linkage, dendrogram
import geopandas as gpd
import textwrap
from matplotlib.patches import ConnectionPatch
from scipy.spatial import Voronoi
from utils.Demographic_Buckets import demographic_buckets
from utils.Demographic_Buckets import get_labels_from_variable_name_dict
from utils.Demographic_Buckets import get_combined_values
#from getData import load_data_from_year_folder


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

def preprocess_data(df, feature_columns, impute_strategy="median", standardize=True):
    """
    Handles missing values and optionally standardizes selected feature columns.

    Parameters:
        df (pd.DataFrame): The input dataset.
        feature_columns (list): List of columns to be used for KNN.
        impute_strategy (str): Strategy to fill missing values ('mean', 'median', etc.).
        standardize (bool): Whether to scale the features using StandardScaler.

    Returns:
        pd.DataFrame: Preprocessed DataFrame containing 'DISTRICT_id' and transformed feature columns.
    """
    df_copy = df[["DISTRICT_id", "DISTNAME"] + feature_columns].copy()

    # Impute missing values
    imputer = SimpleImputer(strategy=impute_strategy)
    df_copy[feature_columns] = imputer.fit_transform(df_copy[feature_columns])

    # Standardize features if required
    if standardize:
        scaler = StandardScaler()
        df_copy[feature_columns] = scaler.fit_transform(df_copy[feature_columns])

    return df_copy

def knn_distance(df, district_id, feature_columns, n_neighbors=5, metric="euclidean", impute_strategy="median"):
    """
    Finds nearest neighbors using Euclidean, Manhattan, or Mahalanobis distance.

    Parameters:
        df (pd.DataFrame): Dataset containing school district data.
        district_id (int or str): District ID to find neighbors for.
        feature_columns (list): Features to use for similarity.
        n_neighbors (int): Number of neighbors to return.
        metric (str): 'euclidean', 'manhattan', or 'mahalanobis'.
        impute_strategy (str): Strategy to impute missing values.

    Returns:
        list: List of DISTRICT_id values of nearest neighbors.
    """
    knn_df = preprocess_data(df, feature_columns, impute_strategy, standardize=True)

    if metric == "mahalanobis":
        # Compute inverse covariance matrix for Mahalanobis distance
        cov_matrix = np.cov(knn_df[feature_columns].values, rowvar=False)
        try:
            inv_cov = np.linalg.inv(cov_matrix)
        except np.linalg.LinAlgError:
            raise ValueError("Covariance matrix is singular; Mahalanobis distance cannot be used.")
        knn_model = NearestNeighbors(n_neighbors=n_neighbors, metric="mahalanobis", metric_params={"VI": inv_cov})
    else:
        knn_model = NearestNeighbors(n_neighbors=n_neighbors, metric=metric)
    print(knn_df["DISTRICT_id"])
    # Fit the model and get nearest neighbors
    knn_model.fit(knn_df[feature_columns])
    query_point = knn_df[knn_df["DISTRICT_id"] == int(district_id)][feature_columns]

    if query_point.empty:
        raise ValueError(f"District ID {district_id} not found in dataset.")

    distances, indices = knn_model.kneighbors(query_point)
    #return indices
    return knn_df.iloc[indices[0]][["DISTRICT_id", "DISTNAME"]]



def knn_cosine(df, district_id, feature_columns, n_neighbors=5, impute_strategy="median"):
    """
    Finds nearest neighbors using Cosine similarity (does not standardize).

    Parameters:
        df (pd.DataFrame): Dataset containing school district data.
        district_id (int or str): District ID to find neighbors for.
        feature_columns (list): Features to use for similarity.
        n_neighbors (int): Number of neighbors to return.
        impute_strategy (str): Strategy to impute missing values.

    Returns:
        list: List of DISTRICT_id values of nearest neighbors.
    """
    knn_df = preprocess_data(df, feature_columns, impute_strategy, standardize=False)
    knn_model = NearestNeighbors(n_neighbors=n_neighbors, metric="cosine")
    knn_model.fit(knn_df[feature_columns])
    query_point = knn_df[knn_df["DISTRICT_id"] == district_id][feature_columns]

    if query_point.empty:
        raise ValueError(f"District ID {district_id} not found in dataset.")

    distances, indices = knn_model.kneighbors(query_point)
    return knn_df.iloc[indices[0]][["DISTRICT_id", "DISTNAME"]]

def knn_canberra(df, district_id, feature_columns, n_neighbors=5, impute_strategy="median"):
    """
    Finds nearest neighbors using Canberra distance (requires non-negative raw values).

    Parameters:
        df (pd.DataFrame): Dataset containing school district data.
        district_id (int or str): District ID to find neighbors for.
        feature_columns (list): Features to use for similarity.
        n_neighbors (int): Number of neighbors to return.
        impute_strategy (str): Strategy to impute missing values.

    Returns:
        list: List of DISTRICT_id values of nearest neighbors.
    """
    knn_df = preprocess_data(df, feature_columns, impute_strategy, standardize=False)

    # Check for non-negativity
    if (knn_df[feature_columns] < 0).any().any():
        raise ValueError("Canberra distance cannot be used with negative values.")

    knn_model = NearestNeighbors(n_neighbors=n_neighbors, metric="canberra")
    knn_model.fit(knn_df[feature_columns])
    query_point = knn_df[knn_df["DISTRICT_id"] == district_id][feature_columns]

    if query_point.empty:
        raise ValueError(f"District ID {district_id} not found in dataset.")

    distances, indices = knn_model.kneighbors(query_point)
    return knn_df.iloc[indices[0]][["DISTRICT_id", "DISTNAME"]]



from utils.getData import load_data_from_github
from utils.Demographic_Buckets import demographic_buckets
from utils.Demographic_Buckets import get_labels_from_variable_name_dict
from utils.Demographic_Buckets import get_combined_values


def find_nearest_districts(year, district_id, feature_columns, n_neighbors=5, distance_metric="euclidean", impute_strategy="median"):
    """
    Wrapper function that selects the appropriate distance metric for finding nearest neighbors.

    Parameters:
        year int: Int representing the year you want for data
        district_id (int or str): District ID to find neighbors for.
        feature_columns (list): Feature Buckets user would like to use for similarity.
        n_neighbors (int): Number of neighbors to return.
        distance_metric (str): Distance metric to use ('euclidean', 'manhattan', 'mahalanobis', 'cosine', 'canberra').
        impute_strategy (str): Strategy to impute missing values.

    Returns:
        pd.DataFrame: Dataframe containing the neighbors DISTRICT_id and DISTNAME. The first term in the df is the target district 
    """
    metric = distance_metric.lower()

    df, key = load_data_from_github(year)
    demographic_buckets_year = get_labels_from_variable_name_dict(demographic_buckets, key)
    all_selected_features = get_combined_values(demographic_buckets_year, feature_columns)


    if metric in ["euclidean", "manhattan", "mahalanobis"]:
        return df, demographic_buckets_year, knn_distance(df, district_id, all_selected_features, n_neighbors, metric, impute_strategy)
    elif metric == "cosine":
        return df, demographic_buckets_year, knn_cosine(df, district_id, all_selected_features, n_neighbors, impute_strategy)
    elif metric == "canberra":
        return df, demographic_buckets_year, knn_canberra(df, district_id, all_selected_features, n_neighbors, impute_strategy)
    else:
        raise ValueError(f"Unsupported distance metric: {distance_metric}")


district_identifiers = [
    "DISTRICT_id",
    "TEA District Type",
    "TEA Description",
    "NCES District Type",
    "NCES Description",
    "Charter School (Y/N)", 
    "COUNTY",
    "REGION",
    "DISTRICT",
    "DISTNAME",
    "CNTYNAME",
    "DFLCHART",
    "DFLALTED",
    "ASVAB_STATUS"
]

def get_neighbor_data(df, feature_columns, neighbors):
    """
    Subsets the given dataframe to only include rows matching the district IDs in neighbors,
    and selects the specified feature columns along with the district identifier columns.

    Parameters:
    - df (pd.DataFrame): Original dataframe with district and feature data.
    - feature_columns (list): List of feature column names to include.
    - neighbors (pd.DataFrame): DataFrame with 'DISTRICT_id' and 'DISTNAME' columns.

    Returns:
    - pd.DataFrame: Filtered dataframe with neighbor districts and desired features.
    """    
    # Ensure district identifiers are included in the column selection
    selected_columns = district_identifiers + feature_columns

    # Subset df to only include rows that match neighbors' DISTRICT_id
    df_subset = df[selected_columns]
    result = df_subset[df_subset['DISTRICT_id'].isin(neighbors['DISTRICT_id'])]

    # Optional: Merge to bring over other neighbor metadata if neighbors has more info
    result = result.merge(neighbors, on='DISTRICT_id', how='left')

    return result
