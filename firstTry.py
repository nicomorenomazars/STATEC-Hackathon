import pandas as pd
import numpy as np

def create_mock_data():
    """
    Creates a mock pandas DataFrame that matches the user's description.
    
    This function generates a panel dataset for two sample cohorts (born 1960 and 1980)
    over their full lifespan, populating all the data fields you specified.
    
    This is necessary to make the main script runnable and to demonstrate
    the logic.
    """
    print("Creating mock data...")
    
    # --- Critical Data Assumptions ---
    # Based on our discussion, your input table needs two clarifications
    # which I've added here:
    # 1. 'contribution_ceiling': We need this to correctly calculate
    #    contributions and benefits for the Régime Général (private).
    # 2. 'revaluation_factor_salary_adj': This is the "Facteur de revalorisation"
    #    used to adjust past salaries (Ingredient C from our recipe).
    # 3. 'pension_adjustment_rate': This is the *future* rate (based on real
    #    wage growth) used to project pensions *after* retirement (Ingredient F).
    #
    # Your 'revalorisation rate' was ambiguous, so I've split it into
    # these two distinct, necessary ingredients.
    # ---
    
    data = []
    cohorts = [1960, 1980]
    start_year = 1982
    end_year = 2068 # Allows 1980 cohort to live to 88
    
    base_salary = 40000
    base_ceiling = 100000
    base_ref_amount = 2000 # (at 1984 base)
    base_adj_factor = 0.8 # (dummy 1984 conversion)
    base_reval_factor = 1.1 # (dummy reval factor)

    for cohort in cohorts:
        # --- Define this cohort's characteristics ---
        cohort_size = 1000
        life_expectancy = 85
        
        # We'll use the data you provided
        if cohort == 1960:
            avg_retirement_age = 61
            public_private_split = 0.20 # 20% public
            is_pre_1999_regime = 1 # This cohort is "Régime Transitoire"
            start_work_age = 22
        else: # cohort == 1980
            avg_retirement_age = 63
            public_private_split = 0.18 # 18% public
            is_pre_1999_regime = 0 # This cohort is "Régime Spécial" (post-1999)
            start_work_age = 22
            
        retirement_year = cohort + avg_retirement_age
        death_year = cohort + life_expectancy

        for year in range(start_year, end_year + 1):
            age = year - cohort
            
            # Skip years before this cohort was born or started working
            if age < start_work_age:
                continue
                
            # Stop generating data after death
            if age > life_expectancy:
                continue

            # Simulate salary growth (simple linear)
            # In a real model, this would be a complex curve
            salary_growth = (age - start_work_age) * 1000
            avg_salary = base_salary + salary_growth
            
            # Simulate economic parameter growth (simple)
            contribution_ceiling = base_ceiling + (year - start_year) * 500
            reference_amount = base_ref_amount + (year - start_year) * 10
            adjustment_factor_1984 = base_adj_factor + (year - start_year) * 0.005
            revaluation_factor_salary_adj = base_reval_factor + (year - start_year) * 0.005
            pension_adjustment_rate = 0.015 # Assume 1.5% real wage growth
            
            row = {
                'year': year,
                'cohort': cohort,
                'age': age,
                'cohort_size': cohort_size,
                'life_expectancy': life_expectancy,
                'avg_retirement_age': avg_retirement_age,
                'avg_salary': avg_salary,
                'contribution_rate': 0.24, # Fixed 24%
                'revaluation_factor_salary_adj': revaluation_factor_salary_adj,
                'pension_adjustment_rate': pension_adjustment_rate,
                'public_private_split': public_private_split,
                'is_pre_1999_regime': is_pre_1999_regime,
                'reference_amount': reference_amount,
                'adjustment_factor_1984': adjustment_factor_1984,
                'contribution_ceiling': contribution_ceiling,
                'retirement_year': retirement_year
            }
            data.append(row)

    df = pd.DataFrame(data)
    # Set the panel data index
    df = df.set_index(['year', 'cohort'])
    print("Mock data created successfully.")
    return df

def get_proportional_rate(retirement_year):
    """
    Calculates the 'taux de majoration proportionnelle' (Ingredient D).
    
    This implements the 2012 reform, which linearly reduces the
    proportional rate from 1.85% (for 2012 retirement) to 1.60%
    (for 2052 retirement).
    """
    start_rate = 1.85 / 100 # 1.85%
    end_rate = 1.60 / 100   # 1.60%
    start_year = 2012
    end_year = 2052

    if retirement_year <= start_year:
        return start_rate
    if retirement_year >= end_year:
        return end_rate
    
    # Linear interpolation
    progress = (retirement_year - start_year) / (end_year - start_year)
    rate = start_rate - (start_rate - end_rate) * progress
    
    return rate

