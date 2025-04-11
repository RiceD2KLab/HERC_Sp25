# module: outcomes

from shiny import ui, render, module
from utils.mapOutcomes import options, suboptions, get_available_demographics

@module.ui
def outcome_ui():
    return ui.nav_panel("Understand outcomes", 
        ui.layout_columns(
            ui.card(ui.card_header("View An Outcome"), ui.input_select("main_option", "Select a metric:", options, selected = "STAAR Testing"),
    ui.output_ui("suboption_ui"),
    ui.output_ui("demographic_options")),
    ui.card(),
    col_widths=(3, 9)),
            value = "panel2"
    )

@module.server
def outcome_server(input, output, session, get_inputs):
    @output
    @render.ui
    def suboption_ui():
        selected = input.main_option()
        if selected in suboptions:
            return ui.input_radio_buttons("suboption", f"{selected} options:", suboptions[selected], selected = suboptions[selected][0])
        else:
            return None

    @output
    @render.ui
    def demographic_options():
        selected = input.main_option()
        suboption = input.suboption() if hasattr(input, 'suboption') else None
        if selected in ['Dropout Rate', 'College, Career, & Military Ready Graduates', 'Attendance', 'Chronic Absenteeism', '4-Year Longitudinal Graduation Rate', "AP/IB", "SAT/ACT"]:
            demographic_options = ['View All Demographics'] + get_available_demographics(selected, suboption, get_inputs()['year'])
            return ui.input_radio_buttons("demographic_buttons", f"Demographics:", demographic_options, selected = demographic_options[0])
        else:
            return None