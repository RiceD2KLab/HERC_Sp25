# app.py
from shiny import App, ui, render, reactive
import pandas as pd
from KNN_Model import find_nearest_districts
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

# Mapping for the feature groups; keys are group names that users see,
# and the values are the corresponding lists of feature column names.
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
# List of group names for checkboxes.
feature_groups = list(feature_mapping.keys())

# Load the dataset (should have columns "DISTNAME" and "DISTRICT_id")
from getData import get_data
df = get_data(r"C:\Users\mmath\OneDrive\Desktop\Capstone", 2023)
district_choices = sorted(df["DISTNAME"].unique())

# Define the UI with a three-column layout.
# - Left: Inputs
# - Middle: Placeholder for visualizations
# - Right: Outputs the DataFrame from find_nearest_districts
app_ui = ui.page_fluid(
    ui.h2("Nearest Districts Finder Dashboard"),
    ui.row(
        ui.column(3,
            ui.h3("Inputs"),
            ui.input_select(
                "district_name", "Select District Name:",
                choices=district_choices, multiple=False
            ),
            ui.input_checkbox_group(
                "feature_groups", "Select Feature Groups:",
                choices=feature_groups
            ),
            ui.input_numeric("n_neighbors", "Number of Neighbors", value=5, min=1),
            ui.input_action_button("run", "Run Model")
        ),
        ui.column(6,
            ui.h3("Visualizations"),
            ui.tags.div("Placeholder for visualizations")
        ),
        ui.column(3,
            ui.h3("Nearest Districts"),
            ui.output_table("results")
        )
    )
)

def server(input, output, session):
    @reactive.event(input.run)
    def get_result():
        # Get the selected district name.
        selected_district_name = input.district_name()
        # Lookup the corresponding DISTRICT_id.
        district_id_lookup = df.loc[df["DISTNAME"] == selected_district_name, "DISTRICT_id"]
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
        print(f"  df: DataFrame with shape {df.shape}")
        print(f"  district_id: {district_id}")
        print(f"  feature_columns: {selected_features}")
        print(f"  n_neighbors: {n_neighbors}")

        # Run the model and return the resulting DataFrame.
        result = find_nearest_districts(
            df=df,
            district_id=district_id,
            feature_columns=selected_features,
            n_neighbors=n_neighbors
        )
        return result

    @output
    @render.table
    def results():
        # Only show a result once the button has been pressed.
        if input.run() == 0:
            return pd.DataFrame()
        return get_result()

# Create and run the Shiny app.
app = App(app_ui, server)

if __name__ == '__main__':
    app.run()