def get_lifetime_adjusted_earnings(working_data_slice, is_public):
    """
    Calculates the 'Sum of All Adjusted Lifetime Earnings' (Ingredient C).
    
    This is the most complex part of the benefit formula. It iterates
    over an agent's entire career to get the total "points"
    for their proportional pension.
    """
    total_adjusted_earnings = 0
    
    for year, row in working_data_slice.iterrows():
        salary = row['avg_salary']
        
        # --- Apply Contribution Ceiling (Régime Général only) ---
        if not is_public:
            ceiling = row['contribution_ceiling']
            contributable_salary = min(salary, ceiling)
        else:
            # Public sector ("Régimes Spéciaux") has NO ceiling
            contributable_salary = salary
            
        # --- Adjust Salary (Two-Step Process) ---
        
        # 1. Adjust to 1984 Base Year
        # (This is your 'ajustement factor pour 1984 euros')
        salary_1984_base = contributable_salary / row['adjustment_factor_1984']
        
        # 2. Revalue to Current Standard of Living
        # (This is your 'revalorisation rate', which I've named
        # 'revaluation_factor_salary_adj' for clarity)
        final_adjusted_salary = salary_1984_base * row['revaluation_factor_salary_adj']
        
        total_adjusted_earnings += final_adjusted_salary
        
    return total_adjusted_earnings

def calculate_initial_annual_pension(cohort_data):
    """
    Calculates the "Initial Annual Pension" (IAP) for one cohort.
    
    This is the "base sauce" (Step 3 in the recipe). It calculates
    the pension amount the agent is first awarded in their
    year of retirement.
    
    It calculates this separately for the Private and Public agents
    and returns a single, weighted-average IAP.
    """
    
    # --- Get key cohort-wide variables ---
    # We can take these from the first row, they are constant for the cohort
    first_row = cohort_data.iloc[0]
    cohort_birth_year = first_row.name[1] # Get cohort from index
    avg_retirement_age = first_row['avg_retirement_age']
    public_private_split = first_row['public_private_split']
    is_pre_1999_regime = first_row['is_pre_1999_regime']
    
    retirement_year = cohort_birth_year + avg_retirement_age
    
    # Get a DataFrame slice containing only the *working* years for this cohort
    # The index is (year, cohort), so we access the year part of the index
    working_years_mask = cohort_data.index.get_level_values('year') < retirement_year
    working_data = cohort_data[working_years_mask]
    
    if working_data.empty:
        # This cohort hasn't started working yet in the dataset
        return 0, retirement_year
        
    # Get parameters from the *year of retirement*
    # We need to query the original df for the retirement year data
    try:
        retirement_year_data = cohort_data.loc[(retirement_year, cohort_birth_year)]
        ref_amount_at_retirement = retirement_year_data['reference_amount']
    except KeyError:
        # Data for retirement year not in slice, use last available
        ref_amount_at_retirement = working_data.iloc[-1]['reference_amount']

    career_length = len(working_data)

    # --- 1. Calculate IAP for the "Private Agent" (Régime Général) ---
    
    # 1a. Fixed Part (Majorations Forfaitaires)
    # Based on duration, capped at 40 years
    fixed_part_private = (min(career_length, 40) / 40) * ref_amount_at_retirement
    
    # 1b. Proportional Part (Majorations Proportionnelles)
    # Based on lifetime income
    lifetime_earnings_private = get_lifetime_adjusted_earnings(working_data, is_public=False)
    prop_rate = get_proportional_rate(retirement_year)
    prop_part_private = lifetime_earnings_private * prop_rate
    
    iap_private = fixed_part_private + prop_part_private

    # --- 2. Calculate IAP for the "Public Agent" (Régime Spécial) ---
    
    if is_pre_1999_regime == 1:
        # --- "Old System" (Régime Transitoire) ---
        # Benefit is based on *last salary*, not lifetime earnings
        final_salary = working_data.iloc[-1]['avg_salary']
        iap_public = final_salary * (5/6) # 83.3% of final salary
        
    else:
        # --- "New System" (Post-1999) ---
        # Benefit formula is same as private, but with NO ceilings
        
        # 2a. Fixed Part
        fixed_part_public = (min(career_length, 40) / 40) * ref_amount_at_retirement
        
        # 2b. Proportional Part
        # We pass is_public=True to ignore the contribution ceiling
        lifetime_earnings_public = get_lifetime_adjusted_earnings(working_data, is_public=True)
        # Proportional rate is the same
        prop_rate_public = get_proportional_rate(retirement_year) 
        prop_part_public = lifetime_earnings_public * prop_rate_public
        
        iap_public = fixed_part_public + prop_part_public
        # Note: We are ignoring the "no maximum pension" rule for simplicity,
        # but it could be added here.

    # --- 3. Calculate Weighted Average IAP for the Cohort ---
    iap_weighted = (iap_private * (1 - public_private_split)) + (iap_public * public_private_split)
    
    return iap_weighted, retirement_year

def calculate_in_year_contributions(row):
    """
    Calculates the total contribution for a single year-cohort.
    This is the "tax" paid *in this year*.
    """
    # This agent is working in this year.
    avg_salary = row['avg_salary']
    split = row['public_private_split']
    rate = row['contribution_rate'] # This is the 24%
    ceiling = row['contribution_ceiling']
    
    # --- Private Sector Contribution (has ceiling) ---
    contributable_salary_private = min(avg_salary, ceiling)
    contribution_private = (1 - split) * contributable_salary_private * rate
    
    # --- Public Sector Contribution (no ceiling) ---
    contributable_salary_public = avg_salary
    contribution_public = split * contributable_salary_public * rate
    
    # --- Total Weighted Contribution ---
    total_contribution = contribution_private + contribution_public
    
    return total_contribution

