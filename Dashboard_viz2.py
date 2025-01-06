import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from sklearn.cluster import KMeans
import geopandas as gpd
from datetime import datetime as dt, timedelta
import matplotlib.pyplot as plt



# Load the CSV file with specified dtypes
input_dataset = pd.read_csv(
    r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\ActivityDashboardJR.csv",
    dtype={
        'ClientID': str,  # ClientID column as string
        'HCPName': str,  # HCPName column as string
        'ClinicDesc': str,  # ClinicDesc column as string
        'TotalCountOfEventPerReferralID': int,  # TotalCountOfEventPerReferralID column as integer
        'AgeAtContact': float  # AgeAtContact column as float
    },
    low_memory=False  # Optimize memory usage
)

# Convert 'Appointment by Day' to datetime
input_dataset['Appointment by Day'] = pd.to_datetime(input_dataset['Appointment by Day'], format='%d/%m/%Y %H:%M', errors='coerce')

# Streamlit app
st.title("Appointment Visualization")

# Sidebar for navigation
st.sidebar.title("Navigation")
view = st.sidebar.radio("Select view", ["Client ID Filter", "ClinicDesc Filter", "Activity Leaderboard", "SPC Chart", "Geographic Hotspot", "Referral ID Distribution", "Pareto Analysis", "Age Cluster Map", "Appointments by Day of Week"])


