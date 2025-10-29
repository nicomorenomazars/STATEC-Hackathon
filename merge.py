import pandas as pd
import numpy as np

# Define the file path
input_file = r'Data\Manually_cleaned_data\Population 1960-2024 by age.xlsx'

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
panel_df.to_csv('population_panel_data.csv', index=False)

panel_pop_1960_2024 = panel_df





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


panel_pop_2025_2100 = panel_df


# --- 4. Combine the DataFrames ---
# This code handles the overlap in years (e.g., 2022-2024) by
# keeping the data from the first file (historical) and only
# adding new years from the second file (projection).

print("Combining DataFrames...")

# Get the last year from the historical data (panel_pop_1960_2024)
last_historical_year = panel_pop_1960_2024['Year'].max()
print(f"Last year in historical data: {last_historical_year}")

# Filter the projection data to only include years *after* the last historical year
panel_pop_future_only = panel_pop_2025_2100[panel_pop_2025_2100['Year'] > last_historical_year]

# Use pd.concat() to stack the two DataFrames vertically
# panel_pop_1960_2024 (contains 1960 -> 2024)
# panel_pop_future_only (contains 2025 -> 2100)
combined_panel_df = pd.concat([panel_pop_1960_2024, panel_pop_future_only], ignore_index=True)

# Sort the final combined DataFrame by Age and then Year for a clean, continuous timeline
combined_panel_df = combined_panel_df.sort_values(by=['Age', 'Year']).reset_index(drop=True)

# --- 5. Save the Final Combined DataFrame ---
combined_panel_df.to_csv('population_panel_data_combined_1960-2100.csv', index=False)

print("Final combined DataFrame created and saved as 'population_panel_data_combined_1960-2100.csv'")
print("\nCombined DataFrame Head:")
print(combined_panel_df.head())
print("\nCombined DataFrame Tail (showing future data):")
print(combined_panel_df.tail())







# Define the file path
input_file = r'Data\Manually_cleaned_data\Lifetime 1960-2024 by age.xlsx'

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
                   value_name='Life_Expectancy')

# --- 3. Clean Final DataFrame ---
# Same cleaning steps as in Solution 1
panel_df['Life_Expectancy'] = panel_df['Life_Expectancy'].astype(str).str.replace(',', '')
panel_df['Life_Expectancy'] = pd.to_numeric(panel_df['Life_Expectancy'], errors='coerce')
panel_df = panel_df.dropna(subset=['Life_Expectancy'])

# Convert Year column to integer and sort
panel_df['Year'] = panel_df['Year'].astype(int)
panel_df = panel_df.sort_values(by=['Age', 'Year']).reset_index(drop=True)

# Ensure 'Age' is numeric (coerce non-numeric to NaN) so comparison works
panel_df['Age'] = pd.to_numeric(panel_df['Age'], errors='coerce')

# panel_df.loc[panel_df['Age'] > 90, 'Life_Expectancy'] = 5



print("Transformation complete.")
print(panel_df.head())
panel_df.to_csv('life_expectancy_panel_data.csv', index=False)


panel_lifeexp = panel_df








# --- 5. Prepare Life Expectancy Data for Merging ---
# This section "stretches" the panel_lifeexp data to match the
# full Age and Year range of combined_panel_df, using your rules.

print("--- Starting Life Expectancy Data Preparation ---")

# First, get the boundaries from the life expectancy data
max_le_age = panel_lifeexp['Age'].max()
min_le_year = panel_lifeexp['Year'].min()
max_le_year = panel_lifeexp['Year'].max()

# Then, get the target boundaries from the main combined data
target_max_age = combined_panel_df['Age'].max()
target_min_year = combined_panel_df['Year'].min()
target_max_year = combined_panel_df['Year'].max()

print(f"Life Expectancy data bounds: Age <= {max_le_age}, Years {min_le_year}-{max_le_year}")
print(f"Target data bounds: Age <= {target_max_age}, Years {target_min_year}-{target_max_year}")

# --- Rule 3: Extrapolate Ages > 83 ---
# "For all ages above 83 the life expectancy must be the same as for person of age 83."

