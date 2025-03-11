# Data Modeling README

## 4.1_Clustering_EDA

### clusterData
The functions in this file prepare the combined datasets found in 0_Datasets/1.7Master_Files/Individual Year Files_Take2 for clustering by selecting the columns specified to us by our sponsor, removing charter schools for reasonable comparison. 

### visualizeClusters
Two functions to assist in visualizing the results of clustering algorithms through t-SNE and PCA. The functions allow a user to input a custom y-variable of their choice, such as the results of an unsupervised clustering algorithm to group school districts. 

### Clustering_Visualization
A notebook demonstrating how to use the clusterData and visualizeClusters modules with basic visualizations using t-SNE and PCA. 
