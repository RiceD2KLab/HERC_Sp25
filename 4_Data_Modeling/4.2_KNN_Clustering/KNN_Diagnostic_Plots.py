from Demographic_Buckets import (
    student_teacher_ratio,
    student_count,
    staff_count,
    race_ethnicity_percent,
    economically_disadvantaged,
    special_ed_504,
    language_education_percent,
    special_populations_percent,
    gifted_students,
    district_identifiers
)

import os
import re
import textwrap

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import ConnectionPatch

from scipy.spatial import Voronoi
import geopandas as gpd

def format_legend_labels(list_of_cols):
    # Rename legend labels to reflect percentages instead of counts
    formatted_legend_labels = [
        re.sub("(District 2022-23 |District 2023 )", "", label) for label in list_of_cols
    ]
    # Format legend with wrapped text to prevent it from being too large
    wrapped_labels = [textwrap.fill(label, width=15) for label in formatted_legend_labels]
    return wrapped_labels

def title_case_with_spaces(text):
    if 'CISD' in text:
        words = text.split()
        words = [word.title() if word != 'CISD' else word for word in words]
        return ' '.join(words)
    if 'ISD' in text:
        words = text.split()
        words = [word.title() if word != 'ISD' else word for word in words]
        return ' '.join(words)
    if 'MSD' in text:
        words = text.split()
        words = [word.title() if word != 'MSD' else word for word in words]
        return ' '.join(words)
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', text).title()

def plot_texas_districts(neighbors, df):
    """
    Plots selected school districts on a Texas map based on district IDs, with intelligent
    label placement to prevent overlap regardless of location density.
    
    Parameters:
    - neighbors (df): DF containing neighbors district id and distname 
    - df (pd.DataFrame): DataFrame containing 'DISTRICT_id', 'DISTNAME', and 'CNTYNAME' columns.
    
    Returns:
    - A map plot of Texas highlighting the selected school districts with smart non-overlapping labels.
    """
    district_ids = list(neighbors["DISTRICT_id"])

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

