from shiny import ui, render, module, reactive
from shinywidgets import output_widget, render_widget
import plotly.graph_objs as go

# --- Plot Mappings ---
bucket_to_plot_ids = {
    "race_ethnicity_percent": "race_ethnicity",
    "special_ed_504": "special_ed_504",
    "student_teacher_ratio": "dot_stack",
    "student_count": "staff_student",
    "staff_count": "staff_student",
    "special_populations_percent": "special_populations",
    "gifted_students": "gifted_talented",
    "economically_disadvantaged": "econ_disadv",
    "language_education_percent": "language_education",
}

# Updated plot_labels with the new order
plot_labels = {
    "dot_stack": "Student Teacher Ratio",
    "staff_student": "Staff & Student Count",
    "race_ethnicity": "Race and Ethnicity Distribution",
    "econ_disadv": "Economically Disadvantaged",
    "special_ed_504": "Special Education & 504 Percentages",
    "language_education": "Language Education",
    "special_populations": "Special Populations",
    "gifted_talented": "Gifted & Talented",
}


@module.ui
def why_districts_ui():
    return ui.nav_panel("Why these districts?",
        ui.div(
            # The toggle section is now part of the static UI
            ui.card(
                ui.card_header("Select Visuals"),
                ui.input_checkbox_group("visible_plots", None, choices= list(plot_labels.values()), selected = list(plot_labels.values())),
                class_="mb-4"
            ),
            ui.output_ui("dynamic_plot_cards"),
            style="width: 100%; padding: 1rem 2rem;"
        ),
        value="panel2"
    )


@module.server
def why_districts_server(input, output, session, run_result, get_inputs):
    from utils.KNN_Demographic_Plots import (
        plot_race_ethnicity_stacked_bar,
        plot_special_ed_504_bar, 
        plot_dot_stack,
        plot_staff_student_dumbbell,
        plot_special_populations_dropdown,
        plot_gifted_talented_horizontal_bar,
        plot_economically_disadvantaged_horizontal,
        plot_language_education_filterable_bar
    )

    plot_funcs = {
        "race_ethnicity": plot_race_ethnicity_stacked_bar,
        "special_ed_504": plot_special_ed_504_bar,
        "dot_stack": plot_dot_stack,
        "staff_student": plot_staff_student_dumbbell,
        "special_populations": plot_special_populations_dropdown,
        "gifted_talented": plot_gifted_talented_horizontal_bar,
        "econ_disadv": plot_economically_disadvantaged_horizontal,
        "language_education": plot_language_education_filterable_bar,
    }



    # --- 1. Dynamically generate cards for the selected plots.
    @output
    @render.ui
    def dynamic_plot_cards():
        cards = []
        selected_labels = input.visible_plots()  # list of human-readable names
        label_to_id = {v: k for k, v in plot_labels.items()}

        for label in selected_labels:
            plot_id = label_to_id[label]

            cards.append(
                ui.layout_columns(
                    ui.card(
                        ui.card_header(label),
                        output_widget(plot_id)
                    ),
                    col_widths=(12,)  # Full width per card; change to (3,9) if you want side-by-side
                )
            )

        return ui.div(*cards, style="width: 100%; padding-bottom: 2rem;")


    # --- 2. Generate the actual plot outputs
    for plot_id, plot_func in plot_funcs.items():
        @output(id=plot_id)
        @render_widget
        def _render(plot_id=plot_id, plot_func=plot_func):  # default args to freeze late binding
            result = run_result.get()
            if result is None or len(result) != 3:
                return go.Figure().update_layout(title="Run a model to view outcomes.")
            df, label_dict, neighbors = result[0], result[1], result[2]
            df['DISTRICT_id'] = df['DISTRICT_id'].astype(str)
            neighbors['DISTRICT_id'] = neighbors['DISTRICT_id'].astype(str)
            return plot_func(df, label_dict, neighbors)