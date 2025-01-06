# Example code to show correlation networks
import random
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Generate client IDs
client_ids = [f"{1000000 + i}" for i in range(150)]

# Generate referral IDs
referral_ids = []
for client_id in client_ids:
    num_referrals = random.randint(1, 5)  # Each client can have 1 to 5 referrals
    for _ in range(num_referrals):
        referral_suffix = random.choice([23, 33])
        referral_ids.append(f"{client_id}_{referral_suffix}")

# Ensure we have exactly 300 referrals
while len(referral_ids) < 300:
    client_id = random.choice(client_ids)
    referral_suffix = random.choice([23, 33])
    referral_ids.append(f"{client_id}_{referral_suffix}")

# If we have more than 300 referrals, trim the list
referral_ids = referral_ids[:300]

# Sample data to simulate the given table
hcp_codes = [
    'SmytheE01', 'TaylorM01', 'BrownJ01', 'JohnsonS01', 'WilsonL01',
    'DavisA01', 'MartinezJ01', 'AndersonE01', 'ThomasM01', 'JacksonH01',
    'WhiteS01', 'HarrisO01', 'MartinE01', 'ThompsonA01', 'GarciaI01',
    'MartinezM01', 'RobinsonC01', 'ClarkA01', 'LewisH01', 'WalkerE01',
    'HallA01', 'AllenE01', 'YoungS01', 'KingG01', 'WrightV01',
    'ScottL01', 'GreenA01', 'AdamsC01', 'BakerL01', 'NelsonZ01',
    'CarterN01', 'MitchellR01', 'PerezL01', 'RobertsA01', 'TurnerE01',
    'PhillipsS01', 'CampbellN01', 'ParkerL01', 'EvansP01', 'EdwardsS01',
    'CollinsC01', 'StewartS01', 'SanchezV01', 'MorrisA01', 'RogersP01',
    'ReedH01', 'CookL01', 'MorganA01', 'BellB01', 'MurphyW01',
    'BaileyL01', 'RiveraA01', 'CooperA01', 'RichardsonS01', 'CoxM01',
    'HowardE01', 'WardA01', 'TorresM01', 'PetersonM01', 'GrayE01',
    'RamirezA01', 'JamesC01', 'WatsonK01', 'BrooksG01', 'KellyK01',
    'SandersA01', 'PriceM01', 'BennettH01', 'WoodG01', 'BarnesN01',
    'RossE01', 'HendersonS01', 'DoeJ01', 'SmithM01', 'JohnsonJ01',
    'BrownR01', 'JonesD01', 'GarciaW01', 'MartinezJ01', 'AndersonC01',
    'TaylorT01', 'ThomasC01', 'HernandezD01', 'MooreM01', 'MartinA01',
    'JacksonM01', 'ThompsonP01', 'WhiteS01', 'HarrisA01', 'ClarkJ01',
    'LewisK01', 'WalkerB01', 'HallG01', 'AllenE01', 'YoungR01',
    'KingT01', 'WrightJ01', 'ScottJ01', 'GreenR01', 'AdamsJ01'
] * (300 // 100 + 1)

hcp_names = [
    'Emily Smythe', 'Michelle Taylor', 'Jessica Brown', 'Sarah Johnson', 'Laura Wilson',
    'Amanda Davis', 'Jennifer Martinez', 'Elizabeth Anderson', 'Megan Thomas', 'Hannah Jackson',
    'Sophia White', 'Olivia Harris', 'Emma Martin', 'Ava Thompson', 'Isabella Garcia',
    'Mia Martinez', 'Charlotte Robinson', 'Amelia Clark', 'Harper Lewis', 'Evelyn Walker',
    'Abigail Hall', 'Ella Allen', 'Scarlett Young', 'Grace King', 'Victoria Wright',
    'Lily Scott', 'Aria Green', 'Chloe Adams', 'Layla Baker', 'Zoe Nelson',
    'Nora Carter', 'Riley Mitchell', 'Lillian Perez', 'Aubrey Roberts', 'Ellie Turner',
    'Stella Phillips', 'Natalie Campbell', 'Lucy Parker', 'Paisley Evans', 'Savannah Edwards',
    'Claire Collins', 'Skylar Stewart', 'Violet Sanchez', 'Aurora Morris', 'Penelope Rogers',
    'Hazel Reed', 'Luna Cook', 'Addison Morgan', 'Brooklyn Bell', 'Willow Murphy',
    'Leah Bailey', 'Audrey Rivera', 'Anna Cooper', 'Samantha Richardson', 'Madison Cox',
    'Eleanor Howard', 'Ariana Ward', 'Mila Torres', 'Maya Peterson', 'Eva Gray',
    'Alyssa Ramirez', 'Caroline James', 'Kennedy Watson', 'Genesis Brooks', 'Kinsley Kelly',
    'Allison Sanders', 'Madeline Price', 'Hailey Bennett', 'Gabriella Wood', 'Naomi Barnes',
    'Elena Ross', 'Sarah Henderson', 'John Doe', 'Michael Smith', 'James Johnson',
    'Robert Brown', 'David Jones', 'William Garcia', 'Joseph Martinez', 'Charles Anderson',
    'Thomas Taylor', 'Christopher Thomas', 'Daniel Hernandez', 'Matthew Moore', 'Anthony Martin',
    'Mark Jackson', 'Paul Thompson', 'Steven White', 'Andrew Harris', 'Joshua Clark',
    'Kevin Lewis', 'Brian Walker', 'George Hall', 'Edward Allen', 'Ronald Young',
    'Timothy King', 'Jason Wright', 'Jeffrey Scott', 'Ryan Green', 'Jacob Adams'
] * (300 // 100 + 1)

teams = ['ACRT TEAM'] * (300 // 2) + ['ACRT SPECIALIST TEAM'] * (300 // 2)

data = {
    'DerReferralID': referral_ids,
    'ClientID': [ref_id.split('_')[0] for ref_id in referral_ids],
    'HCPCode': hcp_codes[:300],
    'HCPName': hcp_names[:300],
    'Team': teams[:300]
}

# Create a DataFrame

df = pd.DataFrame(data)

# Select relevant columns for visualization
selected_columns = df[['DerReferralID', 'ClientID', 'HCPCode', 'HCPName', 'Team']]

# Create a graph
G = nx.Graph()

# Add nodes and edges based on HCPs and their connections
for index, row in selected_columns.iterrows():
    G.add_node(row['HCPCode'], label=row['HCPName'], team=row['Team'])
    G.add_edge(row['ClientID'], row['HCPCode'])

# Draw Spring Layout
pos_spring = nx.spring_layout(G)
plt.figure(figsize=(10, 8))
nx.draw(G, pos=pos_spring, with_labels=True, labels=labels, node_size=3000, node_color='skyblue', font_size=10, font_weight='bold')
plt.title('Spring Layout')
plt.show()

# Draw Circular Layout
pos_circular = nx.circular_layout(G)
plt.figure(figsize=(10, 8))
nx.draw(G, pos=pos_circular, with_labels=True, labels=labels, node_size=3000, node_color='skyblue', font_size=10, font_weight='bold')
plt.title('Circular Layout')
plt.show()

# Draw Kamada-Kawai Layout
pos_kamada_kawai = nx.kamada_kawai_layout(G)
plt.figure(figsize=(10, 8))
nx.draw(G, pos=pos_kamada_kawai, with_labels=True, labels=labels, node_size=3000, node_color='skyblue', font_size=10, font_weight='bold')
plt.title('Kamada-Kawai Layout')
plt.show()
