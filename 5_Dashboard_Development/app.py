from pathlib import Path
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shinywidgets import output_widget, render_widget
import plotly.express as px
import pandas as pd
from utils.shared import demographics, ids
from utils.KNN_Model import find_nearest_districts
from shinyswatch import theme
from modules import matches

from utils.Demographic_Buckets import demographic_buckets, bucket_options

from utils.Performance_Buckets import outcome_mapping

# List of group names for checkboxes.
feature_options = list(bucket_options.keys())

print(feature_options)

outcome_groups = list(outcome_mapping.keys())

district_choices = sorted(demographics["DISTNAME"].unique())

print(len(district_choices))

app_deps = ui.head_content(ui.tags.link(rel="icon", type="image/png", sizes="32x32", href="HERC_Logo_No_Text.png"))

app_ui = ui.page_navbar(
        app_deps,
        matches.matches_ui('matchpage'),
        ui.nav_panel("Why these districts?", "insert content here", value = "panel2"),
        ui.nav_panel("Understand outcomes", "insert content here", value = "panel3"),
        ui.nav_spacer(),
        ui.nav_control(ui.input_dark_mode(id="mode", mode = 'light')),
        title=ui.TagList(
            # Logo (image)
            ui.img(src="HERC_Logo_No_Text.png", height="30px"),
            # Title text next to the logo
            " DistrictMatch"
        ),  
        id="page",  
        sidebar = ui.sidebar(
            ui.input_select(
                "district_name", "Select District Name:",
                choices=district_choices, multiple=False
            ),
            ui.input_checkbox_group(
                "feature_groups", "Select Feature Groups:",
                choices=feature_options
            ),
            ui.input_numeric("n_neighbors", "Number of Neighbors", value=5, min=1),
            ui.input_numeric("year", "View Outcomes For", value=2023, min=2020),
            ui.input_action_button("run", "Run Model")),
        theme=theme.flatly # can be any of these: https://bootswatch.com/
    )  

def server(input, output, session):
    @reactive.effect
    @reactive.event(input.make_light)
    def _():
        ui.update_dark_mode("light")

    @reactive.effect
    @reactive.event(input.make_dark)
    def _():
        ui.update_dark_mode("dark")

    @reactive.event(input.run)
    def get_inputs():
        user_selected = {'DISTNAME':input.district_name(), 'buckets':input.feature_groups(), 'n': input.n_neighbors()}
        return user_selected

    @reactive.event(input.run)
    def get_result():
        if input.year() > 2023:
            return f"Unable to retrieve outcome data from {input.year()}"
        # Get the selected district name.
        selected_district_name = input.district_name()
        # Lookup the corresponding DISTRICT_id.
        district_id_lookup = demographics.loc[demographics["DISTNAME"] == selected_district_name, "DISTRICT_id"]

        if district_id_lookup.empty:
            print(f"DEBUG: District '{selected_district_name}' not found!")
            return pd.DataFrame({"Error": ["District not found!"]})
        district_id = district_id_lookup.iloc[0]

        n_neighbors = input.n_neighbors()

        buckets_selected = input.feature_groups()
        buckets = [bucket_options[key] for key in buckets_selected]
        # Debug print to output the parameters that will be passed to the model.
        print("DEBUG: Calling find_nearest_districts with:")
        print(f"  district_id: {type(district_id)}")

        # Run the model and return the resulting DataFrame.
        result = find_nearest_districts(
            year=input.year(),
            district_id=district_id,
            feature_columns=buckets,
            n_neighbors=n_neighbors
        )
        return result
        
    matches.match_server("matchpage", get_result, get_inputs, demographics, ids)


static_dir = Path(__file__).parent / "static"
app = App(app_ui, server, static_assets=static_dir)

if __name__ == '__main__':
    app.run()