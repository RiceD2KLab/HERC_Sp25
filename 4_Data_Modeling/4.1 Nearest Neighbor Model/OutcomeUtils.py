### OUTCOME PAGE DEPENDENCIES ###

# =============================================================================
# 1. Imports
# =============================================================================
# Standard Imports
import re
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

# Other Imports
from getData import load_data_from_github, engineer_performance, get_subject_level_exclusive_scores
from AppUtils import title_case_with_spaces

# =============================================================================
# 2. Constants / Configuration
# =============================================================================
# The following lists and dictionaries have been used to map the data to the outcomes UI.
options = [
    'STAAR Testing',
    'Dropout Rate',
    'Attendance',
    'Chronic Absenteeism',
    'College, Career, & Military Ready Graduates',
    '4-Year Longitudinal Graduation Rate',
    'AP/IB',
    'SAT/ACT'
]

suboptions = {
    'STAAR Testing': ['Mathematics',
                      'Reading/ELA',
                      'Science', 
                      'Social Studies'
                      ],
    '4-Year Longitudinal Graduation Rate': ['RHSP/DAP or FHSP-E/DLA', 
                                            'FHSP-DLA Graduates'],
    'SAT/ACT': ['Graduates Above Criterion', 
                'Students Above Criterion', 
                'Test Taking']
}

demographics = {
    'All':'All Students',
    'African American':'African American',
    'White': 'White',
    'Econ Disadv': 'Economically Disadvantaged',
    'Special Ed': 'Special Education',
    'EB/EL': 'Emergent Bilingual/English Learner',
    'Hispanic': 'Hispanic'
}

demographic_string_patterns = {
    'AP/IB': {'Course Completion Graduates': r"AP/IB Course Completion Graduates: (.*) Rate",
              'Test Taking':  r'AP/IB: (.*) \((All Subjects)\) % Taking'}, 
            #   'Students Above Criterion': r"AP/IB: (.*) \((All Subjects)\) % Above Criterion"},
    'SAT/ACT': {'Test Taking':r'SAT/ACT: (.*), % Test-Taking', 
                'Graduates Above Criterion':r'SAT/ACT: (.*), % Graduates Above Criterion', 
                'Students Above Criterion':r"SAT/ACT: (.*?), % Above Criterion"},
    '4-Year Longitudinal Graduation Rate': {'RHSP/DAP or FHSP-E/DLA':r"for (.*) Rate$",
                                            'FHSP-DLA Graduates': r"for (.*) Rate$"},
    'College, Career, & Military Ready Graduates': r'College, Career, & Military Ready Graduates: (.*) Rate',
    'Dropout Rate': r'(.*) Dropout Rate',
    'Attendance': r'Attendance: (.*) Rate',
    'Chronic Absenteeism': r'Chronic Absenteeism (.*) Group: Rate'
}

# =============================================================================
# 3. Functions
# =============================================================================
# --- MASTER PLOTTING FUNCTION ---
def plot_selections(plot_func, neighbors, year, subcategory = None):
    """
    Function that takes a DistrictMatch outcomes plotting function as input and 
    plots the input data according to that function. 

    Inputs:
        plot_func (function): function that returns a plotly figure object with inputs neighbors, year, subcategory.
        neighbors (pd.DataFrame): DataFrame with a 'DISTRICT_id' column.
        year (int): a 4-digit year (YYYY) from 2020-2024.
        subcategory (str): specifies what user selected as the subcategory to view from the main option (see suboptions)

    Returns:
        A 'plotly.graph_objs._figure.Figure' object that is returned by the input function. 
    """
    return plot_func(neighbors, year, subcategory)


# --- GRADUATION RATES ---
def plot_graduation_rate_bar(neighbors, year, subcategory):
    """
    DistrictMatch plot function that plots the graduation rates for one of two subcategories.

    Inputs:
        neighbors (pd.DataFrame): DataFrame with a 'DISTRICT_id' column.
        year (int): a 4-digit year (YYYY) from 2020-2024.
        subcategory (str): specifies what user selected as the subcategory 
                            (either 'RHSP/DAP or FHSP-E/DLA' or 'FHSP-DLA Graduates')

    Returns: 
        A 'plotly.graph_objs._figure.Figure' object that shows graduation rates.
    """
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
                  color_discrete_sequence=px.colors.qualitative.Safe)


