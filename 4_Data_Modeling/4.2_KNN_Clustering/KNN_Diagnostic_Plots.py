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

    # Define columns to plot
    special_ed_504_cols = [
        "District 2022-23 Special Education Students Percent",
        "District 2022-23 Section 504 Students Percent"
    ]
    
    district_ids = list(neighbors['DISTRICT_id'])
    target_id = district_ids[0]

    # Step 0: Locate the Inputed District 
    input_dist = df[df["DISTRICT_id"] == target_id]['DISTNAME'].iloc[0]
    print(f"Input District: {input_dist}")

    # Step 1: Filter the DataFrame to include only selected districts
    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME'] + special_ed_504_cols]

    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return

    # Add a 'Highlight' column to flag the target district
    selected_districts['Highlight'] = selected_districts['DISTRICT_id'].apply(lambda x: 'Target District' if x == target_id else 'Neighbor District')

    # Melt the dataframe for easier plotting
    melted_df = selected_districts.melt(id_vars=["DISTNAME", "Highlight"],
                                        value_vars=special_ed_504_cols,
                                        var_name="Category",
                                        value_name="Percent")

    # Clean up category labels
    melted_df["Category"] = melted_df["Category"].str.replace("District 2022-23 ", "").str.replace(" Students Percent", "")

    # Plot
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=melted_df, x="Category", y="Percent", hue="DISTNAME", palette="Set2")

    # Highlight target district label
    handles, labels = ax.get_legend_handles_labels()
    bold_labels = []
    for label in labels:
        if label == input_dist:
            bold_labels.append(f"$\\bf{{{label}}}$")  # Bold with LaTeX
        else:
            bold_labels.append(label)
    ax.legend(handles=handles, labels=bold_labels, title="District", bbox_to_anchor=(1.02, 1), loc='upper left')

    # Formatting
    plt.title(f"Special Education and 504 Student Percentages\n(Target District: {input_dist})", fontsize=14)
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
    # get the data set up
    district_ids = list(neighbors['DISTRICT_id'])
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]

    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME'] + student_count + staff_count].reset_index(drop=True).dropna()
    
    # verify it's not empty
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return
    
    # reorder so that the input district is first
    neighbors = selected_districts[selected_districts['DISTNAME'] != input_dist].reset_index(drop=True)
    input_district = selected_districts[selected_districts['DISTNAME'] == input_dist].reset_index(drop=True)


    ordered_districts = pd.concat([input_district, neighbors]).reset_index(drop=True)
    ordered_districts.set_index("DISTNAME", inplace=True)

    labels = ordered_districts.index
    x = np.arange(len(labels))  # label locations

    # getting the columns
    student_col = student_count[0]
    staff_col = staff_count[0]

    student_vals = ordered_districts[student_col]
    staff_vals = ordered_districts[staff_col]

    bar_width = 0.3
    spacing = 0.05  # space between student and staff bars

    # creating the bars and the plot
    fig, ax = plt.subplots(figsize=(12, 6))

    bars1 = ax.bar(x - bar_width/2 - spacing/2, student_vals, bar_width, label='Student', color='#1f77b4')
    bars2 = ax.bar(x + bar_width/2 + spacing/2, staff_vals, bar_width, label='Staff', color='#ff7f0e')

    # adding numeric labels to the bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.5, f'{int(height)}',
                    ha='center', va='bottom', fontsize=8)

    # change the district labels
    ax.set_xticks(x)
    ax.set_xticklabels([title_case_with_spaces(name) for name in labels],
                       rotation=35, ha='right', fontsize=10)

    for label in ax.get_xticklabels():
        if input_dist.lower() in label.get_text().lower():
            label.set_fontweight('bold')

    # axis and title labels
    ax.set_title(f"Staff and Student Populations for Districts Similar to {title_case_with_spaces(input_dist)}")
    ax.set_xlabel("School District", fontsize=13, labelpad=10)
    ax.set_ylabel("Staff/Student Count", fontsize=13, labelpad=10)

    # create a legend and reformat the Staff column name because it's not clean
    labels = format_legend_labels(student_count + staff_count)
    labels_nicer = [re.sub('Staff: All\nStaff Total\nFull Time Equiv\nCount', "Total Full Time\nEquivalent Staff\nCount", label) for label in labels]
    ax.legend(labels_nicer, title="Population", loc="center left", bbox_to_anchor=(1, 0.5),
              fontsize=10, title_fontsize=12)

    # show the plot
    plt.tight_layout()
    plt.show()

