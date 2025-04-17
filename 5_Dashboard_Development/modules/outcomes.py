### MODULE: OUTCOMES ###

# =============================================================================
# 1. Imports
# =============================================================================
# Shiny
from shiny import ui, render, module, reactive
from shinywidgets import render_widget, output_widget

# Plotly
import plotly.graph_objs as go

# Local Imports
from utils.OutcomeUtils import (
    options, 
    suboptions,
    plot_selections,
    plot_ccmr_rates,
    plot_graduation_rate_bar,
    plot_attendance_rate_bar,
    plot_chronic_absenteeism_bar,
    plot_dropout_rates,
    plot_exclusive_staar_with_filters)


# =============================================================================
# 2. Constants / Configuration
# =============================================================================
# Mapping the UI input options to their respective functions
map_outcome_plot_functions = {
    'STAAR Testing': plot_exclusive_staar_with_filters,
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

# =============================================================================
# 3. Shiny UI
# =============================================================================
@module.ui
def outcome_ui():
    return ui.nav_panel("Understand outcomes", 
        ui.layout_columns(
            ui.card(
                ui.card_header("View An Outcome"),
                ui.input_select("main_option", "Select a metric:", options, selected="STAAR Testing"),
                ui.output_ui("suboption_ui")
            ),
            ui.card(
                output_widget('outcome_plot'),
                style="height: 620px;"  # Taller card for full plot visibility
            ),
            col_widths=(3, 9)
        ),
        ui.card(
            ui.p("If no bars appear or there are bars missing, it means that data is not available for that combination of variables. Please try selecting a different variable to explore available data.")
        ),
        value="panel2"
    )

# =============================================================================
# 4. Shiny Server
# =============================================================================
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
            return ui.input_radio_buttons("suboption", f"{selected} options:", suboptions[selected], selected = suboptions[selected][0])
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
        
        # Avoiding mismatches between the option and suboptions. 
        if main_option in suboptions:
            try:
                maybe_suboption = input.suboption()
                if maybe_suboption in suboptions[main_option]:
                    sub_option = maybe_suboption
                else:
                    print(f"⚠️ Ignoring unexpected suboption: {maybe_suboption}")
            except Exception as e:
                print(f"⚠️ Could not read suboption: {e}")
                # Load an empty plot while we wait for it to load
                return go.Figure().update_layout(title="Please wait...")

        print("Plotting for", main_option, "with suboption", sub_option)

        # If sub_option is still None and required by the plot, show a fallback
        if main_option in ['STAAR Testing', '4-Year Longitudinal Graduation Rate'] and sub_option is None:
            # Wait for the sub_option to be selected
            return go.Figure().update_layout(title="Loading your results...")
        

        plot_function = map_outcome_plot_functions[main_option]
        plot_function = map_outcome_plot_functions[main_option]

        # For STAAR, call the plot function directly with (df, neighbors, subject)
        if main_option == "STAAR Testing":
            return plot_function(result[0], result[2], sub_option)
        else:
            return plot_selections(
                plot_func=plot_function,
                neighbors=result[2],
                year=get_inputs()['year'],
                subcategory=sub_option
            )