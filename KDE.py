import plotly.graph_objects as go
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

# Example data: Date, number of appointments, and number of people
np.random.seed(0)
###dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
df = pd.read_csv(
    r"C:\Users\juski\Desktop\Joel\HSMA\ACRT Projects\DASHBOARD VIZ\ActivityDashboardJR.csv",
    dtype={
        'ClientID': str,
        'HCPName': str,
        'ClinicDesc': str,
        'TotalCountOfEventPerReferralID': int,
        'AgeAtContact': float
    },
    parse_dates=['Appointment by Day'],  # Correct column name for parsing dates
    date_parser=lambda x: pd.to_datetime(x, format='%d/%m/%Y %H:%M'),
    low_memory=True
)

# Filter data for the past 12 months
end_date = pd.to_datetime(df['Appointment by Day'].max())
start_date = end_date - pd.DateOffset(months=12)
df = df[(df['Appointment by Day'] >= start_date) & (df['Appointment by Day'] <= end_date)]

dates = df['Appointment by Day']
appointments = df['TotalCountOfEventPerReferralID']
people = df['AgeAtContact']

# Convert dates to ordinal for KDE
df['Date_ordinal'] = df['Appointment by Day'].apply(lambda x: x.toordinal())

# Perform KDE
kde = gaussian_kde([df['Date_ordinal'], appointments, people])
x, y, z = np.meshgrid(np.linspace(df['Date_ordinal'].min(), df['Date_ordinal'].max(), 50),
                      np.linspace(appointments.min(), appointments.max(), 50),
                      np.linspace(people.min(), people.max(), 50))
positions = np.vstack([x.ravel(), y.ravel(), z.ravel()])
density = np.reshape(kde(positions).T, x.shape)

# Create 3D plot
fig = go.Figure(data=go.Volume(
    x=x.flatten(), y=y.flatten(), z=z.flatten(), value=density.flatten(),
    isomin=0.01, isomax=density.max(),
    opacity=0.1,  # Adjust opacity for better visualization
    surface_count=20,  # Number of isosurfaces
    colorscale='Viridis'
))

fig.update_layout(scene=dict(
    xaxis_title='Time in service',
    yaxis_title='Number of Appointments',
    zaxis_title='Number of People'
))

# Add explanation text
fig.add_annotation(
    text="This 3D plot shows the density of appointments and people over time.",
    xref="paper", yref="paper",
    x=0.5, y=1.1, showarrow=False,
    font=dict(size=12)
)

fig.show()
