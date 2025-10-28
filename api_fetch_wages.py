import requests
import pandas as pd
from io import StringIO
import os
from datetime import datetime

# 1. Define the API query URL (without the 'format' parameter)
url = "https://sdmx.oecd.org/public/rest/data/OECD.ELS.SAE,DSD_EARNINGS@AV_AN_WAGE,1.0/LUX......?startPeriod=1990&endPeriod=2024"

# 2. Define the HTTP Header to request CSV with labels
# This tells the server we accept CSV data with labels.
headers = {
    'Accept': 'application/vnd.sdmx.data+csv; charset=utf-8; labels=both'
}

print(f"Fetching data from: {url}\n")

try:
    # 3. Fetch data, passing the 'headers' argument
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Check for HTTP errors

    # 4. Load the CSV response text into a pandas DataFrame
    df = pd.read_csv(StringIO(response.text))
    out_fname = f"oecd_wages_{datetime.now():%Y%m%d_%H%M%S}.csv"
    out_path = os.path.join(os.path.dirname(__file__), out_fname)
    df.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"Saved DataFrame to: {out_path}")
    # 5. Display the first few rows and all columns
    print(df)
    print("Data fetched successfully. First 5 rows:")
    print(df.head())
    
    print("\nDataFrame columns:")
    print(df.columns)

except requests.exceptions.RequestException as e:
    print(f"API request failed: {e}")
except pd.errors.EmptyDataError:
    print("The API returned no data for the query.")
except Exception as e:
    print(f"An error occurred: {e}")