# --- ATTENDANCE RATES ---
def plot_attendance_rate_bar(neighbors, year, subcategory=None):
    """
    DistrictMatch plot function that plots the attendance rates for different demographics. 

    Inputs:
        neighbors (pd.DataFrame): DataFrame with a 'DISTRICT_id' column.
        year (int): a 4-digit year (YYYY) from 2020-2024.
        subcategory (None): set to None, as there are no suboptions for attendance rates.

    Returns: 
        A 'plotly.graph_objs._figure.Figure' object that shows attendance rates.
    """
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
                  color_discrete_sequence=px.colors.qualitative.Safe)


# --- CHRONIC ABSENTEEISM RATES ---
def plot_chronic_absenteeism_bar(neighbors, year, subcategory=None):
    """
    DistrictMatch plot function that plots the chronic absenteeism rates for different demographics. 

    Inputs:
        neighbors (pd.DataFrame): DataFrame with a 'DISTRICT_id' column.
        year (int): a 4-digit year (YYYY) from 2020-2024.
        subcategory (None): set to None, as there are no suboptions for chronic absenteeism.

    Returns: 
        A 'plotly.graph_objs._figure.Figure' object that shows chronic absenteeism.
    """
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
                  color_discrete_sequence=px.colors.qualitative.Safe)


# --- DROPOUT RATES ---
def plot_dropout_rates(neighbors, year, subcategory=None):
    """
    DistrictMatch plot function that plots the dropout rates for different demographics. 

    Inputs:
        neighbors (pd.DataFrame): DataFrame with a 'DISTRICT_id' column.
        year (int): a 4-digit year (YYYY) from 2020-2024.
        subcategory (None): set to None, as there are no suboptions for dropout rates.

    Returns: 
        A 'plotly.graph_objs._figure.Figure' object that shows dropout rates.
    """
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
                  color_discrete_sequence=px.colors.qualitative.Safe)


# --- CCMR RATES ---
def plot_ccmr_rates(neighbors, year, subcategory = None):
    """
    DistrictMatch plot function that plots the College, Career, and Military Readiness (CCMR) 
    rates for different demographics. 

    Inputs:
        neighbors (pd.DataFrame): DataFrame with a 'DISTRICT_id' column.
        year (int): a 4-digit year (YYYY) from 2020-2024.
        subcategory (None): set to None, as there are no suboptions for CCMR rates.

    Returns: 
        A 'plotly.graph_objs._figure.Figure' object that shows CCMR rates.
    """
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
    df_long['DISTNAME'] = df_long['DISTNAME'].apply(title_case_with_spaces)
    print("post-transformations data", df_long.shape)
    fig = px.bar(df_long, 
                 x='DISTNAME', y='Rate', color = 'Demographic',
                 color_discrete_sequence=px.colors.qualitative.Safe,
                 title="College, Career, & Military Ready Graduate Rates By Demographic Group",
        labels= {"DISTNAME": "District"},
        barmode = 'group')
    return(fig)

