# ==============================
# Install required packages if needed
# ==============================
# pip install pandas yfinance requests

import pandas as pd
import yfinance as yf
import requests
from datetime import datetime, timedelta
import os


# SETTINGS

#set the end of the data set to today
end_date = datetime.today() 
#Calculate the start date to 5 years ago
start_date = end_date - timedelta(days=5*365)
#Convert start and end date to string
start = start_date.strftime('%Y-%m-%d')
end = end_date.strftime('%Y-%m-%d')

print("Fetching data from", start, "to", end)


# Data Extraction: YFINANCE SAFE DOWNLOAD

def safe_download(ticker, col_name):
    try:
        df = yf.download(ticker, start=start, end=end, auto_adjust=False)
        #Convert date to regualr column
        df = df.reset_index()
        #Simlify the tickers that return multi-level column headers
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            #Return empty Dateframe with column name if date and close do not exist
        if "Date" not in df.columns or "Close" not in df.columns:
            return pd.DataFrame(columns=["Date", col_name])
        #Convert date to datetime format
        df["Date"] = pd.to_datetime(df["Date"])
        #keep only the date and close and rename close to the specific column name
        df = df[["Date", "Close"]].rename(columns={"Close": col_name})
        return df
    #Exeption handling if ticker fails
    except Exception as e:
        print(f"Error downloading {ticker}: {e}")
        return pd.DataFrame(columns=["Date", col_name])



# 1️⃣ STOCK INDEX: FTSE/JSE All Share (replaces JTOPI)

# Working symbol on Yahoo Finance: ^JALSH
stock = yf.download("^J203.JO", start=start, end=end, auto_adjust=False)
stock = stock.reset_index()
if isinstance(stock.columns, pd.MultiIndex):
    stock.columns = stock.columns.get_level_values(0)
stock["Date"] = pd.to_datetime(stock["Date"])
#Rename columns to match the dataset
stock = stock.rename(columns={
    "Open":"Open Price",
    "Close":"Close Price",
    "High":"Daily High",
    "Low":"Daily Low",
    "Volume":"Trading Volume"
})
#Add new column called stock index
stock["Stock Index"] = "FTSE/JSE All Share"
#keep this columns only to be mereged later
stock = stock[["Date","Stock Index","Open Price","Close Price","Daily High","Daily Low","Trading Volume"]]


# 2️⃣ FOREX & COMMODITIES

fx = safe_download("ZAR=X", "Forex USD/ZAR")
gold = safe_download("GC=F", "Gold Price (USD per Ounce)")
oil = safe_download("CL=F", "Crude Oil Price (USD per Barrel)")



# 3️⃣ DATA EXTRAXTION: SOUTH AFRICA MACRO DATA (WORLD BANK)


def get_world_bank_series(indicator_code, column_name):
    try:
        url = f"https://api.worldbank.org/v2/country/ZAF/indicator/{indicator_code}?format=json&per_page=500"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Error fetching {column_name}")
            return pd.DataFrame(columns=["Date", column_name])

        data = response.json()

        if len(data) < 2:
            return pd.DataFrame(columns=["Date", column_name])

        records = data[1]
        df = pd.DataFrame(records)

        df = df[["date", "value"]]
        df.columns = ["Date", column_name]

        df["Date"] = pd.to_datetime(df["Date"], format="%Y", errors="coerce")
        df = df.dropna()

        return df

    except Exception as e:
        print(f"Error fetching {column_name}: {e}")
        return pd.DataFrame(columns=["Date", column_name])


# Fetch macro indicators
gdp = get_world_bank_series("NY.GDP.MKTP.KD.ZG", "GDP Growth (%)")
inflation = get_world_bank_series("FP.CPI.TOTL.ZG", "Inflation Rate (%)")
unemployment = get_world_bank_series("SL.UEM.TOTL.ZS", "Unemployment Rate (%)")
interest = get_world_bank_series("FR.INR.RINR", "Interest Rate (%)")

macro_list = [gdp, inflation, unemployment, interest]

macro = None
for m in macro_list:
    if not m.empty:
        if macro is None:
            macro = m
        else:
            macro = pd.merge(macro, m, on="Date", how="outer")

if macro is None:
    macro = pd.DataFrame(columns=["Date"])


# 4️⃣ MERGE EVERYTHING

df = stock.copy()
# Expand macro annual data to daily frequency
if not macro.empty:
    macro = macro.sort_values("Date")
    macro = macro.set_index("Date")
    macro = macro.resample("D").ffill().reset_index()

for dataset in [fx, gold, oil, macro]:
    if not dataset.empty:
        dataset["Date"] = pd.to_datetime(dataset["Date"])
        df = pd.merge(df, dataset, on="Date", how="left")


#for col in extra_cols:
script_dir = os.path.dirname(os.path.abspath(__file__))  # folder of this script
output_file = os.path.join(script_dir, "south_africa_complete_dataset.csv")
df.to_csv(output_file, index=False)


# 7️⃣ DEBUG & CONFIRM

print(f"✅ Dataset saved in the same folder as script: {output_file}")
print(f"Number of rows fetched: {len(df)}")
print(df.head())
