import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv(r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\referrals_test.csv")

# Convert date columns to datetime
df['Referral by Day'] = pd.to_datetime(df['Referral by Day'], format='%d/%m/%Y %H:%M')
df['Discharge by Day'] = pd.to_datetime(df['Discharge by Day'], format='%d/%m/%Y %H:%M')

# Handle NaN values in 'Discharge by Day'
df['Discharge by Day'] = df['Discharge by Day'].fillna(df['Referral by Day'].max())

# Calculate daily counts
daily_referrals = df.groupby(df['Referral by Day'].dt.date).size().reset_index(name='Daily Referrals')
daily_discharges = df.groupby(df['Discharge by Day'].dt.date).size().reset_index(name='Daily Discharges')

# Merge daily counts into a single DataFrame
daily_totals = pd.merge(daily_referrals, daily_discharges, left_on='Referral by Day', right_on='Discharge by Day', how='outer').fillna(0)

# Ensure the merged DataFrame has the correct number of columns before renaming
daily_totals.columns = ['Referral Date', 'Daily Referrals', 'Discharge Date', 'Daily Discharges']

# Rename columns for clarity
daily_totals = daily_totals[['Referral Date', 'Daily Referrals', 'Daily Discharges']]
daily_totals.columns = ['Date', 'Daily Referrals', 'Daily Discharges']

# Filter dates to only show from 2023 and 2024
daily_totals = daily_totals[(daily_totals['Date'].dt.year >= 2023) & (daily_totals['Date'].dt.year <= 2024)]

# Calculate net daily referrals
daily_totals['Net Referrals'] = daily_totals['Daily Referrals'] - daily_totals['Daily Discharges']

# Add a starting count of 100 to the cumulative waiting count
daily_totals['Cumulative Waiting'] = daily_totals['Net Referrals'].cumsum() + 100

# Ensure 'Date' column is of datetime type
daily_totals['Date'] = pd.to_datetime(daily_totals['Date'])

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(12, 6))

# Plot the net daily referrals
ax.bar(daily_totals['Date'], daily_totals['Net Referrals'], color='orange', label='Net Daily Referrals')

# Plot the cumulative number of referrals waiting for service
ax.plot(daily_totals['Date'], daily_totals['Cumulative Waiting'], color='blue', label='Cumulative Waiting for Service')

ax.set_xlim(daily_totals['Date'].min(), daily_totals['Date'].max())
ax.set_ylim(min(daily_totals['Net Referrals'].min(), 0), max(daily_totals['Cumulative Waiting'].max(), 1) * 1.1)

# Labels and title
ax.set_xlabel('Date')
ax.set_ylabel('Count')
ax.set_title('Net Daily Referrals and Cumulative Number of Referrals Waiting for Service Over Time')
ax.legend()

# Show the plot
st.pyplot(fig)

# Print table showing counts for each day
print(daily_totals[['Date', 'Daily Referrals', 'Daily Discharges', 'Net Referrals', 'Cumulative Waiting']])