# --- STAAR RATES ---
def get_subject_level_exclusive_scores(df, subject):
    """
    Returns mutually exclusive STAAR scores (Approaches only, Meets only, Masters, Did Not Meet) by grade level
    for a given subject.

    Args:
        df (pd.DataFrame): Raw district-level STAAR dataset.
        subject (str): One of ['Mathematics', 'Reading/ELA', 'Writing', 'Science', 'Social Studies'].

    Returns:
        pd.DataFrame: Long-format dataframe with DISTNAME, DISTRICT_id, Grade, and exclusive performance levels.
    """
    # Step 1: Build level mapping dynamically
    level_mapping = {
        'Approaches': [col for col in df.columns if subject in col and 'Approaches Grade Level' in col and "Rate" in col and "All Students" in col],
        'Meets': [col for col in df.columns if subject in col and 'Meets Grade Level' in col and "Rate" in col and "All Students" in col],
        'Masters': [col for col in df.columns if subject in col and 'Masters Grade Level' in col and "Rate" in col and "All Students" in col],
    }

    if not any(level_mapping.values()):
        print(f"Warning: No data available for subject '{subject}'.")
        return None

    # Step 2: Create long DataFrames per level
    def melt_level(level):
        cols = level_mapping[level]
        df_level = df[['DISTNAME', 'DISTRICT_id'] + cols].copy()
        df_long = df_level.melt(id_vars=['DISTNAME', 'DISTRICT_id'], value_vars=cols,
                                var_name='raw_column', value_name=level)
        df_long['Grade'] = df_long['raw_column'].str.extract(r'Grade (\d+)')
        return df_long.drop(columns='raw_column')

    df_approaches = melt_level('Approaches')
    df_meets = melt_level('Meets')
    df_masters = melt_level('Masters')

    # Step 3: Merge the levels on DISTRICT, DISTNAME, and Grade
    merged = df_approaches.merge(df_meets, on=['DISTNAME', 'DISTRICT_id', 'Grade'], how='inner')
    merged = merged.merge(df_masters, on=['DISTNAME', 'DISTRICT_id', 'Grade'], how='inner')

    # Step 4: Compute mutually exclusive performance levels
    merged['Masters Grade Level'] = merged['Masters']
    merged['Meets Grade Level'] = merged['Meets'] - merged['Masters']
    merged['Approaches Grade Level'] = merged['Approaches'] - merged['Meets']
    merged['Did Not Meet Grade Level'] = 100 - merged['Approaches']

    # Optional: Round values and reorder
    result = merged[['DISTNAME', 'DISTRICT_id', 'Grade', 'Approaches Grade Level', 'Meets Grade Level', 'Masters Grade Level', 'Did Not Meet Grade Level']]
    return result.round(2)


def plot_exclusive_staar_with_filters(df, neighbors, subject):
    """
    Creates an interactive stacked bar chart of mutually exclusive STAAR scores,
    filtered by neighbor districts and a given subject, with an internal grade dropdown.

    Args:
        df (pd.DataFrame): Full raw STAAR dataset.
        neighbors (pd.DataFrame): DataFrame with a 'DISTRICT_id' column.
        subject (str): Subject to show ['Mathematics', 'Reading/ELA', 'Writing', 'Science', 'Social Studies'].

    Returns:
        plotly.graph_objects.Figure: Interactive Plotly figure with grade-level filtering.
    """
    neighbor_ids = list(neighbors['DISTRICT_id'])

    # Step 1: Get exclusive scores for the given subject
    staar_df = get_subject_level_exclusive_scores(df, subject)

    if staar_df is None or staar_df.empty:
        return go.Figure().add_annotation(
            text=f"No STAAR data available for subject: {subject}",
            showarrow=False,
            font=dict(size=18),
            xref="paper", yref="paper", x=0.5, y=0.5
        )

    staar_df = staar_df[staar_df['DISTRICT_id'].isin(neighbor_ids)].copy()
    staar_df['Subject'] = subject
    staar_df['DISTNAME'] = staar_df["DISTNAME"].apply(title_case_with_spaces)
    # Step 2: Grade options
    grade_options = sorted(staar_df['Grade'].dropna().unique(), key=lambda x: int(x))

    # Step 3: Set up trace categories
    categories = ['Did Not Meet Grade Level', 'Approaches Grade Level', 'Meets Grade Level', 'Masters Grade Level']
    colors = ['#d62728', '#ff7f0e', '#1f77b4', '#2ca02c']
    fig = go.Figure()
    trace_map = {}
    trace_count = 0

    for grade in grade_options:
        key = f"Grade {grade}"
        subset = staar_df[staar_df['Grade'] == grade]
        trace_map[key] = []

        for cat, color in zip(categories, colors):
            fig.add_trace(go.Bar(
                x=subset['DISTNAME'],
                y=subset[cat],
                name=cat,
                visible=False,
                marker_color=color
            ))
            trace_map[key].append(trace_count)
            trace_count += 1

    # Step 4: Dropdown menu for Grade with proper title update
    dropdown_buttons = []
    for grade in grade_options:
        key = f"Grade {grade}"
        vis = [False] * trace_count
        for i in trace_map[key]:
            vis[i] = True
        dropdown_buttons.append(dict(
            label=key,
            method="update",
            args=[
                {"visible": vis},
                {"title.text": f"{subject} STAAR Performance – Grade {grade}"}
            ]
        ))

    # Step 5: Final layout adjustments
    fig.update_layout(
        title={"text": f"{subject} STAAR Performance – Grade {grade_options[0]}"},
        legend=dict(
                    title="Performance Level",
                    orientation="h",  # make it horizontal
                    x=0.5,
                    xanchor="center",
                    y=-0.2,
                    yanchor="top"
                ),
        updatemenus=[{
            "buttons": dropdown_buttons,
            "direction": "down",
            "showactive": True,
            "x": 0.98,
            "xanchor": "right",
            "y": 1.12,
            "yanchor": "top"
        }],
        barmode='stack',
        xaxis_title="District",
        yaxis_title="Percentage of Students"
    )

    # Step 6: Show default trace (first grade)
    first_key = f"Grade {grade_options[0]}"
    for i in trace_map[first_key]:
        fig.data[i].visible = True
    
    return fig

