### MATCHES PAGE ###

# =============================================================================
# 1. Imports
# =============================================================================
# Standard Imports
from shiny import ui, render, module
import pandas as pd

# Local Imports
from utils.matchUtils import plot_texas_districts, generate_table

# =============================================================================
# 2. Matches UI
# =============================================================================
@module.ui
def matches_ui():
    return ui.nav_panel("View my matches", 
        ui.layout_columns(
            ui.card(ui.card_header("Where Are My Matches Located?"),
                    ui.input_radio_buttons("level",  
                                "View Map Results By:",  
                                {"district": "District", "county": "County"}, 
                                inline = True),
                    ui.output_ui("distmap"),
                    full_screen=True),
            ui.card(ui.output_ui("link_to_why"), ui.output_data_frame("results_df"), fillable = True),
            col_widths=(7, 5)),
            value = "panel1"
    )

# =============================================================================
# 3. Matches Server
# =============================================================================
@module.server
def match_server(input, output, session, run_result, get_inputs):
    @output
    @render.ui
    def link_to_why():
        if get_inputs():
            return ui.p("The model identified the following districts as being the most similar to yours based on the inputs you selected.")
        else:
            return ui.NULL 
    @output()
    @render.data_frame
    def results_df():
        result = run_result.get()
        if result is None or len(result) != 3:
            return render.DataGrid(pd.DataFrame({"District": ['Waiting for model results. Run a model to view neighbors.']}))
        for_table = generate_table(result[2], result[0])
        return render.DataGrid(for_table, width = '100%')

    @output()
    @render.ui
    def distmap():
        result = run_result.get()
        if result is None or len(result) != 3:
            return ui.p("Run a model to view the map.")
        result[0]['DISTRICT_id'] = result[0]['DISTRICT_id'].astype(str)
        result[2]['DISTRICT_id'] = result[2]['DISTRICT_id'].astype(str)
        level = input.level()
        print("Rendering map...")
        return plot_texas_districts(result[2], result[0], level)