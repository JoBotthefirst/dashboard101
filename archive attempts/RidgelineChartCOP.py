import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib import patches
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


# Load the data
data_path = r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\ActivityDashboardJR.csv"
data = pd.read_csv(data_path, encoding='ISO-8859-1', dtype={
    'ï»¿DerReferralID': str,
    'ClientID': str,
    'HCPName': str,
    'ClinicDesc': str,
    'TotalCountOfEventPerReferralID': int,
    'AgeAtContact': float
}, low_memory=True)

# Check the column names
st.write("Column names in the dataset:", data.columns)

# Convert 'Appointment by Day' to datetime
data['Appointment by Day'] = pd.to_datetime(data['Appointment by Day'], format='%d/%m/%Y %H:%M', errors='coerce')

# Calculate additional metrics
if 'ï»¿DerReferralID' in data.columns and 'Appointment by Day' in data.columns:
    data['DaysBetween'] = data.groupby('ï»¿DerReferralID')['Appointment by Day'].transform(lambda x: (x.max() - x.min()).days)
else:
    st.error("Column 'ï»¿DerReferralID' or 'Appointment by Day' not found in the dataset.")
    st.stop()

# Prepare data for the ridgeline chart
ridgeline_data = data[['ClinicDesc', 'TotalCountOfEventPerReferralID']].dropna()

# Constants
bandwidth = 1
darkgreen = '#9BC184'
midgreen = '#C2D6A4'
lightgreen = '#E7E5CB'
colors = [lightgreen, midgreen, darkgreen, midgreen, lightgreen]
darkgrey = '#525252'

# Function to plot the distribution of TotalCountOfEventPerReferralID
def plot_distribution(axs, clinics, data, show_legend=False):
    for i, clinic in enumerate(clinics):
        subset = data[data['ClinicDesc'] == clinic]
        sns.kdeplot(subset['TotalCountOfEventPerReferralID'], fill=True, bw_adjust=bandwidth, ax=axs[i], color='grey', edgecolor='lightgrey')
        global_mean = data['TotalCountOfEventPerReferralID'].mean()
        axs[i].axvline(global_mean, color=darkgrey, linestyle='--')
        axs[i].text(-2000, 0, clinic.upper(), ha='left', fontsize=10, color=darkgrey)

        quantiles = np.percentile(subset['TotalCountOfEventPerReferralID'], [2.5, 10, 25, 75, 90, 97.5])
        for j in range(len(quantiles) - 1):
            axs[i].fill_between([quantiles[j], quantiles[j+1]], 0, 0.0002, color=colors[j])
        mean = subset['TotalCountOfEventPerReferralID'].mean()
        axs[i].scatter([mean], [0.0001], color='black', s=10)
        axs[i].set_xlim(0, 100)
        axs[i].set_ylim(0, 0.01)
        axs[i].set_ylabel('')
        axs[i].set_axis_off()
        if show_legend and i == 0:
            add_legend(axs[i], data, colors)

def add_legend(ax, data, colors):
    subax = inset_axes(ax, width="40%", height="350%", loc=1)
    subax.set_xticks([])
    subax.set_yticks([])
    subax.set_axis_off()
    subax.set_title('Legend', fontsize=12, color=darkgrey)
    global_mean = data['TotalCountOfEventPerReferralID'].mean()
    subax.axvline(global_mean, color=darkgrey, linestyle='--', label='Global Mean')
    for i, color in enumerate(colors):
        subax.fill_between([], [], color=color, label=f'Quantile {i+1}')
    subax.legend(loc='center left', frameon=False)

# Plot the ridgeline chart
clinics = ridgeline_data['ClinicDesc'].unique()
fig, axs = plt.subplots(len(clinics), 1, figsize=(10, len(clinics) * 2), sharex=True)
plot_distribution(axs, clinics, ridgeline_data, show_legend=True)

# Calculate the average number of days between the first and last appointment for each ï»¿DerReferralID
referral_duration = data.groupby('ï»¿DerReferralID')['Appointment by Day'].agg(['min', 'max'])
referral_duration['Duration'] = (referral_duration['max'] - referral_duration['min']).dt.days
average_duration = referral_duration['Duration'].mean()

# Create the subchart
fig2, ax2 = plt.subplots(figsize=(12, 4))
sns.histplot(referral_duration['Duration'], bins=30, kde=True, ax=ax2)
ax2.axvline(average_duration, color='r', linestyle='--')
ax2.text(average_duration + 1, ax2.get_ylim()[1] * 0.9, f'Average Duration: {average_duration:.2f} days', color='r')

ax2.set_title('Distribution of Referral Duration')
ax2.set_xlabel('Duration (days)')
ax2.set_ylabel('Count')

# Display the charts using Streamlit
st.title("Ridgeline Chart with Subchart")
st.pyplot(fig)
st.pyplot(fig2)