def calculate_lifetime_flows(df):
    """
    Main function to process the entire panel DataFrame.
    
    It iterates cohort by cohort, calculates the Initial Annual Pension (IAP)
    for each, and then iterates year by year to populate the
    contributions (during work) and benefits (during retirement).
    """
    print("Calculating lifetime flows...")
    
    # Create new columns, initialized to zero
    df['total_contributions_paid_in_year'] = 0.0
    df['total_benefits_received_in_year'] = 0.0
    
    # We must process one cohort at a time
    # We group by the 'cohort' level of the index
    for cohort_birth_year, cohort_data in df.groupby(level='cohort'):
        
        print(f"  Processing Cohort: {cohort_birth_year}")
        
        # --- STEP 1: Calculate the IAP for this entire cohort ---
        # This gives us a single "base pension" value for this cohort
        # and their average retirement year.
        initial_annual_pension, retirement_year = calculate_initial_annual_pension(cohort_data)
        
        if initial_annual_pension == 0:
            print(f"    Skipping cohort {cohort_birth_year} (no working data).")
            continue
            
        print(f"    Cohort {cohort_birth_year} IAP: {initial_annual_pension:.2f} (retiring in {retirement_year})")

        # --- STEP 2: Iterate through each year of this cohort's life ---
        # We now "play" this cohort's life, year by year, and fill in
        # either the contribution they pay or the benefit they receive.
        
        # We need to store the "live" adjusted pension as it grows
        current_projected_pension = initial_annual_pension
        
        for index, row in cohort_data.iterrows():
            current_year = index[0] # Get year from index
            age = row['age']
            avg_retirement_age = row['avg_retirement_age']

            if age < avg_retirement_age:
                # --- WORKING PHASE ---
                # Calculate the contributions paid in this year
                contribution = calculate_in_year_contributions(row)
                df.loc[index, 'total_contributions_paid_in_year'] = contribution
                
            elif age >= avg_retirement_age:
                # --- RETIREMENT PHASE ---
                
                # For the *first year* of retirement, they get the IAP
                # For all subsequent years, we must adjust the *previous*
                # year's pension by the new adjustment rate.
                
                if current_year == retirement_year:
                    # First year of retirement
                    current_projected_pension = initial_annual_pension
                else:
                    # Adjust the *previous* year's pension for this year
                    # This is Ingredient F: Projecting the pension
                    adjustment_rate = row['pension_adjustment_rate']
                    current_projected_pension = current_projected_pension * (1 + adjustment_rate)

                df.loc[index, 'total_benefits_received_in_year'] = current_projected_pension

    print("Calculations complete.")
    return df

# --- Main execution ---
if __name__ == "__main__":
    
    # 1. Create the mock data based on user's schema
    panel_data = create_mock_data()
    
    print("\n--- Input Mock Data (Head) ---")
    print(panel_data.head())
    
    # 2. Run the main recipe
    output_data = calculate_lifetime_flows(panel_data.copy())

    # 3. Show the results
    print("\n\n--- Output Data (Showing 1960 Cohort's Retirement) ---")
    print(output_data.loc[(output_data.index.get_level_values('cohort') == 1960) &
                          (output_data.index.get_level_values('year') >= 2020),
                          ['age', 'avg_salary', 'total_contributions_paid_in_year', 'total_benefits_received_in_year']])
                          
    print("\n\n--- Output Data (Showing 1980 Cohort's Retirement) ---")
    print(output_data.loc[(output_data.index.get_level_values('cohort') == 1980) &
                          (output_data.index.get_level_values('year') >= 2042),
                          ['age', 'avg_salary', 'total_contributions_paid_in_year', 'total_benefits_received_in_year']])

    # 4. To get the final graph, you would now apply the PV calculation
    #    to the output columns and sum them up by cohort.
    
    print("\n\n--- Final Step (for your graph) ---")
    print("To get the final graph, you would now:")
    
    # Create a discount factor column
    # (Assuming r=2.0% and PV year is 2025)
    r = 0.02
    pv_year = 2025
    
    # We need to reset the index to access 'year'
    output_data_reset = output_data.reset_index()
    output_data_reset['discount_factor'] = 1 / ((1 + r) ** (output_data_reset['year'] - pv_year))
    
    # Calculate PV of contributions and benefits
    output_data_reset['pv_contributions'] = output_data_reset['total_contributions_paid_in_year'] * output_data_reset['discount_factor']
    output_data_reset['pv_benefits'] = output_data_reset['total_benefits_received_in_year'] * output_data_reset['discount_factor']

    # Sum by cohort to get the final bars
    final_bars = output_data_reset.groupby('cohort')[['pv_contributions', 'pv_benefits']].sum()
    final_bars['net_transfer'] = final_bars['pv_benefits'] - final_bars['pv_contributions']
    
    print(final_bars)
