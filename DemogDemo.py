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
view = st.sidebar.radio("Select view", ["Age Group", "Gender", "Ethnicity", "Neighbourhood", "Index of Deprivation", "Referral Source", "Referral Urgency"])
neighbourhoods = st.sidebar.multiselect("Select Neighbourhoods", options=["All Neighbourhoods"] + list(input_dataset['Neighbourhood of Residence'].unique()), default=["All Neighbourhoods"])

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
    if "All Neighbourhoods" not in neighbourhoods:
        df = df[df['Neighbourhood of Residence'].isin(neighbourhoods)]
    
    # Bar chart for demographic distribution
    plt.figure(figsize=(12, 8))
    demographic_counts = df[demographic].value_counts()
    palette = sns.color_palette("viridis", len(demographic_counts))
    sns.barplot(x=demographic_counts.index, y=demographic_counts.values, palette=palette)
    plt.title(f'Distribution of {demographic}')
    plt.xlabel(demographic)
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')  # Rotate labels to 45 degrees
    st.pyplot(plt)
    
    # Order the dataframe by the density of the demographic
    df[demographic] = pd.Categorical(df[demographic], categories=demographic_counts.index, ordered=True)
    df = df.sort_values(by=demographic)
    
    fig, ax = plt.subplots(2, 1, figsize=(12, 16), sharex=True)
    
    sns.violinplot(y=demographic, x='Time from Referral to Discharge', data=df, inner=None, split=True, ax=ax[0], palette=palette)
    sns.stripplot(y=demographic, x='Time from Referral to Discharge', data=df, color='black', alpha=0.5, ax=ax[0])
    ax[0].set_title(f'Time from Referral to Discharge by {demographic}')
    ax[0].set_xlabel('Time from Referral to Discharge (days)')
    ax[0].set_ylabel(demographic)
    ax[0].set_ylim(-0.5, len(df[demographic].unique()) - 0.5)
    ax[0].tick_params(axis='y', rotation=45)
    ax[0].legend_ = None

    sns.scatterplot(y=demographic, x='Time from Referral to Discharge', data=df, ax=ax[1], palette=palette)
    ax[1].set_title(f'Time from Referral to Discharge by {demographic}')
    ax[1].set_xlabel('Time from Referral to Discharge (days)')
    ax[1].set_ylabel(demographic)
    ax[1].set_ylim(-0.5, len(df[demographic].unique()) - 0.5)
    ax[1].tick_params(axis='y', rotation=45)

    st.pyplot(fig)

    # Pyramid chart for age distribution
    if demographic == 'Age Range':
        df_age = df[df['AgeAtReferral'] >= 18]
        df_age['Age Group'] = pd.cut(df_age['AgeAtReferral'], bins=range(18, df_age['AgeAtReferral'].max() + 5, 5), right=False)
        age_counts = df_age['Age Group'].value_counts().sort_index(ascending=True)
        
        # Create male and female counts for the pyramid chart
        male_counts = df_age[df_age['Gender'] == 'Male']['Age Group'].value_counts().sort_index(ascending=True)
        female_counts = df_age[df_age['Gender'] == 'Female']['Age Group'].value_counts().sort_index(ascending=True)
        
        # Ensure both series have the same index
        age_counts = age_counts.reindex(male_counts.index.union(female_counts.index), fill_value=0)
        male_counts = male_counts.reindex(age_counts.index, fill_value=0)
        female_counts = female_counts.reindex(age_counts.index, fill_value=0)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.barplot(x=-male_counts.values, y=male_counts.index, palette=sns.color_palette("Purples", len(male_counts)), ax=ax, label='Male')
        sns.barplot(x=female_counts.values, y=female_counts.index, palette=sns.color_palette("Oranges", len(female_counts)), ax=ax, label='Female')
        ax.set_title('Pyramid Chart of Age Distribution (18+)')
        ax.set_xlabel('Count')
        ax.set_ylabel('Age Group')
        ax.legend(title='Gender', labels=['Male', 'Female'], loc='center left', bbox_to_anchor=(1, 0.5))
        ax.set_xlim(-max(male_counts.max(), female_counts.max()), max(male_counts.max(), female_counts.max()))
        ax.invert_yaxis()  # Invert the y-axis
        st.pyplot(fig)

# Create visualizations based on selected view
if view == "Gender":
    create_visualizations(input_dataset, 'Gender', filter_by_neighbourhood=True)
elif view == "Age Group":
    create_visualizations(input_dataset, 'Age Range', filter_by_neighbourhood=True)
elif view == "Ethnicity":
    create_visualizations(input_dataset, 'Ethnicity', filter_by_neighbourhood=True)
elif view == "Neighbourhood":
    create_visualizations(input_dataset, 'Neighbourhood of Residence', filter_by_neighbourhood=False)
elif view == "Index of Deprivation":
    create_visualizations(input_dataset, 'Index of Deprivation', filter_by_neighbourhood=True)
elif view == "Referral Source":
    create_visualizations(input_dataset, 'Referral Source', filter_by_neighbourhood=True)
elif view == "Referral Urgency":
    create_visualizations(input_dataset, 'Referral Urgency', filter_by_neighbourhood=True)




