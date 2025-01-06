# Define a class to represent a client
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import pandas as pd

# Load dataset
input_dataset = pd.read_csv(
    r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\referrals_test.csv")

# Print the columns of the dataset to debug
print("Columns in input_dataset:", input_dataset.columns)

# Convert date columns to datetime
input_dataset['Referral by Day'] = pd.to_datetime(input_dataset['Referral by Day'], format='%d/%m/%Y %H:%M')
input_dataset['Discharge by Day'] = pd.to_datetime(input_dataset['Discharge by Day'], format='%d/%m/%Y %H:%M')

# Calculate the time from referral to discharge
input_dataset['Time from Referral to Discharge'] = (input_dataset['Discharge by Day'] - input_dataset['Referral by Day']).dt.days

# Print the first few rows to debug
print("First few rows of input_dataset:", input_dataset.head())

# Define age ranges
def categorize_age(age):
    if 18 <= age <= 30:
        return '18-30'
    elif 31 <= age <= 50:
        return '31-50'
    elif 51 <= age <= 65:
        return '51-65'
    elif 66 <= age <= 150:
        return '66-150'
    else:
        return 'Unknown'

input_dataset['Age Range'] = input_dataset['AgeAtReferral'].apply(categorize_age)

# Print the unique values in 'Age Range' to debug
print("Unique values in Age Range:", input_dataset['Age Range'].unique())

# Define classes
class Client:
    def __init__(self, client_id, ethnicity, gender, neighbourhood, index_of_deprivation, age_group, referral_status, referral_reason, discharge_reason):
        self.client_id = client_id
        self.ethnicity = ethnicity
        self.gender = gender
        self.neighbourhood = neighbourhood
        self.index_of_deprivation = index_of_deprivation
        self.age_group = age_group
        self.referral_status = referral_status
        self.referral_reason = referral_reason
        self.discharge_reason = discharge_reason

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

    # Count occurrences of each demographic attribute
    for client in clients:
        ethnicity_count[client.ethnicity] = ethnicity_count.get(client.ethnicity, 0) + 1
        gender_count[client.gender] = gender_count.get(client.gender, 0) + 1
        neighbourhood_count[client.neighbourhood] = neighbourhood_count.get(client.neighbourhood, 0) + 1
        deprivation_count[client.index_of_deprivation] = deprivation_count.get(client.index_of_deprivation, 0) + 1
        age_group_count[client.age_group] = age_group_count.get(client.age_group, 0) + 1
        referral_status_count[client.referral_status] = referral_status_count.get(client.referral_status, 0) + 1
        referral_reason_count[client.referral_reason] = referral_reason_count.get(client.referral_reason, 0) + 1
        discharge_reason_count[client.discharge_reason] = discharge_reason_count.get(client.discharge_reason, 0) + 1

    # Print the counts to highlight inequalities
    print("Ethnicity Count:", ethnicity_count)
    print("Gender Count:", gender_count)
    print("Neighbourhood Count:", neighbourhood_count)
    print("Index of Deprivation Count:", deprivation_count)
    print("Age Group Count:", age_group_count)
    print("Referral Status Count:", referral_status_count)
    print("Referral Reason Count:", referral_reason_count)
    print("Discharge Reason Count:", discharge_reason_count)

# Function to create visualizations
def create_visualizations(df):
    # Filterable charts for gender
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Gender', y='Time from Referral to Discharge', data=df)
    plt.title('Time from Referral to Discharge by Gender')
    plt.show()

    # Filterable charts for age range
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Age Range', y='Time from Referral to Discharge', data=df)
    plt.title('Time from Referral to Discharge by Age Range')
    plt.show()

    # Filterable charts for ethnicity
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Ethnicity', y='Time from Referral to Discharge', data=df)
    plt.title('Time from Referral to Discharge by Ethnicity')
    plt.xticks(rotation=90)
    plt.show()

    # Filterable charts for LSOA (neighbourhood)
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Neighbourhood of Residence', y='Time from Referral to Discharge', data=df)
    plt.title('Time from Referral to Discharge by Neighbourhood')
    plt.xticks(rotation=90)
    plt.show()

# Example usage
clients = [
    Client(1000025, "White - Any other background", "Female", "London Fields neighbourhood", 4, "66-85", "Closed", "Assessment", "Patient Requested Discharge"),
    Client(1000075, "White - Any other background", "Female", "London Fields neighbourhood", 2, "85+", "Closed", "Assessment", "Rejected - Returned to Referrer (Inappropriate Referral)")
]

# Convert clients to DataFrame
clients_df = pd.DataFrame([vars(client) for client in clients])

# Print the columns of clients_df to debug
print("Columns in clients_df:", clients_df.columns)

# Merge with input dataset
merged_df = pd.merge(input_dataset, clients_df, left_on='ClientID', right_on='client_id', how='inner')

# Print the columns of merged_df to debug
print("Columns in merged_df:", merged_df.columns)

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
print("First few rows of merged_df:", merged_df.head())

#  Create visualizations
create_visualizations(merged_df)

analyze_inequalities(clients)