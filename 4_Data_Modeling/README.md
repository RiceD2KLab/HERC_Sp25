# Data Modeling README

## 4.1_Clustering_EDA

### clusteringEDA
The functions in this file prepare the combined datasets found in 0_Datasets/1.7Master_Files/Individual Year Files for clustering by selecting the columns specified to us by our sponsor, removing charter schools for reasonable comparison, and joining with the District Type data found in directories 0_Datasets/1.1 to 1.6. 

Finally, this notebook includes a function to run t-SNE on this filtered dataset. t-SNE is used to visualize the dataset in lower dimensions and identify potential patterns to look for when comparing clustering models.

### tSNE_Visualization
This notebook provides example usage of the functions found in clusteringEDA.
