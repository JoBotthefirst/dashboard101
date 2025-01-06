import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
from datetime import datetime as dt, timedelta

# Load the CSV file
input_dataset = pd.read_csv(r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\ActivityDashboardJR.csv")

# Convert 'Appointment by Day' to datetime
input_dataset['Appointment by Day'] = pd.to_datetime(input_dataset['Appointment by Day'], format='%d/%m/%Y %H:%M', errors='coerce')

# Streamlit app
st.title("Appointment Visualization")

# Tabs

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Client ID Filter", "ClinicDesc Filter", "HCP Activity Leaderboard", "SPC Chart", "Geographic Hotspot"])

#
# additional fundtions: distance travelled - caclulate using postcode and distance from base -  add to tab3,  activity by presence - import db from HR showing hours worked/activity completed to, filter by banding/discipline, Demographic comparison- 
# 
# LSOA/ethnicity and time in service

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime as dt, timedelta

# Load the CSV file
input_dataset = pd.read_csv(r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\ActivityDashboardJR.csv")

# Convert 'Appointment by Day' to datetime
input_dataset['Appointment by Day'] = pd.to_datetime(input_dataset['Appointment by Day'], format='%d/%m/%Y %H:%M', errors='coerce')

# Streamlit app
st.title("Appointment Visualization")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Client ID Filter", "ClinicDesc Filter", "HCP Activity Leaderboard", "SPC Chart"])

with tab1:
    # Sidebar form for Client ID Filter
    client_id_list = list(set(input_dataset["ClientID"]))
    client_form = st.sidebar.form("Client_ID_Form")
    client_id = client_form.selectbox(label="Client ID", options=client_id_list, help="Please select a client ID")
    client_form.divider()
    chart_start_date = client_form.date_input(label="Chart Start Date (Optional)", max_value=dt.today(), value=None)
    chart_end_date = client_form.date_input(label="Chart End Date (Optional)", max_value=dt.today(), value=None)
    sbt_btn = client_form.form_submit_button("Submit")

    if sbt_btn:
        if client_id is None:
            st.error("Error: Please enter the valid client id!")
        elif client_id not in client_id_list:
            st.warning(f"Client ID: '{client_id}' is not in the dataset!")
        else:
            client_dataset = input_dataset[input_dataset["ClientID"] == client_id]
            
            if chart_start_date is not None:
                client_dataset = client_dataset[client_dataset["Appointment by Day"] >= pd.to_datetime(chart_start_date)]
            if chart_end_date is not None:
                client_dataset = client_dataset[client_dataset["Appointment by Day"] <= pd.to_datetime(chart_end_date)]
            
            # Automatically select all HCP names
            hcp_names = list(set(input_dataset["HCPName"]))
            client_dataset = client_dataset[client_dataset["HCPName"].isin(hcp_names)]
            
            # Plotting
            fig = px.scatter(
                client_dataset, 
                x="Appointment by Day", 
                y="HCPName", 
                color="HCPName",
                title="Appointments by Day and HCP Name Overlap"
            )
            
            # Customize layout
            fig.update_layout(
                xaxis_title="Appointment Date",
                yaxis_title="Healthcare Provider",
                legend_title="HCP Name",
                title={
                    'text': "Appointments by Day and HCP Name Overlap",
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )
            
            # Customize marker outlines based on outcome
            outcome_colors = {
                "Attended": "green",
                "Cancellation(Other)": "orange",
                "Cancelled By Patient": "red",
                "Cancelled By Service": "red",
                "DNA": "black",
                "UnOutcomed": "white"
            }
            
            # Add 'Color' column to client_dataset based on 'Outcome'
            client_dataset['Color'] = client_dataset['Outcome'].map(outcome_colors)
            
            # Customize marker outlines based on outcome
            for outcome, color in outcome_colors.items():
                fig.update_traces(marker=dict(line=dict(color=color, width=10)),
                                  selector=dict(marker=dict(color=client_dataset[client_dataset['Outcome'] == outcome]['Color'])))
            
            st.plotly_chart(fig)
            
            # Add key for outcome colors
            st.markdown("### Outcome Colors Key")
            for outcome, color in outcome_colors.items():
                st.markdown(f"<span style='color:{color};'>⬤</span> {outcome}", unsafe_allow_html=True)

            
                
with tab2:
    # Sidebar form for ClinicDesc Filter
    clinic_desc_list = list(set(input_dataset["ClinicDesc"]))
    clinic_form = st.sidebar.form("ClinicDesc_Form")
    clinic_desc = clinic_form.selectbox(
        label="Clinic Description", options=clinic_desc_list, 
        help="Please select a clinic description")
    clinic_sbt_btn = clinic_form.form_submit_button("Submit")

    if clinic_sbt_btn:
        if clinic_desc is None:
            st.error("Error: Please select a valid clinic description!")
        elif clinic_desc not in clinic_desc_list:
            st.warning(f"Clinic Description: '{clinic_desc}' is not in the dataset!")
        else:
            clinic_dataset = input_dataset[input_dataset["ClinicDesc"] == clinic_desc]
            
            # Plotting
            fig2 = px.bar(clinic_dataset, x="OutcomeDetails", color="OutcomeDetails",
                          title=f"Outcome Details for Clinic: {clinic_desc}")
            
            # Customize layout
            fig2.update_layout(
                xaxis_title="Outcome Details",
                yaxis_title="Count",
                legend_title="Outcome Details",
                title={
                    'text': f"Outcome Details for Clinic: {clinic_desc}",
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )
            
            st.plotly_chart(fig2)
            

with tab3:
    # Sidebar for leaderboard of monthly HCP activity
    st.sidebar.header("Leaderboard Filter")
    months = input_dataset['Appointment by Day'].dt.strftime('%Y-%m').unique()
    selected_month = st.sidebar.selectbox("Select Month", options=months, help="Select a month to filter the leaderboard")

    # Filter dataset by selected month
    leaderboard_dataset = input_dataset[input_dataset['Appointment by Day'].dt.strftime('%Y-%m') == selected_month]

    # Group by HCPName and count the number of appointments
    leaderboard = leaderboard_dataset.groupby('HCPName').size().reset_index(name='Appointment Count')
    leaderboard = leaderboard.sort_values(by='Appointment Count', ascending=False)

    # Plotting
    fig3 = px.bar(leaderboard, x='Appointment Count', y= 'HCPName', title=f"Leaderboard of HCP Activity for {selected_month}")

    # Customize layout
    fig3.update_layout(
        xaxis_title="Appointment Count",
        yaxis_title="Healthcare Provider",
        title={
            'text': f"Leaderboard of HCP Activity for {selected_month}",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    st.plotly_chart(fig3)
  
with tab4:
    # Sidebar for SPC chart of monthly activity over time
    st.sidebar.header("SPC Chart Filter")
    hcp_names_list = list(set(input_dataset["HCPName"]))
    selected_hcp = st.sidebar.selectbox("Select HCP", options=hcp_names_list, help="Select a healthcare provider to view SPC chart")

    # Filter dataset to include only the last 12 months
    twelve_months_ago = dt.today() - timedelta(days=365)
    spc_dataset = input_dataset[(input_dataset["HCPName"] == selected_hcp) & (input_dataset["Appointment by Day"] >= twelve_months_ago)]

    # Group by month and count the number of appointments
    spc_dataset['Month'] = spc_dataset['Appointment by Day'].dt.to_period('M')
    monthly_counts = spc_dataset.groupby('Month').size().reset_index(name='Appointment Count')

    # Calculate control limits
    mean_count = monthly_counts['Appointment Count'].mean()
    std_dev = monthly_counts['Appointment Count'].std()
    upper_control_limit = mean_count + 3 * std_dev
    lower_control_limit = mean_count - 3 * std_dev

    # Plotting
    fig4 = go.Figure()

    # Add traces for the SPC chart
    fig4.add_trace(go.Scatter(x=monthly_counts['Month'].astype(str), y=monthly_counts['Appointment Count'],
                              mode='lines+markers', name='Appointment Count'))
    fig4.add_trace(go.Scatter(x=monthly_counts['Month'].astype(str), y=[mean_count]*len(monthly_counts),
                              mode='lines', name='Mean', line=dict(dash='dash')))
    fig4.add_trace(go.Scatter(x=monthly_counts['Month'].astype(str), y=[upper_control_limit]*len(monthly_counts),
                              mode='lines', name='Upper Control Limit', line=dict(dash='dash', color='red')))
    fig4.add_trace(go.Scatter(x=monthly_counts['Month'].astype(str), y=[lower_control_limit]*len(monthly_counts),
                              mode='lines', name='Lower Control Limit', line=dict(dash='dash', color='red')))

    # Customize layout
    fig4.update_layout(
        xaxis_title="Month",
        yaxis_title="Appointment Count",
        legend_title="Legend",
        title={
            'text': f"SPC Chart for {selected_hcp}",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    st.plotly_chart(fig4)
    
    
with tab5:
    # Sidebar for geographic hotspot of activity (EXAMPLE - NEED TO MAP LSOA POSTCODES to LSOA LOOK UP FROM ONS?)
    st.sidebar.header("Geographic Hotspot Filter")
    selected_date_range = st.sidebar.date_input("Select Date Range", [dt.today() - timedelta(days=30), dt.today()])
    selected_date_range = [pd.to_datetime(date) for date in selected_date_range]

    # Filter dataset by selected date range
    geo_dataset = input_dataset[(input_dataset["Appointment by Day"] >= selected_date_range[0]) & (input_dataset["Appointment by Day"] <= selected_date_range[1])]

    # Convert postcode to coordinates (this requires a geocoding service or a pre-existing mapping of postcodes to coordinates)
    # For simplicity, let's assume we have a function `postcode_to_coordinates` that converts postcodes to latitude and longitude
    def postcode_to_coordinates(postcode):
        # Dummy implementation, replace with actual geocoding logic
        return (51.509865, -0.118092)  # Coordinates for London, UK

    geo_dataset[['Latitude', 'Longitude']] = geo_dataset['PatientAddressPostcode'].apply(postcode_to_coordinates).apply(pd.Series)

    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame(geo_dataset, geometry=gpd.points_from_xy(geo_dataset.Longitude, geo_dataset.Latitude))

    # Plotting
    fig5 = px.scatter_mapbox(gdf, lat="Latitude", lon="Longitude", hover_name="PatientAddressPostcode",
                             hover_data=["Appointment by Day", "OutcomeDetails"], color_discrete_sequence=["fuchsia"], zoom=10, height=600)
    fig5.update_layout(mapbox_style="open-street-map")
    fig5.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    st.plotly_chart(fig5)