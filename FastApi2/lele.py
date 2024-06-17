import pandas as pd

# Load the CSV file into a DataFrame
file_path = 'vectorizedLandmarks.csv'
df = pd.read_csv(file_path)

# Apply the transformation to encapsulate the 'Landmark' value in a list
df['Landmark'] = df['Landmark'].apply(lambda x: [x])

# Save the modified DataFrame back to the CSV file
df.to_csv('vectorizedLandmarks2.csv', index=False)

print("CSV file updated successfully.")

# Reload the CSV file into a DataFrame to verify
df_reloaded = pd.read_csv(file_path)

# Verify that 'Landmark' column values are lists
for index, row in df_reloaded.iterrows():
    print(type(row['Landmark']), row['Landmark'])
