from shiny import ui, render, module, reactive
from shinywidgets import output_widget, render_widget

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

plot_labels = {
    "race_ethnicity": "Race and Ethnicity Distribution",
    "special_ed_504": "Special Education & 504 Percentages",
    "dot_stack": "Student Teacher Ratio",
    "staff_student": "Staff & Student Count",
    "special_populations": "Special Populations",
    "gifted_talented": "Gifted & Talented",
    "econ_disadv": "Economically Disadvantaged",
    "language_education": "Language Education",
}


@module.ui
def why_districts_ui():
    return ui.nav_panel("Why these districts?",
        ui.div(
            # The toggle section is now part of the static UI
            ui.card(
                ui.card_header("Select Visuals"),
                ui.input_checkbox_group("visible_plots", None, choices=list(plot_labels.values())),
                class_="mb-4"
            ),
            ui.output_ui("dynamic_plot_cards"),
            style="width: 100%; padding: 1rem 2rem;"
        ),
        value="panel2"
    )


@module.server
def why_districts_server(input, output, session, get_result, get_inputs):
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

    # --- 1. Auto-check visible_plots based on get_inputs()
    # Tie this effect to the Run Model button so it fires when the model is run.
    @reactive.effect
    @reactive.event(input.run)
    def _auto_check_visible_plots():
        inputs = get_inputs()
        selected_plots = set()
        if inputs and "buckets" in inputs:
            buckets = inputs["buckets"]
            for bucket in buckets:
                if bucket in bucket_to_plot_ids:
                    selected_plots.add(plot_labels[bucket_to_plot_ids[bucket]])
        ui.update_checkbox_group("visible_plots", selected=list(selected_plots))

    # --- 2. Dynamically generate cards for the selected plots.
    @output
    @render.ui
    def dynamic_plot_cards():
        cards = []
        selected_labels = input.visible_plots()  # list of human-readable names
        # Create a reverse mapping: human-readable label -> plot id
        label_to_id = {v: k for k, v in plot_labels.items()}
        for label in selected_labels:
            plot_id = label_to_id[label]
            cards.append(ui.card(ui.card_header(label), output_widget(plot_id)))
        # Force full width by setting the style on the containing div
        return ui.div(*cards, style="width: 100%;")

    # --- 3. Generate the actual plot outputs
    for plot_id, plot_func in plot_funcs.items():
        @output(id=plot_id)
        @render_widget
        def _render(plot_id=plot_id, plot_func=plot_func):  # default args to freeze late binding
            df, label_dict, neighbors = get_result()
            return plot_func(df, label_dict, neighbors)