# Get the complete life expectancy data for the oldest available age
lifeexp_at_max_age = panel_lifeexp[panel_lifeexp['Age'] == max_le_age]

# This list will hold our original data + the new extrapolated age data
age_dfs_to_append = [panel_lifeexp]

if target_max_age > max_le_age:
    print(f"Extrapolating data for ages {max_le_age + 1} to {target_max_age}...")
    # Loop from the next age up to the target max age
    for age in range(max_le_age + 1, target_max_age + 1):
        # Copy the data from the max age (e.g., 83)
        new_age_df = lifeexp_at_max_age.copy()
        # Re-assign the 'Age' column to the new, older age
        new_age_df['Age'] = age
        age_dfs_to_append.append(new_age_df)

# Rebuild the DataFrame with the new ages included
panel_lifeexp_filled_age = pd.concat(age_dfs_to_append, ignore_index=True)


# --- Rules 1 & 2: Extrapolate Years < 1971 and > 2023 ---
# "For all years before 1971... use the value of 1971"
# "For all years after 2023... use the same as in 2023"

# Get the data for the earliest and latest available years
# (from the new, age-filled DataFrame)
lifeexp_at_min_year = panel_lifeexp_filled_age[panel_lifeexp_filled_age['Year'] == min_le_year]
lifeexp_at_max_year = panel_lifeexp_filled_age[panel_lifeexp_filled_age['Year'] == max_le_year]

# This list will hold our age-filled data + the new extrapolated year data
year_dfs_to_append = [panel_lifeexp_filled_age]

# Rule 1: Fill past years (e.g., 1960 to 1970)
if target_min_year < min_le_year:
    print(f"Extrapolating data for past years {target_min_year} to {min_le_year - 1}...")
    for year in range(target_min_year, min_le_year):
        # Copy the data from the earliest year (e.g., 1971)
        new_year_df = lifeexp_at_min_year.copy()
        # Re-assign the 'Year' to the new, past year
        new_year_df['Year'] = year
        year_dfs_to_append.append(new_year_df)

# Rule 2: Fill future years (e.g., 2024 to 2100)
if target_max_year > max_le_year:
    print(f"Extrapolating data for future years {max_le_year + 1} to {target_max_year}...")
    for year in range(max_le_year + 1, target_max_year + 1):
        # Copy the data from the latest year (e.g., 2023)
        new_year_df = lifeexp_at_max_year.copy()
        # Re-assign the 'Year' to the new, future year
        new_year_df['Year'] = year
        year_dfs_to_append.append(new_year_df)

# Rebuild the final, fully-filled DataFrame
# This DataFrame now has a 'Life_Expectancy' value for every 'Age'/'Year' combination
panel_lifeexp_ready_to_merge = pd.concat(year_dfs_to_append, ignore_index=True)


# --- 6. Perform the Final Merge ---
print("Merging population data with prepared life expectancy data...")

# We use a 'left' merge to ensure we keep all rows from the main
# 'combined_panel_df' and add the 'Life_Expectancy' column.
# Because we manually filled the data, there will be no new NaNs.
final_combined_df = pd.merge(
    combined_panel_df,
    panel_lifeexp_ready_to_merge,
    on=['Age', 'Year'],
    how='left'
)

# Sort for a clean final table
final_combined_df = final_combined_df.sort_values(by=['Age', 'Year']).reset_index(drop=True)

# Save the final result
final_combined_df.to_csv('population_and_life_exp_panel_data_1960-2100.csv', index=False)

print("\n--- Merge Complete ---")
print("Final combined DataFrame with Population and Life Expectancy:")
print(final_combined_df.head())
print("...")
print(final_combined_df.tail())
print("Saved to 'population_and_life_exp_panel_data_1960-2100.csv'")



try:
    # Get the 2023 Life Expectancy for each unique Age group
    le_2023_by_age = final_combined_df[final_combined_df['Year'] == 2023].set_index('Age')['Life_Expectancy']
except KeyError:
    # This handles cases where 2023 data might not be present for all ages,
    # or if the data structure is unexpected, focusing on robustness.
    print("Warning: Could not find 'Life_Expectancy' for all 'Age' groups in 2023. Check your data.")
    # Fallback: fill only for those where 2023 data exists
    le_2023_by_age = final_combined_df[final_combined_df['Year'] == 2023].set_index('Age')['Life_Expectancy']


