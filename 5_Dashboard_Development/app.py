from pathlib import Path
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shinywidgets import output_widget, render_widget
import plotly.express as px
import pandas as pd
from utils.shared import demographics, ids
from utils.KNN_Model import find_nearest_districts
from shinyswatch import theme
from modules import matches, why_districts, outcomes

from utils.Demographic_Buckets import bucket_options

from utils.Performance_Buckets import outcome_mapping

# List of group names for checkboxes.
feature_options = list(bucket_options.keys())

outcome_groups = list(outcome_mapping.keys())

district_choices = sorted(ids[ids['Charter School (Y/N)'] == 'N']["DISTNAME"].unique())

app_deps = ui.head_content(
    ui.tags.link(rel="icon", type="image/png", sizes="32x32", href="HERC_Logo_No_Text.png"),
    ui.tags.link(href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap", rel="stylesheet")  # Google Font link
)

app_ui = ui.page_navbar(
    app_deps,
 ui.nav_panel(
    "About District Match", 
      ui.div(
            ui.img(src=str("Logo300x300.png"), height="300px"),  # Logo image
            style="text-align: center; margin-bottom: 20px;"  # Center-align the logo
        ),
    ui.TagList(
        ui.HTML("""
            <h3><strong>About DistrictMatch</strong></h3>
            <p>The District Match App is the creation of Team Kinder HERC from Rice University's Data to Knowledge Lab. The purpose of the app is to assist school districts in finding similar districts (neighbors) based upon their chosen demographic metrics. The tabs which will assist in district matching are “View My Matches”, “Why These Districts”, and “Understand Outcomes”. Furthermore, there is the 
             "How To Use" page which will directly explain how to navigate each of the DistrictMatch pages. </p>
            <h4><strong>View My Matches</strong></h4>
            <p>The "View My Matches" tab allows you to find districts similar to your selected district. You can view a specified number of matched districts. </p>                        
            <h4><strong>Why These Districts?</strong></h4>
            <p>The "Why These Districts" tab explains why your selected district was matched with specific neighboring districts. It provides visualizations that highlight similarities in key demographic features, allowing for more direct and meaningful comparisons across selected feature groups. </p>
            <h4><strong>Understand Outcomes</strong></h4> 
            <p>The "Understand Outcomes" tab serves as  way to view specific comparisons between your selected district and its neighboring districts based on certain outcomes data such as STAAR testing results, attendance, dropout rate and more.  </p>
        """)
    )
), ui.nav_panel(
    "How To Use DistrictMatch", 
    ui.TagList(
        ui.HTML("""    
            <h1 style="text-align:center; margin-bottom: 30px;">How To Use Each DistrictMatch Page</h1>
                
            <figure style="text-align:center;">
                <img src="ViewMyMatches.png" alt="View My Matches Overview" style="max-width:45%; height:auto;">
                <figcaption style="margin-top: 10px; font-style: italic; color: #555;">View my matches page example</figcaption>
            </figure>

            <h3><strong>Using "View my matches" tab </strong></h3>
            <ul>
                <li>On the left-hand side panel first choose a district under "Select District Name". This will act as the district you are finding similar districts to. </li>
                <li>Select the feature groups under "Select Feature Group" to choose the demographic characteristics you consider important when identifying similar districts. </li>
                <li>Choose how many similar districts you'd like to view by selecting a value under "Number of Neighbors". </li>
                <li>Under "View Outcomes For," select the academic year you want to base the data on. For example, choosing 2024 will reflect data from the 2023–24 academic year. </li>
                <li>Click the "Run Model" Button to populate neighbor districts. </li>
                <li>Once the modeling is done you will be able to view a map of the resulting neighboring districts by district or county level. </li>
                <li>The table on the far right will also display the districts that are most similar to your districts based on your selected parameters. </li>
            </ul>  
            <figure style="text-align:center;">
                <img src="WhyTheseDistricts.png" alt="Why These Districts Overview" style="max-width:45%; height:auto;">
                <figcaption style="margin-top: 10px; font-style: italic; color: #555;">Why these districts? page example</figcaption>
            </figure>    
            <h3><strong>Using "Why These Districts?" tab </strong></h3>
            <ul>
                <li>This page displays visualizations that show how your selected district compares to its neighbors in terms of key demographic features. </li>
                <li>The similarity of these plots depends on the feature groups you selected when running the matching model. </li>
                <li>You can choose which specific demographic plots to view by toggling the checkboxes at the top of the page.</li>
            </ul>    
            <figure style="text-align:center;">
                <img src="UnderstandOutcomes.png" alt="Understand Outcomes Overview" style="max-width:45%; height:auto;">
                <figcaption style="margin-top: 10px; font-style: italic; color: #555;">Understand outcomes page example</figcaption>
            </figure>    
            <h3><strong>Using Understand outcomes</strong></h3>
            <ul>
                <li>This page displays visualizations taht show how your selected district compares to its neighbors in terms of key outcome features. </li>
                <li>Using the "View An Outcome" dropdown, select which outcome variable you want to explore among neighbors. Make sure to toggle additional information if requested. </li>
            </ul>   
        """) #note to add pictures here
    )
), 
    ui.head_content(
        ui.include_css(Path(__file__).parent / "static" / "ricetheme.css")
    ),
        matches.matches_ui('matchpage'),
        why_districts.why_districts_ui('demographicpage'),
        #ui.nav_panel("Why these districts?", "insert content here", value = "panel2"),
        outcomes.outcome_ui('outcomepage'),
        ui.nav_spacer(),
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
            ui.input_numeric("year", "View Outcomes For", value=2024, min=2020, max = 2024),
            ui.input_action_button("run", "Run Model")),
            theme = theme.flatly,
    )  

def server(input, output, session):
    result_data = reactive.value(None)

    @reactive.event(input.run)
    def get_inputs():
        user_selected = {'DISTNAME':input.district_name(), 'buckets':input.feature_groups(), 'n': input.n_neighbors(), 'year': input.year()}
        return user_selected
    
    @reactive.event(input.run)
    def test_button_click():
        print("DEBUG: Button clicked!")

    @reactive.effect
    @reactive.event(input.run)
    def get_result():
        # Get the selected district name.
        selected_district_name = input.district_name()
        # Lookup the corresponding DISTRICT_id.
        district_id_lookup = ids.loc[ids["DISTNAME"] == selected_district_name, "DISTRICT_id"]

        if district_id_lookup.empty:
            print(f"DEBUG: District '{selected_district_name}' not found!")
            return pd.DataFrame({"Error": ["District not found!"]})
        district_id = district_id_lookup.iloc[0]

        n_neighbors = input.n_neighbors()

        buckets_selected = input.feature_groups()
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
        
    matches.match_server("matchpage", result_data, get_inputs)
    why_districts.why_districts_server("demographicpage", result_data, get_inputs)
    outcomes.outcome_server("outcomepage", get_inputs, result_data)


static_dir = Path(__file__).parent / "static"
app = App(app_ui, server, static_assets=static_dir)

if __name__ == '__main__':
    app.run()