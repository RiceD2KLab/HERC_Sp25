from KNN_Diagnostic_Plots import plot_texas_districts, plot_race_ethnicity_stacked_bar, plot_class_size_k6_bar, plot_special_ed_504_bar

from KNN_Model import find_nearest_districts

import pandas as pd

def compare_neighbors_plotter(metrics, features, plot_func, df):
    models = {}
    for distance_metric in metrics: 
        knn_model = find_nearest_districts(df, 101912, features, 5, distance_metric, "median")
        models[distance_metric] = knn_model
    concat_neighbors = pd.concat(models.values()).drop_duplicates()
    plot_func(concat_neighbors, df)
    return concat_neighbors