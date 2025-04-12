import os
import re
import textwrap

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import ConnectionPatch

import geopandas as gpd

#New plotly graphs packages 
import plotly.express as px
import plotly.graph_objects as go


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


# Note the docstrings will be the same excited for the description moving forward. 
#Parameters, and returns will be left out in the remaining visualizations
def plot_race_ethnicity_stacked_bar(df, buckets, neighbors):
    """
    Interactive stacked bar chart for race/ethnicity distributions using Plotly.

    Parameters:
    - df (df): DataFrame of all districts and features.
    - buckets (dict): Dictionary of demographic buckets.
    - neighbors (df): DataFrame of neighbors DISTRICT_ID and DISTNAME.

    Returns:
    - Interactive Plotly figure
    """
    race_ethnicity_percent = buckets['race_ethnicity_percent']

    # Step 0: Locate the input district
    district_ids = list(neighbors['DISTRICT_id'])
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]

    # Step 1: Filter and prepare data
    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME'] + race_ethnicity_percent].dropna().reset_index(drop=True)
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return

    neighbors_df = selected_districts[selected_districts['DISTNAME'] != input_dist].copy()
    neighbors_df['group'] = 'Neighboring District'

    input_df = selected_districts[selected_districts['DISTNAME'] == input_dist].copy()
    input_df['group'] = 'Input District'

    combined_df = pd.concat([input_df, neighbors_df]).reset_index(drop=True)

    # Step 2: Calculate percentages
    combined_df["Total Students"] = combined_df[race_ethnicity_percent].sum(axis=1)
    for col in race_ethnicity_percent:
        combined_df[col] = (combined_df[col] / combined_df["Total Students"]) * 100

    # Step 3: Melt for Plotly
    melted_df = combined_df.melt(
        id_vars=["DISTNAME", "group"],
        value_vars=race_ethnicity_percent,
        var_name="Race/Ethnicity",
        value_name="Percentage"
    )

    # Optional: sort by input district on top
    melted_df["DISTNAME"] = pd.Categorical(
        melted_df["DISTNAME"],
        categories=combined_df["DISTNAME"],
        ordered=True
    )

    # Step 4: Plot
    fig = px.bar(
        melted_df,
        x="DISTNAME",
        y="Percentage",
        color="Race/Ethnicity",
        color_discrete_sequence= px.colors.qualitative.D3,
        hover_data={"group": True, "Percentage": ':.2f'},
        labels={"DISTNAME": "District", "Percentage": "Percentage (%)"},
        title=f"Race/Ethnicity % Distribution for Schools Similar to {title_case_with_spaces(input_dist)}"
    )

    fig.update_layout(
        barmode='stack',
        height=600,  # Increase vertical space
        xaxis_title="District",
        yaxis_title="Percentage (%)",
        legend_title="Race/Ethnicity",
        xaxis_tickangle=-35,
        legend=dict(x=1.05, y=0.5),
        margin=dict(r=180, t=60)
    )

    return fig


