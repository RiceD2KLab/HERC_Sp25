import os
import re
import textwrap

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import ConnectionPatch

def plot_graduation_rate_bar(neighbors, year, subcategory):
    df = engineer_performance(year)
    district_ids = list(neighbors["DISTRICT_id"])
    pattern = demographic_string_patterns['4-Year Longitudinal Graduation Rate'][subcategory]

    df = df[df["DISTRICT_id"].astype(str).isin(district_ids)]
    cols = [col for col in df.columns if "4-Year Longitudinal" in col and subcategory in col]
    df = df[["DISTNAME", "DISTRICT_id"] + cols].copy()
    df["DISTNAME"] = df["DISTNAME"].apply(title_case_with_spaces)

    rename_dict = {col: re.search(pattern, col).group(1) for col in cols}
    df.rename(columns=rename_dict, inplace=True)

    columns_to_keep = [value for value in demographics.values() if value in df.columns]
    columns_to_keep += ['DISTNAME']

    columns_to_keep = [column for column in columns_to_keep if df[column].sum() != 0]
    print(columns_to_keep)

    melted = df.drop(columns=["DISTRICT_id"]).melt(id_vars=["DISTNAME"], var_name="Group", value_name="Rate", value_vars = columns_to_keep)
    print(df[["DISTNAME"] + list(rename_dict.values())])
    return px.bar(melted, x="DISTNAME", y="Rate", color="Group", barmode="group",
                  title="4-Year Longitudinal Graduation Rate by Group", labels={"DISTNAME": "District"},
                  color_discrete_sequence=px.colors.qualitative.G10)


def plot_attendance_rate_bar(neighbors, year, subcategory=None):
    df = engineer_performance(year)
    district_ids = list(neighbors["DISTRICT_id"])
    pattern = demographic_string_patterns['Attendance']

    df = df[df["DISTRICT_id"].astype(str).isin(district_ids)]
    cols = [col for col in df.columns if "Attendance" in col and "Rate" in col]
    df = df[["DISTNAME", "DISTRICT_id"] + cols].copy()
    df["DISTNAME"] = df["DISTNAME"].apply(title_case_with_spaces)

    rename_dict = {col: re.search(pattern, col).group(1) for col in cols if re.search(pattern, col)}
    df.rename(columns=rename_dict, inplace=True)

    columns_to_keep = [value for value in demographics.values() if value in df.columns]
    columns_to_keep += ['DISTNAME']

    columns_to_keep = [column for column in columns_to_keep if df[column].sum() != 0]
    print(columns_to_keep)
    melted = df.drop(columns=["DISTRICT_id"]).melt(id_vars=["DISTNAME"], var_name="Group", value_name="Rate", value_vars = columns_to_keep)
    print(df[["DISTNAME"] + list(rename_dict.values())])
    return px.bar(melted, x="DISTNAME", y="Rate", color="Group", barmode="group",
                  title="Attendance Rate by Group", labels={"DISTNAME": "District"},
                  color_discrete_sequence=px.colors.qualitative.G10)


def plot_chronic_absenteeism_bar(neighbors, year, subcategory=None):
    df = engineer_performance(year)
    district_ids = list(neighbors["DISTRICT_id"])
    pattern = demographic_string_patterns['Chronic Absenteeism']

    df = df[df["DISTRICT_id"].astype(str).isin(district_ids)]
    cols = [col for col in df.columns if "Chronic Absenteeism" in col and "Rate" in col]
    df = df[["DISTNAME", "DISTRICT_id"] + cols].copy()
    df["DISTNAME"] = df["DISTNAME"].apply(title_case_with_spaces)

    rename_dict = {col: re.search(pattern, col).group(1) for col in cols if re.search(pattern, col)}
    df.rename(columns=rename_dict, inplace=True)
    columns_to_keep = [value for value in demographics.values() if value in df.columns]
    columns_to_keep += ['DISTNAME']

    columns_to_keep = [column for column in columns_to_keep if df[column].sum() != 0]
    print(columns_to_keep)
    melted = df.drop(columns=["DISTRICT_id"]).melt(id_vars=["DISTNAME"], var_name="Group", value_name="Rate", value_vars = columns_to_keep)
    print(df[["DISTNAME"] + list(rename_dict.values())])
    return px.bar(melted, x="DISTNAME", y="Rate", color="Group", barmode="group",
                  title="Chronic Absenteeism by Group", labels={"DISTNAME": "District"},
                  color_discrete_sequence=px.colors.qualitative.G10)


