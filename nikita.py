import pandas as pd
import numpy as np
from typing import Union

def disaggregate_population_data(input_excel_path: str, output_excel_path: str):
    """
    Transforms aggregated population data (5-year age groups) from an Excel file
    into a disaggregated (single-year age) format, then saves it to a new Excel file.

    The disaggregation is performed by dividing the 5-year group total by 5.

    Args:
        input_excel_path (str): Path to the source Excel file.
        output_excel_path (str): Path to save the resulting Excel file.
    """
    print("🚀 Starting population data disaggregation...")

    # --- 1. Load and Clean the Data ---
    # Load the data: row 12 (0-indexed 11) is the header (Years), column B (0-indexed 1) is the index (Age Labels).
    try:
        df_raw = pd.read_excel(
            input_excel_path,
            sheet_name='Sheet 1',
            header=11,      # Row 12 contains the years (headers)
            index_col=1,    # Column B contains the AGE (Labels)
            usecols='B:DZ'  # Selects from column B (Age Labels) to DZ (beyond 2024)
        )
    except Exception as e:
        # We include the helpful exception message for better debugging if a new error occurs.
        print(f"🛑 Error reading the Excel file. Please ensure the path is correct and the sheet/range structure is as expected: {e}")
        return

    # Filter out non-standard age groups to simplify the 5-year group disaggregation
    rows_to_drop = [
        'Total',
        'Unknown',
        '75 years or over',
        'From 80 to 84 years',
        '80 years or over',
        'Less than 5 years',
        '85 years or over'
    ]
    df_clean = df_raw.drop(rows_to_drop, errors='ignore', axis=0)

    # --- FIX FOR KEYERROR: 1990 ---
    # 1. Convert column headers to numeric, coercing non-year headers (like empty cells) to NaN.
    numeric_cols = pd.to_numeric(df_clean.columns, errors='coerce')

    # 2. Create a boolean mask to filter for columns that are numbers AND within the target range [1990, 2024]
    # This safely handles missing years without raising a KeyError.
    year_mask = (numeric_cols >= 1990) & (numeric_cols <= 2024) & (~numeric_cols.isna())
    
    # 3. Apply the mask to select only the valid columns
    df_filtered = df_clean.loc[:, year_mask].copy()
    
    # 4. Assign the cleaned numeric years as the new column headers
    df_filtered.columns = numeric_cols[year_mask].astype(int)
    # --- END FIX ---

    print(f"✅ Data loaded and columns filtered. {len(df_filtered.columns)} years found in the 1990-2024 range.")

    # --- 2. Melting (Unpivoting) the Data ---
    # Convert the wide table (Years as columns) into a long table
    df_long = df_filtered.melt(
        ignore_index=False, # Keep the age group as the index for now
        var_name='Year',
        value_name='Population_5y_Group'
    ).reset_index()

    df_long.rename(columns={'AGE (Labels)': 'Age_Group_5y'}, inplace=True)

    # Drop rows where population data is NaN (i.e., truly missing data points)
    df_long.dropna(subset=['Population_5y_Group'], inplace=True)

    print(f"✅ Data unpivoted. Total {len(df_long)} aggregated data points to disaggregate.")

    # --- 3. Disaggregating Age Groups ---

    def parse_age_group(group: str) -> Union[tuple[int, int], None]:
        """Extracts start and end age from the age group string."""
        if 'From' in group and 'to' in group:
            try:
                # Example: 'From 5 to 9 years' -> (5, 9)
                parts = group.replace('From', '').replace('to', '').replace('years', '').strip().split()
                start_age = int(parts[0])
                end_age = int(parts[1])
                return start_age, end_age
            except:
                return None
        return None

    def expand_and_divide(row: pd.Series) -> pd.DataFrame:
        """
        Creates new rows for each single age within the 5-year group and estimates
        the population per year age by dividing the 5-year total by 5.
        """
        parsed_ages = parse_age_group(row['Age_Group_5y'])
        if parsed_ages is None:
            return pd.DataFrame()

        start, end = parsed_ages
        
        # Calculate the single-age population: 5-year total divided by 5
        population_per_age = int(row['Population_5y_Group'] / 5)

        # Create a new row for every single age within the group
        new_rows = []
        for age in range(start, end + 1): # +1 to include the end age (e.g., 9 in 5-9)
            if 5 <= age <= 90: # Apply the required age filter (5 to 90)
                new_rows.append({
                    'Year': row['Year'],
                    'Age': age,
                    'Population': population_per_age
                })
        
        return pd.DataFrame(new_rows)

    # Apply the disaggregation function to every aggregated data point
    # Using a list comprehension and pd.concat is very efficient
    df_disaggregated_list = [expand_and_divide(row) for _, row in df_long.iterrows()]
    df_final = pd.concat(df_disaggregated_list, ignore_index=True)

    # --- 4. Final Touches and Saving ---
    # Ensure columns have the correct types for a clean output
    df_final['Year'] = df_final['Year'].astype(int)
    df_final['Age'] = df_final['Age'].astype(int)
    df_final['Population'] = df_final['Population'].astype(int)

    # Order the final columns as requested: Year, Age, Population
    df_final = df_final[['Year', 'Age', 'Population']]
    df_final.sort_values(by=['Year', 'Age'], inplace=True)
    
    print(f"🎉 Disaggregation complete. Final table has {len(df_final)} single-age data points.")
    
    # Export to Excel
    df_final.to_excel(output_excel_path, index=False)
    print(f"📁 Data saved successfully to: {output_excel_path}")



# Run the function
# disaggregate_population_data(INPUT_FILE, OUTPUT_FILE)
# --- EXECUTION EXAMPLE ---
# Define your file paths
INPUT_FILE = r'C:\Users\Nikita.Gaponiuk\Desktop\Statec Hackathon\STATEC-Hackathon\Data\Benefits\Population 1960-2024 by age.xlsx'
OUTPUT_FILE = 'disaggregated_population_data.xlsx'

# Run the function
disaggregate_population_data(INPUT_FILE, OUTPUT_FILE)
print("\nExecution completed. Check your output file.")