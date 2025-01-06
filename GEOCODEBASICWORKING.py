from matplotlib import pyplot as plt
import pandas as pd
import geopandas as gpd
import plotly.express as px
import contextily as cx
import warnings

# Load the CSV file containing postcodes
print("Loading activity CSV file...")
activity_csv_path = r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\REFERRALSGEO.csv"
data = pd.read_csv(activity_csv_path, encoding='ISO-8859-1')
print("Activity data loaded. Number of records:", len(data))

# Ensure the LSOA column is in the correct format
data['LSOA'] = data['LSOA'].str.replace(' ', '').str.upper()
print("Formatted LSOA column.")

# Load the postcode to LSOA mapping file
print("Loading postcode to LSOA mapping CSV file...")
mapping_csv_path = r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\PCD_OA21_LSOA21_MSOA21_LAD_AUG24_UK_LU_CHJR.csv"
postcode_to_lsoa = pd.read_csv(mapping_csv_path, encoding='ISO-8859-1')
print("Postcode to LSOA mapping data loaded. Number of records:", len(postcode_to_lsoa))

# Ensure the Postcode column in the mapping file is in the correct format
postcode_to_lsoa['pcds'] = postcode_to_lsoa['pcds'].str.replace(' ', '').str.upper()
postcode_to_lsoa['lsoa21nm'] = postcode_to_lsoa['lsoa21nm'].str.replace(' ', '').str.upper()
print("Formatted pcds and lsoa21nm columns in postcode to LSOA mapping data.")

# Merge the data with the postcode to LSOA mapping
print("Merging activity data with postcode to LSOA mapping...")
mapped_data = data.merge(postcode_to_lsoa, left_on='LSOA', right_on='lsoa21nm', how='left')
print("Data merged. Number of records in merged data:", len(mapped_data))
warnings.filterwarnings("ignore")

# Check if the column exists before accessing it
if 'lsoa21nm' in mapped_data.columns:
    new_dataframe = mapped_data[['LSOA', 'lsoa21nm']]
    print("Column 'lsoa21nm' found in merged data.")
else:
    print("Column 'lsoa21nm' not found in the merged DataFrame.")
    exit()

# Aggregate data by LSOA
print("Aggregating data by LSOA...")
lsoa_counts = new_dataframe['lsoa21nm'].value_counts().reset_index()
lsoa_counts.columns = ['lsoa21nm', 'Count']
print("Data aggregated. Number of unique LSOAs:", len(lsoa_counts))

# Load the LSOA boundaries
print("Loading LSOA boundaries GeoJSON file...")
lsoa_boundaries_2021 = gpd.read_file(r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\Lower_layer_Super_Output_Areas_2021_EW_BGC_V3.geojson")
print("LSOA boundaries loaded. Number of records:", len(lsoa_boundaries_2021))

# Merge the aggregated data with the LSOA boundaries GeoJSON
print("Merging aggregated data with LSOA boundaries...")
lsoa_boundaries_2021 = lsoa_boundaries_2021.merge(lsoa_counts, left_on='LSOA21NM', right_on='lsoa21nm', how='left')
print("Data merged with LSOA boundaries.")

# Fill NaN values with 0
lsoa_boundaries_2021['Count'] = lsoa_boundaries_2021['Count'].fillna(0)
print("Filled NaN values in 'Count' column with 0.")

try:
    # Filter lsoa_boundaries_2021 to include only the LSOAs present in mapped_data
    filtered_lsoa_boundaries = lsoa_boundaries_2021[lsoa_boundaries_2021['LSOA21NM'].isin(mapped_data['lsoa21nm'].unique())]
    print("Filtered LSOA boundaries to include only relevant LSOAs.")
except KeyError:
    print("KeyError: 'lsoa21nm' not found in mapped_data.")

# Convert filtered GeoDataFrame to GeoJSON
filtered_lsoa_geojson = filtered_lsoa_boundaries.to_json()
print("Converted filtered LSOA boundaries to GeoJSON.")

# Create a choropleth map using Plotly with the filtered data
print("Creating choropleth map...")
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
print("Displaying choropleth map...")
fig.show()

# Ensure the data is in a web mercator projection
filtered_lsoa_boundaries = filtered_lsoa_boundaries.to_crs(epsg=3857)
print("Converted filtered LSOA boundaries to web mercator projection.")

# Create the plot
print("Creating matplotlib plot...")
fig, ax = plt.subplots(figsize=(10, 10))
filtered_lsoa_boundaries.plot(
    column='Count',  # Adjust column name as needed
    ax=ax,
    legend=True,
    cmap='viridis'  # You can change the colormap
)

# Add basemap 
cx.add_basemap(
    ax,
    crs=filtered_lsoa_boundaries.crs.to_string(),
    source=cx.providers.OpenStreetMap.Mapnik,
    zoom=14
)

# Customize the plot
plt.title('Referrals to ACRT by LSOA')
plt.tight_layout()

# Show the plot
print("Displaying matplotlib plot...")
plt.show()
