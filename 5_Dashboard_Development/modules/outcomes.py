# module: outcomes

from shiny import ui, render, module
from utils.mapOutcomes import options, suboptions
from shinywidgets import render_widget, output_widget
from utils.KNN_Outcome_Plots import plot_staar, plot_selections

map_outcome_plot_functions = {'STAAR Testing': plot_staar,
    'Dropout Rate': None,
    'Attendance': None,
    'Chronic Absenteeism': None,
    'College, Career, & Military Ready Graduates': None,
    '4-Year Longitudinal Graduation Rate': None,
    'AP/IB': None,
    'SAT/ACT': None}

@module.ui
def outcome_ui():
    return ui.nav_panel("Understand outcomes", 
        ui.layout_columns(
            ui.card(ui.card_header("View An Outcome"), ui.input_select("main_option", "Select a metric:", options, selected = "STAAR Testing"),
    ui.output_ui("suboption_ui")),
    ui.card(output_widget('outcome_plot')),
    col_widths=(3, 9)),
            value = "panel2"
    )

@module.server
def outcome_server(input, output, session, get_inputs, get_result):
    @output
    @render.ui
    def suboption_ui():
        selected = input.main_option()
        if selected in suboptions:
            return ui.input_radio_buttons("suboption", f"{selected} options:", suboptions[selected], selected = suboptions[selected][0])
        else:
            return None
        
    @output
    @render_widget
    def outcome_plot():
        selections = [input.main_option(), input.suboption()]
        plot_function = map_outcome_plot_functions[selections[0]]
        return plot_selections(plot_func = plot_function, neighbors=get_result()[2], year = get_inputs()['year'], subcategory= selections[1])

        