def plot_special_ed_504_bar(df, buckets, neighbors):
    """
    Interactive grouped bar chart for Special Ed and Section 504 percentages using Plotly.

    Parameters:
    - df (pd.DataFrame): DataFrame containing district demographic data.
    - buckets (dict): Dictionary containing 'special_ed_504' keys for plotting.
    - neighbors (pd.DataFrame): DataFrame of neighbors with DISTRICT_ID and DISTNAME.

    Returns:
    - Interactive Plotly figure
    """
    special_ed_504 = buckets['special_ed_504']

    # Step 0: Locate input district
    district_ids = list(neighbors['DISTRICT_id'])
    input_dist = df[df["DISTRICT_id"] == district_ids[0]]['DISTNAME'].iloc[0]

    # Step 1: Filter and structure data
    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME'] + special_ed_504].dropna().reset_index(drop=True)
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return

    neighbors_df = selected_districts[selected_districts['DISTNAME'] != input_dist].copy()
    neighbors_df['group'] = 'Neighboring District'

    input_df = selected_districts[selected_districts['DISTNAME'] == input_dist].copy()
    input_df['group'] = 'Input District'

    combined_df = pd.concat([input_df, neighbors_df]).reset_index(drop=True)

    # Step 2: Melt for Plotly
    melted_df = combined_df.melt(
        id_vars=["DISTNAME", "group"],
        value_vars=special_ed_504,
        var_name="Category",
        value_name="Percent"
    )

    # Clean up category names
    melted_df["Category"] = (
        melted_df["Category"]
        .str.replace("District 2022-23 ", "", regex=False)
        .str.replace(" Students Percent", "", regex=False)
    )

    # Step 3: Create interactive grouped bar chart
    fig = px.bar(
        melted_df,
        x="Category",
        y="Percent",
        color="DISTNAME",
        barmode="group",
        color_discrete_sequence=px.colors.qualitative.D3,
        hover_data={"group": True, "Percent": ':.2f'},
        labels={"Category": "Student Category", "Percent": "Percent of Students", "DISTNAME": "District"},
        title=f"Special Education and 504 Student Percentages<br><sup>Target District: {title_case_with_spaces(input_dist)}</sup>"
    )

    # Step 4: Formatting
    fig.update_layout(
        xaxis_title="Student Category",
        yaxis_title="Percent of Students",
        legend_title="District",
        xaxis_tickangle=30,
        height=500,
        margin=dict(r=160, t=80)
    )

    return fig


def plot_dot_stack(df, buckets, neighbors, unit_label="Student-Teacher Ratio"):
    """
    Dot-stack plot showing rounded units of the metric across districts.

    Parameters:
    - df: Full dataframe with all district info
    - buckets: Dict containing metric columns (e.g., 'student_teacher_ratio')
    - neighbors: DataFrame with DISTRICT_id and DISTNAME
    - unit_label: Label for the y-axis

    Returns:
    - Interactive Plotly dot stack plot
    """
    metric_col = buckets['student_teacher_ratio'][0]

    # Identify input district
    district_ids = list(neighbors['DISTRICT_id'])
    input_id = district_ids[0]
    input_dist = df[df["DISTRICT_id"] == input_id]['DISTNAME'].iloc[0]

    # Filter and prep data
    selected = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME', metric_col]].dropna().copy()
    selected["Group"] = selected["DISTRICT_id"].apply(lambda x: "Input District" if x == input_id else "Neighbor")
    selected[metric_col + "_rounded"] = selected[metric_col].round()

    # Sort: input district first
    selected['sort_order'] = selected['Group'].apply(lambda g: 0 if g == "Input District" else 1)
    selected = selected.sort_values(by=['sort_order', metric_col], ascending=[True, False])
    district_order = selected["DISTNAME"].tolist()

    # Build stacked dots
    dot_rows = []
    for _, row in selected.iterrows():
        for i in range(int(row[metric_col + "_rounded"])):
            dot_rows.append({
                "District": row["DISTNAME"],
                "Dot": i + 1,
                "Group": row["Group"],
                "Ratio": row[metric_col]
            })

    dot_df = pd.DataFrame(dot_rows)

    # Plot
    fig = px.scatter(
        dot_df,
        x="District",
        y="Dot",
        color="Group",
        hover_data={"Dot": False, "Group": False, "District": True, "Ratio": ':.2f'},
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={"Dot": unit_label, "District": "District"},
        title=f"{unit_label} for Districts Similar to {title_case_with_spaces(input_dist)}"
    )

    fig.update_traces(marker=dict(size=12), selector=dict(mode='markers'))

    fig.update_layout(
        height=500,
        yaxis=dict(title=unit_label, dtick=1, showgrid=False),
        xaxis=dict(title="District", categoryorder="array", categoryarray=district_order, showgrid=False),
        xaxis_tickangle=30,
        margin=dict(r=100, t=60),
        showlegend=True,
        plot_bgcolor="white"
    )

    return fig



