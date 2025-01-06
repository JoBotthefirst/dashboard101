from matplotlib import pyplot as plt
import pandas as pd
import geopandas as gpd
import plotly.express as px
import contextily as cx
import warnings

# Load the CSV file containing postcodes

activity_csv_path = r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\ActivityDashboardJR.csv"
data = pd.read_csv(activity_csv_path, encoding='ISO-8859-1')

# Ensure the PatientAddressPostcode column is in the correct format
data['PatientAddressPostcode'] = data['PatientAddressPostcode'].str.replace(' ', '').str.upper()

# Load the postcode to LSOA mapping file
mapping_csv_path = r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\PCD_OA21_LSOA21_MSOA21_LAD_AUG24_UK_LU.csv"
postcode_to_lsoa = pd.read_csv(mapping_csv_path, encoding='ISO-8859-1')

# Ensure the Postcode column in the mapping file is in the correct format
postcode_to_lsoa['pcds'] = postcode_to_lsoa['pcds'].str.replace(' ', '').str.upper()

# Merge the data with the postcode to LSOA mapping
mapped_data = data.merge(postcode_to_lsoa, left_on='PatientAddressPostcode', right_on='pcds', how='left')
warnings.filterwarnings("ignore")

# Check if the column exists before accessing it
if 'lsoa21nm' in mapped_data.columns:
    new_dataframe = mapped_data[['PatientAddressPostcode', 'lsoa21nm']]
else:
    print("Column 'lsoa21nm' not found in the merged DataFrame.")
    exit()

# Aggregate data by LSOA
lsoa_counts = new_dataframe['lsoa21nm'].value_counts().reset_index()
lsoa_counts.columns = ['lsoa21nm', 'Count']

# Load the LSOA boundaries
lsoa_boundaries_2021 = gpd.read_file(r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\Lower_layer_Super_Output_Areas_2021_EW_BGC_V3.geojson")

# Merge the aggregated data with the LSOA boundaries GeoJSON
lsoa_boundaries_2021 = lsoa_boundaries_2021.merge(lsoa_counts, left_on='LSOA21NM', right_on='lsoa21nm', how='left')

# Fill NaN values with 0
lsoa_boundaries_2021['Count'] = lsoa_boundaries_2021['Count'].fillna(0)

try:
    # Filter lsoa_boundaries_2021 to include only the LSOAs present in mapped_data
    filtered_lsoa_boundaries = lsoa_boundaries_2021[lsoa_boundaries_2021['LSOA21NM'].isin(mapped_data['lsoa21nm'].unique())]
except KeyError:
    print("KeyError: 'lsoa21nm' not found in mapped_data.")

# Convert filtered GeoDataFrame to GeoJSON
filtered_lsoa_geojson = filtered_lsoa_boundaries.to_json()

# Create a choropleth map using Plotly with the filtered data
fig = px.choropleth(
    filtered_lsoa_boundaries,
    geojson=filtered_lsoa_geojson,
    locations=filtered_lsoa_boundaries.index,
    color='Count',
    hover_name='LSOA21NM',
    hover_data={'LSOA21NM': True, 'Count': True},
    title='Choropleth Map of ACRT Referrals by LSOA'
)

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# Display the map in an interactive window
fig.show()

# Ensure the data is in a web mercator projection
filtered_lsoa_boundaries = filtered_lsoa_boundaries.to_crs(epsg=3857)

# Create the plot
fig, ax = plt.subplots(figsize=(10, 10))
filtered_lsoa_boundaries.plot(
    column='Count',  # Adjust column name as needed
    ax=ax,
    legend=True,
    cmap='viridis'  # You can change the colormap
)

# Add basemap (multiple options)
# Option 1: OpenStreetMap
cx.add_basemap(
    ax,
    crs=filtered_lsoa_boundaries.crs,
    source=cx.providers.OpenStreetMap.Mapnik,
    zoom=14
)

# Alternative basemap styles (uncomment to try):
# cx.add_basemap(ax, source=cx.providers.CartoDB.Positron)
# cx.add_basemap(ax, source=cx.providers.CartoDB.DarkMatter)
# cx.add_basemap(ax, source=cx.providers.Esri.WorldImagery)

# Customize the plot
plt.title('Your Map Title')
plt.tight_layout()

# Show the plot
plt.show()
