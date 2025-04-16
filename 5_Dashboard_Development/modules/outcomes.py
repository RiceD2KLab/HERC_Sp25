# module: outcomes

from shiny import ui, render, module
from utils.mapOutcomes import options, suboptions
from shinywidgets import render_widget, output_widget
from utils.KNN_Outcome_Plots import plot_staar, plot_selections, plot_ccmr_rates, plot_graduation_rate_bar, plot_attendance_rate_bar, plot_chronic_absenteeism_bar, plot_dropout_rates
import plotly.graph_objs as go

map_outcome_plot_functions = {'STAAR Testing': plot_staar,
    'Dropout Rate': plot_dropout_rates,
    'Attendance': plot_attendance_rate_bar,
    'Chronic Absenteeism': plot_chronic_absenteeism_bar,
    'College, Career, & Military Ready Graduates': plot_ccmr_rates,
    '4-Year Longitudinal Graduation Rate': plot_graduation_rate_bar,
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
def outcome_server(input, output, session, get_inputs, run_result):
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
        result = run_result.get()
        print("Plotting outcomes...")
        if result is None or len(result) != 3:
            return go.Figure().update_layout(title="Run a model to view outcomes.")
        result[0]['DISTRICT_id'] = result[0]['DISTRICT_id'].astype(str)
        result[2]['DISTRICT_id'] = result[2]['DISTRICT_id'].astype(str)
        print("these are the neighbors")
        print(result[2])
        main_option = input.main_option()
        sub_option = input.suboption() if main_option in suboptions else None
        # print(selections)
        print(main_option, sub_option)
        plot_function = map_outcome_plot_functions[main_option]
        return plot_selections(plot_func = plot_function, neighbors=result[2], year = get_inputs()['year'], subcategory= sub_option)