def plot_staff_student_dumbbell(df, buckets, neighbors):
    """
    Creates a dumbbell plot comparing student and staff counts across input + neighboring districts.

    Parameters:
    - df: Full dataframe with DISTRICT_id, DISTNAME, staff and student count columns.
    - buckets: Dict containing 'staff_count' and 'student_count'.
    - neighbors: DataFrame of neighboring district IDs.

    Returns:
    - Interactive Plotly dumbbell plot.
    """
    staff_col = buckets['staff_count'][0]
    student_col = buckets['student_count'][0]

    district_ids = list(neighbors['DISTRICT_id'])
    input_id = district_ids[0]
    input_dist = df[df['DISTRICT_id'] == input_id]['DISTNAME'].iloc[0]

    # Filter and sort data
    selected = df[df['DISTRICT_id'].isin(district_ids)][['DISTNAME', staff_col, student_col]].dropna().copy()
    selected["Group"] = selected["DISTNAME"].apply(lambda x: "Input District" if x == input_dist else "Neighbor")
    selected = selected.sort_values(by=student_col, ascending=False)
    selected["DISTNAME"] = selected["DISTNAME"].apply(title_case_with_spaces)

    fig = go.Figure()

    # Add lines (the dumbbell connectors)
    for _, row in selected.iterrows():
        fig.add_trace(go.Scatter(
            x=[row[staff_col], row[student_col]],
            y=[row["DISTNAME"], row["DISTNAME"]],
            mode="lines",
            line=dict(color="#B0BEC5", width=2),
            showlegend=False,
            hoverinfo='skip'
        ))

    # Add staff markers (left side of dumbbell)
    fig.add_trace(go.Scatter(
        x=selected[staff_col],
        y=selected["DISTNAME"],
        mode="markers",
        name="Staff",
        marker=dict(color="#FF7F0E", size=12),
        hovertemplate="<b>%{y}</b><br>Staff Count: %{x:,}<extra></extra>"
    ))

    # Add student markers (right side of dumbbell)
    fig.add_trace(go.Scatter(
        x=selected[student_col],
        y=selected["DISTNAME"],
        mode="markers",
        name="Students",
        marker=dict(color="#1F77B4", size=12),
        hovertemplate="<b>%{y}</b><br>Student Count: %{x:,}<extra></extra>"
    ))

    fig.update_layout(
        title=f"Staff and Student Counts for Districts Similar to {title_case_with_spaces(input_dist)}",
        xaxis_title="Count",
        yaxis_title="District",
        height=600,
        margin=dict(r=100, t=60),
        plot_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        legend=dict(title="", orientation="h", x=0.35, y=-0.15)
    )

    return fig



def plot_special_populations_dropdown(df, buckets, neighbors):
    """
    Interactive dot plot with dropdown filter for special population categories.

    Parameters:
    - df: Full dataframe with DISTRICT_id, DISTNAME, and special population columns
    - buckets: Dict with 'special_populations_percent'
    - neighbors: DF with DISTRICT_ID and DISTNAME
    """
    special_cols = buckets['special_populations_percent']
    district_ids = list(neighbors['DISTRICT_id'])
    input_id = district_ids[0]
    input_dist = df[df['DISTRICT_id'] == input_id]['DISTNAME'].iloc[0]

    selected = df[df['DISTRICT_id'].isin(district_ids)][['DISTNAME'] + special_cols].dropna().copy()
    for col in special_cols:
        if selected[col].sum() == 0:
            selected.drop(columns=col, inplace=True)

    valid_cols = [col for col in special_cols if col in selected.columns]
    if selected.empty or not valid_cols:
        print("No valid data to plot.")
        return

    selected["Group"] = selected["DISTNAME"].apply(lambda x: "Input District" if x == input_dist else "Neighbor")
    selected["DISTNAME"] = selected["DISTNAME"].apply(title_case_with_spaces)

    melted_df = selected.melt(id_vars=["DISTNAME", "Group"], value_vars=valid_cols,
                              var_name="Category", value_name="Percent")
    melted_df["Category"] = (
        melted_df["Category"]
        .str.replace("District 2022-23 ", "", regex=False)
        .str.replace(" Students Percent", "", regex=False)
    )

    categories = melted_df["Category"].unique()
    base_category = categories[0]
    base_df = melted_df[melted_df["Category"] == base_category]

    fig = px.scatter(
        base_df,
        x="Percent",
        y="DISTNAME",
        symbol="Group",
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={"Percent": "Percent of Students", "DISTNAME": "District"},
        title=f"{base_category} Percentage for Districts Similar to {title_case_with_spaces(input_dist)}",
        hover_data={"Percent": ':.2f'},
    )

    fig.update_traces(marker=dict(size=11))
    fig.update_layout(showlegend=False)

    # FIXED: Use "title.text" instead of "title"
    buttons = []
    for cat in categories:
        df_cat = melted_df[melted_df["Category"] == cat]
        buttons.append(dict(
            label=cat,
            method="update",
            args=[
                {
                    "x": [df_cat["Percent"]],
                    "y": [df_cat["DISTNAME"]],
                },
                {
                    "title.text": f"{cat} Percentage for Districts Similar to {title_case_with_spaces(input_dist)}"
                }
            ]
        ))

    fig.update_layout(
        updatemenus=[dict(
            buttons=buttons,
            direction="down",
            showactive=True,
            x=1.01,
            xanchor="left",
            y=1,
            yanchor="top"
        )],
        height=600,
        xaxis=dict(title="Percent of Students", showgrid=False),
        yaxis=dict(title="District", showgrid=False),
        margin=dict(t=100, r=80, l=60, b=40),
        plot_bgcolor="white"
    )

    return fig

