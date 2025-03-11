
from sklearn.manifold import TSNE
import plotly.express as px
import re
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def visualize_tnse(year, data_dict, components = 2, selected_columns = None, y_var = 'TEA Description'):
    """
    Runs t-SNE based on two specified columns, to visualize the relationship between the two. 

    Inputs:
    - year: a 4 digit integer representing a year, YYYY, such as 2020
    - components: the number of components you want t-SNE to use. Default is 2
    - data_dict: a dictionary with key-value pairs where the key is a year, and the value is a DISTPROF dataset as a dataframe
    - column1: a string representing the first demographic you want plotted
    - column2: a string representing the second demographic you want plotted
    - y_var: a string or a Pandas series representing a column that you want to classify the data with. Default is TEA Description. 
             If a series, must have the same rows as the data_dict[year]
    """
    data = data_dict[year].dropna()
    if y_var == 'TEA Description' or y_var == 'NCES Description':
        if selected_columns != None:
            X = data[selected_columns]
            y = data[y_var]
        else:
            X = data.drop(['District Number', 'District', 'TEA Description', 'NCES Description'], axis = 1)
            y = data[y_var]

    if y_var in data.columns:
        if selected_columns != None:
            X = data[selected_columns].drop(y_var, axis=1)
            y = data[y_var]

        else:
            X = data.drop(['District Number', 'District', 'TEA Description', 'NCES Description', y_var], axis = 1)
            y = data[y_var]

    else: 
        if selected_columns != None:
            X = data[selected_columns]
            y = y_var
        else:
            X = data.drop(['District Number', 'District', 'TEA Description', 'NCES Description'], axis = 1)
            y = y_var

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

def visualize_pca(year, data_dict, components = 2, selected_columns = None, y_var = 'TEA Description'):
    data = data_dict[year].dropna()

    if y_var == 'TEA Description' or y_var == 'NCES Description':
        if selected_columns != None:
            X = data[selected_columns]
            y = data[y_var]
        else:
            X = data.drop(['District Number', 'District', 'TEA Description', 'NCES Description'], axis = 1)
            y = data[y_var]

    if y_var in data.columns:
        if selected_columns != None:
            X = data[selected_columns].drop(y_var, axis=1)
            y = data[y_var]

        else:
            X = data.drop(['District Number', 'District', 'TEA Description', 'NCES Description', y_var], axis = 1)
            y = data[y_var]

    else: 
        if selected_columns != None:
            X = data[selected_columns]
            y = y_var
        else:
            X = data.drop(['District Number', 'District', 'TEA Description', 'NCES Description'], axis = 1)
            y = y_var

    label = re.sub(f"District {year} ", "", y_var)

    scaled_data = pd.DataFrame(StandardScaler() .fit_transform(X)) #scaling the data
    pca = PCA(n_components=components)
    transformed_data = pca.fit_transform(scaled_data)

    # Plotting the transformed data
    sns.scatterplot(x = transformed_data[:, 0], y = transformed_data[:, 1], hue = y)
    plt.title('PCA of High-Dimensional Data')
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.show()