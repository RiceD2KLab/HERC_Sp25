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

def plot_texas_districts(district_ids, df):
    """
    Plots selected school districts on a Texas map based on district IDs, with intelligent
    label placement to prevent overlap regardless of location density.
    
    Parameters:
    - district_ids (list): List of district IDs to plot. The first district is the main focus.
    - df (pd.DataFrame): DataFrame containing 'DISTRICT_id', 'DISTNAME', and 'CNTYNAME' columns.
    
    Returns:
    - A map plot of Texas highlighting the selected school districts with smart non-overlapping labels.
    """
    
    if not district_ids:
        print("No district IDs provided.")
        return

    # Step 1: Filter the DataFrame to get district info
    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][["DISTRICT_id", "DISTNAME", "CNTYNAME"]]
    
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return
        
    # Get the main district name (first in the list)
    main_district_info = df[df['DISTRICT_id'] == district_ids[0]]
    if main_district_info.empty:
        main_district_name = "Unknown District"
    else:
        main_district_name = main_district_info.iloc[0]["DISTNAME"]

    # Step 2: Load Texas counties shapefile
    shapefile_url = "https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_county_20m.zip"
    texas_counties = gpd.read_file(shapefile_url)

    # Step 3: Filter for Texas counties only (STATEFP = '48' for Texas)
    texas_counties = texas_counties[texas_counties["STATEFP"] == "48"]

    # Step 4: Extract county names from selected districts
    county_to_districts = selected_districts.groupby("CNTYNAME")["DISTNAME"].apply(list).to_dict()

    # Step 5: Select only the target counties from the full Texas dataset
    selected_counties = texas_counties[texas_counties["NAME"].str.upper().isin(county_to_districts.keys())]

    # Step 6: Plot the Texas map
    fig, ax = plt.subplots(figsize=(12, 10))
    texas_counties.plot(ax=ax, color="lightgray", edgecolor="black", linewidth=0.5)  # All counties

    # Highlight the counties - main district's county in blue, others in red
    main_county = df[df['DISTRICT_id'] == district_ids[0]]["CNTYNAME"].iloc[0]
    
    for county_name, district_list in county_to_districts.items():
        county = selected_counties[selected_counties["NAME"].str.upper() == county_name]
        if not county.empty:
            color = "blue" if county_name == main_county else "red"
            county.plot(ax=ax, color=color, edgecolor="black", linewidth=1, alpha=0.7)

    # Step 7: Smart label placement system
    county_centroids = {}  # Store county centroids
    all_district_data = []  # Store all district data for processing
    
    # First, collect all county centroids and district information
    for row in selected_counties.itertuples():
        county_name = row.NAME.upper()
        if county_name in county_to_districts:
            centroid = row.geometry.centroid
            county_centroids[county_name] = (centroid.x, centroid.y)
            
            districts = county_to_districts[county_name]
            for district_name in districts:
                is_main = district_name == main_district_name
                all_district_data.append({
                    'county': county_name,
                    'district': district_name,
                    'centroid_x': centroid.x,
                    'centroid_y': centroid.y,
                    'is_main': is_main
                })
    
    # Convert to DataFrame for easier manipulation
    district_df = pd.DataFrame(all_district_data)
    
    # Analyze spatial density of county centroids
    if len(county_centroids) >= 3:  # Need at least 3 points for Voronoi
        points = np.array(list(county_centroids.values()))
        
        # Try to use Voronoi to analyze spatial relationships
        try:
            vor = Voronoi(points)
            # Calculate the average distance between neighboring points
            distances = []
            for i in range(len(points)):
                for j in range(i+1, len(points)):
                    dist = np.sqrt(np.sum((points[i] - points[j])**2))
                    distances.append(dist)
            
            if distances:
                avg_distance = np.mean(distances)
                density_factor = 1.0 / (avg_distance + 1e-10)  # Avoid division by zero
            else:
                density_factor = 1.0
        except:
            # Fallback if Voronoi fails
            density_factor = 1.0
    else:
        density_factor = 1.0
    
    # Adaptive spacing based on point density
    base_spacing = 2.0
    county_districts_count = district_df.groupby('county').size()
    
    # Calculate the number of districts per county and identify crowded counties
    crowded_counties = county_districts_count[county_districts_count > 1].index.tolist()
    
    # Function to intelligently place labels with adaptive spacing
    def get_label_position(row, all_positions, attempt=0, max_attempts=10):
        """Intelligently determine label position using adaptive spacing based on spatial density."""
        x, y = row['centroid_x'], row['centroid_y']
        county = row['county']
        
        # Adjust spacing based on:
        # 1. If county is crowded (has multiple districts)
        # 2. General spatial density of all counties
        # 3. Number of placement attempts so far
        
        is_crowded = county in crowded_counties
        crowd_factor = 1.5 if is_crowded else 1.0
        attempt_factor = 1.0 + (attempt * 0.2)  # Increase radius with each attempt
        
        # Adaptive radius calculation
        radius = base_spacing * density_factor * crowd_factor * attempt_factor
        
        # Strategic angle calculation - spread points apart
        angle_base = (hash(row['district']) % 36) * 10  # Pseudorandom starting angle based on district name
        angle_offset = attempt * 30  # Rotate by 30 degrees with each attempt
        angle = (angle_base + angle_offset) % 360
        angle_rad = np.radians(angle)
        
        # Calculate position
        label_x = x + radius * np.cos(angle_rad)
        label_y = y + radius * np.sin(angle_rad)
        
        # Check for conflicts with existing positions
        min_distance = 0.8  # Minimum allowed distance between labels
        conflict = False
        
        for pos in all_positions:
            dist = np.sqrt((label_x - pos[0])**2 + (label_y - pos[1])**2)
            if dist < min_distance:
                conflict = True
                break
        
        if conflict and attempt < max_attempts:
            # Try again with different parameters
            return get_label_position(row, all_positions, attempt + 1, max_attempts)
        
        return (label_x, label_y)
    
    # Sort by importance (main district first) and then by county name
    district_df = district_df.sort_values(by=['is_main', 'county'], ascending=[False, True])
    
    # Place labels one by one, avoiding conflicts
    label_positions = {}
    used_positions = []
    
    for _, row in district_df.iterrows():
        district_name = row['district']
        label_pos = get_label_position(row, used_positions)
        label_positions[district_name] = label_pos
        used_positions.append(label_pos)
        
        # Draw connection line
        centroid_x, centroid_y = row['centroid_x'], row['centroid_y']
        label_x, label_y = label_pos
        
        # Use curved lines for cleaner appearance
        conn_style = '-' if row['is_main'] else ':'
        conn_width = 1.0 if row['is_main'] else 0.7
        
        # Draw the line - use ConnectionPatch for better appearance
        conn = ConnectionPatch(
            (centroid_x, centroid_y), (label_x, label_y),
            "data", "data", 
            arrowstyle="-", 
            linestyle=conn_style,
            linewidth=conn_width,
            color="black"
        )
        ax.add_artist(conn)
        
        # Draw the label with appropriate styling
        is_main = row['is_main']
        text_color = "blue" if is_main else "black"
        
        plt.text(
            label_x, label_y, district_name, 
            fontsize=9, 
            ha='center', va='center',
            color=text_color, 
            weight='bold' if is_main else 'normal',
            bbox=dict(
                facecolor='white', 
                alpha=0.9, 
                edgecolor='black', 
                boxstyle='round,pad=0.3',
                linewidth=1.5 if is_main else 0.8
            )
        )
    
    # Step 8: Formatting and display
    ax.set_title(f"Nearest Neighbors for {main_district_name}", fontsize=14)
    
    # Add legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='white', markerfacecolor='blue', markersize=10, label='Main District County'),
        Line2D([0], [0], marker='o', color='white', markerfacecolor='red', markersize=10, label='Neighbor District County')
    ]
    ax.legend(handles=legend_elements, loc='lower right')
    
    ax.axis("off")  # Hide axes
    plt.tight_layout()
    plt.show()

