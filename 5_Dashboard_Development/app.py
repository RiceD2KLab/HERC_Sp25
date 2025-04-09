from shiny import App, ui, reactive
from shinywidgets import output_widget, render_widget
import plotly.express as px
import pandas as pd
from shared import demographics, performance
from KNN_Model import find_nearest_districts
from dashboardVisuals import dash_map

from Demographic_Buckets import (
    student_teacher_ratio,
    student_count,
    staff_count,
    race_ethnicity_percent,
    economically_disadvantaged,
    special_ed_504,
    language_education_percent,
    special_populations_percent,
    gifted_students
)

from Performance_Buckets import sat_act, ap_ib, longitudinal_graduation_rates, chronic_absenteeism, attendance_rates, ccmr_rates, dropout_rates, staar_results, district_identifiers

feature_mapping = {
    "Student Teacher Ratio": student_teacher_ratio,
    "Student Count": student_count,
    "Staff Count": staff_count,
    "Race/Ethnicity Student %": race_ethnicity_percent,
    "Economically Disadvantaged Student %": economically_disadvantaged,
    "Special Education / 504 Student %": special_ed_504,
    "Language Education Student %": language_education_percent,
    "Special Populations Student %": special_populations_percent,
    "Gifted Student %": gifted_students
}

outcome_mapping = {
    "SAT/ACT": sat_act,
    "AP/IB": ap_ib,
    "Longitudinal Graduation Rates": longitudinal_graduation_rates,
    "Chronic Absenteeism": chronic_absenteeism,
    "Attendance Rates": attendance_rates,
    "CCMR Rates": ccmr_rates,
    "Dropout Rates": dropout_rates,
    "STAAR Results": staar_results,
    "District Identifiers": district_identifiers
}

# List of group names for checkboxes.
feature_groups = list(feature_mapping.keys())

outcome_groups = list(outcome_mapping.keys())

district_choices = sorted(demographics["DISTNAME"].unique())

app_ui = ui.page_navbar(
        ui.nav_panel("View my matches", output_widget("distmap")),
        ui.nav_panel("Why these districts?", "insert content here"),
        ui.nav_panel("Understand outcomes", "insert content here"),
        title="DistrictMatch",  
        id="page",  
        sidebar = ui.sidebar(
            ui.input_select(
                "district_name", "Select District Name:",
                choices=district_choices, multiple=False
            ),
            ui.input_checkbox_group(
                "feature_groups", "Select Feature Groups:",
                choices=feature_groups
            ),
            ui.input_numeric("n_neighbors", "Number of Neighbors", value=5, min=1),
            ui.input_action_button("run", "Run Model"), 
            ui.input_select(
                "outcomes", "View Outcome:",
                choices=outcome_groups, multiple=False
            ),
            bg="#ffffff"),
        navbar_options=ui.navbar_options(bg = "#4D9AD4")
    )  

def server(input, output, session):
    @reactive.event(input.run)
    def get_result():
        # Get the selected district name.
        selected_district_name = input.district_name()
        # Lookup the corresponding DISTRICT_id.
        district_id_lookup = demographics.loc[demographics["DISTNAME"] == selected_district_name, "DISTRICT_id"]
        if district_id_lookup.empty:
            print(f"DEBUG: District '{selected_district_name}' not found!")
            return pd.DataFrame({"Error": ["District not found!"]})
        district_id = district_id_lookup.iloc[0]

        # Get the selected feature groups and aggregate feature columns.
        selected_feature_groups = input.feature_groups()
        selected_features = []
        for group in selected_feature_groups:
            selected_features.extend(feature_mapping[group])

        n_neighbors = input.n_neighbors()

        # Debug print to output the parameters that will be passed to the model.
        print("DEBUG: Calling find_nearest_districts with:")
        print(f"  df: DataFrame with shape {demographics.shape}")
        print(f"  district_id: {district_id}")
        print(f"  feature_columns: {selected_features}")
        print(f"  n_neighbors: {n_neighbors}")

        # Run the model and return the resulting DataFrame.
        result = find_nearest_districts(
            df=demographics,
            district_id=district_id,
            feature_columns=selected_features,
            n_neighbors=n_neighbors
        )
        return result
    @render_widget()  
    def distmap(): 
        fig = dash_map(demographics, get_result()) 
        print("ran fig func")
        return fig

app = App(app_ui, server)

if __name__ == '__main__':
    app.run()