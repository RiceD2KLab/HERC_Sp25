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
            <p>The District Match App is the creation of Team Kinder HERC from Rice University. The purpose of the app is to assist school districts in finding similar districts based upon their chosen metrics. The tabs which will assist in district matching are “View My Matches”, “Why These Districts”, and “Understand Outcomes”. Furthremore there is the 
             "How To Use" page which will directly expplain how to navigate each of the DistrictMatch pages. </p>
            <h4><strong>View My Matches</strong></h4>
            <p>The View My Matches tab is to directly find a match to your district of choice based upon selected buckets of measurement categories such as Student Teacher Ratio, Staff Count Student Demographics, and more. Which will then allow you to select and see a selected number of similar districts based on a certain set of outcomes. </p>                        
            <h4><strong>Why These Districts?</strong></h4>
            <p>The tab for Why These Districts will give an explanation as to why you received the matching neighboring districts. On the page there are the options to select specific visuals for feature groups for more direct distrcit comparisons. </p>
            <h4><strong>Understand Outcomes</strong></h4> 
            <p>The Understand Outcomes page serves as  way to view specifc comparisons between your selected distrcit and its closest neighbors based on certain outcomes such as STARR testing, attendance, dropout rate and more.  </p>
        """)
    )
), ui.nav_panel(
    "How To Use DistrictMatch", 
    ui.TagList(
        ui.HTML("""    
            <h3><strong>Using View my matches</strong></h3>
            <ul>
                <li>On the left-hand side panel first choose a distrcit under "Select District Name". </li>
                <li>Choose the feature group for distrcitcomparison under "Select Feature Group". </li>
                <li>Pick a number of neighbors (districts) you want to see under "Number of Neighbors". </li>
                <li>Under "View Outcomes For" choose a specific year of outcomes of which districts will be. </li>
                <li>Click the Run Model Button. </li>
                <li>Once the modeling is done you will be able to view a map of the resulting neighboring distrcts by district or county level. </li>
                <li>Additionally on the far right will be a table listing the districts that are most similar to your selection based on the parameters. </li>
            </ul>  
            <h3><strong>Using Why These Districts? </strong></h3>
            <ul>
                <li>Press Run Model once again on the left hand tab panel with the selection process as for the "View my matches" page. </li>
                <li>In the middle of the page there will be checkboxes to select specific feature groups to visualize. </li>
                <li>Once the features are selected multiple graphs will pop up showing a comparison between your distrcit and other similar districts for the feature groups. </li>
                <li>Under "View Outcomes For" choose a specific year of outcomes of which districts will be. </li>
            </ul>    
            <h3><strong>Using Understand outcomes</strong></h3>
            <ul>
                <li>Follow the first five steps of "View my matches". </li>
                <li> Navigate to the middle of the page under "View An Outcome" and pic one of seven outcomes of visually compare. </li>
                <li>Once a metric is selected look below to see if there are further options to to specify. In the case of STAAR Testing there will be four testing subjects which you can select to see. </li>
                <li>Wait for the model to run and graphed visuals of the your selected district and similar districts will show up with their respective results for your chosen outcome. </li>
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
            ui.input_numeric("year", "View Outcomes For", value=2023, min=2020),
            ui.input_action_button("run", "Run Model")),
            theme = theme.flatly
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