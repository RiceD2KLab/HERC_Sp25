import pandas as pd

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