import pandas as pd
import geopandas
import folium
import requests

# def get_geocode(postcode):
#     url = f"http://api.postcodes.io/postcodes/{postcode}"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         if data['status'] == 200:
#             result = data['result']
#             return result['latitude'], result['longitude']
#     return None, None

LSOA_ACRT_df = geopandas.read_file(r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\agedateteam.csv")
LSOA_ACRT_df.head()
LSOA_GEO_df = geopandas.read_file(r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\PCD_OA21_LSOA21_MSOA21_LAD_AUG24_UK_LU_CHJR.csv")
LSOA_GEO_df.head()

# Ensure the column name matches the actual column name in your CSV file
# For example, if the column name is 'postcode' instead of 'Postcode', update it accordingly
# LSOA_ACRT_df['Latitude'], LSOA_ACRT_df['Longitude'] = zip(*LSOA_ACRT_df['postcode'].apply(get_geocode))

#create base map
ACRT_Refs_interactive = folium.Map(
    location=[50.71671, -3.50668],
    zoom_start=9,
    tiles='cartodbpositron'
)

# create and add choropleth map
choropleth = folium.Choropleth(
    geo_data=LSOA_GEO_df,
    data=LSOA_ACRT_df,
    columns=['LSOA11NM', 'Referral Location'],
    key_on='feature.properties.LSOA11NM',
    fill_color='OrRd',
    fill_opacity=0.4,
    line_weight=0.3,
    legend_name='ACRT Referrals',
    highlight=True,
    smooth_factor=0
)

choropleth = choropleth.add_to(ACRT_Refs_interactive)

choropleth.geojson.add_child(
    folium.features.GeoJsonTooltip(
        ['LSOA11NM', 'Referral Location'],
        labels=True
    )
)

ACRT_Refs_interactive