def plot_race_ethnicity_stacked_bar(neighbors, df):
    """
    Visualizes race/ethnicity distribution as percentages using a stacked bar chart.

    Parameters:
    - neighbors (df): DF of neighbors DISTRICT_ID and DISTNAME
    - df (pd.DataFrame): DataFrame containing district race/ethnicity data.

    Returns:
    - A stacked bar chart comparing race/ethnicity distributions as percentages.
    """
    # Step 0: Locate the Inputed District 
    district_ids = list(neighbors['DISTRICT_id'])
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]

    # Step 1: Filter the dataframe and verify it isn't empty
    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME'] + race_ethnicity_percent].reset_index(drop=True).dropna()
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return

    # Step 2: reorder the dataframe to ensure that the input district is the 0th index
    neighbors = selected_districts[selected_districts['DISTNAME'] != input_dist].reset_index(drop=True)
    input_district = selected_districts[selected_districts['DISTNAME'] == input_dist].reset_index(drop=True)

    neighbors['group'] = 'Neighboring District'
    input_district['group'] = 'Input District'

    ordered_districts = pd.concat([input_district, neighbors]).reset_index(drop=True)

    # Step 3: Calculate total student count per district
    ordered_districts["Total Students"] = ordered_districts[race_ethnicity_percent].sum(axis=1)

    # Step 4: Convert race/ethnicity counts to percentages
    for col in race_ethnicity_percent:
        ordered_districts[col] = (ordered_districts[col] / ordered_districts["Total Students"]) * 100

    # Step 5: Set the district names as index for plotting
    ordered_districts.set_index("DISTNAME", inplace=True)

    # Step 6: Plot the stacked bar chart
    ax = ordered_districts[race_ethnicity_percent].plot(
        kind='bar', 
        figsize=(12, 7), 
        stacked=True, 
        colormap="tab10",
        width=0.8
    )

    # Step 7: Formatting
    plt.title(f"Race/Ethnicity Percentage Distribution for Schools Similar to {title_case_with_spaces(input_dist)}", fontsize=14)
    plt.xlabel("School Districts", fontsize=12)
    plt.ylabel("Percentage (%)", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    # X-ticks and labels
    ax.set_xticks(np.arange(len(ordered_districts.index)))
    ax.set_xticklabels([title_case_with_spaces(name) for name in ordered_districts.index],
                       rotation=35, ha='right', fontsize=10)
    plt.ylim(0, 100)  # Ensure the y-axis represents 0% to 100%

    # Bold input district label
    for label in ax.get_xticklabels():
        if input_dist.lower() in label.get_text().lower():
            label.set_fontweight('bold')

    # Format legend with wrapped text to prevent it from being too large
    wrapped_labels = format_legend_labels(race_ethnicity_percent)
    
    # Move legend to the right and wrap text for better readability
    ax.legend(wrapped_labels, title= f"Race/Ethnicity (Percentage)", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10, title_fontsize=12)

    # Improve layout
    plt.tight_layout()
    plt.show()

class_size_k6_cols = [
    "District 2023 Class Size: Kindergarten- Avg Size",
    "District 2023 Class Size: Grade 1     - Avg Size",
    "District 2023 Class Size: Grade 2     - Avg Size",
    "District 2023 Class Size: Grade 3     - Avg Size",
    "District 2023 Class Size: Grade 4     - Avg Size",
    "District 2023 Class Size: Grade 5     - Avg Size",
    "District 2023 Class Size: Grade 6     - Avg Size"
]

def plot_class_size_k6_bar(neighbors, df):
    """
    Visualizes class sizes from Kindergarten through Grade 6 across selected districts using a grouped bar chart.

    Parameters:
    - neighbors (df): DF of neighbors DISTRICT_ID and DISTNAME
    - df (pd.DataFrame): DataFrame containing district class size data.

    Returns:
    - A grouped bar chart comparing K-6 class sizes across selected districts.
    """
    district_ids = list(neighbors['DISTRICT_id'])
    
    # Step0: Locate the Inputed District 
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]
    print(f"Input District: {input_dist}")
    
    # Step 1: Filter the DataFrame to include only selected districts
    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME'] + class_size_k6_cols]

    # Step 2: Check if any districts were found
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return

    # Step 3: Melt the dataframe for easier plotting
    melted_df = selected_districts.melt(id_vars=["DISTNAME"], 
                                        value_vars=class_size_k6_cols, 
                                        var_name="Grade", 
                                        value_name="Avg Class Size")

    # Step 4: Clean up grade labels
    melted_df["Grade"] = melted_df["Grade"].str.extract(r'Class Size:\s*(.*)- Avg Size')

    # Step 5: Plot
    plt.figure(figsize=(14, 7))
    ax = sns.barplot(data=melted_df, x="Grade", y="Avg Class Size", hue="DISTNAME")

    # Step 6: Formatting
    plt.title(f"K-6 Average Class Sizes for Districts Similar to {input_dist}", fontsize=14)
    plt.xlabel("Grade", fontsize=12)
    plt.ylabel("Average Class Size", fontsize=12)
    plt.xticks(rotation=30, ha='right')
    plt.legend(title="District", bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
    plt.tight_layout()
    plt.show()


def plot_special_ed_504_bar(neighbors, df):
    """
    Visualizes the percentage of Special Education and Section 504 students across selected districts using a grouped bar chart.
    Highlights the target (first) district.

    Parameters:
    - neighbors (df): DF of neighbors DISTRICT_ID and DISTNAME
    - df (pd.DataFrame): DataFrame containing district demographic data.

    Returns:
    - A grouped bar chart comparing Special Education and Section 504 student percentages across selected districts.
    """

    # Get the data set up
    district_ids = list(neighbors['DISTRICT_id'])
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]

    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME'] + special_ed_504].reset_index(drop=True).dropna()
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return

    # Reorder the data frame so that the input district is index = 0
    # This will ensure it is the leftmost column, which helps make the visual more clear
    neighbors = selected_districts[selected_districts['DISTNAME'] != input_dist].reset_index(drop=True)
    input_district = selected_districts[selected_districts['DISTNAME'] == input_dist].reset_index(drop=True)

    ordered_districts = pd.concat([input_district, neighbors]).reset_index(drop=True)
    
    # Melt the dataframe for easier plotting
    melted_df = ordered_districts.melt(id_vars=["DISTNAME"],
                                        value_vars=special_ed_504,
                                        var_name="Category",
                                        value_name="Percent")

    # Clean up category labels
    melted_df["Category"] = melted_df["Category"].str.replace("District 2022-23 ", "").str.replace(" Students Percent", "")

    # Plot
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=melted_df, x="Category", y="Percent", hue="DISTNAME", palette="Set2")

    # Highlight target district label
    handles, labels = ax.get_legend_handles_labels()

    # Modify labels in the legend
    for i, label in enumerate(labels):
        if input_dist.lower() in label.lower():  # Match the target district
            # Update the fontweight to bold for the target district
            handles[i].set_label(title_case_with_spaces(label))
            labels = [title_case_with_spaces(label) for label in labels]
            ax.legend(handles=handles, labels=labels, title="District", bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=12)

            # Apply bold to target district in the legend
            label_obj = ax.legend_.get_texts()[i]
            label_obj.set_fontweight('bold')  # Make the label bold

    # Formatting
    plt.title(f"Special Education and 504 Student Percentages\n(Target District: {title_case_with_spaces(input_dist)})", fontsize=14)
    plt.xlabel("Student Category", fontsize=12)
    plt.ylabel("Percent of Students", fontsize=12)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.show()