# Step 2: Fill the missing 'Life_Expectancy' values (NaN) only for years > 2023.

# a. Filter to the rows that are missing 'Life_Expectancy' AND are after 2023.
missing_le_mask = final_combined_df['Life_Expectancy'].isna()
future_years_mask = final_combined_df['Year'] > 2023
impute_mask = missing_le_mask & future_years_mask

# b. For these specific rows, use the 'Age' column to look up the corresponding 2023 value
# from our pre-calculated 'le_2023_by_age' Series.
final_combined_df.loc[impute_mask, 'Life_Expectancy'] = final_combined_df.loc[impute_mask, 'Age'].map(le_2023_by_age)

# Save the final result
final_combined_df.to_csv('population_and_life_exp_panel_data_1960-2100_interpolated.csv', index=False)










# --- 7. Load and Prepare Retirement Age Data ---
print("\n--- Starting Retirement Age Data Preparation ---")

# Define file path and the *only* columns to load
retire_file = r'Data\Manually_cleaned_data\ageretraite.xlsx'
target_cols = ['Année', 'Pensions de vieillesse et de vieillesse annticipée']

try:
    # Use 'usecols' to load only the two required columns
    df_retire = pd.read_excel(retire_file, usecols=target_cols)
except FileNotFoundError:
    print(f"Error: The file '{retire_file}' was not found.")
    # Exit or handle error appropriately
    exit()
except ValueError as e:
    # This error happens if the specified columns aren't in the file
    print(f"Error: Could not find required columns in '{retire_file}'. Check names.")
    print(f"Details: {e}")
    exit()

# Rename columns for clarity and consistency
df_retire = df_retire.rename(columns={
    'Année': 'Year',
    'Pensions de vieillesse et de vieillesse annticipée': 'Retirement_age'
})

# --- 8. Extrapolate Retirement Age Data (1960-2100) ---

# Get boundaries from the loaded retirement data
min_retire_year = df_retire['Year'].min() # Should be 1991
max_retire_year = df_retire['Year'].max() # Should be 2023

# Get target boundaries from the main combined DataFrame
target_min_year = final_combined_df['Year'].min() # Should be 1960
target_max_year = final_combined_df['Year'].max() # Should be 2100

print(f"Retirement data bounds: Years {min_retire_year}-{max_retire_year}")
print(f"Target data bounds: Years {target_min_year}-{target_max_year}")

# Get the specific values for extrapolation as per the rules
# Value for years before 1991 (use 1991's value)
val_pre_1991 = df_retire[df_retire['Year'] == min_retire_year]['Retirement_age'].iloc[0]
# Value for years after 2023 (use 2023's value)
val_post_2023 = df_retire[df_retire['Year'] == max_retire_year]['Retirement_age'].iloc[0]

# This list will hold our original data + new extrapolated data
dfs_to_append = [df_retire]

# Rule 1: Fill past years (e.g., 1960 to 1990)
if target_min_year < min_retire_year:
    print(f"Extrapolating retirement age for past years {target_min_year} to {min_retire_year - 1}...")
    # Create a DataFrame for all past years at once
    past_years = range(target_min_year, min_retire_year)
    df_past = pd.DataFrame({
        'Year': past_years,
        'Retirement_age': val_pre_1991
    })
    dfs_to_append.append(df_past)

# Rule 2: Fill future years (e.g., 2024 to 2100)
if target_max_year > max_retire_year:
    print(f"Extrapolating retirement age for future years {max_retire_year + 1} to {target_max_year}...")
    # Create a DataFrame for all future years at once
    future_years = range(max_retire_year + 1, target_max_year + 1)
    df_future = pd.DataFrame({
        'Year': future_years,
        'Retirement_age': val_post_2023
    })
    dfs_to_append.append(df_future)

# Rebuild the final, fully-filled DataFrame
# This DataFrame now has a 'Retirement_age' value for every 'Year' from 1960-2100
panel_retire_ready_to_merge = pd.concat(dfs_to_append, ignore_index=True)
panel_retire_ready_to_merge = panel_retire_ready_to_merge.sort_values(by='Year')