from Demographic_Buckets import race_ethnicity_percent
def plot_race_ethnicity_stacked_bar(district_ids, df):
    """
    Visualizes race/ethnicity distribution as percentages using a stacked bar chart.

    Parameters:
    - district_ids (list): List of district IDs to visualize.
    - df (pd.DataFrame): DataFrame containing district race/ethnicity data.

    Returns:
    - A stacked bar chart comparing race/ethnicity distributions as percentages.
    """
    # Step0: Locate the Inputed District 
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]
    print((input_dist))
    
    # Step 1: Filter the DataFrame to include only selected districts
    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME'] + race_ethnicity_percent]

    # Step 2: Check if any districts were found
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return

    # Step 3: Calculate total student count per district
    selected_districts["Total Students"] = selected_districts[race_ethnicity_percent].sum(axis=1)

    # Step 4: Convert race/ethnicity counts to percentages
    for col in race_ethnicity_percent:
        selected_districts[col] = (selected_districts[col] / selected_districts["Total Students"]) * 100

    # Step 5: Set the district names as index for plotting
    selected_districts.set_index("DISTNAME", inplace=True)

    # Step 6: Plot the stacked bar chart
    ax = selected_districts[race_ethnicity_percent].plot(
        kind='bar', 
        figsize=(12, 7), 
        stacked=True, 
        colormap="tab10",
        width=0.8
    )

    # Step 7: Formatting
    plt.title(f"Race/Ethnicity Percentage Distribution for Schools Similar to {input_dist}", fontsize=14)
    plt.xlabel("School Districts", fontsize=12)
    plt.ylabel("Percentage (%)", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)  # Ensure the y-axis represents 0% to 100%

    # Rename legend labels to reflect percentages instead of counts
    formatted_legend_labels = [
        label.replace("District 2022-23", "") for label in race_ethnicity_percent
    ]
    # Format legend with wrapped text to prevent it from being too large
    wrapped_labels = [textwrap.fill(label, width=15) for label in formatted_legend_labels]
    
    # Move legend to the right and wrap text for better readability
    ax.legend(wrapped_labels, title= f"Race/Ethnicity (Percentage)", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10, title_fontsize=12)

    # Improve layout
    plt.tight_layout()
    plt.show()