def plot_gifted_talented_horizontal_bar(df, buckets, neighbors):
    """
    Horizontal bar chart showing % of students in gifted and talented programs by district.
    Each district has its own unique color using the D3 palette.
    """
    col = buckets['gifted_students'][0]

    # Identify input district
    district_ids = list(neighbors['DISTRICT_id'])
    input_id = district_ids[0]
    input_dist = df[df['DISTRICT_id'] == input_id]['DISTNAME'].iloc[0]

    # Filter and prep
    selected = df[df['DISTRICT_id'].isin(district_ids)][['DISTNAME', col]].dropna().copy()
    selected["DISTNAME"] = selected["DISTNAME"].apply(title_case_with_spaces)

    # Sort: input district on top, then by value
    selected['sort_order'] = selected["DISTNAME"].apply(lambda x: 0 if x == title_case_with_spaces(input_dist) else 1)
    selected = selected.sort_values(by=['sort_order', col], ascending=[True, False])

    fig = px.bar(
        selected,
        x=col,
        y="DISTNAME",
        orientation='h',
        color="DISTNAME",
        color_discrete_sequence=px.colors.qualitative.D3,
        text=col,
        labels={col: "Percent of Students", "DISTNAME": "District"},
        title=f"Percent Students in Gifted and Talented Programs for Districts Similar to {title_case_with_spaces(input_dist)}"
    )

    fig.update_traces(
        texttemplate='%{text:.1f}%', 
        textposition='outside'
    )

    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        height=500,
        xaxis_title="Percent of Students",
        yaxis_title="",
        margin=dict(l=100, r=60, t=60, b=40),
        plot_bgcolor="white",
        showlegend=False  # Optional: turn on if you want color legend
    )

    return fig


def plot_economically_disadvantaged_horizontal(df, buckets, neighbors):
    """
    Interactive horizontal grouped bar chart showing economically disadvantaged percentages.
    """
    econ_cols = buckets['economically_disadvantaged']
    district_ids = list(neighbors['DISTRICT_id'])
    input_id = district_ids[0]
    input_dist = df[df['DISTRICT_id'] == input_id]['DISTNAME'].iloc[0]

    # Filter data
    selected = df[df['DISTRICT_id'].isin(district_ids)][['DISTNAME'] + econ_cols].dropna().copy()
    if selected.empty:
        print("No matching districts found. Check the district IDs.")
        return

    # Label group and clean district names
    selected["Group"] = selected["DISTNAME"].apply(lambda x: "Input District" if x == input_dist else "Neighboring District")
    selected["DISTNAME"] = selected["DISTNAME"].apply(title_case_with_spaces)

    # Reorder: input district first
    selected['sort_order'] = selected["Group"].apply(lambda g: 0 if g == "Input District" else 1)
    selected = selected.sort_values(by=['sort_order'] + econ_cols, ascending=[True] + [False]*len(econ_cols))

    # Melt data for grouped bar plotting
    melted_df = selected.melt(
        id_vars=["DISTNAME", "Group"],
        value_vars=econ_cols,
        var_name="Category",
        value_name="Percent"
    )

    # Clean column labels
    melted_df["Category"] = melted_df["Category"].str.replace("District 2022-23 ", "", regex=False).str.replace(" Students Percent", "", regex=False)

    # Plot
    fig = px.bar(
        melted_df,
        x="Percent",
        y="DISTNAME",
        color="Category",
        orientation='h',
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.D3,
        labels={"DISTNAME": "District", "Percent": "Percent of Students"},
        title=f"Economically Disadvantaged Percentages for Districts Similar to {title_case_with_spaces(input_dist)}",
        hover_data={"Percent": ':.2f'}
    )

    fig.update_layout(
        height=600,
        xaxis_title="Percent of Students",
        yaxis_title="",
        margin=dict(t=60, l=120, r=100),
        plot_bgcolor="white",
        legend_title="",
    )

    return fig