# --- 9. Perform Final Merge with Retirement Age ---
print("Merging main data with prepared retirement age data...")

# We use a 'left' merge to add the 'Retirement_age' column.
# It will match each 'Year' in the main df to the single value
# in the panel_retire_ready_to_merge df.
final_combined_df = pd.merge(
    final_combined_df,
    panel_retire_ready_to_merge,
    on=['Year'],
    how='left'
)

# Sort for a clean final table
final_combined_df = final_combined_df.sort_values(by=['Age', 'Year']).reset_index(drop=True)

# Save the new final result
output_filename = 'population_life_exp_retire_panel_data_1960-2100.csv'
final_combined_df.to_csv(output_filename, index=False)

print("\n--- Merge Complete ---")
print(f"Final combined DataFrame with Population, Life Expectancy, and Retirement Age:")
print(final_combined_df.head())
print("...")
print(final_combined_df.tail())
print(f"Saved to '{output_filename}'")








# Assume final_combined_df is already loaded

# Add the new column and set the constant rate
final_combined_df['Contribution_rate'] = 0.24
final_combined_df.loc[final_combined_df['Year'] < 1990, 'Contribution_rate'] = 0.24



# Assume final_combined_df is already loaded and has a 'Year' column

final_combined_df['1999_dummy'] = (final_combined_df['Year'] > 1999).astype(int)

final_combined_df['Reference_amount_1984'] = 2085

final_combined_df['Birth_Year'] = final_combined_df['Year'] - final_combined_df['Age']

# Save the new final result
output_filename = 'population_life_exp_retire_crate_panel_data_1960-2100.csv'
final_combined_df.to_csv(output_filename, index=False)







# --- 7. Load, Prepare, and Merge Revalorisation Rate ---
print("\n--- Starting Revalorisation Rate Merge ---")
input_file_reval = r'Data\Manually_cleaned_data\adapt_salaire.xlsx'

# --- 7.1 Load and Clean Data ---
try:
    # Load the file *without* assuming a header (header=None).
    # This reads the *actual* headers ('Adaptation des...') as the first row of data.
    df_reval = pd.read_excel(input_file_reval, header=None)
except FileNotFoundError:
    print(f"Error: The file '{input_file_reval}' was not found.")
    # Exit or handle error appropriately
    exit()

# Now, set the column names using the data from the first row (iloc[0])
df_reval.columns = df_reval.iloc[0]

# Remove the first row, as it's now just a redundant header
df_reval = df_reval.iloc[1:].reset_index(drop=True)

print(f"Successfully loaded and set headers: {df_reval.columns.to_list()}")

# Now, the rename will work because the columns are correct
df_reval = df_reval.rename(columns={
    'Adaptation des salaires de ': 'Year',
    'Facteur de revalorisation': 'Revaleurisation_rate'
})

# Clean data types
df_reval['Year'] = pd.to_numeric(df_reval['Year'], errors='coerce')
df_reval['Revaleurisation_rate'] = pd.to_numeric(df_reval['Revaleurisation_rate'], errors='coerce')
df_reval = df_reval.dropna(subset=['Year', 'Revaleurisation_rate'])
df_reval['Year'] = df_reval['Year'].astype(int)


# --- 7.2 Extrapolate Future Values (Rule: ffill) ---
# We must fill the 'Revaleurisation_rate' for years after its data ends (e.g., 2023).
# Rule: "for years after 2023 keep Revaleurisation_rate at 1.595"
# This is a "forward fill" (ffill).

# Find the boundaries
target_max_year = final_combined_df['Year'].max() # e.g., 2100
max_reval_year = df_reval['Year'].max()           # e.g., 2023

# Get the last available rate from the data
last_rate_value = df_reval.loc[df_reval['Year'] == max_reval_year, 'Revaleurisation_rate'].values[0]

# This list will hold our original data + the new extrapolated data
dfs_to_append = [df_reval]