def plot_student_teacher_ratio_bars(neighbors, df):
    """
    Plots a bar chart showing student-teacher ratio by district using a list of neighbors and a dataframe with the necessary columns.

    Inputs:
    - neighbors: a Pandas dataframe that has the column DISTRICT_id of the neighbors of a given input district. The given input district 
    is assumed to be the 0th row of the dataframe.
    - df: a Pandas dataframe that has the columns DISTRICT_id, DISTNAME, and student-teacher ratio. 

    Outputs: 
    - a matplotlib bar chart
    """
    # Get the data set up
    district_ids = list(neighbors['DISTRICT_id'])
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]

    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME'] + student_teacher_ratio].reset_index(drop=True).dropna()
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return

    # Reorder the data frame so that the input district is index = 0
    # This will ensure it is the leftmost column, which helps make the visual more clear
    neighbors = selected_districts[selected_districts['DISTNAME'] != input_dist].reset_index(drop=True)
    input_district = selected_districts[selected_districts['DISTNAME'] == input_dist].reset_index(drop=True)

    ordered_districts = pd.concat([input_district, neighbors]).reset_index(drop=True)
    ordered_districts.set_index("DISTNAME", inplace=True)

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 6))
    ratio_col = student_teacher_ratio[0]
    values = ordered_districts[ratio_col].round(2)
    bars = ax.bar(ordered_districts.index, values, color='#1f77b4', width=0.6)

    # adding number labels to the bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 0.2, f"{value:.2f}",
                ha='center', va='bottom', fontsize=9)

    # X-ticks and labels
    ax.set_xticks(np.arange(len(ordered_districts.index)))
    ax.set_xticklabels([title_case_with_spaces(name) for name in ordered_districts.index],
                       rotation=35, ha='right', fontsize=10)

    # Bold input district label for readability
    for label in ax.get_xticklabels():
        if input_dist.lower() in label.get_text().lower():
            label.set_fontweight('bold')

    # Title and axis labels
    ax.set_title(f"Student-Teacher Ratios for Districts Similar to {title_case_with_spaces(input_dist)}")
    ax.set_xlabel("School District", fontsize=13, labelpad=10)
    ax.set_ylabel("Student-Teacher Ratio", fontsize=13, labelpad=10)

    plt.tight_layout()
    plt.show()