def plot_special_populations_bar(neighbors, df):
    """
    Visualizes special populations as a grouped bar chart

    Parameters:
    - neighbors (df): DF of neighbors DISTRICT_ID and DISTNAME
    - df (pd.DataFrame): DataFrame containing district special populations

    Returns:
    - A stacked bar chart comparing special populalations distributions as percentages.
    """
    # Step 0: Locate the Inputed District 
    district_ids = list(neighbors['DISTRICT_id'])
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]

    # Step 1: Filter the dataframe and verify it isn't empty
    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME'] + special_populations_percent].reset_index(drop=True).dropna()
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return

    # Step 2: reorder the dataframe to ensure that the input district is the 0th index
    neighbors = selected_districts[selected_districts['DISTNAME'] != input_dist].reset_index(drop=True)
    input_district = selected_districts[selected_districts['DISTNAME'] == input_dist].reset_index(drop=True)

    neighbors['group'] = 'Neighboring District'
    input_district['group'] = 'Input District'

    ordered_districts = pd.concat([input_district, neighbors]).reset_index(drop=True)

    ordered_districts.set_index("DISTNAME", inplace=True)

    # create the series for the bars
    homeless = ordered_districts[special_populations_percent[0]]
    immigrant = ordered_districts[special_populations_percent[1]]
    migrant = ordered_districts[special_populations_percent[2]]
    military = ordered_districts[special_populations_percent[3]]
    foster = ordered_districts[special_populations_percent[4]]

    tab10_colors = plt.cm.tab10.colors

    labels = list(ordered_districts.index)
    x = np.arange(len(labels))

    bar_width = 0.125
    spacing = 0.04

    # Create plot
    fig, ax = plt.subplots(figsize=(16, 7))

    bars1 = ax.bar(x - 2*bar_width - spacing*2, homeless, bar_width, label='Homeless', color=tab10_colors[0])
    bars2 = ax.bar(x - bar_width - spacing, immigrant, bar_width, label='Immigrant', color=tab10_colors[1])
    bars3 = ax.bar(x, migrant, bar_width, label='Migrant', color=tab10_colors[2])
    bars4 = ax.bar(x + bar_width + spacing, military, bar_width, label='Military-Connected', color=tab10_colors[3])
    bars5 = ax.bar(x + 2*bar_width + spacing*2, foster, bar_width, label='Foster Care', color=tab10_colors[4])

    # Add value labels
    for bars in [bars1, bars2, bars3, bars4, bars5]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.1, f'{height:.1f}%', 
                    ha='center', va='bottom', fontsize=8)

    # X-axis labels
    ax.set_xticks(x)
    ax.set_xticklabels([title_case_with_spaces(name) for name in labels], 
                    rotation=35, ha='right', fontsize=10)

    # Highlight input district
    for label in ax.get_xticklabels():
        if input_dist.lower() in label.get_text().lower():
            label.set_fontweight('bold')

    # Titles and axis labels
    ax.set_title(f"Special Population Percentages for Districts Similar to {title_case_with_spaces(input_dist)}", fontsize=14)
    ax.set_xlabel("School District", fontsize=13, labelpad=10)
    ax.set_ylabel("Percent of Students", fontsize=13, labelpad=10)

    # Legend
    ax.legend(title="Special Population (Percent)", fontsize=10, title_fontsize=12, loc="center left", bbox_to_anchor=(1, 0.5))

    plt.tight_layout()
    plt.show()