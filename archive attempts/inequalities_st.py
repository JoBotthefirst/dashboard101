import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import pandas as pd
import numpy as np

# Load dataset
input_dataset = pd.read_csv(
    r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\referrals_test.csv")

# Streamlit app
st.title("ACRT Demographics")

# Sidebar for navigation
st.sidebar.title("Navigation")
view = st.sidebar.radio("Select view", ["Age Group", "Gender", "Ethnicity", "Index of Deprivation", "Neighbourhood", "Referral Source", "Referral Urgency"])

# Convert date columns to datetime
input_dataset['Referral by Day'] = pd.to_datetime(input_dataset['Referral by Day'], format='%d/%m/%Y %H:%M')
input_dataset['Discharge by Day'] = pd.to_datetime(input_dataset['Discharge by Day'], format='%d/%m/%Y %H:%M')

# Calculate the time from referral to discharge
input_dataset['Time from Referral to Discharge'] = (input_dataset['Discharge by Day'] - input_dataset['Referral by Day']).dt.days

# Define age ranges
def categorize_age(age):
    if 18 <= age <= 30:
        return '18-30'
    elif 31 <= age <= 50:
        return '31-50'
    elif 51 <= age <= 65:
        return '51-65'
    elif 66 <= age:
        return 'over 66'
    else:
        return 'Unknown'

input_dataset['Age Range'] = input_dataset['AgeAtReferral'].apply(categorize_age)

# Define classes
class Client:
    def __init__(self, client_id, ethnicity, gender, neighbourhood, index_of_deprivation, age_group, referral_status, referral_reason, discharge_reason, referral_date, discharge_date):
        self.client_id = client_id
        self.ethnicity = ethnicity
        self.gender = gender
        self.neighbourhood = neighbourhood
        self.index_of_deprivation = index_of_deprivation
        self.age_group = age_group
        self.referral_status = referral_status
        self.referral_reason = referral_reason
        self.discharge_reason = discharge_reason
        self.time_in_service = (pd.to_datetime(discharge_date) - pd.to_datetime(referral_date)).days

# Function to analyze inequalities
def analyze_inequalities(clients):
    # Initialize counters for different demographics
    ethnicity_count = {}
    gender_count = {}
    neighbourhood_count = {}
    deprivation_count = {}
    age_group_count = {}
    referral_status_count = {}
    referral_reason_count = {}
    discharge_reason_count = {}

    # Prepare data for visualization
    data = {
        'ClientID': [],
        'Ethnicity': [],
        'Gender': [],
        'Neighbourhood': [],
        'Index of Deprivation': [],
        'Age Group': [],
        'Referral Status': [],
        'Referral Reason': [],
        'Discharge Reason': [],
        'Time in Service': [],
        'Count of Activities': []
    }

    # Count occurrences of each demographic attribute and prepare data for visualization
    for client in clients:
        ethnicity_count[client.ethnicity] = ethnicity_count.get(client.ethnicity, 0) + 1
        gender_count[client.gender] = gender_count.get(client.gender, 0) + 1
        neighbourhood_count[client.neighbourhood] = neighbourhood_count.get(client.neighbourhood, 0) + 1
        deprivation_count[client.index_of_deprivation] = deprivation_count.get(client.index_of_deprivation, 0) + 1
        age_group_count[client.age_group] = age_group_count.get(client.age_group, 0) + 1
        referral_status_count[client.referral_status] = referral_status_count.get(client.referral_status, 0) + 1
        referral_reason_count[client.referral_reason] = referral_reason_count.get(client.referral_reason, 0) + 1
        discharge_reason_count[client.discharge_reason] = discharge_reason_count.get(client.discharge_reason, 0) + 1

        data['ClientID'].append(client.client_id)
        data['Ethnicity'].append(client.ethnicity)
        data['Gender'].append(client.gender)
        data['Neighbourhood'].append(client.neighbourhood)
        data['Index of Deprivation'].append(client.index_of_deprivation)
        data['Age Group'].append(client.age_group)
        data['Referral Status'].append(client.referral_status)
        data['Referral Reason'].append(client.referral_reason)
        data['Discharge Reason'].append(client.discharge_reason)
        data['Time in Service'].append(client.time_in_service)
        data['Count of Activities'].append(1)  # Assuming each client has one activity for simplicity

    df = pd.DataFrame(data)

    # Visualize time in service by demographic attributes
    fig, ax = plt.subplots(figsize=(10, 6))

    # Half-violin plot
    sns.violinplot(
        x="Time in Service", y="Age Group", data=df, palette="muted", inner=None, ax=ax, split=True
    )

    # Rain chart
    for i, age_group in enumerate(df['Age Group'].unique()):
        data = df[df['Age Group'] == age_group]
        y = i + np.random.uniform(high=0.2, size=len(data))
        x = data['Time in Service']
        ax.scatter(x, y, alpha=0.6)

    ax.set_title("Half-Violin Plot and Rain Chart")
    ax.set_xlabel("Time in Service")
    ax.set_ylabel("Age Group")

    st.pyplot(fig)

# Function to create visualizations
def create_visualizations(df, demographic, filter_by_neighbourhood=False):
    if filter_by_neighbourhood:
        neighbourhoods = st.multiselect("Select Neighbourhoods", df['Neighbourhood of Residence'].unique(), default=df['Neighbourhood of Residence'].unique())
        df = df[df['Neighbourhood of Residence'].isin(neighbourhoods)]
    
    plt.figure(figsize=(10, 6))
    sns.violinplot(x=demographic, y='Time from Referral to Discharge', data=df)
    plt.title(f'Time from Referral to Discharge by {demographic}')
    plt.axhline(df['Time from Referral to Discharge'].mean(), color='r', linestyle='--', label='Mean')
    plt.legend()
    st.pyplot(plt)

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=demographic, y='Activity Count', data=df)
    plt.title(f'Activity Count by {demographic}')
    st.pyplot(plt)

    # Print the first few rows of filtered dataset to debug
    st.write("First few rows of filtered_dataset:", df.head())