def plot_student_staff_counts(neighbors, df):
    """
    Plots a grouped bar chart with different color bars for student and staff counts by district 
    using a list of neighbors and a dataframe with the necessary columns.

    Inputs:
    - neighbors: a Pandas dataframe that has the column DISTRICT_id of the neighbors of a given input district. The given input district 
    is assumed to be the 0th row of the dataframe.
    - df: a Pandas dataframe that has the columns DISTRICT_id, DISTNAME, and student and staff count as denoted in the Demographic_Buckets file.

    Outputs: 
    - a matplotlib bar chart
    """
    # Get the data set up
    district_ids = list(neighbors['DISTRICT_id'])
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]

    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME'] + staff_count + student_count].reset_index(drop=True).dropna()
            
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return

    # Reorder the data frame so that the input district is index = 0
    # This will ensure it is the leftmost column, which helps make the visual more clear
    neighbors = selected_districts[selected_districts['DISTNAME'] != input_dist].reset_index(drop=True)
    input_district = selected_districts[selected_districts['DISTNAME'] == input_dist].reset_index(drop=True)

    ordered_districts = pd.concat([input_district, neighbors]).reset_index(drop=True)
    
    # Melt the dataframe for easier plotting
    melted_df = ordered_districts.melt(id_vars=["DISTNAME"],
                                        value_vars=staff_count + student_count,
                                        var_name="Category",
                                        value_name="Percent")

    # Clean up category labels
    melted_df["Category"] = melted_df["Category"].str.replace("District 2022-23 ", "").str.replace("District 2023 Staff: All Staff Total Full Time Equiv Count", "Full Time\nEquivalent Staff").str.replace(" Count", "")

    # Plot
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=melted_df, x="Category", y="Percent", hue="DISTNAME", palette="Set2")

    # Highlight target district label
    handles, labels = ax.get_legend_handles_labels()

    # Modify labels in the legend
    for i, label in enumerate(labels):
        if input_dist.lower() in label.lower():  # Match the target district
            # Update the fontweight to bold for the target district
            handles[i].set_label(title_case_with_spaces(label))  # Keep the label unchanged
            labels = [title_case_with_spaces(label) for label in labels]
            ax.legend(handles=handles, labels=labels, title="District", bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=12)

            # Apply bold to target district in the legend
            label_obj = ax.legend_.get_texts()[i]
            label_obj.set_fontweight('bold')  # Make the label bold

    # Formatting
    plt.title(f"Staff and Student Counts for Districts Similar to {title_case_with_spaces(input_dist)}", fontsize=14)
    plt.xlabel("Population", fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.show()

def plot_special_populations_bar(neighbors, df):
    """
    Visualizes the percentage of students in different special populations across selected districts using a grouped bar chart.
    Highlights the target (first) district.

    Parameters:
    - neighbors (df): DF of neighbors DISTRICT_ID and DISTNAME
    - df (pd.DataFrame): DataFrame containing district demographic data.

    Returns:
    - A grouped bar chart comparing special population student percentages across selected districts.
    """

    # Get the data set up
    district_ids = list(neighbors['DISTRICT_id'])
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]

    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME'] + special_populations_percent].reset_index(drop=True).dropna()

    valid_cols = special_populations_percent
    for column in selected_districts.select_dtypes(include='number'):
        if selected_districts[column].sum() == 0:
            selected_districts = selected_districts.drop(column, axis=1)
            valid_cols.remove(column)
            
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return

    # Reorder the data frame so that the input district is index = 0
    # This will ensure it is the leftmost column, which helps make the visual more clear
    neighbors = selected_districts[selected_districts['DISTNAME'] != input_dist].reset_index(drop=True)
    input_district = selected_districts[selected_districts['DISTNAME'] == input_dist].reset_index(drop=True)

    ordered_districts = pd.concat([input_district, neighbors]).reset_index(drop=True)
    
    # Melt the dataframe for easier plotting
    melted_df = ordered_districts.melt(id_vars=["DISTNAME"],
                                        value_vars=valid_cols,
                                        var_name="Category",
                                        value_name="Percent")

    # Clean up category labels
    melted_df["Category"] = melted_df["Category"].str.replace("District 2022-23 ", "").str.replace(" Students Percent", "")

    # Plot
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=melted_df, x="Category", y="Percent", hue="DISTNAME", palette="Set2")

    # Highlight target district label
    handles, labels = ax.get_legend_handles_labels()

    # Modify labels in the legend
    for i, label in enumerate(labels):
        if input_dist.lower() in label.lower():  # Match the target district
            # Update the fontweight to bold for the target district
            handles[i].set_label(title_case_with_spaces(label))  # Keep the label unchanged
            labels = [title_case_with_spaces(label) for label in labels]
            ax.legend(handles=handles, labels=labels, title="District", bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=12)

            # Apply bold to target district in the legend
            label_obj = ax.legend_.get_texts()[i]
            label_obj.set_fontweight('bold')  # Make the label bold

    # Formatting
    plt.title(f"Student Special Population Percentages for Districts Similar to {title_case_with_spaces(input_dist)}", fontsize=14)
    plt.xlabel("Student Category", fontsize=12)
    plt.ylabel("Percent of Students", fontsize=12)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.show()

