import pandas as pd

# Define the file path
input_file = r'Data\Manually_cleaned_data\Projection total population 2022-2100 by age.xlsx'

# --- 1. Load and Prepare the Data ---
try:
    df = pd.read_excel(input_file)
except FileNotFoundError:
    print(f"Error: The file '{input_file}' was not found.")
    # Exit or handle error appropriately
    exit()

# Rename the 'TIME' column to 'Age'
df = df.rename(columns={'TIME': 'Age'})

# --- 2. Transform the Data ---
# Use pd.melt() to 'unpivot' the table
# - id_vars: The column(s) to keep as identifiers (don't unpivot).
# - var_name: The name for the new column holding the old column headers (the years).
# - value_name: The name for the new column holding the values.
print("Starting data transformation with melt()...")
panel_df = df.melt(id_vars=['Age'], 
                   var_name='Year', 
                   value_name='Population')

# --- 3. Clean Final DataFrame ---
# Same cleaning steps as in Solution 1
panel_df['Population'] = panel_df['Population'].astype(str).str.replace(',', '')
panel_df['Population'] = pd.to_numeric(panel_df['Population'], errors='coerce')
panel_df = panel_df.dropna(subset=['Population'])

# Convert Year column to integer and sort
panel_df['Year'] = panel_df['Year'].astype(int)
panel_df = panel_df.sort_values(by=['Age', 'Year']).reset_index(drop=True)

print("Transformation complete.")
print(panel_df.head())
panel_df.to_csv('population_panel_data_projected.csv', index=False)