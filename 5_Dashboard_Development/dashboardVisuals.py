import plotly.express as px
import geopandas as gpd
import pandas as pd

def dash_map(df, neighbors):
    # Load shapefile
    gdf = gpd.read_file("Texas_SchoolDistricts_2024.geojson")

    # Ensure consistent types
    df['DISTRICT_id'] = df['DISTRICT_id'].astype(str)
    neighbors = neighbors.copy().reset_index(drop=True)
    neighbors['DISTRICT_id'] = neighbors['DISTRICT_id'].astype(str)
    gdf['DISTRICT_N'] = gdf['DISTRICT_N'].astype(str)

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

    # Select and categorize districts
    selected_districts = df[df['DISTRICT_id'].isin(district_ids)][['DISTRICT_id', 'DISTNAME']].dropna().reset_index(drop=True)
    neighbors_df = selected_districts[selected_districts['DISTNAME'] != input_dist].copy()
    input_district_df = selected_districts[selected_districts['DISTNAME'] == input_dist].copy()
    neighbors_df['Group'] = 'Neighboring District'
    input_district_df['Group'] = 'Input District'
    ordered_districts = pd.concat([input_district_df, neighbors_df]).reset_index(drop=True)

    district_group_map = ordered_districts.set_index('DISTRICT_id')['Group']
    print(gdf.columns)
    gdf['District'] = gdf['NAME']
    gdf['Group'] = gdf['DISTRICT_N'].map(district_group_map).fillna('Other')
    gdf = gdf.set_index("District")
    
    fig = px.choropleth(gdf,
                   geojson=gdf.geometry,
                   locations=gdf.index,
                   color="Group",
                   projection="mercator",
                   color_discrete_sequence=["lightgrey", "red", "blue"],
                   hover_data = {'Group':False})
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_traces(marker_line_width=.25)
    return fig