def plot_gifted_talented_bars(neighbors, df):
    """
    Plots a bar chart showing percent of students in gifted and talented programs by district 
    using a list of neighbors and a dataframe with the necessary columns.

    Inputs:
    - neighbors: a Pandas dataframe that has the column DISTRICT_id of the neighbors of a given input district. The given input district 
    is assumed to be the 0th row of the dataframe.
    - df: a Pandas dataframe that has the columns DISTRICT_id, DISTNAME, and gifted and talented percent.

    Outputs: 
    - a matplotlib bar chart
    """
    # Get the data set up
    district_ids = list(neighbors['DISTRICT_id'])
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]

    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME'] + gifted_students].reset_index(drop=True).dropna()
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return

    # Reorder the data frame so that the input district is index = 0
    # This will ensure it is the leftmost column, which helps make the visual more clear
    neighbors = selected_districts[selected_districts['DISTNAME'] != input_dist].reset_index(drop=True)
    input_district = selected_districts[selected_districts['DISTNAME'] == input_dist].reset_index(drop=True)

    ordered_districts = pd.concat([input_district, neighbors]).reset_index(drop=True)
    ordered_districts.set_index("DISTNAME", inplace=True)

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 6))
    col = gifted_students[0]
    values = ordered_districts[col].round(2)
    bars = ax.bar(ordered_districts.index, values, color='#1f77b4', width=0.6)

    # adding number labels to the bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 0.2, f'{height:.1f}%',
                ha='center', va='bottom', fontsize=9)

    # X-ticks and labels
    ax.set_xticks(np.arange(len(ordered_districts.index)))
    ax.set_xticklabels([title_case_with_spaces(name) for name in ordered_districts.index],
                       rotation=35, ha='right', fontsize=10)

    # Bold input district label for readability
    for label in ax.get_xticklabels():
        if input_dist.lower() in label.get_text().lower():
            label.set_fontweight('bold')

    # Title and axis labels
    ax.set_title(f"Percent Students in Gifted and Talented Programs for Districts Similar to {title_case_with_spaces(input_dist)}")
    ax.set_xlabel("School District", fontsize=13, labelpad=10)
    ax.set_ylabel("Percent Students", fontsize=13, labelpad=10)

    plt.tight_layout()
    plt.show()

