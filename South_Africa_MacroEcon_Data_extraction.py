# Import pandas for data manipulation and analysis
import pandas as pd

# Import yfinance to download financial market data from Yahoo Finance
import yfinance as yf

# Import requests to call APIs (World Bank macro data)
import requests

# Import datetime tools to calculate date ranges
from datetime import datetime, timedelta

# Import os to handle file paths and save the output in the correct folder
import os


# SETTINGS


# Set the end date of the dataset to today’s date
end_date = datetime.today() 

# Calculate the start date as 5 years ago from today
start_date = end_date - timedelta(days=5*365)

# Convert the start date to string format YYYY-MM-DD (required by yfinance)
start = start_date.strftime('%Y-%m-%d')

# Convert the end date to string format YYYY-MM-DD
end = end_date.strftime('%Y-%m-%d')

# Print confirmation of the time range being fetched
print("Fetching data from", start, "to", end)



# DATA EXTRACTION FUNCTION: YFINANCE SAFE DOWNLOAD
# =========================

def safe_download(ticker, col_name):
    try:
        # Download historical market data for the given ticker
        df = yf.download(ticker, start=start, end=end, auto_adjust=False)

        # Reset index so Date becomes a normal column instead of index
        df = df.reset_index()

        # If the dataframe has multi-level columns (sometimes happens),
        # flatten them to single-level column names
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # If required columns are missing, return an empty dataframe
        if "Date" not in df.columns or "Close" not in df.columns:
            return pd.DataFrame(columns=["Date", col_name])

        # Convert Date column to proper datetime format
        df["Date"] = pd.to_datetime(df["Date"])

        # Keep only Date and Close price, rename Close to custom column name
        df = df[["Date", "Close"]].rename(columns={"Close": col_name})

        return df

    # If download fails, print error and return empty dataframe
    except Exception as e:
        print(f"Error downloading {ticker}: {e}")
        return pd.DataFrame(columns=["Date", col_name])


# 1. STOCK INDEX: FTSE/JSE ALL SHARE


# Download FTSE/JSE All Share index data
stock = yf.download("^J203.JO", start=start, end=end, auto_adjust=False)

# Convert Date index into a normal column
stock = stock.reset_index()

# Flatten multi-level column names if present
if isinstance(stock.columns, pd.MultiIndex):
    stock.columns = stock.columns.get_level_values(0)

# Ensure Date column is in datetime format
stock["Date"] = pd.to_datetime(stock["Date"])

# Rename columns to more descriptive names for dashboard use
stock = stock.rename(columns={
    "Open":"Open Price",
    "Close":"Close Price",
    "High":"Daily High",
    "Low":"Daily Low",
    "Volume":"Trading Volume"
})

# Add a column identifying the stock index name
stock["Stock Index"] = "FTSE/JSE All Share"

# Keep only relevant columns for merging later
stock = stock[[
    "Date",
    "Stock Index",
    "Open Price",
    "Close Price",
    "Daily High",
    "Daily Low",
    "Trading Volume"
]]


# 2. FOREX & COMMODITIES

# Download USD/ZAR exchange rate
fx = safe_download("ZAR=X", "Forex USD/ZAR")

# Download Gold futures price
gold = safe_download("GC=F", "Gold Price (USD per Ounce)")

# Download Crude Oil futures price
oil = safe_download("CL=F", "Crude Oil Price (USD per Barrel)")



# 3. MACRO DATA: WORLD BANK API

def get_world_bank_series(indicator_code, column_name):
    try:
        # Build API URL for South Africa (ZAF)
        url = f"https://api.worldbank.org/v2/country/ZAF/indicator/{indicator_code}?format=json&per_page=500"

        # Send request to World Bank API
        response = requests.get(url)

        # If request fails, return empty dataframe
        if response.status_code != 200:
            print(f"Error fetching {column_name}")
            return pd.DataFrame(columns=["Date", column_name])

        # Convert response to JSON
        data = response.json()

        # If no data returned, return empty dataframe
        if len(data) < 2:
            return pd.DataFrame(columns=["Date", column_name])

        # Extract actual data records
        records = data[1]

        # Convert records to DataFrame
        df = pd.DataFrame(records)

        # Keep only year and value columns
        df = df[["date", "value"]]

        # Rename columns
        df.columns = ["Date", column_name]

        # Convert year to datetime format
        df["Date"] = pd.to_datetime(df["Date"], format="%Y", errors="coerce")

        # Drop rows with missing values
        df = df.dropna()

        return df

    # Handle exceptions safely
    except Exception as e:
        print(f"Error fetching {column_name}: {e}")
        return pd.DataFrame(columns=["Date", column_name])


# Fetch macroeconomic indicators from World Bank
gdp = get_world_bank_series("NY.GDP.MKTP.KD.ZG", "GDP Growth (%)")
inflation = get_world_bank_series("FP.CPI.TOTL.ZG", "Inflation Rate (%)")
unemployment = get_world_bank_series("SL.UEM.TOTL.ZS", "Unemployment Rate (%)")
interest = get_world_bank_series("FR.INR.RINR", "Interest Rate (%)")

# Store macro datasets in list
macro_list = [gdp, inflation, unemployment, interest]

# Initialize macro dataframe
macro = None

# Merge all macro datasets together on Date
for m in macro_list:
    if not m.empty:
        if macro is None:
            macro = m
        else:
            macro = pd.merge(macro, m, on="Date", how="outer")

# If all macro data failed, create empty dataframe
if macro is None:
    macro = pd.DataFrame(columns=["Date"])



# 4. MERGE EVERYTHING

# Start with stock index data as base dataframe
df = stock.copy()

# Expand annual macro data into daily frequency
if not macro.empty:
    macro = macro.sort_values("Date")  # Sort by date
    macro = macro.set_index("Date")    # Set Date as index
    macro = macro.resample("D").ffill().reset_index()  # Convert yearly → daily using forward fill

# Merge FX, gold, oil, and macro datasets into main dataframe
for dataset in [fx, gold, oil, macro]:
    if not dataset.empty:
        dataset["Date"] = pd.to_datetime(dataset["Date"])
        df = pd.merge(df, dataset, on="Date", how="left")


# SAVE DATASET

# Get the folder where this Python script is saved
script_dir = os.path.dirname(os.path.abspath(__file__))

# Create full path for output CSV file in same folder
output_file = os.path.join(script_dir, "south_africa_complete_dataset.csv")

# Save final merged dataset to CSV
df.to_csv(output_file, index=False)


# DEBUG & CONFIRM

# Confirm file saved successfully
print(f"✅ Dataset saved in the same folder as script: {output_file}")

# Print number of rows
print(f"Number of rows fetched: {len(df)}")

# Print first few rows for verification
print(df.head())