def plot_language_education_filterable_bar(df, buckets, neighbors):
    """
    Vertical bar chart with a dropdown filter to toggle between language education categories.
    """
    lang_cols = buckets['language_education_percent']
    district_ids = list(neighbors['DISTRICT_id'])
    input_id = district_ids[0]
    input_dist = df[df['DISTRICT_id'] == input_id]['DISTNAME'].iloc[0]

    # Prep and clean
    selected = df[df['DISTRICT_id'].isin(district_ids)][['DISTNAME'] + lang_cols].dropna().copy()
    if selected.empty:
        print("No matching districts.")
        return

    selected["Group"] = selected["DISTNAME"].apply(lambda x: "Input District" if x == input_dist else "Neighbor")
    selected["DISTNAME"] = selected["DISTNAME"].apply(title_case_with_spaces)
    selected['sort_order'] = selected["Group"].apply(lambda g: 0 if g == "Input District" else 1)
    selected = selected.sort_values(by=['sort_order'] + lang_cols, ascending=[True] + [False]*len(lang_cols))

    melted_df = selected.melt(
        id_vars=["DISTNAME", "Group"],
        value_vars=lang_cols,
        var_name="Category",
        value_name="Percent"
    )

    melted_df["Category"] = (
        melted_df["Category"]
        .str.replace("District 2022-23 ", "", regex=False)
        .str.replace(" Students Percent", "", regex=False)
    )

    categories = melted_df["Category"].unique()

    fig = go.Figure()

    # Add one trace per category, and use visibility toggle
    for i, cat in enumerate(categories):
        df_cat = melted_df[melted_df["Category"] == cat]

        visible = True if i == 0 else False

        fig.add_trace(go.Bar(
            x=df_cat["DISTNAME"],
            y=df_cat["Percent"],
            marker_color=df_cat["Group"].map({
                "Input District": "#1f77b4",
                "Neighbor": "#aec7e8"
            }),
            text=df_cat["Percent"].round(1),
            textposition='outside',
            name=cat,
            hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra></extra>",
            visible=visible
        ))

    # ✅ FIX: Replace "title" with "title.text" in update args
    buttons = []
    for i, cat in enumerate(categories):
        visible = [j == i for j in range(len(categories))]
        buttons.append(dict(
            label=cat,
            method="update",
            args=[
                {"visible": visible},
                {"title.text": f"{cat} Percentage for Districts Similar to {title_case_with_spaces(input_dist)}"}
            ]
        ))

    fig.update_layout(
        updatemenus=[dict(
            buttons=buttons,
            direction="down",
            x=1.01,
            xanchor="left",
            y=1,
            yanchor="top",
            showactive=True
        )],
        title_text=f"{categories[0]} Percentage for Districts Similar to {title_case_with_spaces(input_dist)}",  # ✅ Use title_text instead of title
        yaxis_title="Percent of Students",
        xaxis_title="District",
        xaxis_tickangle=35,
        height=600,
        margin=dict(t=80, r=100),
        plot_bgcolor="white",
        showlegend=False
    )

    return fig


