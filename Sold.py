# %%

import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# %%
# Week 1

files = glob.glob('raw/CRMLSSold*.csv')
data = []
count1 = 0

for f in files:
    file = pd.read_csv(f)
    count1 += len(file)
    data.append(file)
combined_sold = pd.concat(data, ignore_index=True)
print(count1)
##Before concat count = 591733

count2 = len(combined_sold)
print(count2)
##After concat count = 591733

combined_sold = combined_sold[combined_sold['PropertyType'] == 'Residential']

count3 = len(combined_sold)
print(count3)
##After filter count = 397603

combined_sold.to_csv('sold.csv', index=False)

# %%
# Week 2

sold = pd.read_csv("sold.csv", low_memory=False)

#converting dates to datetime format
sold['CloseDate'] = pd.to_datetime(sold['CloseDate'], errors="coerce")
sold['ListingContractDate'] = pd.to_datetime(sold['ListingContractDate'], errors="coerce")
sold['PurchaseContractDate'] = pd.to_datetime(sold['PurchaseContractDate'], errors="coerce")
sold['ContractStatusChangeDate'] = pd.to_datetime(sold['ContractStatusChangeDate'], errors="coerce")

#getting null count and percentages
null_sold = sold.isnull().sum()
pct_sold = (null_sold / len(sold)) * 100

sold_report = pd.DataFrame({'total null': null_sold, 'perecnt null': pct_sold})

#finding high null columns
high_null_sold = sold_report[sold_report['perecnt null'] > 90]

print("possible sold columns to drop:\n", high_null_sold)

#saving high null columns with value and finding other columns to drop
save_list = ['WaterfrontYN', 'BasementYN']
single_val_sold = [col for col in sold.columns if (sold[col].nunique() <= 1) & (col not in save_list)]

print("single val drops:\n", single_val_sold)

#combining columns to drop and save
drop_sold = [col for col in high_null_sold.index.tolist() if col not in save_list]
drop_sold = list(set(drop_sold + single_val_sold))

print("listed columns to drop:\n", drop_sold)

#dropping columns
print("before drop shape:", sold.shape)

sold = sold.drop(columns=drop_sold)

print("after drop shape:", sold.shape)

#creating numeric distribution summary for key variables
cols = ["ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea",
             "LotSizeAcres", "BedroomsTotal", "BathroomsTotalInteger",
             "DaysOnMarket", "YearBuilt"]

for col in cols:
    if col in sold.columns:
        s = sold[col].dropna()
        print(f"\n{col}:")
        print(f"count: {len(s)}")
        print(f"mean: {s.mean():.2f}")
        print(f"median: {s.median():.2f}")
        print(f"min: {s.min():.2f}")
        print(f"max: {s.max():.2f}")
        print(f"pct1: {s.quantile(0.01):.2f}")
        print(f"pct5: {s.quantile(0.05):.2f}")
        print(f"pct25: {s.quantile(0.25):.2f}")
        print(f"pct75: {s.quantile(0.75):.2f}")
        print(f"pct95: {s.quantile(0.95):.2f}")
        print(f"pct99: {s.quantile(0.99):.2f}")

#creating boxplots and histograms
for col in cols:
    if col in sold.columns:
        plt.figure(figsize = (10,6))
        sns.histplot(sold[col], bins=50, kde=True)
        plt.title(f"Sold Distribution of {col}")
        plt.savefig(f"Plots/sold_histogram/sold_{col}_histogram.png")
        plt.show()
        plt.close()

        plt.figure(figsize = (10,6))
        sns.boxplot(x=sold[col])
        plt.title(f"Sold Boxplot of {col}")
        plt.savefig(f"Plots/sold_boxplot/sold_{col}_boxplot.png")
        plt.show()
        plt.close()

sold.to_csv('sold_eda.csv', index=False)

# %%
# Week 3

sold = pd.read_csv("sold_eda.csv", low_memory=False)

sold['CloseDate'] = pd.to_datetime(sold['CloseDate'], errors="coerce")
sold['ListingContractDate'] = pd.to_datetime(sold['ListingContractDate'], errors="coerce")
sold['PurchaseContractDate'] = pd.to_datetime(sold['PurchaseContractDate'], errors="coerce")
sold['ContractStatusChangeDate'] = pd.to_datetime(sold['ContractStatusChangeDate'], errors="coerce")

# Fetch the mortgage rate data from FRED import pandas as pd
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US" 
mortgage = pd.read_csv(url, parse_dates=['observation_date']) 
mortgage.columns = ['date', 'rate_30yr_fixed']

# Resample weekly rates to monthly averages 
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (mortgage.groupby('year_month')['rate_30yr_fixed'].mean().reset_index())

# Create a matching year_month key on the MLS datasets and merge
sold['year_month'] = sold['CloseDate'].dt.to_period('M')
sold = sold.merge(mortgage_monthly, on='year_month', how='left')

# Validate the merge
print(sold['rate_30yr_fixed'].isnull().sum())
print(sold[['CloseDate', 'year_month', 'ClosePrice', 'rate_30yr_fixed']].head())

sold.to_csv('sold_mortgage.csv', index=False)

# %%
# Weeks 4,5

sold = pd.read_csv("sold_mortgage.csv", low_memory=False)

print("original shape:", sold.shape) #(397603, 69)

#converting date fields to datetime format and proving values are properly changed
date_cols = [
    'CloseDate',
    'ListingContractDate',
    'PurchaseContractDate',
    'ContractStatusChangeDate'
]

date_report = sold[date_cols].dtypes
print(date_report)