def plot_economically_disadvantaged_side_by_side(neighbors, df):
    """
    Visualizes economically disadvantaged distribution as percentages using side-by-side bar charts.

    Parameters:
    - neighbors (df): DF of neighbors DISTRICT_ID and DISTNAME
    - df (pd.DataFrame): DataFrame containing district economically disadvantaged data.

    Returns:
    - A side-by-side bar chart comparing economically disadvantaged distributions.
    """
    district_ids = list(neighbors['DISTRICT_id'])
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]

    # Step 1: Filter the dataframe and verify it isn't empty
    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME'] + economically_disadvantaged].reset_index(drop=True).dropna()
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return

    # Step 2: reorder the dataframe to ensure that the input district is the 0th index
    neighbors = selected_districts[selected_districts['DISTNAME'] != input_dist].reset_index(drop=True)
    input_district = selected_districts[selected_districts['DISTNAME'] == input_dist].reset_index(drop=True)

    neighbors['group'] = 'Neighboring District'
    input_district['group'] = 'Input District'

    ordered_districts = pd.concat([input_district, neighbors]).reset_index(drop=True)

    # Step 5: Set the district names as index for plotting
    ordered_districts.set_index("DISTNAME", inplace=True)

    # Step 6: Plot the side-by-side bar chart
    ax = ordered_districts[economically_disadvantaged].plot(
        kind='bar', 
        figsize=(12, 6), 
        width=0.8, 
        position=1,  # This parameter makes bars display side-by-side
        colormap="tab10"
    )

    # Step 7: Formatting
    plt.title(f"Economically Disadvantaged Percentage Distribution for Schools Similar to {title_case_with_spaces(input_dist)}", fontsize=14)
    plt.xlabel("School Districts", fontsize=12)
    plt.ylabel("Percentage (%)", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    # X-ticks and labels
    ax.set_xticks(np.arange(len(ordered_districts.index)))
    ax.set_xticklabels([title_case_with_spaces(name) for name in ordered_districts.index],
                       rotation=35, ha='right', fontsize=10)

    # Bold input district label for readability
    for label in ax.get_xticklabels():
        if input_dist.lower() in label.get_text().lower():
            label.set_fontweight('bold')

    wrapped_labels = format_legend_labels(economically_disadvantaged)
    
    # Move legend to the right and wrap text for better readability
    ax.legend(wrapped_labels, title= f"Economically Disadvantaged (Percentage)", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10, title_fontsize=12)

    # Improve layout
    plt.tight_layout()
    plt.show()

dropout_rates = ['District 2022 Annual Dropout for Grades 09-12: All Students Rate',
 'District 2022 Annual Dropout for Grades 09-12: Male Rate', 'District 2022 Annual Dropout for Grades 09-12: Female Rate',
  'District 2022 Annual Dropout for Grades 09-12: Asian Rate', 'District 2022 Annual Dropout for Grades 09-12: African American Rate', 
  'District 2022 Annual Dropout for Grades 09-12: Hispanic Rate', 'District 2022 Annual Dropout for Grades 09-12: American Indian Rate', 
  'District 2022 Annual Dropout for Grades 09-12: Pacific Islander Rate', 'District 2022 Annual Dropout for Grades 09-12: Two or More Races Rate',
   'District 2022 Annual Dropout for Grades 09-12: White Rate', 'District 2022 Annual Dropout for Grades 09-12: Econ Disadv Rate',
    'District 2022 Annual Dropout for Grades 09-12: Special Ed Rate', 'District 2022 Annual Dropout for Grades 09-12: At Risk Rate', 
    'District 2022 Annual Dropout for Grades 09-12: EB/EL Rate', 'District 2021 Annual Dropout for Grades 09-12: All Students Rate',
     'District 2021 Annual Dropout for Grades 09-12: Male Rate', 'District 2021 Annual Dropout for Grades 09-12: Female Rate',
      'District 2021 Annual Dropout for Grades 09-12: Asian Rate', 'District 2021 Annual Dropout for Grades 09-12: African American Rate', 
      'District 2021 Annual Dropout for Grades 09-12: Hispanic Rate', 'District 2021 Annual Dropout for Grades 09-12: American Indian Rate', 
      'District 2021 Annual Dropout for Grades 09-12: Pacific Islander Rate', 'District 2021 Annual Dropout for Grades 09-12: Two or More Races Rate', 
      'District 2021 Annual Dropout for Grades 09-12: White Rate', 'District 2021 Annual Dropout for Grades 09-12: Econ Disadv Rate',
       'District 2021 Annual Dropout for Grades 09-12: Special Ed Rate',
 'District 2021 Annual Dropout for Grades 09-12: At Risk Rate', 'District 2021 Annual Dropout for Grades 09-12: EL Rate']

def plot_dropout_rates(neighbors, df, year):
    """
    Visualizes dropout rates for the year 2022 as percentages using side-by-side bar charts.

    Parameters:
    - neighbors (pd.DataFrame): DataFrame containing DISTRICT_ID and DISTNAME of neighboring districts.
    - df (pd.DataFrame): DataFrame containing district dropout rate data.

    Returns:
    - A side-by-side bar chart comparing dropout rate distributions for 2022.
    """
    district_ids = list(neighbors['DISTRICT_id'])

    # Step 0: Locate the Inputed District
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]
    print(input_dist)
    
    # Step 1: Filter dropout rate columns for 2022
    dropout_rates_filt = [col for col in dropout_rates if year in col]

    # Step 2: Filter the DataFrame to include only selected districts and 2022 dropout rate columns
    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTNAME'] + dropout_rates_filt]

    # Step 3: Check if any districts were found
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return

    # Step 4: Set the district names as index for plotting
    selected_districts.set_index("DISTNAME", inplace=True)

    # Step 5: Determine max dropout rate dynamically
    max_value = selected_districts[dropout_rates_filt].max().max()  # Max across all categories and districts
    buffer = max_value * 0.1  # Add 10% buffer for readability

    # Step 6: Assign more diverse colors (tab20 colormap for more variety)
    num_categories = len(dropout_rates_filt)
    color_map = plt.cm.get_cmap("tab20", num_categories)  # Use "tab20" for more diverse colors
    colors = [color_map(i) for i in range(num_categories)]

    # Step 7: Plot the side-by-side bar chart
    ax = selected_districts[dropout_rates_filt].plot(
        kind='bar', 
        figsize=(14, 8), 
        width=0.8, 
        color=colors  # Apply diverse colors
    )

    # Step 8: Formatting
    plt.title(f"Annual Dropout Rate Distribution for Grades 09-12 in {year} for Districts Similar to {input_dist}", fontsize=14)
    plt.xlabel("School Districts", fontsize=12)
    plt.ylabel("Dropout Rate (%)", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, min(100, max_value + buffer))  # Scale dynamically but cap at 100%

    # Rename legend labels for clarity
    formatted_legend_labels = [label.replace(f"District {year} Annual Dropout for Grades 09-12: ", "") for label in  dropout_rates_filt]
    wrapped_labels = [textwrap.fill(label, width=15) for label in formatted_legend_labels]

    # Move legend to the right and wrap text for better readability
    ax.legend(wrapped_labels, title="Dropout Rates (%)", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10, title_fontsize=12)

    # Improve layout
    plt.tight_layout()
    plt.show()

