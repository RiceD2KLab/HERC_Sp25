### DISTRICTMATCH APP ###

# =============================================================================
# 1. Imports
# =============================================================================
# Shiny
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shinyswatch import theme

# Other Imports
from pathlib import Path
import pandas as pd

# Local Imports
from utils.KNN_Model import find_nearest_districts
from utils.AppUtils import bucket_options, ids
from modules import matches, why_districts, outcomes, about, howto


# =============================================================================
# 2. Constants and Settings
# =============================================================================
# List of group names for checkboxes
feature_options = list(bucket_options.keys())

ids2 = ids.copy()

# Find which DISTNAMEs are duplicated
dupes = ids2['DISTNAME'].duplicated(keep=False)

# Create new ID: combine DISTNAME and CNTYNAME if duplicated, otherwise just DISTNAME
ids2['ID'] = ids2.apply(
    lambda row: f"{row['DISTNAME']} ({row['CNTYNAME']})" if dupes[row.name] else row['DISTNAME'],
    axis=1
)

district_choices = sorted(ids2[ids2['Charter School (Y/N)'] == 'N']["ID"].unique())

app_deps = ui.head_content(
    ui.tags.link(rel="icon", type="image/png", sizes="32x32", href="HERC_Logo_No_Text.png"),
    ui.tags.link(href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap", rel="stylesheet")  # Google Font link
)

# =============================================================================
# 3. App UI
# =============================================================================
app_ui = ui.page_navbar(
    app_deps,
    ui.head_content(
        ui.include_css(Path(__file__).parent / "static" / "ricetheme.css")
    ),
    about.about_ui('about'),
    howto.howto_ui('howto'),
    matches.matches_ui('matchpage'),
    why_districts.why_districts_ui('demographicpage'),
    outcomes.outcome_ui('outcomepage'),
    ui.nav_spacer(),
    title=ui.TagList(
            # Logo (image)
            ui.img(src="HERC_Logo_No_Text.png", height="40px"),
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
            ui.input_numeric("year", "View Outcomes For", value=2024, min=2020, max = 2024),
            ui.input_action_button("run", "Run Model"),
            width = 300),
    theme = theme.flatly,
    )  

# =============================================================================
# 4. App Server
# =============================================================================
def server(input, output, session):
    # Creating a reactive value to save all of the nearest neighbor results
    result_data = reactive.value(None)

    # Saving user's inputs for use in the module servers
    @reactive.event(input.run)
    def get_inputs():
        user_selected = {'DISTNAME':input.district_name(), 
                         'buckets':input.feature_groups(), 
                         'n': input.n_neighbors(), 
                         'year': input.year()}
        return user_selected

    # Test
    @reactive.event(input.run)
    def test_button_click():
        print("DEBUG: Button clicked!")

    # When user clicks run model button, this runs the nearest neighbors model
    @reactive.effect
    @reactive.event(input.run)
    def get_result():
        # Get the selected district name.
        selected_district_name = input.district_name()
        print("the selected district is", selected_district_name)
        # Lookup the corresponding DISTRICT_id.
        district_id_lookup = ids2.loc[ids2["ID"] == selected_district_name, "DISTRICT_id"]

        if district_id_lookup.empty:
            print(f"DEBUG: District '{selected_district_name}' not found!")
            return pd.DataFrame({"Error": ["District not found!"]})
        district_id = district_id_lookup.iloc[0]

        n_neighbors = input.n_neighbors() + 1

        buckets_selected = input.feature_groups()
        if not buckets_selected:
            print("DEBUG: No feature groups selected!")
            # Show an error modal asking the user to select at least one feature group
            m = ui.modal(
                    "Please select at least one feature group before running the model.",
                    title= "Error",
                    easy_close=True
                )
            ui.modal_show(m)  
            return "None"
        buckets = [bucket_options[key] for key in buckets_selected]
        # Debug print to output the parameters that will be passed to the model.
        print("DEBUG: Calling find_nearest_districts with:")
        print(f"  district_id: {district_id}")
        # Run the model and return the resulting DataFrame.
        result = find_nearest_districts(
            year=input.year(),
            district_id=district_id,
            feature_columns=buckets,
            n_neighbors=n_neighbors
        )
        df, features_used, neighbors_list = result
        # Store all 3 in one dictionary
        result_data.set({
            0: df,
            1: features_used,
            2: neighbors_list
        })

        return "Model run complete"
    
    # Server for the matches page
    matches.match_server("matchpage", result_data, get_inputs)

    # Server for the why districts page
    why_districts.why_districts_server("demographicpage", result_data, get_inputs)

    # Server for the outcomes page
    outcomes.outcome_server("outcomepage", get_inputs, result_data)


# Setting the directory to locate images, stylesheet, etc.
static_dir = Path(__file__).parent / "static"
app = App(app_ui, server, static_assets=static_dir)

if __name__ == '__main__':
    app.run()
