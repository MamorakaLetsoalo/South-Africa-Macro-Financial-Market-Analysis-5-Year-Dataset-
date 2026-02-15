# South-Africa-Macro-Financial-Market-Analysis-5-Year-Dataset

#Project Overview

This project builds a 5-year integrated macro-financial dataset for South Africa, combining:

📈 FTSE/JSE All Share Index (daily)
💱 USD/ZAR exchange rate (daily)
🛢️ Crude Oil price (daily)
🥇 Gold price (daily)
📊 GDP Growth (%)
📈 Inflation Rate (%)
👥 Unemployment Rate (%)
💰 Interest Rate (%)

The objective is to analyze the relationship between macroeconomic indicators, global commodities, currency movements, and South Africa’s equity market performance.

#This repository includes:

Python data collection & transformation script
Clean merged dataset (CSV)
Power BI dashboard structure
Case study framework
 
#How We Got the Data:
The dataset was built using publicly available APIs and financial data sources.

#1.Market Data (Daily)
Source: Yahoo Finance via yfinance

Pulled using Python:
^J203.JO → FTSE/JSE All Share Index
ZAR=X → USD/ZAR exchange rate
GC=F → Gold Futures
CL=F → Crude Oil Futures

Data frequency: Daily
Period: Last 5 years

Fields collected:
Open Price
Close Price
Daily High
Daily Low
rading Volume

#2.Macroeconomic Data (Annual)
Source: World Bank Open Data API
Country Code: ZAF (South Africa)

Indicators used:
Indicator	World Bank Code
GDP Growth (%)	NY.GDP.MKTP.KD.ZG
Inflation Rate (%)	FP.CPI.TOTL.ZG
Unemployment Rate (%)	SL.UEM.TOTL.ZS
Real Interest Rate (%)	FR.INR.RINR
World Bank macro data is annual, so:
Annual values were forward-filled to daily frequency,this allows alignment with daily market data

#3.Data Processing
Steps performed:
Download daily financial data
Download macroeconomic data
Convert all date formats to datetime
Resample macro data to daily frequency
merge all datasets on Date
Export clean dataset to CSV

Final output:south_africa_complete_dataset.csv

#📊 What Analysis Can Be Performed?

This dataset enables multiple levels of financial and macroeconomic analysis.

1. Market Performance Analysis
5-year equity trend analysis
Annualized returns
Volatility analysis
Bull vs bear market identification

 2. Currency Impact Analysis
Analyze relationship between:
USD/ZAR depreciation/appreciation
JSE index performance
Key questions:
Does a weaker Rand benefit equities?
Is currency risk driving equity volatility?

3. Commodity Sensitivity
Examine:
Gold vs JSE correlation
Oil vs JSE correlation
Test hypotheses such as:
Does gold act as a safe haven?
Does oil price movement affect equity performance?

4. Macroeconomic Influence
Study relationships between:
Interest rates and equity returns
Inflation and market drawdowns
GDP growth and market expansion
Unemployment and investor sentiment

5. Correlation Analysis
Build correlation matrix across:
Equity returns
FX returns
Gold returns
Oil returns
Inflation
Interest rate
GDP growth

Identify:
Diversification opportunities
Risk drivers
Leading indicators

6. Regression Modeling
Model:
Equity Returns = f(FX, Gold, Oil, Inflation, Interest Rate, GDP)

This helps identify:
Which variables significantly impact market returns
Magnitude of macro sensitivity
Predictive relationships

 7. Crisis & Event Analysis
Use time-based filtering to study:
COVID period
Inflation spikes
Monetary tightening cycles
Analyze how each asset class behaved during stress.

🧠 Key Insights This Project Can Deliver

How sensitive is South Africa’s equity market to currency movements?
Do commodities hedge local equity risk?
Does monetary tightening reduce equity returns?
Is inflation a leading indicator of market volatility?
What macro variable explains the most market variance?

⚙️ Tech Stack

Python
pandas
yfinance
requests
World Bank API
Power BI
CSV data pipeline

📁 Repository Structure
/data
    south_africa_complete_dataset.csv
/scripts
    export_south_africa_data.py
/powerbi
    South_Africa_Market_Dashboard.pbix
README.md

📌 Disclaimer

This project is for educational and analytical purposes only.
Market data is sourced from public APIs and may be delayed.
Not financial advice.

