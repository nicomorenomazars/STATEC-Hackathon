import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# -----------------------------------------------------------------------------
# 1. USER INPUTS
# -----------------------------------------------------------------------------
# Please set these variables before running the script.

# This is the path to your panel data CSV file.
# Make sure the file contains all required columns.
FILE_PATH = "final_dataset_with_wages_1960-2100.csv"  # <<< SET THIS

# Percentage of the representative agent considered a public servant
# This applies ONLY to cohorts where 1999_dummy = 1.
# E.g., 0.25 for 25%.
PCT_PUBLIC = 0.25

# The assumed age when a person in a cohort starts working.
# E.g., 20.
WORK_START_AGE = 20

# The statutory rate applied to the fixed (duration-based) part of the
# private pension. As you noted, this is ~24.85%.
FIXED_INCREASE_RATE = 0.2485 # <<< ADDED THIS

# This table maps a retirement year to the "Proportional Rate" used
# in the private pension calculation. This is the "Taux de majoration proportionnelle".
# The script will find the closest year if an exact match is not found.
# Format: {RetirementYear: Rate, ...}
PROP_RATE_TABLE = {
    2020: 1.78,
    2021: 1.77,
    2022: 1.76,
    2023: 1.75,
    # ... add more values ...
    2052: 1.60
}
# -----------------------------------------------------------------------------

def get_prop_rate(rate_map, retirement_year):
    """
    Helper function to get the proportional rate from the user-defined table.
    If an exact year match is not found, it finds the closest year available.
    """
    if retirement_year in rate_map:
        return rate_map[retirement_year]
    
    # Fallback: find the closest year in the map
    if not rate_map:
        print(f"    - WARNING: PROP_RATE_TABLE is empty. Defaulting rate to 0.")
        return 0
        
    closest_year = min(rate_map.keys(), key=lambda year: abs(year - retirement_year))
    rate = rate_map[closest_year]
    
    print(f"    - INFO: No prop_rate for {retirement_year}. Using closest year {closest_year} with rate {rate}.")
    return rate

def plot_results(results_df):
    """
    Generates a horizontal stacked bar chart of the results, similar to the user's image.
    The plot is saved as 'pension_lifetime_chart.png'.
    """
    if results_df.empty:
        print("No data to plot.")
        return

    # Sort by cohort for a clean plot
    results_df = results_df.sort_values(by='Cohort')

    # Create the figure and axes
    fig, ax = plt.subplots(figsize=(12, len(results_df) * 0.6 + 2))

    # --- Plotting the bars ---
    # We plot 'Total_Contributions' and 'Net_Benefit' stacked.
    # The total length of the bar will be Total_Benefits.
    
    # 1. Plot Total Contributions
    ax.barh(
        results_df['Cohort'].astype(str),
        results_df['Total_Contributions'],
        label='Total Lifetime Contributions',
        color=(255/255, 99/255, 132/255, 0.7), # Reddish
        edgecolor=(255/255, 99/255, 132/255, 1),
        linewidth=1
    )
    
    # 2. Plot Net Wealth Transfer (stacked on top of contributions)
    ax.barh(
        results_df['Cohort'].astype(str),
        results_df['Net_Benefit'],
        left=results_df['Total_Contributions'],
        label='Net Wealth Transfer',
        color=(75/255, 192/255, 192/255, 0.7), # Greenish
        edgecolor=(75/255, 192/255, 192/255, 1),
        linewidth=1
    )

    # --- Formatting the plot ---
    ax.set_xlabel('Lifetime Amount (in 1984 €)', fontsize=12)
    ax.set_ylabel('Cohort (Year of Birth)', fontsize=12)
    ax.set_title('Lifetime Pension Contributions vs. Benefits by Cohort', fontsize=16, pad=20)
    
    # Add a legend
    ax.legend(loc='lower right')
    
    # Add gridlines
    ax.xaxis.grid(True, linestyle='--', alpha=0.6)
    ax.set_axisbelow(True)
    
    # Invert y-axis to have older cohorts at the top (like the image)
    ax.invert_yaxis()
    
    # Add a vertical line at x=0
    ax.axvline(x=0, color='black', linewidth=0.8, linestyle='--')

    plt.tight_layout()
    
    # Save the plot
    save_path = 'pension_lifetime_chart.png'
    plt.savefig(save_path)
    print(f"\n--- Plot saved to {os.path.abspath(save_path)} ---")