# --- SAT/ACT Rates ---
def plot_sat_act(neighbors, year, subcategory="Graduates Above Criterion"):
    """
    DistrictMatch plot function for SAT/ACT metrics.

    Inputs:
        neighbors (pd.DataFrame): DataFrame with a 'DISTRICT_id' column.
        year (int): a 4-digit year (YYYY) from 2020-2024.
        subcategory (str): must be one of ['Graduates Above Criterion', 'Students Above Criterion', 'Test Taking']

    Returns: 
        A 'plotly.graph_objs._figure.Figure' object that shows SAT/ACT outcome by demographic.
    """
    df = engineer_performance(year)
    district_ids = list(neighbors["DISTRICT_id"])
    df = df[df["DISTRICT_id"].astype(str).isin(district_ids)]
    
    # Determine correct match substring instead of just using subcategory
    match_substring = {
        "Graduates Above Criterion": "% Graduates Above Criterion",
        "Students Above Criterion": "% Above Criterion",
        "Test Taking": "% Test-Taking"
    }[subcategory]

    # Only pull columns for the selected year and metric
    cols = [col for col in df.columns if f"District {year - 1}" in col and "SAT/ACT" in col and match_substring in col]
    print("SAT/ACT matched columns:", cols)

    if not cols:
        print(f"No SAT/ACT columns matched for subcategory: {subcategory}. Try checking the actual column names in the dataset.")

    # Keep DISTNAME, DISTRICT_id, and the SAT/ACT columns
    df = df[["DISTNAME", "DISTRICT_id"] + cols].copy()
    df["DISTNAME"] = df["DISTNAME"].apply(title_case_with_spaces)

    # Rename columns using the regex match
    pattern = demographic_string_patterns['SAT/ACT'][subcategory]
    rename_dict = {col: re.search(pattern, col).group(1) for col in cols if re.search(pattern, col)}
    print("SAT/ACT rename_dict:", rename_dict)
    df.rename(columns=rename_dict, inplace=True)

    # Match renamed columns to demographics using fuzzy containment
    demographic_values = [v.lower() for v in demographics.values()]
    columns_to_keep = [col for col in df.columns if any(demo in col.lower() for demo in demographic_values)]
    columns_to_keep += ['DISTNAME']

    # Drop groups with no data
    print("Column sums before filtering:", df[columns_to_keep].sum(skipna=True))
    columns_to_keep = [column for column in columns_to_keep if df[column].sum(skipna=True) != 0]
    print("SAT/ACT columns_to_keep:", columns_to_keep)

    # Debug: show raw values for selected columns
    print(df[["DISTNAME"] + columns_to_keep])
    print("SAT/ACT NaN counts:\n", df[columns_to_keep].isna().sum())

    # Melt for plotly
    melted = df.drop(columns=["DISTRICT_id"]).melt(id_vars=["DISTNAME"], value_vars=columns_to_keep,
                                                    var_name="Group", value_name="Rate")

    return px.bar(melted, x="DISTNAME", y="Rate", color="Group", barmode="group",
                  title=f"SAT/ACT – {subcategory} by Group", labels={"DISTNAME": "District"},
                  color_discrete_sequence=px.colors.qualitative.Safe)

