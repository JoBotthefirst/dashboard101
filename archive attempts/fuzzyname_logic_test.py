import pandas as pd
from fuzzywuzzy import fuzz, process

# Load the data
hcp_df = pd.read_csv('hcp_names.csv')  # First CSV file with HCPName column
professions_df = pd.read_csv('professions.csv')  # Second CSV file with Name and Profession columns

# Function to match names using fuzzy logic
def match_names(name, choices, scorer=fuzz.token_sort_ratio, cutoff=80):
    match, score = process.extractOne(name, choices, scorer=scorer)
    if score >= cutoff:
        return match, score
    return None, 0

# List to store matched names, professions, and confidence scores
matched_names = []

# Perform fuzzy matching
for hcp_name in hcp_df['HCPName']:
    # Extract first and last name from HCPName
    name_parts = hcp_name.split()
    if len(name_parts) >= 2:
        first_name = name_parts[0]
        last_name = name_parts[-1]
        full_name = f"{first_name} {last_name}"
        
        # Match the full name to the names in the professions DataFrame
        matched_name, score = match_names(full_name, professions_df['Name'])
        if matched_name:
            profession = professions_df.loc[professions_df['Name'] == matched_name, 'Profession'].values[0]
            matched_names.append((hcp_name, matched_name, profession, score))
        else:
            matched_names.append((hcp_name, None, "Unknown", 0))

# Create a DataFrame with matched names, professions, and confidence scores
matched_df = pd.DataFrame(matched_names, columns=['OriginalName', 'MatchedName', 'Profession', 'ConfidenceScore'])

# Save the DataFrame to a CSV file
matched_df.to_csv('matched_names_with_professions.csv', index=False)

# Print the DataFrame
print(matched_df)