def calculate_pension_wealth():
    """
    Main function to load data, process each cohort, and calculate results.
    """
    print(f"--- Starting Pension Lifetime Calculator ---")
    
    # --- 1. Load Data ---
    print(f"Loading data from '{FILE_PATH}'...")
    try:
        df = pd.read_csv(FILE_PATH)
    except FileNotFoundError:
        print(f"FATAL ERROR: File not found at '{FILE_PATH}'.")
        print("Please check the FILE_PATH variable at the top of the script.")
        return
    except Exception as e:
        print(f"FATAL ERROR: Could not read file. Error: {e}")
        return

    # --- 2. Data Preparation ---
    # List of columns required for the calculation
    required_cols = [
        'Birth_Year', 'Year', 'Population', 'Life_Expectancy', 
        'Retirement_age', 'Contribution_rate', '1999_dummy', 
        'Reference_amount_1984', 'Revaleurisation_rate', 'Salary',
        'Adjustment_factor_1984'
    ]
    
    # Check if all required columns exist
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"FATAL ERROR: The CSV is missing the following required columns:")
        for col in missing_cols:
            print(f"- {col}")
        return

    # Convert columns to numeric, handling any errors
    for col in required_cols:
        if col not in ['Birth_Year']: # Keep cohort as object for grouping
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # Drop rows where essential data is missing
    df = df.dropna(subset=required_cols)
    print("Data loaded and validated successfully.")

    # --- 3. Process Data by Cohort ---
    print("Grouping data by cohort ('Birth_Year')...")
    grouped = df.groupby('Birth_Year')
    cohort_results = []
    
    print(f"Found {len(grouped)} cohorts. Starting calculations...")

    for cohort, cohort_data in grouped:
        print(f"\nProcessing Cohort: {cohort}")
        
        try:
            # --- A. Get Cohort-Level Data ---
            Y_start_work = cohort + WORK_START_AGE
            
            # Get cohort-wide stats from the row corresponding to their start-of-work year
            work_start_row = cohort_data[cohort_data['Year'] == Y_start_work]
            
            if work_start_row.empty:
                print(f"  - SKIPPING: No data found for assumed work start year {Y_start_work}.")
                continue
                
            work_start_row = work_start_row.iloc[0]
            
            # Read float values from data
            retirement_age_float = work_start_row['Retirement_age']
            life_expectancy_float = work_start_row['Life_Expectancy']
            dummy_1999 = work_start_row['1999_dummy']
            
            # --- FIX: Round ages to nearest integer ---
            # This converts float ages (e.g., 61.4) to integers (e.g., 61)
            # to ensure all year calculations result in integers.
            retirement_age = round(retirement_age_float)
            life_expectancy = round(life_expectancy_float)
            
            # These calculations will now produce integer years
            Y_retire = cohort + retirement_age
            Y_end_work = Y_retire - 1
            Y_end_life = Y_start_work + life_expectancy
            
            print(f"  - Cohort Lifecycle: Born {cohort} | Work Start {Y_start_work} | Retire {Y_retire} | Life End {Y_end_life}")

            # --- B. Filter Data to Lifespan ---
            # This is critical: only consider the years this cohort is alive and relevant
            lifespan_data = cohort_data[
                (cohort_data['Year'] >= Y_start_work) & 
                (cohort_data['Year'] < Y_end_life)
            ]
            
            if lifespan_data.empty:
                print(f"  - SKIPPING: No lifespan data found between {Y_start_work} and {Y_end_life}.")
                continue

            # --- C. Formula 1: Total Lifetime Contributions ---
            working_life_data = lifespan_data[
                (lifespan_data['Year'] >= Y_start_work) & 
                (lifespan_data['Year'] <= Y_end_work)
            ]
            
            if working_life_data.empty:
                print(f"  - SKIPPING: No working life data found between {Y_start_work} and {Y_end_work}.")
                continue
                
            # Calculate total contributions
            total_contributions = (
                working_life_data['Salary'] * working_life_data['Contribution_rate']
            ).sum()
            
            print(f"  - Total Contributions: {total_contributions:,.0f}")

            # --- D. Formula 2: Total Lifetime Benefits ---
            
            # --- Stage 1: Calculate Initial Annual Pension (IAP) ---
            N_years = min(retirement_age - WORK_START_AGE, 40)
            
            # --- A. IAP Private ("Régime Général") ---
            
            # Get data from the year of retirement
            # This lookup will now use an integer Y_retire
            retirement_row = lifespan_data[lifespan_data['Year'] == Y_retire]
            if retirement_row.empty:
                print(f"  - SKIPPING: No data found for retirement year {Y_retire}.")
                continue
                
            reference_amount = retirement_row.iloc[0]['Reference_amount_1984']
            
            # 1. Fixed Increases
            fixed_increases = (N_years / 40) * reference_amount
            
            # 2. Proportional Increases
            sum_adjusted_earnings = (
                working_life_data['Salary'] / working_life_data['Adjustment_factor_1984'] / working_life_data['Revaleurisation_rate']
            ).sum()
            
            prop_rate = get_prop_rate(PROP_RATE_TABLE, Y_retire)
            proportional_increases = sum_adjusted_earnings * prop_rate
            
            iap_private = fixed_increases + proportional_increases
            
            # --- B. IAP Public Old ("Régime Spécial Transitoire") ---
            
            # Get data from the final working year
            # This lookup will now use an integer Y_end_work
            final_salary_row = working_life_data[working_life_data['Year'] == Y_end_work]
            if final_salary_row.empty:
                print(f"  - SKIPPING: No data found for final working year {Y_end_work}.")
                continue
                
            final_salary = final_salary_row.iloc[0]['Salary']
            
            iap_public_old = (5 / 6) * final_salary * (N_years / 40)
            
            # --- Core IAP Formula (Weighted Average) ---
            # This handles all cases as described in the logic
            iap_C = (1 - PCT_PUBLIC * (1 - dummy_1999)) * iap_private + \
                    (PCT_PUBLIC * (1 - dummy_1999)) * iap_public_old
            
            # --- Stage 2: Sum IAP Over Retirement ---
            # This calculation will now use the rounded integer ages
            num_retire_years = (WORK_START_AGE + life_expectancy) - retirement_age
            if num_retire_years < 0:
                num_retire_years = 0
                print(f"  - WARNING: Life Expectancy ({life_expectancy}) is less than Retirement Age ({retirement_age}). Setting retirement years to 0.")
                
            total_lifetime_benefits = iap_C * num_retire_years
            print(f"  - Total Benefits: {total_lifetime_benefits:,.0f}")

            # --- E. Formula 3: Net Lifetime Benefit ---
            net_benefit = total_lifetime_benefits - total_contributions
            print(f"  - Net Benefit: {net_benefit:,.0f}")

            # --- F. Store Results ---
            # Disaggregate benefits for reporting
            weight_private = 1 - PCT_PUBLIC * (1 - dummy_1999)
            weight_public = PCT_PUBLIC * (1 - dummy_1999)
            
            lifetime_fixed_benefit = fixed_increases * weight_private * num_retire_years
            lifetime_prop_benefit = proportional_increases * weight_private * num_retire_years
            lifetime_public_benefit = iap_public_old * weight_public * num_retire_years

            cohort_results.append({
                'Cohort': cohort,
                'Total_Contributions': total_contributions,
                'Total_Benefits': total_lifetime_benefits,
                'Net_Benefit': net_benefit,
                'Lifetime_Fixed_Benefit': lifetime_fixed_benefit,
                'Lifetime_Prop_Benefit': lifetime_prop_benefit,
                'Lifetime_Public_Benefit': lifetime_public_benefit
            })
            
        except Exception as e:
            print(f"  - ERROR processing cohort {cohort}: {e}")
            # Continue to the next cohort
            pass

    # --- 4. Final Output ---
    if not cohort_results:
        print("\n--- No cohorts were successfully processed. ---")
        return

    print("\n--- All cohorts processed. ---")
    
    # Convert results to a DataFrame
    results_df = pd.DataFrame(cohort_results)
    
    # Set display options for printing
    pd.set_option('display.float_format', '{:,.0f}'.format)
    pd.set_option('display.width', 1000)
    
    print("\n--- Results Summary Table ---")
    print(results_df)
    
    # Save results to CSV
    results_save_path = 'pension_lifetime_results.csv'
    results_df.to_csv(results_save_path, index=False, float_format='%.2f')
    print(f"\n--- Results table saved to {os.path.abspath(results_save_path)} ---")
    
    # Generate the plot
    plot_results(results_df)

# --- Run the main function ---
if __name__ == "__main__":
    # Check for minimal PROP_RATE_TABLE
    if not PROP_RATE_TABLE:
        print("WARNING: The 'PROP_RATE_TABLE' is empty.")
        print("Calculations for the 'Proportional Increases' will be 0.")
        print("Please edit the script to add retirement years and rates.")
        
    calculate_pension_wealth()


