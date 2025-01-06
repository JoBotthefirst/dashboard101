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
view = st.sidebar.radio("Select view", ["Referral Source", "Referral Urgency", "Age Group", "Gender", "Ethnicity", "Neighbourhood", "Index of Deprivation"])

# Convert date columns to datetime
input_dataset['Referral by Day'] = pd.to_datetime(input_dataset['Referral by Day'], format='%d/%m/%Y %H:%M')
input_dataset['Discharge by Day'] = pd.to_datetime(input_dataset['Discharge by Day'], format='%d/%m/%Y %H:%M')

# Calculate the time from referral to discharge
input_dataset['Time from Referral to Discharge'] = (input_dataset['Discharge by Day'] - pd.to_datetime(input_dataset['Referral by Day'])).dt.days

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

# Function to create visualizations
def create_visualizations(df, demographic, filter_by_neighbourhood=False):
    if filter_by_neighbourhood:
        neighbourhoods = st.multiselect("Select Neighbourhoods", df['Neighbourhood of Residence'].unique(), default=df['Neighbourhood of Residence'].unique())
        df = df[df['Neighbourhood of Residence'].isin(neighbourhoods)]
    
    fig, ax = plt.subplots(2, 1, figsize=(12, 16), sharex=True)
    
    sns.violinplot(y=demographic, x='Time from Referral to Discharge', data=df, inner=None, split=True, ax=ax[0])
    sns.stripplot(y=demographic, x='Time from Referral to Discharge', data=df, color='black', alpha=0.5, ax=ax[0])
    mean_values = df.groupby(demographic)['Time from Referral to Discharge'].mean().reset_index()
    sns.pointplot(y=demographic, x='Time from Referral to Discharge', data=mean_values, color='red', ax=ax[0], join=False, markers='D')
    ax[0].set_title(f'Time from Referral to Discharge by {demographic}')
    ax[0].set_xlabel('Time from Referral to Discharge (days)')
    ax[0].set_ylabel(demographic)
    ax[0].set_ylim(-0.5, len(df[demographic].unique()) - 0.5)
    ax[0].tick_params(axis='y', rotation=45)
    ax[0].legend_ = None

    sns.scatterplot(y=demographic, x='Time from Referral to Discharge', data=df, ax=ax[1])
    ax[1].set_title(f'Time from Referral to Discharge by {demographic}')
    ax[1].set_xlabel('Time from Referral to Discharge (days)')
    ax[1].set_ylabel(demographic)
    ax[1].set_ylim(-0.5, len(df[demographic].unique()) - 0.5)
    ax[1].tick_params(axis='y', rotation=45)

    st.pyplot(fig)

    # Bar chart for demographic distribution
    plt.figure(figsize=(12, 8))
    demographic_counts = df[demographic].value_counts()
    sns.barplot(x=demographic_counts.index, y=demographic_counts.values)
    plt.title(f'Distribution of {demographic}')
    plt.xlabel(demographic)
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    st.pyplot(plt)

# Create visualizations based on selected view
if view == "Referral Source":
    create_visualizations(input_dataset, 'Referral Source', filter_by_neighbourhood=True)
elif view == "Referral Urgency":
    create_visualizations(input_dataset, 'Referral Urgency', filter_by_neighbourhood=True)
elif view == "Age Group":
    create_visualizations(input_dataset, 'Age Range', filter_by_neighbourhood=True)
elif view == "Gender":
    create_visualizations(input_dataset, 'Gender', filter_by_neighbourhood=True)
elif view == "Ethnicity":
    create_visualizations(input_dataset, 'Ethnicity', filter_by_neighbourhood=True)
elif view == "Neighbourhood":
    create_visualizations(input_dataset, 'Neighbourhood of Residence', filter_by_neighbourhood=False)
elif view == "Index of Deprivation":
    create_visualizations(input_dataset, 'Index of Deprivation', filter_by_neighbourhood=True)