def plot_language_education_bars(neighbors, df):
    """
    Plots a grouped bar chart with different color bars for student and staff counts by district 
    using a list of neighbors and a dataframe with the necessary columns.

    Inputs:
    - neighbors: a Pandas dataframe that has the column DISTRICT_id of the neighbors of a given input district. The given input district 
    is assumed to be the 0th row of the dataframe.
    - df: a Pandas dataframe that has the columns DISTRICT_id, DISTNAME, and student and staff count as denoted in the Demographic_Buckets file.

    Outputs: 
    - a matplotlib bar chart
    """
    # Get the data set up
    district_ids = list(neighbors['DISTRICT_id'])
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]

    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME'] + language_education_percent].reset_index(drop=True).dropna()
            
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return

    # Reorder the data frame so that the input district is index = 0
    # This will ensure it is the leftmost column, which helps make the visual more clear
    neighbors = selected_districts[selected_districts['DISTNAME'] != input_dist].reset_index(drop=True)
    input_district = selected_districts[selected_districts['DISTNAME'] == input_dist].reset_index(drop=True)

    ordered_districts = pd.concat([input_district, neighbors]).reset_index(drop=True)
    
    # Melt the dataframe for easier plotting
    melted_df = ordered_districts.melt(id_vars=["DISTNAME"],
                                        value_vars=language_education_percent,
                                        var_name="Category",
                                        value_name="Percent")

    # Clean up category labels
    melted_df["Category"] = melted_df["Category"].str.replace("District 2022-23 ", "").str.replace(" Students Percent", "")

    # Plot
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=melted_df, x="Category", y="Percent", hue="DISTNAME", palette="Set2")

    # Highlight target district label
    handles, labels = ax.get_legend_handles_labels()

    # Modify labels in the legend
    for i, label in enumerate(labels):
        if input_dist.lower() in label.lower():  # Match the target district
            # Update the fontweight to bold for the target district
            handles[i].set_label(title_case_with_spaces(label))  # Keep the label unchanged
            labels = [title_case_with_spaces(label) for label in labels]
            ax.legend(handles=handles, labels=labels, title="District", bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=12)

            # Apply bold to target district in the legend
            label_obj = ax.legend_.get_texts()[i]
            label_obj.set_fontweight('bold')  # Make the label bold

    # Formatting
    plt.title(f"Language Education Student Percentages for Districts Similar to {title_case_with_spaces(input_dist)}", fontsize=14)
    plt.xlabel("Population", fontsize=12)
    plt.ylabel("Percent Students", fontsize=12)
    plt.xticks(rotation=30, ha='right')
    ax.set_xticks(np.arange(2))
    ax.set_xticklabels(['Bilingual/ESL\nEducation', 'Emergent Bilingual/\nEnglish Learner'],
                       rotation=35, ha='right', fontsize=10)
    plt.tight_layout()
    plt.show()

def plot_graduation_rate_bar(neighbors, df, groups=None):
    """
    Diagnostic bar plot comparing graduation rates across demographic subgroups.

    Parameters:
    - neighbors (DataFrame): DataFrame with DISTRICT_id and DISTNAME of neighbors
    - df (DataFrame): Full dataset containing graduation rate breakdowns
    - groups (list, optional): A list of demographic group names to include in the plot. Default is to include all available groups.

    Output:  
        - Displays a grouped bar chart comparing rates across selected districts for the specified demographic groups.
    """

    # only includes race/ethnic groups, does not include EB/EL, Econ Disadv, At Risk, etc
    grad_cols = {
            'African American': 'District 2022 4-Year Longitudinal: [FHSP-DLA Graduates] for African American Rate',
            'American Indian':  'District 2022 4-Year Longitudinal: [FHSP-DLA Graduates] for American Indian Rate',
            'Asian':            'District 2022 4-Year Longitudinal: [FHSP-DLA Graduates] for Asian Rate',
            'Hispanic':         'District 2022 4-Year Longitudinal: [FHSP-DLA Graduates] for Hispanic Rate',
            'Pacific Islander': 'District 2022 4-Year Longitudinal: [FHSP-DLA Graduates] for Pacific Islander Rate',
            'White':            'District 2022 4-Year Longitudinal: [FHSP-DLA Graduates] for White Rate',
            'Two or More':      'District 2022 4-Year Longitudinal: [FHSP-DLA Graduates] for Two or More Races Rate',
    }

    if groups is None:
        groups = list(grad_cols.keys())

    selected_cols = [grad_cols[group] for group in groups if group in grad_cols]

    district_ids = list(neighbors["DISTRICT_id"])
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]

    selected = df[df["DISTRICT_id"].isin(district_ids)][["DISTNAME"] + selected_cols]
    melted = selected.melt(id_vars="DISTNAME", var_name="Group", value_name="Grad Rate (%)")
    melted["Group"] = melted["Group"].str.replace("District 2022-23 Graduation Rate - ", "")

    plt.figure(figsize=(12, 6))
    sns.barplot(data=melted, x="DISTNAME", y="Grad Rate (%)", hue="Group")
    plt.title(f"Graduation Rate by Group for Districts Similar to {input_dist}")
    plt.xlabel("School Districts")
    plt.ylabel("Graduation Rate (%)")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Group", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.show()