def plot_dropout_rates(neighbors, year, subcategory=None):
    df = engineer_performance(year)
    district_ids = list(neighbors["DISTRICT_id"])
    pattern = demographic_string_patterns['Dropout Rate']

    df = df[df["DISTRICT_id"].astype(str).isin(district_ids)]
    cols = [col for col in df.columns if "Dropout Rate" in col]
    df = df[["DISTNAME", "DISTRICT_id"] + cols].copy()
    df["DISTNAME"] = df["DISTNAME"].apply(title_case_with_spaces)

    rename_dict = {col: re.search(pattern, col).group(1) for col in cols if re.search(pattern, col)}
    df.rename(columns=rename_dict, inplace=True)

    columns_to_keep = [value for value in demographics.values() if value in df.columns]
    columns_to_keep += ['DISTNAME']

    columns_to_keep = [column for column in columns_to_keep if df[column].sum() != 0]
    print(columns_to_keep)
    melted = df.drop(columns=["DISTRICT_id"]).melt(id_vars=["DISTNAME"], var_name="Group", value_name="Rate", value_vars = columns_to_keep)
    print(df[["DISTNAME"] + list(rename_dict.values())])
    return px.bar(melted, x="DISTNAME", y="Rate", color="Group", barmode="group",
                  title="Dropout Rate by Group", labels={"DISTNAME": "District"},
                  color_discrete_sequence=px.colors.qualitative.G10)


# BEGIN INTERACTIVE PLOTTING 

import plotly.express as px
from utils.getData import engineer_performance
from utils.mapOutcomes import suboptions, options
import re
from utils.helper import title_case_with_spaces

def plot_staar(neighbors, year, subject):
    
    district_ids = list(neighbors['DISTRICT_id'])
    df = engineer_performance(year)
    print("Engineer performance shape",df.shape)
    string_pattern = next((x for x in suboptions['STAAR Testing'] if x == subject), None)
    # First select relevant columns
    df_selected_outcome = df.filter(regex=f"({string_pattern}|DISTNAME|DISTRICT_id)")
    df_selected_outcome['DISTRICT_id'] = df_selected_outcome['DISTRICT_id'].astype(str)
    print("Selected relevant columns shape", df_selected_outcome.shape)
    # get only neighbors
    df_filtered = df_selected_outcome[df_selected_outcome['DISTRICT_id'].isin(district_ids)].copy()
    print("Only neighbors shape", df_filtered.shape)
    df_filtered.columns = [
    re.sub(r'^.*\((Masters|Approaches|Meets) Grade Level\)$', r'\1 Grade Level', col)
    for col in df_filtered.columns
    ]   
    df_filtered = df_filtered.copy()
    df_filtered['DISTNAME'] = [title_case_with_spaces(distname) for distname in df_filtered['DISTNAME']]
    print("Pre-long shape", df_filtered.shape)
    other_cols = ['Masters Grade Level', 'Meets Grade Level', 'Approaches Grade Level']
    df_long = df_filtered.melt(id_vars=["DISTNAME", "DISTRICT_id"], value_vars=other_cols, var_name="Category", value_name="Rate")
    df_long = df_long.copy()
    df_long['District'] = df_long['DISTNAME']
    print("post-transformations data", df_long.shape)
    category_order = ['Approaches Grade Level', 'Meets Grade Level', 'Masters Grade Level']

    fig = px.bar(df_long, 
                 x='District', y='Rate', color = 'Category',
                 color_discrete_sequence=px.colors.qualitative.Set1,
                 title=f"{subject} STAAR Performance for All Grade Levels",
        category_orders={'Category': category_order},
        barmode = "group")
    return(fig)

from utils.mapOutcomes import demographic_string_patterns, demographics