if target_max_year > max_reval_year:
    print(f"Extrapolating revalorisation rate for years {max_reval_year + 1} to {target_max_year}...")
    print(f"Using rate from {max_reval_year}: {last_rate_value}")
    
    # Create a list of all the years we need to add
    future_years = list(range(max_reval_year + 1, target_max_year + 1))
    
    # Create a DataFrame for these new future years
    df_future_reval = pd.DataFrame({
        'Year': future_years,
        'Revaleurisation_rate': [last_rate_value] * len(future_years)
    })
    
    dfs_to_append.append(df_future_reval)

# Combine the original revaluation data with the new future data
reval_ready_to_merge = pd.concat(dfs_to_append, ignore_index=True)


# --- 7.3 Perform the Final Merge ---
# Merge the complete revaluation data into the main DataFrame
print("Merging revalorisation rate into final DataFrame...")
final_combined_df = pd.merge(
    final_combined_df,
    reval_ready_to_merge,
    on='Year',
    how='left'
)

# --- 7.4 Extrapolate Past Values (Rule: bfill) ---
# Fill any early years (e.g., 1960-1969) with the *first* available
# rate (e.g., from 1970). This is a "backward fill".
final_combined_df['Revaleurisation_rate'] = final_combined_df['Revaleurisation_rate'].bfill()

# Sort and save the final, complete DataFrame
final_combined_df = final_combined_df.sort_values(by=['Age', 'Year']).reset_index(drop=True)
final_combined_df.to_csv('population_and_life_exp_reval_panel_data_1960-2100.csv', index=False)

print("\n--- Merge Complete ---")
print("Final DataFrame with Population, Life Expectancy, and Revaleurisation Rate:")
print(final_combined_df.head())
print("...")
print(final_combined_df.tail())
print("Saved to 'population_and_life_exp_reval_panel_data_1960-2100.csv'")








# --- 8. Load, Prepare, and Merge Adjustment Factor ---
print("\n--- Starting Adjustment Factor 1984 Merge ---")
input_file_index = r'Data\Manually_cleaned_data\index.xls'

# --- 8.1 Load and Clean Data ---
try:
    # Attempt to read the .xls file
    df_index = pd.read_excel(input_file_index)
except FileNotFoundError:
    print(f"Error: The file '{input_file_index}' was not found.")
    exit()
except Exception as e:
    print(f"Error reading Excel file: {e}")
    print("This might be a file format issue (e.g., .xls vs .xlsx) or a protected file.")
    exit()

# Rename columns
df_index = df_index.rename(columns={
    'Année et mois': 'Year',
    'raccordés à la base 1948': 'Adjustment_factor_1984'
})

# Clean data
df_index['Year'] = pd.to_numeric(df_index['Year'], errors='coerce')
df_index['Adjustment_factor_1984'] = pd.to_numeric(df_index['Adjustment_factor_1984'], errors='coerce')
df_index = df_index.dropna(subset=['Year', 'Adjustment_factor_1984'])
df_index['Year'] = df_index['Year'].astype(int)
print(f"Loaded index data from {df_index['Year'].min()} to {df_index['Year'].max()}.")


# --- 8.2 Perform the Merge ---
# Merge the index data. This will create NaNs where the years don't match.
print("Merging adjustment factor into final DataFrame...")
final_combined_df = pd.merge(
    final_combined_df,
    df_index,
    on='Year',
    how='left'
)

# --- 8.3 Fill Missing Values Based on Rules ---
# We apply the rules in a specific order to get the desired outcome

# 1. Forward-fill: This fills all NaNs *after* 1983 with the 1983 value.
#    (e.g., 1984-2100 will be filled with the 1983 value).
#    NaNs before 1970 remain NaN.
print("Applying gap-fill rule (ffill)...")
final_combined_df['Adjustment_factor_1984'] = final_combined_df['Adjustment_factor_1984'].ffill()

# 2. Backward-fill: This fills the remaining NaNs *before* 1970 with the 1970 value.
#    (e.g., 1960-1969 will be filled with 166.4).
#    This also satisfies the "before 1970" rule.
print("Applying past-fill rule (bfill)...")
final_combined_df['Adjustment_factor_1984'] = final_combined_df['Adjustment_factor_1984'].bfill()

