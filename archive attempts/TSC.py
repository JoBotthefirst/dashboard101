import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

st.title("Time Series of Discharge Counts")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
        
        # Ensure necessary columns exist. Handle missing gracefully.
        if not all(col in data.columns for col in ['Referral by Day', 'Discharge by Day']):
            st.error("CSV must contain 'Referral by Day' and 'Discharge by Day' columns.")
            st.stop()

    except pd.errors.ParserError:
        st.error("Error parsing CSV file. Please ensure the file is correctly formatted.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.stop()

    try:
        data['Referral by Day'] = pd.to_datetime(data['Referral by Day'], errors='coerce', dayfirst=True)
        data['Discharge by Day'] = pd.to_datetime(data['Discharge by Day'], errors='coerce', dayfirst=True)
        data = data.sort_values(by='Referral by Day')

        # Remove duplicate labels
        data = data.drop_duplicates(subset=['Referral by Day'])

        # Fill NaN values in 'Referral by Day' with NaT
        data = data.set_index('Referral by Day').asfreq('D').reset_index()
        data['Discharge by Day'].fillna(value=pd.NaT, inplace=True)
        data['Referral by Day'].fillna(value=pd.NaT, inplace=True)

        # User selects date range
        start_date = st.date_input('Start date', data['Referral by Day'].min())
        end_date = st.date_input('End date', data['Referral by Day'].max())
        if start_date > end_date:
            st.error('Error: End date must fall after start date.')
            st.stop()

        # Filter data by selected date range
        data = data[(data['Referral by Day'] >= pd.to_datetime(start_date)) & (data['Referral by Day'] <= pd.to_datetime(end_date))]

        # Count discharges by day
        # referral_counts = data['Referral by Day'].dropna().value_counts().sort_index()
        discharge_counts = data['Discharge by Day'].dropna().value_counts().sort_index()

        # Ensure all dates in the range are included
        all_dates = pd.date_range(start=start_date, end=end_date)
        # referral_counts = referral_counts.reindex(all_dates, fill_value=0)
        discharge_counts = discharge_counts.reindex(all_dates, fill_value=0)

        # Create a figure and axis
        fig, ax = plt.subplots()
        # ax.plot(referral_counts.index, referral_counts.values, label='Referral by Day', color='blue')
        ax.plot(discharge_counts.index, discharge_counts.values, label='Discharge by Day', color='red')

        # Customize layout
        ax.set_xlabel('Date')
        ax.set_ylabel('Count')
        ax.set_title('Discharge Counts Over Time')
        ax.legend()

        # Display the plot
        st.pyplot(fig)

        # Print table of discharges for the past 180 days
        past_180_days = data[data['Referral by Day'] >= (datetime.now() - pd.Timedelta(days=180))]
        # referral_counts_180 = past_180_days['Referral by Day'].value_counts().sort_index()
        discharge_counts_180 = past_180_days['Discharge by Day'].dropna().value_counts().sort_index()

        # Create a DataFrame for the table
        table_data = pd.DataFrame({
            'Date': discharge_counts_180.index,
            # 'Referral Count': referral_counts_180.values,
            'Discharge Count': discharge_counts_180.values
        })

        st.write("Discharges for the Past 180 Days")
        st.write(table_data)

    except ValueError as e:
        st.error(f"Error parsing dates: {e}")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.stop()