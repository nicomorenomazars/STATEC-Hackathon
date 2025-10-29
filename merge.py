import pandas as pd
import os

def refactor_population_data(input_file, output_file):
    """
    Refactors a wide-format population Excel file (Ages as rows, Years as columns)
    into a long-format panel data file (Age, Year, Population).

    Args:
        input_file (str): The path to the input .xlsx file.
        output_file (str): The path to save the refactored .xlsx file.
    """
    
    print(f"Starting refactoring of '{input_file}'...")

    try:
        # ----------------------------------------------------------------------
        # 1. Read the Excel File
        # ----------------------------------------------------------------------
        # We assume the first column contains the ages and the first row
        # contains the years (starting from the second column).
        df = pd.read_excel(input_file)

        # ----------------------------------------------------------------------
        # 2. Rename the first column to 'Age' for clarity
        # ----------------------------------------------------------------------
        # Get the name of the first column (e.g., 'TIME' in your sample)
        age_column_name = df.columns[0]
        if age_column_name != 'Age':
            print(f"Renaming first column '{age_column_name}' to 'Age'.")
            df = df.rename(columns={age_column_name: 'Age'})

        # ----------------------------------------------------------------------
        # 3. "Melt" the DataFramee
        # ----------------------------------------------------------------------
        # This is the core step. 'id_vars' are the columns to keep (our 'Age').
        # All other columns (the years) will be "unpivoted".
        # 'var_name' is the name for the new column holding the old column headers (Years).
        # 'value_name' is the name for the new column holding the cell values (Population).
        print("Melting DataFrame from wide to long format...")
        df_long = pd.melt(df, 
                          id_vars=['Age'], 
                          var_name='Year', 
                          value_name='Population')

        # ----------------------------------------------------------------------
        # 4. Clean the Data
        # ----------------------------------------------------------------------
        print("Cleaning data...")

        # A) Remove commas from 'Population' and convert to string first
        # This handles cases where some numbers are read as text (e.g., '4,867')
        df_long['Population'] = df_long['Population'].astype(str).str.replace(',', '', regex=False)

        # B) Convert 'Population' to numeric.
        # Errors (like '#VALUE!') will be converted to 'NaN' (Not a Number).
        df_long['Population'] = pd.to_numeric(df_long['Population'], errors='coerce')

        # C) Drop rows where 'Population' is now NaN (i.e., the original '#VALUE!' cells)
        original_rows = len(df_long)
        df_long = df_long.dropna(subset=['Population'])
        dropped_rows = original_rows - len(df_long)
        if dropped_rows > 0:
            print(f"Dropped {dropped_rows} rows with invalid population data (e.g., #VALUE!).")

        # ----------------------------------------------------------------------
        # 5. Convert Columns to Proper Data Types
        # ----------------------------------------------------------------------
        # This ensures Age, Year, and Population are stored as integers.
        try:
            df_long['Age'] = df_long['Age'].astype(int)
            df_long['Year'] = df_long['Year'].astype(int)
            df_long['Population'] = df_long['Population'].astype(int)
        except ValueError as e:
            print(f"Warning: Could not convert all columns to integer. Check 'Year' headers. Error: {e}")

        # ----------------------------------------------------------------------
        # 6. Save the Result
        # ----------------------------------------------------------------------
        # 'index=False' prevents pandas from writing the DataFrame index as a column.
        df_long.to_excel(output_file, index=False)
        print(f"\nSuccess! Refactored data saved to '{output_file}'.")
        print(df_long.head())

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- How to use this script ---
if __name__ == "__main__":
    # 1. Set your input and output file names
    # Make sure 'input_population_data.xlsx' is in the same directory as this script,
    # or provide the full path to it.
    input_filename = r'C:\Users\Nikita.Gaponiuk\Desktop\Statec Hackathon\STATEC-Hackathon\Data\Benefits\Population 1960-2024 by age.xlsx' 
    output_filename = 'output_panel_data.xlsx'

    # 2. Check if a dummy input file exists, create one if not
    if not os.path.exists(input_filename):
        print(f"Creating dummy input file: '{input_filename}'")
        # Create a sample DataFrame based on your image
        dummy_data = {
            'TIME': [1, 2, 3, 4, 5, 6, 7, 8],
            '1960': ['4,867', '4,867', '4,867', '4,867', '4,867', '4,473', '4,473', '4,473'],
            '1961': ['4,896', '4,896', '4,896', '4,896', '4,896', '4,499', '4,499', '4,499'],
            '1962': ['#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!'],
            '1963': ['#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!'],
            '1964': ['#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!'],
            '1965': ['5,098', '5,098', '5,098', '5,098', '5,098', '5,045', '5,045', '5,045'],
            '1966': ['#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!', '#VALUE!'],
            '1967': ['5,172', '5,172', '5,172', '5,172', '5,172', '5,118', '5,118', '5,118']
        }
        dummy_df = pd.DataFrame(dummy_data)
        dummy_df.to_excel(input_filename, index=False)
    
    # 3. Run the refactoring function
    refactor_population_data(input_filename, output_filename)