# 3. Explicit Rule: "For all years after 2024 replace missing values with 981.89"
#    Now, we *over-write* the forward-filled values for years > 2024.
print("Applying future rule (for years > 2024)...")
final_combined_df.loc[final_combined_df['Year'] > 2024, 'Adjustment_factor_1984'] = 981.89

final_combined_df.loc[final_combined_df['Year'] < 1970, 'Adjustment_factor_1984'] = 150

# final_combined_df['Adjustment_factor_1984'] = final_combined_df['Adjustment_factor_1984'] / 432.37

# --- 8.4 Final Save ---
# Sort and save
final_combined_df = final_combined_df.sort_values(by=['Age', 'Year']).reset_index(drop=True)
final_combined_df.to_csv('population_and_life_exp_reval_index_panel_data_1960-2100.csv', index=False)

print("\n--- Merge Complete ---")
print("Final DataFrame with Population, Life Expectancy, Reval Rate, and Index:")
print(final_combined_df.head())
print("...")
# Print a sample from the gap (e.g., 2024) and the future (e.g., 2025)
print(final_combined_df[final_combined_df['Year'].isin([1969, 1970, 1983, 2024, 2025]) & (final_combined_df['Age'] == 1)].to_string())
print("...")
print(final_combined_df.tail())
print("Saved to 'population_and_life_exp_reval_index_panel_data_1960-2100.csv'")












num_rows = len(final_combined_df)
# Generate a random integer between 30,000 (inclusive) and 120,001 (exclusive)
# for each row in the DataFrame.
random_salaries = np.random.randint(30000, 120001, size=num_rows)
# Assign the array of random salaries to the new 'Salary' column
final_combined_df['Salary'] = random_salaries

final_combined_df.to_csv('final_1960-2100.csv', index=False)



############ Name of the file to be read ############
Wages_File = r'Data\Benefits\Annual wages.xlsx'
Income_File = r'Data\Benefits\Income per year - cleaned_version.xls'

wages_File=r'Data\Manually_cleaned_data\Annual wages.xlsx'
Wages_data_annually = pd.read_excel(wages_File, header=0)
incomefile=r'Data\Manually_cleaned_data\Income per year - cleaned_version.xls'
income_data = pd.read_excel(incomefile, sheet_name=None) 
 

from Wages_Calculation import *

df_new123 = Reval_avg_An_wages(Wages_data_annually)

wage_panel_df = Wages_Calculation(df_new123, income_data)

print("Final DataFrame with Population, Life Expectancy, Reval Rate, and Index:")
print(wage_panel_df.head())
print("...")
# Print a sample from the gap (e.g., 2024) and the future (e.g., 2025)
print(wage_panel_df[wage_panel_df['Year'].isin([1969, 1970, 1983, 2024, 2025]) & (wage_panel_df['Age'] == 1)].to_string())
print("...")
print(wage_panel_df.tail())


# --- 11. Load, Prepare, and Merge Wage Data ---
print("\n--- Starting Wage Data Merge ---")

# --- 11.1 (Rule 1) Filter main DataFrame ---
# Drop ages 14 or younger from the main DataFrame *before* merging
print(f"Original main df shape: {final_combined_df.shape}")
final_combined_df = final_combined_df[final_combined_df['Age'] > 14].reset_index(drop=True)
print(f"New main df shape (ages 15+): {final_combined_df.shape}")

# --- 11.2 Prepare Wage Panel (Extrapolate Ages) ---
# (Rule 2: "For people with age above maximum... keep the salary at the max age")

# Find the boundaries of the wage data
max_wage_age = wage_panel_df['Age'].max()
min_wage_age = wage_panel_df['Age'].min()
max_wage_year = wage_panel_df['Year'].max()
min_wage_year = wage_panel_df['Year'].min()

# Find the target boundaries from the main DataFrame
target_max_age = final_combined_df['Age'].max()

# Get the income data for the oldest available age (e.g., age 65)
wage_at_max_age = wage_panel_df[wage_panel_df['Age'] == max_wage_age]

# This list will hold the original data + new extrapolated age data
age_dfs_to_append = [wage_panel_df]