def plot_ccmr_rates(neighbors, year, subcategory):
    district_ids = list(neighbors['DISTRICT_id'])
    df = engineer_performance(year)
    print("Engineer performance shape",df.shape)
    df_selected_outcome = df.filter(regex=f"(College, Career, & Military Ready Graduates|DISTNAME|DISTRICT_id)")
    df_selected_outcome['DISTRICT_id'] = df_selected_outcome['DISTRICT_id'].astype(str)
    df_filtered = df_selected_outcome[df_selected_outcome['DISTRICT_id'].isin(district_ids)].copy()
    
    print(df_filtered)
    df_renamed = df_filtered.rename(columns={
    col: re.search(demographic_string_patterns['College, Career, & Military Ready Graduates'], col).group(1)
    for col in df_filtered.columns if re.search(demographic_string_patterns['College, Career, & Military Ready Graduates'], col)
})
    columns_to_keep = [value for value in demographics.values() if value in df_renamed.columns]
    columns_to_keep += ['DISTNAME', 'DISTRICT_id']

    filtered_df = df_renamed[columns_to_keep]
    columns_to_keep = [column for column in columns_to_keep if filtered_df[column].sum() != 0]
    df_long = filtered_df.melt(id_vars=["DISTNAME", "DISTRICT_id"], value_vars=columns_to_keep, var_name="Demographic", value_name="Rate")
    print("post-transformations data", df_long.shape)
    fig = px.bar(df_long, 
                 x='DISTNAME', y='Rate', color = 'Demographic',
                 color_discrete_sequence=px.colors.qualitative.G10,
                 title="College, Career, & Military Ready Graduate Rates By Demographic Group",
        labels= {"DISTNAME": "District"},
        barmode = 'group')
    return(fig)

def plot_selections(plot_func, neighbors, year, subcategory = None):
    return plot_func(neighbors, year, subcategory)


import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
from utils.getData import get_subject_level_averages

def plot_staar2(df, neighbors):
    """
    Generates an interactive Plotly bar chart showing STAAR performance levels 
    (Approaches, Meets, Masters Grade Level) for selected districts across 
    different subjects. Users can filter by subject using a dropdown.

    Parameters:
    -----------
    df : pandas.DataFrame
        The full dataset containing subject-level STAAR performance columns and district identifiers.
        Must include columns like 'Mathematics (Approaches Grade Level)', etc.

    neighbors : pandas.DataFrame
        A DataFrame containing a column 'DISTRICT_id' which lists district IDs to include in the plot.

    Returns:
    --------
    plotly.graph_objs.Figure
        An interactive grouped bar chart with a dropdown filter to toggle between STAAR subjects.
    """

    staar_df = get_subject_level_averages(df)
    neighbor_ids = list(neighbors['DISTRICT_id'])

    # Filter to only include selected districts
    staar_df = staar_df[staar_df['DISTRICT_id'].isin(neighbor_ids)]

    # Define subjects and performance levels
    subjects = ['Mathematics', 'Reading/ELA', 'Writing', 'Science', 'Social Studies']
    levels = ['Approaches Grade Level', 'Meets Grade Level', 'Masters Grade Level']

    # Predefine traces and buttons
    data = []
    buttons = []

    for i, subject in enumerate(subjects):
        traces = []
        for level in levels:
            col = f"{subject} ({level})"
            trace = go.Bar(
                x=staar_df['DISTNAME'],
                y=staar_df[col],
                name=level,
                visible=(i == 0)  # Only show the first subject initially
            )
            traces.append(trace)
            data.append(trace)

        # Create visibility mask for this subject
        visibility = [False] * len(subjects) * len(levels)
        for j in range(len(levels)):
            visibility[i * len(levels) + j] = True

        button = dict(
            label=subject,
            method="update",
            args=[{"visible": visibility},
                  {"title": f"STAAR Performance for {subject}"}]
        )
        buttons.append(button)

    layout = go.Layout(
        title="STAAR Performance for Mathematics",
        barmode='group',
        xaxis_title="District Name",
        yaxis_title="Percent of Students",
        updatemenus=[dict(
            active=0,
            buttons=buttons,
            x=1.1,
            xanchor="left",
            y=1.15,
            yanchor="top"
        )]
    )

    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(legend_title_text="Performance Level", height=600)
    return fig
