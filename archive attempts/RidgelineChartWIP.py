import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib import patches
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import streamlit as st

# Load data
# Load the CSV file with specified dtypes ?datadictionary
input_dataset = pd.read_csv(
    r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\ActivityDashboardJR.csv",
    encoding='unicode_escape',
    dtype={
        'ï»¿DerReferralID': str, # referral id as string
        'ClientID': str,  # ClientID column as string
        'HCPName': str,  # HCPName column as string
        'ClinicDesc': str,  # ClinicDesc column as string
        'TotalCountOfEventPerReferralID': int,  # TotalCountOfEventPerReferralID column as integer
        'AgeAtContact': float  # AgeAtContact column as float
    },
    low_memory=False  # Optimize memory usage TRUE would mean slower but less memory usage
)

data = input_dataset.copy()
# Calculate additional metrics
data['Appointment by Day'] = pd.to_datetime(data['Appointment by Day'], format='%d/%m/%Y %H:%M')
data['DaysBetween'] = data.groupby('ï»¿DerReferralID')['Appointment by Day'].transform(lambda x: (x.max() - x.min()).days)
                 
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
    example_subset = data[data['ClinicDesc'] == data['ClinicDesc'].unique()[0]]
    sns.kdeplot(example_subset['TotalCountOfEventPerReferralID'], fill=True, ax=subax, color='grey', edgecolor='lightgrey')
    quantiles = np.percentile(example_subset['TotalCountOfEventPerReferralID'], [2.5, 10, 25, 75, 90, 97.5])
    for j in range(len(quantiles) - 1):
        subax.fill_between([quantiles[j], quantiles[j+1]], 0, 0.00004, color=colors[j])
    subax.set_xlim(-5, 100)
    subax.set_ylim(-0.0002, 0.01)
    mean = example_subset['TotalCountOfEventPerReferralID'].mean()
    subax.scatter([mean], [0.00002], color='black', s=10)
    subax.text(-3, 0.009, 'Legend', ha='left', fontsize=12)
    subax.text(80, 0.005, 'Distribution\nof counts', ha='center', fontsize=7)
    subax.text(mean+5, 0.003, 'Mean', ha='center', fontsize=7)
    subax.text(90, -0.001, "95% of counts", ha='center', fontsize=6)
    subax.text(60, -0.001, "80% of counts", ha='center', fontsize=6)
    subax.text(20, -0.0015, "50% of counts\nfall within this range", ha='center', fontsize=6)
    add_arrow((mean, 0.005), (mean+5, 0.007), subax)
    add_arrow((mean+20, 0), (mean+25, -0.001), subax)
    add_arrow((mean+40, 0), (mean+45, -0.001), subax)
    add_arrow((mean-10, 0), (mean-15, -0.001), subax)

def add_arrow(head_pos, tail_pos, ax):
    style = "Simple, tail_width=0.01, head_width=1, head_length=2"
    kw = dict(arrowstyle=style, color="k", linewidth=0.2)
    arrow = patches.FancyArrowPatch(tail_pos, head_pos, connectionstyle="arc3,rad=.5", **kw)
    ax.add_patch(arrow)

def add_line(xpos, ypos, fig):
    line = Line2D(xpos, ypos, color='lightgrey', lw=0.2, transform=fig.transFigure)
    fig.lines.append(line)

# Plotting
clinics = data['ClinicDesc'].unique().tolist()
num_clinics = len(clinics)
fig, axs = plt.subplots(nrows=num_clinics, ncols=1, figsize=(8, 10))
axs = axs.flatten()
plot_distribution(axs, clinics, data, show_legend=False)

fig.text(0.35, 0.88, 'Mean count of events per referral ID', ha='center', fontsize=10)

fig, axs = plt.subplots(nrows=num_clinics, ncols=1, figsize=(8, 10))
axs = axs.flatten()
plot_distribution(axs, clinics, data, show_legend=True)

fig.text(0.35, 0.88, 'Mean count of events per referral ID', ha='center', fontsize=10)
fig.text(-0.03, -0.08, """
Axis capped at 100 counts.
Data: Activity Dashboard.
Visualization: Joel
""", ha='left', fontsize=8)
fig.text(0.5, 0.03, "Count of events", ha='center', fontsize=14)
fig.text(-0.03, 0.93, """
Distribution of event counts per referral ID for different clinics.
""", ha='left', fontsize=12)
fig.text(-0.03, 1.04, "EVENT COUNTS PER REFERRAL ID", ha='left', fontsize=18)

add_line([0.317, 0.317], [0.1, 0.9], fig)
add_line([0.51, 0.51], [0.1, 0.9], fig)
add_line([0.703, 0.703], [0.1, 0.9], fig)
add_line([0.896, 0.896], [0.1, 0.9], fig)

output_path = 'C:/Users/juski/Desktop/Joel/HSMA/ACRT Projects/DASHBOARD VIZ/web-ridgeline-by-clinic.png'
# Ensure the directory exists or update the path
import os
if not os.path.exists(os.path.dirname(output_path)):
    os.makedirs(os.path.dirname(output_path))

plt.savefig(output_path, dpi=300, bbox_inches='tight')
st.pyplot(fig)