if target_max_age > max_wage_age:
    print(f"Extrapolating wages for ages {max_wage_age + 1} to {target_max_age}...")
    # Loop from the next age up to the target max age
    for age in range(max_wage_age + 1, target_max_age + 1):
        # Copy the data from the max age
        new_age_df = wage_at_max_age.copy()
        # Re-assign the 'Age' column to the new, older age
        new_age_df['Age'] = age
        age_dfs_to_append.append(new_age_df)

# Rebuild the wage DataFrame with the new ages included
# This df now has ages from 15 up to target_max_age (e.g., 90)
# but still only for the original years (e.g., 1990-2024)
wage_df_filled_age = pd.concat(age_dfs_to_append, ignore_index=True)

# --- 11.3 Prepare Wage Panel (Extrapolate Years) ---
# (Rule 3: "To interpolate salaries to years after 2024, use 2% annual growth rate")

# Find the target boundaries from the main DataFrame
target_max_year = final_combined_df['Year'].max()
target_min_year = final_combined_df['Year'].min()

# This list will hold all data (past, present, and future)
all_year_dfs_to_append = []

# --- Part A: Extrapolate Future Years (2025-2100) with 2% Growth ---
print(f"Extrapolating future wages (2025-{target_max_year}) with 2% annual growth...")

# Get the data for the base year (2024), now including all ages 15-90
# This will be the starting point for our growth calculation
base_year_data = wage_df_filled_age[wage_df_filled_age['Year'] == max_wage_year].copy()

# Add the known data (1990-2024) to our list
all_year_dfs_to_append.append(wage_df_filled_age)

current_year_data = base_year_data
for year in range(max_wage_year + 1, target_max_year + 1):
    # Create a new DataFrame for this future year
    future_year_data = current_year_data.copy()
    
    # Set the new year
    future_year_data['Year'] = year
    
    # Apply the 2% growth rate
    future_year_data['Income_per_year'] *= 1
    
    # Add this new year's data to our list
    all_year_dfs_to_append.append(future_year_data)
    
    # Set this as the base for the *next* year's calculation
    current_year_data = future_year_data

# --- Part B: Extrapolate Past Years (1960-1989) ---
# (Implied Rule: Use the earliest available data for all prior years)
print(f"Extrapolating past wages ({target_min_year}-1989) using 1990 data...")

# Get data for the earliest available year (1990), for all ages 15-90
wage_at_min_year = wage_df_filled_age[wage_df_filled_age['Year'] == min_wage_year]

for year in range(target_min_year, min_wage_year):
    # Copy the 1990 data
    new_year_df = wage_at_min_year.copy()
    # Set the year to the past year
    new_year_df['Year'] = year
    # Add to our list
    all_year_dfs_to_append.append(new_year_df)

# --- 11.4 Create the Final Wage Panel ---
# Combine all the DataFrames (past, present, future) into one
wage_panel_ready_to_merge = pd.concat(all_year_dfs_to_append, ignore_index=True)

# --- 11.5 Perform the Final Merge ---
print("Merging prepared wage data into final DataFrame...")
# We use a 'left' merge to keep all rows from our filtered main DataFrame
# and add the matching income data.
final_combined_df = pd.merge(
    final_combined_df,
    wage_panel_ready_to_merge,
    on=['Year', 'Age'],
    how='left'
)

# Calculate salary by dividing Income_per_year by Revaleurisation_rate
final_combined_df['Salary'] = final_combined_df['Income_per_year'] / final_combined_df['Revaleurisation_rate']

# --- 11.6 Final Save ---
final_combined_df = final_combined_df.sort_values(by=['Age', 'Year']).reset_index(drop=True)


final_combined_df.loc[final_combined_df['Age'] > 90, 'Life_Expectancy'] = 5

final_combined_df.to_csv('final_dataset_with_wages_1960-2100.csv', index=False)

print("\n--- Merge Complete ---")
print("Final DataFrame with Population, Life Exp, Reval, Index, and Wages:")
print(final_combined_df.head())
print("...")
print(final_combined_df.tail())
print("Saved to 'final_dataset_with_wages_1960-2100.csv'")




stats = final_combined_df.describe()

# You would then print the 'stats' variable to see the output
print(stats)

# Get descriptive stats and save to a file
stats_df = final_combined_df.describe()
stats_df.to_csv('descriptive_stats.csv')