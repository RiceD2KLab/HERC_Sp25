### MATCHES DEPENDENCIES ###

# =============================================================================
# 1. Imports and Settings
# =============================================================================
# Standard Imports
import geopandas as gpd
import pandas as pd
from urllib.request import urlopen
import folium

# Dashboard Imports
from utils.AppUtils import title_case_with_spaces


# =============================================================================
# 2. Constants / Configuration
# =============================================================================
# Loading county and district geometries
countygeo = gpd.read_file('https://raw.githubusercontent.com/RiceD2KLab/HERC_Sp25/refs/heads/main/5_Dashboard_Development/data/geo/texas_counties.json')
districtgeo = gpd.read_file('https://raw.githubusercontent.com/RiceD2KLab/HERC_Sp25/refs/heads/main/5_Dashboard_Development/data/geo/Texas_SchoolDistricts_2024.json')


# =============================================================================
# 3. Creating DataFrame for the neighbors table
# =============================================================================
def generate_table(neighbors, df):
        """
        Function that generates a clean dataframe for the matches module to create a DataGrid

        Parameters:
            - neighbors (df): DF containing neighbors district id and distname .
            - df (pd.DataFrame): DataFrame containing 'DISTRICT_id', 'DISTNAME', and 'CNTYNAME' columns.

        Returns: 
            a DataFrame with district names, TEA district types, and counties of the neighbors.
        """
        neighbor_names = neighbors['DISTNAME']
        selected_df = df[['DISTNAME', 'TEA Description', 'CNTYNAME']]
        selected_df.columns = ['District', 'TEA District Type', 'County']
        for_table = selected_df[selected_df['District'].isin(neighbor_names)].copy()

        for_table['District'] = [title_case_with_spaces(distname) for distname in for_table['District']]
        for_table['County'] = [title_case_with_spaces(cty) for cty in for_table['County']]
        return for_table


# =============================================================================
# 4. Plot Districts Function
# =============================================================================
def plot_texas_districts(neighbors, df, level):
    """
    Plots selected school districts on a Texas map based on district IDs, with intelligent
    label placement to prevent overlap regardless of location density.
    
    Parameters:
    - neighbors (df): DF containing neighbors district id and distname 
    - df (pd.DataFrame): DataFrame containing 'DISTRICT_id', 'DISTNAME', and 'CNTYNAME' columns.
    - level (str): a string that is either "county" or "district", which determines what geometry to use.
    
    Returns:
    - A map plot of Texas highlighting the selected school districts, either with county or district shapes.
    """    
    
    # Get selected district IDs from the neighbors DataFrame
    district_ids = list(neighbors["DISTRICT_id"])
    print(district_ids)
    if not district_ids:
        print("No district IDs provided.")
        return

    # Filter the DataFrame for the selected districts
    selected_districts = df[df["DISTRICT_id"].isin(district_ids)]
    if selected_districts.empty:
        print("No matching districts found. Check the district IDs.")
        return
    if level == 'county':
        # Group selected districts by county and create a comma-separated string
        county_to_districts = (selected_districts
                            .groupby("CNTYNAME")["DISTNAME"]
                            .apply(list)
                            .to_dict())
        # Convert keys to uppercase for matching with shapefile data
        county_to_districts = {k.upper(): ", ".join(v) for k, v in county_to_districts.items()}

        # Look for the Texas counties file in a relative "data" directory
        
        # Load the Texas counties from the bundled file
        try:
            texas_counties = countygeo
        except Exception as e:
            print(f"Error loading Texas counties: {e}")
            print("Please ensure the texas_counties.geojson file is present in the 'data' folder.")
            return None
        
        # Create a new column for uppercase county names and map district info
        texas_counties["NAME_UPPER"] = texas_counties["NAME"].str.upper()
        texas_counties["districts"] = texas_counties["NAME_UPPER"].map(county_to_districts)
        texas_counties['labels'] = texas_counties["districts"].fillna("No district match")
    
        print(county_to_districts)

        # Define the Texas bounding box (SW and NE corners)
        texas_bounds = [[25.84, -106.65], [36.5, -93.51]]

        # Create the Folium map, centered on Texas.
        m = folium.Map(location=[31.0, -99.0], zoom_start=6, tiles="cartodbpositron", max_bounds=True)
        
        # Force the map view to the Texas bounds.
        m.fit_bounds(texas_bounds)
        m.options['maxBounds'] = texas_bounds
        # Define a style function for the GeoJSON layer.
        def style_function(feature):
            if feature["properties"].get("districts"):
                return {
                    'fillColor': 'blue',
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7,
                }
            else:
                return {
                    'fillColor': 'lightgray',
                    'color': 'black',
                    'weight': 0.5,
                    'fillOpacity': 0.5,
                }

        # Add the GeoJSON layer with tooltips to the map.
        folium.GeoJson(
            texas_counties.to_json(),
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=["NAME", "labels"],
                aliases=["County:", "Districts:"],
                localize=True
            )
        ).add_to(m)

        return m
    if level == 'district':
        try:
            geojson = districtgeo.copy()
        except Exception as e:
            print(f"Error loading district GeoJSON: {e}")
            return None

        texas_bounds = [[25.84, -106.65], [36.5, -93.51]]

        df['DISTRICT_id'] = df['DISTRICT_id'].astype(str)
        neighbors = neighbors.copy().reset_index(drop=True)
        neighbors['DISTRICT_id'] = neighbors['DISTRICT_id'].astype(str)
        geojson['DISTRICT_N'] = geojson['DISTRICT_N'].astype(str)

        # Extract district IDs
        district_ids = list(neighbors['DISTRICT_id'].dropna().unique())
        if not district_ids:
            print("No district IDs found in neighbors.")
            return

        # Get input district name
        input_rows = df[df["DISTRICT_id"] == district_ids[0]]
        if input_rows.empty:
            print(f"No matching DISTNAME found for DISTRICT_id: {district_ids[0]}")
            return
        input_dist = input_rows['DISTNAME'].iloc[0]

        # Set group labels
        selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME']].dropna().reset_index(drop=True)
        selected_districts['group'] = selected_districts['DISTNAME'].apply(
            lambda name: 'Input District' if name == input_dist else 'Neighboring District'
        )

        # Map group info to geojson
        district_group_map = selected_districts.set_index('DISTRICT_id')['group']
        geojson['group'] = geojson['DISTRICT_N'].map(district_group_map)
        geojson['group'] = geojson['group'].fillna("Other")
        geojson['color'] = geojson['group'].map({
            "Input District": "blue",
            "Neighboring District": "red",
            "Other": "lightgrey"
        })

        # Filter geojson to include only input + neighbors
        filtered_geojson = geojson[geojson['group'].isin(['Input District', 'Neighboring District'])].copy()

        # Create the map
        m = folium.Map(location=[31.0, -99.0], zoom_start=6, tiles="cartodbpositron", max_bounds=True)
        m.fit_bounds(texas_bounds)
        m.options['maxBounds'] = texas_bounds

        # Add GeoJson layer
        folium.GeoJson(
            filtered_geojson.to_json(),
            style_function=lambda feature: {
                'fillColor': feature['properties']['color'],
                'color': 'black',
                'weight': 0.25,
                'fillOpacity': 0.7
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["NAME", "group"],
                aliases=["District:", "Type:"],
                localize=True
            )
        ).add_to(m)

        return m