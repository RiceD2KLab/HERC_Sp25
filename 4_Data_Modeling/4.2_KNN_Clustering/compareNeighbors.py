import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from KNN_Model import find_nearest_districts

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


def compareMetrics(district_id, df, k=5, distance_metrics = ['euclidean', 'manhattan', 'mahalanobis', 'cosine', 'canberra'], selected_features = race_ethnicity_percent +  student_teacher_ratio + special_ed_504):
    results = {}
    for i in range(len(distance_metrics)): 
        knn_model = find_nearest_districts(df, district_id, selected_features, k, distance_metrics[i], "median")
        knn_model['metric'] = f"Method {i+1}"
        results[distance_metrics[i]] = knn_model
    return pd.concat(results.values())

def comparePlotter(district_id, plot_func, df, k=5, distance_metrics = ['euclidean', 'manhattan', 'mahalanobis', 'cosine', 'canberra'], selected_features = race_ethnicity_percent +  student_teacher_ratio + special_ed_504):
    """
    Function that plots a given function of all neighbors identified for an input school district based on 'euclidean', 'manhattan', 'mahalanobis', 'cosine', 'canberra' distances
    and race_ethnicity_percent +  student_teacher_ratio + special_ed_504 buckets. 
    """
    concat_neighbors = compareMetrics(district_id, df, k, distance_metrics, selected_features)
    plot_func(concat_neighbors, df)
    return concat_neighbors

import seaborn as sns
import matplotlib.pyplot as plt

def title_case_with_spaces(s):
    """
    Converts a string to title case (replacing underscores with spaces) 
    and ensures that if it ends with 'isd', that ending is in uppercase ('ISD').
    """
    s = s.replace("_", " ").title()
    if len(s) >= 3 and s[-3:].lower() == "isd":
        s = s[:-3] + "ISD"
    return s


def plot_demographic_feature_presence2(demographic_feature, target_district_id):
    """
    Visualizes the presence of a demographic feature across different methods using a heatmap.
    
    The input DataFrame 'demographic_feature' must contain the following columns:
      - DISTRICT_id
      - DISTNAME
      - metric
      
    The heatmap displays:
      - x-axis: School District (DISTNAME), with the district corresponding to target_district_id 
                as the first column and its label bolded.
      - y-axis: Method (metric).
      
    Parameters:
    -----------
    demographic_feature : pd.DataFrame
        DataFrame with columns 'DISTRICT_id', 'DISTNAME', and 'metric'.
    target_district_id : int or str
        The district ID for the target district. Its corresponding district name will be placed
        as the first column in the heatmap and highlighted.
        
    Returns:
    --------
    matrix_T : pd.DataFrame
        The transposed presence matrix used for the visualization.
    """
    # Ensure district names are in title case for consistency
    demographic_feature['DISTNAME'] = demographic_feature['DISTNAME'].apply(title_case_with_spaces)
    
    # Identify the target district name using the provided target_district_id
    try:
        target_district = demographic_feature.loc[
            demographic_feature['DISTRICT_id'] == target_district_id, 'DISTNAME'
        ].iloc[0]
    except IndexError:
        raise ValueError(f"Target district id {target_district_id} not found in the demographic feature DataFrame.")
    
    # Build the presence matrix:
    # - Drop duplicate rows
    # - Assign a value of 1 to each occurrence
    # - Pivot the table so that rows are district names and columns are the methods (metric)
    presence_matrix = (
        demographic_feature.drop_duplicates()
                         .assign(value=1)
                         .pivot_table(index="DISTNAME", columns="metric", values="value", fill_value=0)
    )
    
    # Transpose so that methods are on the y-axis and districts on the x-axis
    matrix_T = presence_matrix.T

    # Reorder the columns so that the target district is first (if present)
    if target_district in matrix_T.columns:
        cols = list(matrix_T.columns)
        cols.remove(target_district)
        new_cols = [target_district] + cols
        matrix_T = matrix_T[new_cols]
    
    # Dynamically adjust figure width based on the number of districts
    n_districts = matrix_T.shape[1]
    fig_width = max(10, n_districts * 0.6)
    
    sns.set(style="whitegrid", font_scale=1.1)
    plt.figure(figsize=(fig_width, 5))
    ax = sns.heatmap(
        matrix_T,
        cmap=sns.color_palette(["#f0f0f0", "#1f77b4"]),
        linewidths=0.7,
        linecolor="white",
        cbar=False,
        square=False
    )
    
    # Formatting the plot
    ax.set_title("Neighbor Identification Across Methods", fontsize=14, pad=15)
    ax.set_xlabel("School District", fontsize=12)
    ax.set_ylabel("Method", fontsize=12)
    
    # Rotate x-axis and y-axis tick labels for clarity
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=10)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=11)
    
    # Bold the target district label on the x-axis for emphasis
    for label in ax.get_xticklabels():
        if target_district in label.get_text():
            label.set_fontweight("bold")
    
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.show()
    
    return matrix_T


