####colab code imported - for editing and 
# 
# # Import packages
import pandas as pd
import plotly.graph_objects as go
import io
# from google.colab import files

# Upload or read the CSV file
uploaded = files.upload()

# Get the correct key from the uploaded dictionary
file_name = list(uploaded.keys())[0]  # Get the first key
df = pd.read_csv(io.BytesIO(uploaded[file_name]))

# Print the columns of the DataFrame
print(df.columns)

# Replace blank 'Discharge Reason' with 'Accepted for LTC rehabilitation'
df['Discharge Reason'].fillna('Accepted for LTC rehabilitation', inplace=True)

# Combine 'Source of referral' into 'GP Written' or 'Other source of referral'
df['Source of referral'] = df['Source of referral'].apply(lambda x: 'GP Written' if x == 'GP Written' else 'Other source of referral')

# Create a list of unique labels for the Sankey diagram
labels = list(df['Neighbourhood of residence'].unique()) + \
         list(df['Source of referral'].unique()) + \
         list(df['Team Name'].unique()) + \
         list(df['Discharge Reason'].unique())

# Create a dictionary to map labels to indices
label_indices = {label: i for i, label in enumerate(labels)}

# Assign specific colors to each neighbourhood
neighbourhood_colors = {
    'Hackney Marshes': 'rgba(128,0,128,0.8)',  # Purple
    'London Fields': 'rgba(0,128,0,0.8)',      # Green
    'Hackney Downs': 'rgba(0,0,255,0.8)',      # Blue
    'Shoreditch Park': 'rgba(255,0,0,0.8)',    # Red
    'Springfield Park': 'rgba(255,165,0,0.8)', # Orange
    'Clissold Park': 'rgba(75,0,130,0.8)',     # Indigo
    'Woodberry Wetlands': 'rgba(0,255,255,0.8)', # Cyan
    'Well Street Common': 'rgba(255,20,147,0.8)', # Deep Pink
    # Add more neighbourhoods and their colors as needed
}

# Create lists to store source, target, value, and color for the Sankey diagram
source = []
target = []
value = []
link_colors = []

# Add flows from 'Neighbourhood of residence' to 'Source of referral'
for neighbourhood in df['Neighbourhood of residence'].unique():
    neighbourhood_data = df[df['Neighbourhood of residence'] == neighbourhood]
    for source_referral in neighbourhood_data['Source of referral'].unique():
        source.append(label_indices[neighbourhood])
        target.append(label_indices[source_referral])
        value.append(len(neighbourhood_data[neighbourhood_data['Source of referral'] == source_referral]))
        link_colors.append(neighbourhood_colors.get(neighbourhood, 'rgba(200,200,200,0.8)'))  # Default color if not specified

# Add flows from 'Source of referral' to 'Team Name'
for source_referral in df['Source of referral'].unique():
    source_referral_data = df[df['Source of referral'] == source_referral]
    for team in source_referral_data['Team Name'].unique():
        source.append(label_indices[source_referral])
        target.append(label_indices[team])
        value.append(len(source_referral_data[source_referral_data['Team Name'] == team]))
        link_colors.append(neighbourhood_colors.get(source_referral_data.iloc[0]['Neighbourhood of residence'], 'rgba(200,200,200,0.8)'))

# Add flows from 'Team Name' to 'Discharge Reason'
for team in df['Team Name'].unique():
    team_data = df[df['Team Name'] == team]
    for discharge_reason in team_data['Discharge Reason'].unique():
        source.append(label_indices[team])
        target.append(label_indices[discharge_reason])
        value.append(len(team_data[team_data['Discharge Reason'] == discharge_reason]))
        link_colors.append(neighbourhood_colors.get(team_data.iloc[0]['Neighbourhood of residence'], 'rgba(200,200,200,0.8)'))

# Define node colors with opacity
node_colors = [neighbourhood_colors.get(label, 'rgba(200,200,200,0.8)') for label in labels]

# Create the Sankey diagram
fig = go.Figure(data=[go.Sankey(
    valueformat=".0f",
    valuesuffix="",
    node=dict(
        pad=15,
        thickness=15,
        line=dict(color="black", width=0.5),
        label=labels,
        color=node_colors
    ),
    link=dict(
        source=source,
        target=target,
        value=value,
        color=link_colors
    )
)])

# Update layout settings
fig.update_layout(title_text="ACRT Team referrals Source and Outcome", font_size=10)

# Render the plot
fig.show()
