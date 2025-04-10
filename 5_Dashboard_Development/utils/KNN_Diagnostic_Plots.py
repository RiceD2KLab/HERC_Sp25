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

import folium
from adjustText import adjust_text

plt.rcParams['axes.grid'] = False

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
    # Get selected district IDs from the neighbors DataFrame
    district_ids = list(neighbors["DISTRICT_id"])
    if not district_ids:
        print("No district IDs provided.")
        return

    # Filter the DataFrame for the selected districts
    selected_districts = df[df["DISTRICT_id"].isin(district_ids)]
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return

    # Group selected districts by county and create a comma-separated string
    county_to_districts = (selected_districts
                          .groupby("CNTYNAME")["DISTNAME"]
                          .apply(list)
                          .to_dict())
    # Convert keys to uppercase for matching with shapefile data
    county_to_districts = {k.upper(): ", ".join(v) for k, v in county_to_districts.items()}

    # Look for the Texas counties file in a relative "data" directory
    import os
    data_dir = "data"
    texas_counties_path = os.path.join(data_dir, "texas_counties.geojson")
    
    # Load the Texas counties from the bundled file
    try:
        texas_counties = gpd.read_file(texas_counties_path)
    except Exception as e:
        print(f"Error loading Texas counties: {e}")
        print("Please ensure the texas_counties.geojson file is present in the 'data' folder.")
        return None

    # Create a new column for uppercase county names and map district info
    texas_counties["NAME_UPPER"] = texas_counties["NAME"].str.upper()
    texas_counties["districts"] = texas_counties["NAME_UPPER"].map(county_to_districts)

    # Define the Texas bounding box (SW and NE corners)
    texas_bounds = [[25.84, -106.65], [36.5, -93.51]]

    # Create the Folium map, centered on Texas.
    m = folium.Map(location=[31.0, -99.0], zoom_start=6, tiles="cartodbpositron", max_bounds=True)
    
    # Force the map view to the Texas bounds.
    m.fit_bounds(texas_bounds)
    m.options['maxBounds'] = texas_bounds

    # Define a style function for the GeoJSON layer.
    def style_function(feature):
        if feature["properties"].get("districts"):
            return {
                'fillColor': 'blue',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7,
            }
        else:
            return {
                'fillColor': 'lightgray',
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.5,
            }

    # Add the GeoJSON layer with tooltips to the map.
    folium.GeoJson(
        texas_counties.to_json(),
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["NAME", "districts"],
            aliases=["County:", "Districts:"],
            localize=True
        )
    ).add_to(m)

    return m



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
    ax.grid(False)
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
    ax.grid(False)
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

def district_map(df, neighbors, root_directory, metric = None):
    # Load shapefile
    gdf = gpd.read_file(f"{root_directory}/HERC_Sp25/0_Datasets/2.1Geometry/Texas_SchoolDistricts_2024.geojson")

    # Ensure consistent types
    df['DISTRICT_id'] = df['DISTRICT_id'].astype(str)
    neighbors = neighbors.copy().reset_index(drop=True)
    neighbors['DISTRICT_id'] = neighbors['DISTRICT_id'].astype(str)
    gdf['DISTRICT_N'] = gdf['DISTRICT_N'].astype(str)

    # Extract district IDs
    district_ids = list(neighbors['DISTRICT_id'].dropna().unique())
    if not district_ids:
        print("No district IDs found in neighbors.")
        return

    # Get input district name
    input_rows = df[df["DISTRICT_id"] == district_ids[0]]
    if input_rows.empty:
        print(f"No matching DISTNAME found for DISTRICT_id: {district_ids[0]}")
        return
    input_dist = input_rows['DISTNAME'].iloc[0]

    # Select and categorize districts
    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME']].dropna().reset_index(drop=True)
    neighbors_df = selected_districts[selected_districts['DISTNAME'] != input_dist].copy()
    input_district_df = selected_districts[selected_districts['DISTNAME'] == input_dist].copy()
    neighbors_df['group'] = 'Neighboring District'
    input_district_df['group'] = 'Input District'
    ordered_districts = pd.concat([input_district_df, neighbors_df]).reset_index(drop=True)

    # Assign color
    def get_color(cat):
        return {"Input District": "blue", "Neighboring District": "red"}.get(cat, "lightgrey")

    district_group_map = ordered_districts.set_index('DISTRICT_id')['group']
    gdf['group'] = gdf['DISTRICT_N'].map(district_group_map)
    gdf['color'] = gdf['group'].apply(get_color)

    # Reproject and calculate centroids
    gdf_proj = gdf.to_crs(epsg=3857)
    label_gdf = gdf_proj[gdf_proj['DISTRICT_N'].isin(ordered_districts['DISTRICT_id'])].copy()
    label_gdf['centroid'] = label_gdf.geometry.centroid

    # Extract positions
    x = label_gdf.centroid.x
    y = label_gdf.centroid.y
    l = label_gdf['NAME']

    # Plot
    fig, ax = plt.subplots(figsize=(12, 12))
    gdf_proj.plot(ax=ax, color=gdf_proj["color"], edgecolor="w", linewidth=0.25)
    texts = [
    ax.text(
        x.iloc[i],
        y.iloc[i],
        l.iloc[i],
        ha='center',
        va='center',
        zorder = 10,
        bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.3', alpha=0.9)
    )
    for i in range(len(l))
]

    for text in texts:
        if input_dist.lower() in text.get_text().lower():
            text.set_fontweight('bold')

    adjust_text(
        texts,
        expand=(1.2, 2),
        arrowprops=dict(arrowstyle="-|>", color='black'),
        only_move={'points': 'y', 'text': 'y'},
        force_text=0.5,
        force_points=0.5,
        lim=100,
        zorder = 2
    )

    title = f"School Districts Most Similar to {title_case_with_spaces(input_dist)}"
    if metric is not None:
        title += f" with {metric}"

    ax.set_title(title, fontsize=14)
    ax.axis("off")
    plt.tight_layout()
    plt.show()
