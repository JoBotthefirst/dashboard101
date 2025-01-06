# read user input, and call it from an uploaded file

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
        
        # Ask for user input of column names
        date_column = st.text_input("Paste the name of the date column")
        referral_column = st.text_input("Paste the name of the referral column")
        discharge_column = st.text_input("Paste the name of the discharge column")
        
        # Ensure necessary columns exist. Handle missing gracefully.
        if not all(col in data.columns for col in [date_column, referral_column, discharge_column]):
            st.error(f"CSV must contain '{date_column}', '{referral_column}', and '{discharge_column}' columns.")
            st.stop()
        
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