# --- AP/IB Metrics  ---
def plot_ap_ib_performance(neighbors, year, subcategory=None):
    """
    Interactive bar chart showing AP/IB % Above Criterion across districts,
    with % Taking shown in hover. Subjects and years are dynamically inferred.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Dataset containing AP/IB % Taking and % Above Criterion for each subject.

    neighbors : pandas.DataFrame
        DataFrame with 'DISTRICT_id' to filter districts.

    Returns:
    --------
    plotly.graph_objs.Figure
        Interactive Plotly chart for Shiny with subject filter and hover info.
    """
    data = load_data_from_github(year)
    df = data[0]
    df['DISTRICT_id'] = df['DISTRICT_id'].astype(str)
    apib_df = df[df['DISTRICT_id'].isin(neighbors['DISTRICT_id'])].copy()
    apib_df['DISTNAME'] = [title_case_with_spaces(dist) for dist in apib_df['DISTNAME']]
    districts = apib_df['DISTNAME']
    # --- Dynamically find all relevant AP/IB columns ---
    relevant_cols = [
        col for col in df.columns
        if "AP/IB" in col and "All Students" in col and 
        ("% Students Above Criterion" in col or "% Taking" in col)
    ]

    # --- Extract subjects and years from column names ---
    subjects = set()
    years = set()

    for col in relevant_cols:
        match = re.search(r"District (\d{4}) AP/IB: All Students \((.*?)\)", col)
        if match:
            year, subject = match.groups()
            subjects.add(subject)
            years.add(year)

    subjects = sorted(subjects)
    year = max(years)  # Use most recent year

    # --- Build column maps for the selected year ---
    col_taking = {
        subj: f'District {year} AP/IB: All Students ({subj}) % Taking' for subj in subjects
    }
    col_above = {
        subj: f'District {year} AP/IB: All Students ({subj}) % Students Above Criterion' for subj in subjects
    }

    # --- Create plot ---
    fig = go.Figure()

    for i, subj in enumerate(subjects):
        visible = (i == 0)

        hover_text = (
            "District: " + districts +
            "<br>% Above Criterion: " + apib_df[col_above[subj]].round(1).astype(str) + "%" +
            "<br>% Taking: " + apib_df[col_taking[subj]].round(1).astype(str) + "%"
        )

        fig.add_trace(go.Bar(
            x=districts,
            y=apib_df[col_above[subj]],
            name=subj,
            text=apib_df[col_above[subj]].round(1).astype(str) + '%',
            textposition='auto',
            marker_color='seagreen',
            visible=visible,
            hovertext=hover_text,
            hoverinfo='text'
        ))

    # --- Dropdown buttons ---
    buttons = []
    for i, subj in enumerate(subjects):
        visibility = [False] * len(subjects)
        visibility[i] = True

        buttons.append(dict(
            label=subj,
            method='update',
            args=[{'visible': visibility}]
        ))

    # --- Final layout ---
    fig.update_layout(
        updatemenus=[dict(
            buttons=buttons,
            direction='down',
            showactive=True,
            x=0.98,
            xanchor='right',
            y=1.15,
            yanchor='top'
        )],
        title=f"AP/IB Performance ({year}): % Above Criterion by District<br><sup>(Hover for % Taking)</sup>",
        xaxis_title='District',
        yaxis_title='% Students Above Criterion',
        yaxis=dict(range=[0, 100]),
        template='plotly_white',
        showlegend=False
    )

    return fig