def plot_attendance_rate_bar(neighbors, df, groups=None):
    """
    Diagnostic bar plot comparing attendance rates across demographic subgroups.

    Parameters:
        - neighbors (DataFrame): DataFrame with DISTRICT_id and DISTNAME of neighbors
        - df (DataFrame): Full dataset containing graduation rate breakdowns
        - groups (list, optional): A list of demographic group names to include in the plot. Default is to include all available groups.

    Output:  
        - Displays a grouped bar chart comparing rates across selected districts for the specified demographic groups.
    """
    attendance_cols = {
        'African American':  'District 2022 Attendance: African American Rate',
        'American Indian':   'District 2022 Attendance: American Indian Rate',
        'Asian':             'District 2022 Attendance: Asian Rate',
        'Hispanic':          'District 2022 Attendance: Hispanic Rate',
        'Pacific Islander':  'District 2022 Attendance: Pacific Islander Rate',
        'White':             'District 2022 Attendance: White Rate',
        'Two or More':       'District 2022 Attendance: Two or More Races Rate',
    }

    if groups is None:
        groups = list(attendance_cols.keys())

    selected_cols = [attendance_cols[group] for group in groups if group in attendance_cols]

    district_ids = list(neighbors["DISTRICT_id"])
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]

    selected = df[df["DISTRICT_id"].isin(district_ids)][["DISTNAME"] + selected_cols]
    melted = selected.melt(id_vars="DISTNAME", var_name="Group", value_name="Attendance Rate (%)")
    melted["Group"] = melted["Group"].str.replace("District 2022-23 Attendance Rate - ", "")

    plt.figure(figsize=(12, 6))
    sns.barplot(data=melted, x="DISTNAME", y="Attendance Rate (%)", hue="Group")
    plt.title(f"Attendance Rate by Group for Districts Similar to {input_dist}")
    plt.xlabel("School Districts")
    plt.ylabel("Attendance Rate (%)")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Group", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.show()

def plot_chronic_absenteeism_bar(neighbors, df, groups=None):
    """
    Diagnostic bar plot comparing chronic absenteeism rates across demographic subgroups.

    Parameters:
        - neighbors (DataFrame): DataFrame with DISTRICT_id and DISTNAME of neighbors
        - df (DataFrame): Full dataset containing graduation rate breakdowns
        - groups (list, optional): A list of demographic group names to include in the plot. Default is to include all available groups.

    Output:  
        - Displays a grouped bar chart comparing rates across selected districts for the specified demographic groups.
    """
    absentee_cols = {
        'African American':    '2022 district Chronic Absenteeism African American Group: Rate',
        'Hispanic':            '2022 district Chronic Absenteeism Hispanic Group: Rate',
        'White':               '2022 district Chronic Absenteeism White Group: Rate',
        'American Indian':     '2022 district Chronic Absenteeism American Indian Group: Rate',
        'Asian':               '2022 district Chronic Absenteeism Asian Group: Rate',
        'Pacific Islander':    '2022 district Chronic Absenteeism Pacific Islander Group: Rate',
        'Two or More':         '2022 district Chronic Absenteeism Two or More Races Group: Rate',
    }

    if groups is None:
        groups = list(absentee_cols.keys())

    selected_cols = [absentee_cols[group] for group in groups if group in absentee_cols]

    district_ids = list(neighbors["DISTRICT_id"])
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]

    selected = df[df["DISTRICT_id"].isin(district_ids)][["DISTNAME"] + selected_cols]
    melted = selected.melt(id_vars="DISTNAME", var_name="Group", value_name="Absenteeism Rate (%)")
    melted["Group"] = melted["Group"].str.replace("District 2022-23 Chronic Absenteeism Rate - ", "")

    plt.figure(figsize=(12, 6))
    sns.barplot(data=melted, x="DISTNAME", y="Absenteeism Rate (%)", hue="Group")
    plt.title(f"Chronic Absenteeism Rate by Group for Districts Similar to {input_dist}")
    plt.xlabel("School Districts")
    plt.ylabel("Absenteeism Rate (%)")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Group", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.show()