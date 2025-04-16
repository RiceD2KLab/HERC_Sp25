# module: outcomes

from shiny import ui, render, module, reactive
from utils.mapOutcomes import options, suboptions
from shinywidgets import render_widget, output_widget
from utils.KNN_Outcome_Plots import plot_staar, plot_selections, plot_ccmr_rates, plot_graduation_rate_bar, plot_attendance_rate_bar, plot_chronic_absenteeism_bar, plot_dropout_rates
import plotly.graph_objs as go

map_outcome_plot_functions = {'STAAR Testing': plot_staar,
    'Dropout Rate': plot_dropout_rates,
    'Attendance': plot_attendance_rate_bar,
    'Chronic Absenteeism': plot_chronic_absenteeism_bar,
    'College, Career, & Military Ready Graduates': plot_ccmr_rates,
    '4-Year Longitudinal Graduation Rate': plot_graduation_rate_bar}

# temporarily excluding IB/AP and SAT/ACT
options = [
    'STAAR Testing',
    'Dropout Rate',
    'Attendance',
    'Chronic Absenteeism',
    'College, Career, & Military Ready Graduates',
    '4-Year Longitudinal Graduation Rate']

@module.ui
def outcome_ui():
    return ui.nav_panel("Understand outcomes", 
        ui.layout_columns(
            ui.card(ui.card_header("View An Outcome"), ui.input_select("main_option", "Select a metric:", options, selected = "STAAR Testing"),
    ui.output_ui("suboption_ui")),
    ui.card(output_widget('outcome_plot')),
    col_widths=(3, 9)),
    ui.card(ui.p("If no bars appear, it means that data is not available for that combination of variables. Please try selecting a different variable to explore available data.")),
            value = "panel2"
    )

@module.server
def outcome_server(input, output, session, get_inputs, run_result):
    @reactive.Calc
    def current_suboptions():
        return suboptions[input.main_option()]

    @output
    @render.ui
    def suboption_ui():
        selected = input.main_option()
        if selected in suboptions and selected == 'STAAR Testing':
            return ui.input_radio_buttons("suboption", f"{selected} options:", suboptions[selected], selected = suboptions[selected][0]), ui.p("Students who achieve Approaches Grade Level or higher on STAAR have passed the test, so it includes both Meets and Masters Grade Level categories.")
        elif selected in suboptions:
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
        sub_option = None
        
        if main_option in suboptions:
            # Try to get suboption safely
            try:
                maybe_suboption = input.suboption()
                if maybe_suboption in suboptions[main_option]:
                    sub_option = maybe_suboption
                else:
                    print(f"⚠️ Ignoring unexpected suboption: {maybe_suboption}")
            except Exception as e:
                print(f"⚠️ Could not read suboption: {e}")
                return go.Figure().update_layout(title="Please wait...")

        print("Plotting for", main_option, "with suboption", sub_option)

        # If sub_option is still None and required by the plot, show a fallback
        if main_option in ['STAAR Testing', '4-Year Longitudinal Graduation Rate'] and sub_option is None:
            return go.Figure().update_layout(title="Loading your results...")

        plot_function = map_outcome_plot_functions[main_option]
        return plot_selections(plot_func = plot_function, neighbors=result[2], year = get_inputs()['year'], subcategory= sub_option)