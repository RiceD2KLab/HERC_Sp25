## AppUtils.py
- Loads ids.csv from the data/ directory
- title_case_with_spaces: formats district names in title case while preserving acronyms like ISD, CISD, and MSD.
- Defines bucket_options and demographic_buckets to group TEA variable names into readable demographic categories.
- get_labels_from_variable_name_dict: maps raw TEA variable names to readable labels. 
- get_combined_values: flattens and combines values from specified keys in a dictionary into a single list.

## getData.py
- load_data_from_github: Loads and cleans district-level education data for a given year from the HERC GitHub repository.
- get_subject_level_exclusive_scores: Extracts STAAR scores by subject and grade level. Transforms performance levels into mutually exclusive categories (Did Not Meet Grade Level, Approaches only, Meets only, and Masters)
- compute_dropout_rates: Calculates average dropout rates for grades 7–8 and 9–12 by demographics.
- get_existing_columns: Selects and returns only relevant columns from a dataset based on the provided year.

## DemographicUtils.py
- bucket_to_plot_ids and bucket_to_plot_ids are used to connect the plot functions to the app UI
- Demographic Plot Functions: this section includes various plotting functions using plotly, used by the why_districts module.

## OutcomeUtils.py
- options, suboptions, and demographics are used to filter the data according to inputs from the outcomes module and connect the plot functions to the app.
- demographic_string_patterns is a dictionary used to filter the data to only include that particular outcome variable dynamically for different years of data
- plot_selections: a master function that plots all of the outcome plot functions, except the STAAR plot
- Plot functions: the rest of this section includes various plotting functions using plotly, used by the outcomes module to show different outcome variables.

## MatchUtils.py
- loads in geometries for Texas counties and school districts
- generate_table: sets up a DataFrame that is ready to be rendered as a DataGrid in the matches server function.
- plot_texas_districts: plots selected school districts on a Texas map based on district IDs by either county or by district geometry using folium to make it interactive
