from shiny import ui, render, module
from utils.dashboardVisuals import plot_texas_districts
from utils.helper import title_case_with_spaces

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
def match_server(input, output, session, get_result, get_inputs, demographics, ids):
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
        result = get_result()[2]
        print(result)

    @output()
    @render.ui
    def distmap():
        result = get_result()
        print(result[2]['DISTRICT_id'])
        level = input.level()
        return plot_texas_districts(result[2], result[0], level)