sold['CloseDate'] = pd.to_datetime(sold['CloseDate'], errors="coerce")
sold['ListingContractDate'] = pd.to_datetime(sold['ListingContractDate'], errors="coerce")
sold['PurchaseContractDate'] = pd.to_datetime(sold['PurchaseContractDate'], errors="coerce")
sold['ContractStatusChangeDate'] = pd.to_datetime(sold['ContractStatusChangeDate'], errors="coerce")

date_report = sold[date_cols].dtypes
print(date_report)

#ensuring and proving numeric values are properly typed
numeric_cols = [
    'ClosePrice',
    'OriginalListPrice',
    'ListPrice',
    'LivingArea',
    'LotSizeAcres',
    'LotSizeSquareFeet',
    'DaysOnMarket',
    'ParkingTotal',
    'BathroomsTotalInteger',
    'BedroomsTotal',
    'Stories',
    'MainLevelBedrooms',
    'GarageSpaces',
    'AssociationFee',
    'rate_30yr_fixed',
    'Latitude',
    'Longitude'
]

numeric_report = sold[numeric_cols].dtypes
print(numeric_report)

#null report to help find areas to clean
null_sold = sold.isnull().sum()
pct_sold = (null_sold / len(sold)) * 100

sold_report = pd.DataFrame({'total null': null_sold, 'perecnt null': pct_sold})
print(sold_report)

#dropping duplicates and duplicate columns ending in .1
sold = sold.drop(list(sold.filter(regex='.1$')), axis=1)
sold = sold.drop_duplicates(subset="ListingKey", keep="last")

print("after duplicate drop shape:", sold.shape) #(397273, 69)

#dropping unnecessary and redundant columns
drop_cols = [
    #email not needed
    'ListAgentEmail',
    #use list agent full name
    'ListAgentFirstName',
    'ListAgentLastName',
    #lat and lon generation no needed
    'latfilled',
    'lonfilled',
    #use lot size acres and square feet 
    'LotSizeArea',
    #trivial info and often same as list office name
    'CoListOfficeName',
    #use buyer agent id
    'BuyerAgentFirstName',
    'BuyerAgentLastName',
    #use only co-list agent last name
    'CoListAgentFirstName',
    #use listing key
    'ListingId',
    'ListingKeyNumeric',
    #use address or lat and lon
    'StreetNumberNumeric'
]

sold = sold.drop(columns=drop_cols)

print("after unnecessary and redundant drop shape:", sold.shape) #(397273, 56)

#filling in Y/N feature columns with N 
#waterfront and basement only have true values making null false
#private pool likely to only be null if there is no pool
fill_cols = ['WaterfrontYN', 'BasementYN', 'PoolPrivateYN']
sold[fill_cols] = sold[fill_cols].fillna(False)

#finding rows with missing core values and dropping
core_null = (
    (sold['ClosePrice'].isnull()) |
    (sold['LivingArea'].isnull()) |
    (sold['ListPrice'].isnull()) |
    (sold['ListingKey'].isnull()) |
    (sold['CloseDate'].isnull()) |
    (sold['DaysOnMarket'].isnull()) |
    (sold['ListingContractDate'].isnull())
)

sold = sold[~core_null]

print("after null core drop shape:", sold.shape) #(397041, 56)

#finding rows with impossible numeric values and dropping
invalid_numeric_values = (
    (sold['ClosePrice'] <= 0) |
    (sold['OriginalListPrice'] <= 0) |
    (sold['ListPrice'] <= 0) |
    (sold['LivingArea'] <= 0) |
    (sold['LotSizeAcres'] < 0) |
    (sold['LotSizeSquareFeet'] < 0) |
    (sold['DaysOnMarket'] < 0) |
    (sold['ParkingTotal'] < 0) |
    (sold['BathroomsTotalInteger'] < 0) |
    (sold['BedroomsTotal'] < 0) |
    (sold['Stories'] < 0) |
    (sold['MainLevelBedrooms'] < 0) |
    (sold['GarageSpaces'] < 0) |
    (sold['AssociationFee'] < 0)
)

sold = sold[~invalid_numeric_values]

print("after impossible numeric values drop shape:", sold.shape) #(396751, 56)

#finding all invalid longitude or latitude values and flagging them with new column in csv
invalid_geo_values = (
    (sold['Latitude'].isnull()) | 
    (sold['Longitude'].isnull()) |
    (sold['Latitude'] == 0) | 
    (sold['Longitude'] == 0) |
    (sold['Longitude'] > 0) |
    (sold['Latitude'] < 32) | 
    (sold['Latitude'] > 42) |
    (sold['Longitude'] < -125) | 
    (sold['Longitude'] > -114)
)

sold['invalid_geo_flag'] = invalid_geo_values
invalid_geo_summary = sold[sold['invalid_geo_flag'] == True]

print(invalid_geo_summary)
print("total rows with invalid coordinates:", len(invalid_geo_summary)) #15883

#finding all invalid dates or timelines and flagging them with new column in csv
invalid_dates = (
    (sold['CloseDate'] < sold['ListingContractDate']) | 
    (sold['CloseDate'] < sold['PurchaseContractDate']) |
    (sold['PurchaseContractDate'] < sold['ListingContractDate']) |
    (sold['ContractStatusChangeDate'] < sold['ListingContractDate'])
)

sold['invalid_dates_flag'] = invalid_dates
invalid_dates_summary = sold[sold['invalid_dates_flag'] == True]

print(invalid_dates_summary)
print("total rows with invalid dates:", len(invalid_dates_summary)) #499

print("final shape:", sold.shape) #(396751, 58)

sold.to_csv('sold_cleaned.csv', index=False)

# %%
