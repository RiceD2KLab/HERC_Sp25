import os
import re
import textwrap

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import ConnectionPatch

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

import plotly.express as px
from utils.getData import engineer_performance
from utils.mapOutcomes import suboptions, options
import re
from utils.helper import title_case_with_spaces

def plot_staar(neighbors, year, subject):
    
    district_ids = list(neighbors['DISTRICT_id'])
    df = engineer_performance(year)
    string_pattern = next((x for x in suboptions['STAAR Testing'] if x == subject), None)
    # First select relevant columns
    df_selected_outcome = df.filter(regex=f"({string_pattern}|DISTNAME|DISTRICT_id)")

    # get only neighbors
    df_filtered = df_selected_outcome[df_selected_outcome['DISTRICT_id'].isin(district_ids)].copy()
    df_filtered.columns = [
    re.sub(r'^.*\((Masters|Approaches|Meets) Grade Level\)$', r'\1 Grade Level', col)
    for col in df_filtered.columns
    ]   
    df_filtered = df_filtered.copy()
    df_filtered['DISTNAME'] = [title_case_with_spaces(distname) for distname in df_filtered['DISTNAME']]
    other_cols = ['Masters Grade Level', 'Meets Grade Level', 'Approaches Grade Level']
    df_long = df_filtered.melt(id_vars=["DISTNAME", "DISTRICT_id"], value_vars=other_cols, var_name="Category", value_name="Percent")
    df_long = df_long.copy()
    df_long['District'] = df_long['DISTNAME']
    print(df_long)
    category_order = ['Approaches Grade Level', 'Meets Grade Level', 'Masters Grade Level']

    fig = px.bar(df_long, 
                 x='District', y='Percent', color = 'Category',
                 color_discrete_sequence=px.colors.qualitative.Set1,
                 title=f"{subject} STAAR Performance for All Grade Levels",
        labels= {"Percent": "Percent of Students"},
        category_orders={'Category': category_order})
    return(fig)

from utils.mapOutcomes import demographic_string_patterns, demographics

def plot_ccmr_rates(neighbors, year, subcategory):
    district_ids = list(neighbors['DISTRICT_id'])
    df = engineer_performance(year)
    df_selected_outcome = df.filter(regex=f"(College, Career, & Military Ready Graduates|DISTNAME|DISTRICT_id)")
    df_filtered = df_selected_outcome[df_selected_outcome['DISTRICT_id'].isin(district_ids)].copy()
    df_renamed = df_filtered.rename(columns={
    col: re.search(demographic_string_patterns['College, Career, & Military Ready Graduates'], col).group(1)
    for col in df_filtered.columns if re.search(demographic_string_patterns['College, Career, & Military Ready Graduates'], col)
})
    columns_to_keep = [value for value in demographics.values() if value in df_renamed.columns]
    columns_to_keep += ['DISTNAME', 'DISTRICT_id']

    filtered_df = df_renamed[columns_to_keep]

    df_long = filtered_df.melt(id_vars=["DISTNAME", "DISTRICT_id"], value_vars=columns_to_keep, var_name="Demographic", value_name="Rate")
    fig = px.bar(df_long, 
                 x='DISTNAME', y='Rate', color = 'Demographic',
                 color_discrete_sequence=px.colors.qualitative.G10,
                 title="College, Career, & Military Ready Graduate Rates By Demographic Group",
        labels= {"DISTNAME": "District"},
        barmode = 'group')
    return(fig)

def plot_selections(plot_func, neighbors, year, subcategory = None):
    return plot_func(neighbors, year, subcategory)
