from shiny import ui, render, module
from utils.dashboardVisuals import plot_texas_districts
from utils.helper import title_case_with_spaces
import pandas as pd

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

@module.server
def match_server(input, output, session, run_result, get_inputs):
    @output
    @render.ui
    def link_to_why():
        if get_inputs():
            return ui.p("The model identified the following districts as being the most similar to yours based on the inputs you selected."), ui.a("Understand why these districts are similar", href="#panel2")
        else:
            return ui.NULL  # Do not show the link if the condition is not met
    @output()
    @render.data_frame
    def results_df():
        result = run_result.get()
        if result is None or len(result) != 3:
            return render.DataGrid(pd.DataFrame({"District": ['Waiting for model results. Run a model to view neighbors.']}))
        neighbor_names = result[2]['DISTNAME']
        print("Rendering matches table...")

        df = result[0][['DISTNAME', 'TEA Description', 'CNTYNAME']]
        df.columns = ['District', 'TEA District Type', 'County']
        for_table = df[df['District'].isin(neighbor_names)].copy()
        for_table['District'] = [title_case_with_spaces(distname) for distname in for_table['District']]
        for_table['County'] = [title_case_with_spaces(cty) for cty in for_table['County']]
        return render.DataGrid(for_table, width = '100%')

    @output()
    @render.ui
    def distmap():
        result = run_result.get()
        if result is None or len(result) != 3:
            return ui.p("Run a model to view the map.")
        level = input.level()
        print("Rendering map...")
        return plot_texas_districts(result[2], result[0], level)