if view == "Client ID Filter":
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
            st.error("Error: Please enter a valid client ID!")
        elif client_id not in client_id_list:
            st.warning(f"Client ID '{client_id}' is not in the dataset!")
        else:
            client_dataset = input_dataset[input_dataset["ClientID"] == client_id]

            if chart_start_date is not None:
                client_dataset = client_dataset[client_dataset["Appointment by Day"] >= pd.to_datetime(chart_start_date)]
            if chart_end_date is not None:
                client_dataset = client_dataset[client_dataset["Appointment by Day"] <= pd.to_datetime(chart_end_date)]

            # Automatically select all HCP names
            hcp_names = list(set(input_dataset["HCPName"]))
            client_dataset = client_dataset[client_dataset["HCPName"].isin(hcp_names)]

            # Define outcome colors
            outcome_colors = {
                "Attended": "green",
                "Cancellation(Other)": "orange",
                "Cancelled By Patient": "purple",
                "Cancelled By Service": "red",
                "DNA": "black",
                "UnOutcomed": "white"
            }

            # Plotting
            fig = px.scatter(
                client_dataset,
                x="Appointment by Day",
                y="HCPName",
                color="Outcome",
                title="Appointments by Day and HCP Name Overlap",
                color_discrete_map=outcome_colors
            )

            # Customize layout
            fig.update_layout(
                xaxis_title="Appointment Date",
                yaxis_title="Healthcare Provider",
                legend_title="Appointment Outcome",
                height=300,
                title={
                    'text': "Appointments by Day and HCP Name Overlap",
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                yaxis=dict(
                    categoryorder='total ascending',  # Order categories by total count
                    categoryarray=hcp_names,  # Use the list of HCP names to control the order
                    tickvals=hcp_names,  # Ensure all HCP names are shown
                    ticktext=hcp_names,  # Use the HCP names as tick labels
                    tickfont=dict(size=14), # Adjust the font size to reduce space
                    automargin=True
                )
            )

            # Customize marker outlines based on outcome
            for outcome, color in outcome_colors.items():
                fig.update_traces(
                    marker=dict(size=10, line=dict(color=color, width=2)),
                    selector=dict(mode='markers', marker_color=color)
                )

            st.plotly_chart(fig)

            # Add key for outcome colors
            st.markdown("### Outcome Colors Key")
            for outcome, color in outcome_colors.items():
                st.markdown(f"<span style='color:{color};'>⬤</span> {outcome}", unsafe_allow_html=True)
            
            
elif view == "ClinicDesc Filter":
    # Sidebar form for ClinicDesc Filter
    clinic_desc_list = list(set(input_dataset["ClinicDesc"]))
    option = st.radio(
        "Choose a view",
        ("Details", "Summary")
    )

    # Date range input for 12-month periods
    end_date = dt.today()
    start_date = end_date - timedelta(days=365)
    date_range = st.sidebar.date_input("Select Date Range", [start_date, end_date])

    if option == 'Details':
        st.write("Showing Details")
        clinic_form = st.sidebar.form("ClinicDesc_Form")
        clinic_descs = clinic_form.multiselect(label="Clinic Description", 
            options=clinic_desc_list, default=[], 
            help="Please select clinic descriptions")
        clinic_sbt_btn = clinic_form.form_submit_button("Submit")

        if clinic_sbt_btn:
            if not clinic_descs:
                st.error("Error: Please select at least one clinic description!")
            else:
                clinic_dataset = input_dataset[(input_dataset["ClinicDesc"].isin(clinic_descs)) & 
                                               (input_dataset["Appointment by Day"] >= pd.to_datetime(date_range[0])) & 
                                               (input_dataset["Appointment by Day"] <= pd.to_datetime(date_range[1]))]
                
                if not clinic_dataset.empty:
                    # Plotting the violin plot
                    fig, ax = plt.subplots(figsize=(10, 6))
                    plt.xticks(rotation=45)
                    sns.violinplot(x="ClinicDesc", y="TotalCountOfEventPerReferralID", data=clinic_dataset, ax=ax)
                    ax.set_title("Distribution of Total Count of Events per Referral ID by Clinic Description")
                    ax.set_xlabel("Clinic Description")
                    ax.set_ylabel("Total Count of Events per Referral ID")
                    st.pyplot(fig)
                    
                    # Display details table
                    st.write("### Details Table")
                    st.dataframe(clinic_dataset)
                else:
                    st.warning("No data available for the selected date range and clinic descriptions.")
    else:
        # summary visualization here
        st.write("Showing Summary")
        clinic_dataset = input_dataset[(input_dataset["Appointment by Day"] >= pd.to_datetime(date_range[0])) & 
                                       (input_dataset["Appointment by Day"] <= pd.to_datetime(date_range[1]))]
        summary = clinic_dataset.groupby('ClinicDesc')['OutcomeDetails'].value_counts().unstack().fillna(0)
        st.dataframe(summary)

elif view == "Activity Leaderboard":
    # Sidebar for leaderboard of monthly HCP activity
    st.sidebar.header("Leaderboard Filter")
    months = input_dataset['Appointment by Day'].dt.strftime('%Y-%m').unique()
    selected_month = st.sidebar.selectbox("Select Month", options=months, help="Select a month to filter the leaderboard")

    # Filter dataset by selected month
    leaderboard_dataset = input_dataset[input_dataset['Appointment by Day'].dt.strftime('%Y-%m') == selected_month]

    # Group by HCPName and count the number of appointments
    leaderboard = leaderboard_dataset.groupby('HCPName').size().reset_index(name='Appointment Count')
    leaderboard = leaderboard.sort_values(by='Appointment Count', ascending=True)

    # Plotting
    fig3 = px.bar(leaderboard, x='Appointment Count', y='HCPName', title=f"Leaderboard of HCP Activity for {selected_month}")

    # Customize layout
    fig3.update_layout(
        xaxis_title="Healthcare Provider",
        yaxis_title="Appointment Count",
        title={
            'text': f"Leaderboard of HCP Activity for {selected_month}",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    st.plotly_chart(fig3)

    # Additional section for line graph of HCP activity over time
    st.sidebar.header("HCP Activity Over Time")
    date_range = st.sidebar.date_input("Select Date Range", [dt.today() - timedelta(days=30), dt.today()])
    selected_hcps = st.sidebar.multiselect("Select HCPs", options=list(set(input_dataset["HCPName"])), help="Select healthcare providers to view activity over time")

    if selected_hcps:
        # Filter dataset by selected date range and HCPs
        activity_dataset = input_dataset[(input_dataset["Appointment by Day"] >= pd.to_datetime(date_range[0])) & 
                                         (input_dataset["Appointment by Day"] <= pd.to_datetime(date_range[1])) & 
                                         (input_dataset["HCPName"].isin(selected_hcps))]

        # Group by day and HCP, and count the number of appointments
        activity_counts = activity_dataset.groupby([activity_dataset['Appointment by Day'].dt.date, 'HCPName']).size().reset_index(name='Appointment Count')

        # Plotting
        fig4 = px.line(activity_counts, x='Appointment by Day', y='Appointment Count', color='HCPName', title="Activity of Selected HCPs Over Time")

        # Customize layout
        fig4.update_layout(
            xaxis_title="Date",
            yaxis_title="Appointment Count",
            title={
                'text': "Activity of Selected HCPs Over Time",
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        st.plotly_chart(fig4)
    else:
        st.write("Please select at least one HCP to view the activity over time.")

elif view == "SPC Chart":
    # Sidebar for SPC chart of monthly activity over time
    st.sidebar.header("SPC Chart Filter")
    hcp_names_list = list(set(input_dataset["HCPName"]))
    select_all_hcps = st.sidebar.checkbox("Select All HCPs")
    
    if select_all_hcps:
        selected_hcps = st.sidebar.multiselect("Select HCPs", options=hcp_names_list, default=hcp_names_list, help="Select healthcare providers to view SPC chart")
    else:
        selected_hcps = st.sidebar.multiselect("Select HCPs", options=hcp_names_list, help="Select healthcare providers to view SPC chart")
    
    combine_hcps = st.sidebar.checkbox("Combine selected HCPs")

    if selected_hcps:
        # Filter dataset to include only the last 12 months
        twelve_months_ago = dt.today() - timedelta(days=365)
        spc_dataset = input_dataset[(input_dataset["HCPName"].isin(selected_hcps)) & (input_dataset["Appointment by Day"] >= twelve_months_ago)]

        if combine_hcps:
            # Group by month and count the number of appointments for combined HCPs
            spc_dataset['Month'] = spc_dataset['Appointment by Day'].dt.to_period('M')
            monthly_counts = spc_dataset.groupby('Month').size().reset_index(name='Appointment Count')

            # Calculate control limits for combined HCPs
            mean_count = monthly_counts['Appointment Count'].mean()
            std_dev = monthly_counts['Appointment Count'].std()
            upper_control_limit = mean_count + 3 * std_dev
            lower_control_limit = mean_count - 3 * std_dev

            # Identify outliers
            monthly_counts['Outlier'] = (monthly_counts['Appointment Count'] > upper_control_limit) | (monthly_counts['Appointment Count'] < lower_control_limit)

            # Plotting
            fig4 = go.Figure()

            fig4.add_trace(go.Scatter(x=monthly_counts['Month'].astype(str), y=monthly_counts['Appointment Count'],
                                      mode='lines+markers', name='Combined Appointment Count'))

            fig4.add_trace(go.Scatter(x=monthly_counts['Month'].astype(str), y=[mean_count] * len(monthly_counts),
                                      mode='lines', name='Mean', line=dict(dash='dash')))

            fig4.add_trace(go.Scatter(x=monthly_counts['Month'].astype(str), y=[upper_control_limit] * len(monthly_counts),
                                      mode='lines', name='Upper Control Limit', line=dict(dash='dash', color='red')))

            fig4.add_trace(go.Scatter(x=monthly_counts['Month'].astype(str), y=[lower_control_limit] * len(monthly_counts),
                                      mode='lines', name='Lower Control Limit', line=dict(dash='dash', color='red')))

            # Highlight outliers
            outliers = monthly_counts[monthly_counts['Outlier']]
            fig4.add_trace(go.Scatter(x=outliers['Month'].astype(str), y=outliers['Appointment Count'],
                                      mode='markers', marker=dict(color='red', size=10), name='Outliers'))

        else:
            # Group by month and HCP, and count the number of appointments for each HCP
            spc_dataset['Month'] = spc_dataset['Appointment by Day'].dt.to_period('M')
            monthly_counts = spc_dataset.groupby(['Month', 'HCPName']).size().reset_index(name='Appointment Count')

            # Calculate control limits for each HCP
            control_limits = monthly_counts.groupby('HCPName')['Appointment Count'].agg(['mean', 'std']).reset_index()
            control_limits['Upper Control Limit'] = control_limits['mean'] + 3 * control_limits['std']
            control_limits['Lower Control Limit'] = control_limits['mean'] - 3 * control_limits['std']

            # Plotting
            fig4 = go.Figure()

            for hcp in selected_hcps:
                hcp_data = monthly_counts[monthly_counts['HCPName'] == hcp]
                hcp_limits = control_limits[control_limits['HCPName'] == hcp]

                # Identify outliers
                hcp_data['Outlier'] = (hcp_data['Appointment Count'] > hcp_limits['Upper Control Limit'].values[0]) | (hcp_data['Appointment Count'] < hcp_limits['Lower Control Limit'].values[0])

                fig4.add_trace(go.Scatter(x=hcp_data['Month'].astype(str), y=hcp_data['Appointment Count'],
                                          mode='lines+markers', name=f'{hcp} Appointment Count'))

                fig4.add_trace(go.Scatter(x=hcp_data['Month'].astype(str), y=[hcp_limits['mean'].values[0]] * len(hcp_data),
                                          mode='lines', name=f'{hcp} Mean', line=dict(dash='dash')))

                fig4.add_trace(go.Scatter(x=hcp_data['Month'].astype(str), y=[hcp_limits['Upper Control Limit'].values[0]] * len(hcp_data),
                                          mode='lines', name=f'{hcp} Upper Control Limit', line=dict(dash='dash', color='red')))

                fig4.add_trace(go.Scatter(x=hcp_data['Month'].astype(str), y=[hcp_limits['Lower Control Limit'].values[0]] * len(hcp_data),
                                          mode='lines', name=f'{hcp} Lower Control Limit', line=dict(dash='dash', color='red')))

                # Highlight outliers
                outliers = hcp_data[hcp_data['Outlier']]
                fig4.add_trace(go.Scatter(x=outliers['Month'].astype(str), y=outliers['Appointment Count'],
                                          mode='markers', marker=dict(color='red', size=10), name=f'{hcp} Outliers'))

        # Customize layout
        fig4.update_layout(
            xaxis_title="Month",
            yaxis_title="Appointment Count",
            title={
                'text': "SPC Chart of Monthly Activity",
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        st.plotly_chart(fig4)
    else:
        st.write("Please select at least one HCP to view the SPC chart.")

elif view == "Appointments by Day of Week":
    # Sidebar for date range filter
    st.sidebar.header("Date Range Filter")
    date_range = st.sidebar.date_input("Select Date Range", [dt.today() - timedelta(days=30), dt.today()])

    # Filter dataset by selected date range
    filtered_dataset = input_dataset[(input_dataset["Appointment by Day"] >= pd.to_datetime(date_range[0])) & 
                                     (input_dataset["Appointment by Day"] <= pd.to_datetime(date_range[1]))]

    # Extract day of the week
    filtered_dataset['Day of Week'] = filtered_dataset['Appointment by Day'].dt.day_name()

    # Group by day of the week and count the number of appointments
    day_counts = filtered_dataset['Day of Week'].value_counts().sort_index().reset_index()
    day_counts.columns = ['Day of Week', 'Appointment Count']

    # Plotting
    fig5 = px.bar(day_counts, x='Day of Week', y='Appointment Count', title="Appointments by Day of Week")

    # Customize layout
    fig5.update_layout(
        xaxis_title="Day of Week",
        yaxis_title="Appointment Count",
        title={
            'text': "Appointments by Day of Week",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    st.plotly_chart(fig5)
    
elif view == "Referral ID Distribution":
    # Sidebar for HCP selection
    st.sidebar.header("HCP Filter")
    hcp_names_list = list(set(input_dataset["HCPName"]))
    selected_hcp = st.sidebar.selectbox("Select HCP", options=hcp_names_list, help="Select a healthcare provider to view referral ID distribution")
    combine_hcps = st.sidebar.checkbox("Combine all HCPs")

    if combine_hcps:
        # Use the entire dataset for all HCPs
        hcp_dataset = input_dataset
    else:
        # Filter dataset by selected HCP
        hcp_dataset = input_dataset[input_dataset["HCPName"] == selected_hcp]

    # Plotting the density heatmap
    fig6 = px.density_heatmap(
        hcp_dataset,
        x="TotalCountOfEventPerReferralID",
        y="HCPName" if combine_hcps else None,
        title=f"Referral ID Distribution for {selected_hcp}" if not combine_hcps else "Referral ID Distribution for All HCPs",
        labels={'TotalCountOfEventPerReferralID': 'Number of Appointments'},
        marginal_x="rug", marginal_y="box",
        nbinsx=30, nbinsy=30
    )

    # Add interactive tooltips
    fig6.update_traces(
        hovertemplate='HCP: %{y}<br>Appointments: %{x}<br>Count: %{z}'
    )

    # Add clustering (if desired)
    kmeans = KMeans(n_clusters=3)
    hcp_dataset['Cluster'] = kmeans.fit_predict(hcp_dataset[['TotalCountOfEventPerReferralID']])
    fig6.add_trace(go.Scatter(
        x=hcp_dataset['TotalCountOfEventPerReferralID'],
        y=hcp_dataset['Cluster'],
        mode='markers',
        marker=dict(color=hcp_dataset['Cluster'], colorscale='Viridis')
    ))

    # Customize layout
    fig6.update_layout(
        xaxis_title="Number of Appointments",
        yaxis_title="Density - Number of",
        title={
            'text': f"Referral ID Distribution for {selected_hcp}" if not combine_hcps else "Referral ID Distribution for All HCPs",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    st.plotly_chart(fig6)

elif view == "Pareto Analysis":
    # Calculate the total number of appointments for each DerReferralID
    referral_appointments = input_dataset.groupby('DerReferralID')['TotalCountOfEventPerReferralID'].sum().reset_index()
    
    # Sort the DerReferralIDs by the total number of appointments in descending order
    referral_appointments = referral_appointments.sort_values(by='TotalCountOfEventPerReferralID', ascending=False)
    
    # Calculate the cumulative percentage of appointments
    referral_appointments['CumulativeCount'] = referral_appointments['TotalCountOfEventPerReferralID'].cumsum()
    referral_appointments['CumulativePercentage'] = 100 * referral_appointments['CumulativeCount'] / referral_appointments['TotalCountOfEventPerReferralID'].sum()
    
    # Find the count of Referral IDs that make up 80% of appointments
    top_80_referrals_count = referral_appointments[referral_appointments['CumulativePercentage'] <= 80].shape[0]
    
    # Create a Pareto chart
    fig7 = px.bar(referral_appointments, x=referral_appointments.index + 1, y='TotalCountOfEventPerReferralID', title='Pareto Analysis of Referral ID Appointments')
    
    # Add a line for the cumulative percentage
    fig7.add_trace(go.Scatter(
        x=referral_appointments.index + 1,
        y=referral_appointments['CumulativePercentage'],
        mode='lines+markers',
        name='Cumulative Percentage',
        yaxis='y2'
    ))
    
    # Add a horizontal line for the 80% threshold
    fig7.add_shape(
        type='line',
        x0=0,
        y0=80,
        x1=len(referral_appointments),
        y1=80,
        line=dict(color='Red', dash='dash')
    )
    
    # Customize layout
    fig7.update_layout(
        xaxis_title="Referral Count",
        yaxis_title="Total Number of Events",
        yaxis2=dict(
            title="Cumulative Percentage of Events",
            overlaying='y',
            side='right'
        ),
        title={
            'text': "Pareto Analysis of Referral ID Appointments",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    st.plotly_chart(fig7)

elif view == "Age Cluster Map":
    # Sidebar for HCP selection
    st.sidebar.header("HCP Filter")
    hcp_names_list = list(set(input_dataset["HCPName"]))
    selected_hcps = st.sidebar.multiselect("Select HCPs", options=hcp_names_list, help="Select healthcare providers to view demographics cluster map")
    combine_hcps = st.sidebar.checkbox("Combine all HCPs")

    if combine_hcps:
        # Use the entire dataset for all HCPs
        hcp_dataset = input_dataset
    else:
        # Filter dataset by selected HCPs
        hcp_dataset = input_dataset[input_dataset["HCPName"].isin(selected_hcps)]

    # Check if the filtered dataset is empty
    if hcp_dataset.empty:
        st.warning("No data available for the selected HCPs.")
    else:
        # Clustering on demographic data
        demographic_data = hcp_dataset[['AgeAtContact']].dropna()  # Handle missing values if any

        if demographic_data.shape[0] < 1:
            st.warning("Not enough data available to perform clustering.")
        else:
            kmeans = KMeans(n_clusters=3)
            hcp_dataset['Cluster'] = kmeans.fit_predict(demographic_data)

            # Plotting the cluster map
            fig8 = px.scatter(
                hcp_dataset,
                x='AgeAtContact',  # Replace with actual demographic column
                y='TotalCountOfEventPerReferralID',  # Replace with actual demographic column
                color='Cluster',
                title='Demographics Cluster Map',
                hover_data=['AgeAtContact', 'TotalCountOfEventPerReferralID']  # Add other columns as needed
            )

            # Customize layout
            fig8.update_layout(
                xaxis_title="Age At Contact",  # Replace with actual title
                yaxis_title="Total Number of People at this age",  # Replace with actual title
                title={
                    'text': "Age Cluster Map",
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )
# GEOCODE - Not WORKING
#     # Display the merged GeoDataFrame
#     st.write("LSOA Boundaries with Patient Counts:")
#     st.write(lsoa_boundaries_2021)
    # # Apply the function to get coordinates
    # input_dataset[['Latitude', 'Longitude']] = input_dataset['PatientAddressPostcode'].apply(lambda x: pd.Series(postcode_to_coordinates(x)))

    # # Drop rows with missing coordinates
    # input_dataset = input_dataset.dropna(subset=['Latitude', 'Longitude'])

    # # Create a GeoDataFrame from the patient data
    # patient_gdf = gpd.GeoDataFrame(input_dataset, geometry=gpd.points_from_xy(input_dataset.Longitude, input_dataset.Latitude))

    # # Load the LSOA boundaries
    # lsoa_boundaries_2021 = gpd.read_file("Lower_layer_Super_Output_Areas_2021_EW_BGC_V3.geojson")

    # # Perform a spatial join
    # joined_gdf = gpd.sjoin(patient_gdf, lsoa_boundaries_2021, how="left", op="within")

    # # Count the number of patients in each LSOA
    # lsoa_counts = joined_gdf['LSOA21CD'].value_counts()

    # # Display the counts
    # st.write("Patient counts per LSOA:")
    # st.write(lsoa_counts)
        
    # # lsoa_boundaries_2021 = geopandas.read_file("Lower_layer_Super_Output_Areas_2021_EW_BGC_V3.geojson")
    
    # # Sidebar for geographic hotspot of activity
    # st.sidebar.header("Geographic Hotspot Filter")
    # selected_date_range = st.sidebar.date_input("Select Date Range", [dt.today() - timedelta(days=30), dt.today()])
    # selected_date_range = [pd.to_datetime(date) for date in selected_date_range]
    
    # # Filter dataset by selected date range
    # geo_dataset = input_dataset[(input_dataset["Appointment by Day"] >= selected_date_range[0]) & (input_dataset["Appointment by Day"] <= selected_date_range[1])]
    
    # # Convert postcode to coordinates
    # geo_dataset[['Latitude', 'Longitude']] = geo_dataset['PatientAddressPostcode'].apply(
    #     lambda x: pd.Series(postcode_to_coordinates(x))
    # )
    
    # # Create a GeoDataFrame
    # gdf = gpd.GeoDataFrame(geo_dataset, geometry=gpd.points_from_xy(geo_dataset.Longitude, geo_dataset.Latitude))
    
    # # Plotting
    # fig9 = px.scatter_mapbox(gdf, lat="Latitude", lon="Longitude", hover_name="PatientAddressPostcode",
    #                         hover_data=["Appointment by Day", "OutcomeDetails"], color_discrete_sequence=["fuchsia"], zoom=10, height=600)
    # fig9.update_layout(mapbox_style="open-street-map")
    # fig9.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    # st.plotly_chart(fig9)