# Streamlit app
st.title("Inequalities Visualization Dashboard")

# Filter dataset based on age range
filtered_dataset = input_dataset

# Create visualizations based on selected view
if view == "Age Group":
    create_visualizations(filtered_dataset, 'Age Range', filter_by_neighbourhood=True)
elif view == "Gender":
    create_visualizations(filtered_dataset, 'Gender', filter_by_neighbourhood=True)
elif view == "Ethnicity":
    create_visualizations(filtered_dataset, 'Ethnicity', filter_by_neighbourhood=True)
elif view == "Index of Deprivation":
    create_visualizations(filtered_dataset, 'Index of Deprivation', filter_by_neighbourhood=True)
elif view == "Neighbourhood":
    create_visualizations(filtered_dataset, 'Neighbourhood of Residence', filter_by_neighbourhood=False)
elif view == "Referral Source":
    create_visualizations(filtered_dataset, 'Referral Source', filter_by_neighbourhood=True)
elif view == "Referral Urgency":
    create_visualizations(filtered_dataset, 'Referral Urgency', filter_by_neighbourhood=True)

# Example usage
clients = [
    Client(1000025, "White - Any other background", "Female", "London Fields neighbourhood", 4, "66-85", "Closed", "Assessment", "Patient Requested Discharge", "2021-01-01", "2021-06-01"),
    Client(1000075, "White - Any other background", "Female", "London Fields neighbourhood", 2, "85+", "Closed", "Assessment", "Rejected - Returned to Referrer (Inappropriate Referral)", "2021-02-01", "2021-07-01")
]

# Convert clients to DataFrame
clients_df = pd.DataFrame([vars(client) for client in clients])

# Print the columns of clients_df to debug
st.write("Columns in clients_df:", clients_df.columns)

# Merge with input dataset
merged_df = pd.merge(input_dataset, clients_df, left_on='ClientID', right_on='client_id', how='inner')

# Print the columns of merged_df to debug
st.write("Columns in merged_df:", merged_df.columns)

# Ensure correct handling of "Neighbourhood of Residence" values
neighbourhoods = [
    "London Fields neighbourhood",
    "Springfield Park neighbourhood",
    "Clissold Park neighbourhood",
    "Hackney Downs neighbourhood",
    "Hackney Marshes neighbourhood",
    "Woodberry Wetlands neighbourhood",
    "Shoreditch Park and City neighbourhood",
    "Well Street Common neighbourhood",
    "OutOfArea"
]

merged_df = merged_df[merged_df['Neighbourhood of Residence'].isin(neighbourhoods)]

# Print the first few rows of merged_df to debug
st.write("First few rows of merged_df:", merged_df.head())

# Analyze inequalities
analyze_inequalities(clients)

# Calculate and show mean for each index of deprivation separately
def show_mean_by_deprivation(df):
    deprivation_means = df.groupby('Index of Deprivation')['Time from Referral to Discharge'].mean().reset_index()
    st.write("Mean Time from Referral to Discharge by Index of Deprivation:")
    st.write(deprivation_means)

show_mean_by_deprivation(filtered_dataset)