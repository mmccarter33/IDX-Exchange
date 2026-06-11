# %%
import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# %%
# Week 1

files = glob.glob('raw/CRMLSListing*.csv')
data = []
count1 = 0

for f in files:
    file = pd.read_csv(f, low_memory=False)
    count1 += len(file)
    data.append(file)
combined_listed = pd.concat(data, ignore_index=True)
print(count1)
##Before concat count = 929165

count2 = len(combined_listed)
print(count2)
##After concat count = 929165

combined_listed = combined_listed[combined_listed['PropertyType'] == 'Residential']

count3 = len(combined_listed)
print(count3)
##After filter count = 591452

combined_listed.to_csv('listed.csv', index=False)

# %%
# Week 2

listed = pd.read_csv("listed.csv", low_memory=False)

#converting dates to datetime format
listed["CloseDate"] = pd.to_datetime(listed["CloseDate"], errors="coerce")
listed["ListingContractDate"] = pd.to_datetime(listed["ListingContractDate"], errors="coerce")
listed["PurchaseContractDate"] = pd.to_datetime(listed["PurchaseContractDate"], errors="coerce")
listed["ContractStatusChangeDate"] = pd.to_datetime(listed["ContractStatusChangeDate"], errors="coerce")

#getting null count and percentages
null_listed = listed.isnull().sum()
pct_listed = (null_listed / len(listed)) * 100

listing_report = pd.DataFrame({'total null': null_listed, 'perecnt null': pct_listed})

#finding high null columns
high_null_listing = listing_report[listing_report['perecnt null'] > 90]

drop_listed = high_null_listing.index.tolist()

print("listed columns to drop:\n", drop_listed)

#creating numeric distribution summary for key variables
cols = ["ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea",
             "LotSizeAcres", "BedroomsTotal", "BathroomsTotalInteger",
             "DaysOnMarket", "YearBuilt"]

for col in cols:
    if col in listed.columns:
        s = listed[col].dropna()
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

for col in cols:
    if col in listed.columns:
        plt.figure(figsize = (10,6))
        sns.histplot(listed[col], bins=50, kde=True)
        plt.title(f"Listed Distribution of {col}")
        plt.savefig(f"Plots/listed_histogram/listed_{col}_histogram.png")
        plt.close()

        plt.figure(figsize = (10,6))
        sns.boxplot(x=listed[col])
        plt.title(f"Listed Boxplot of {col}")
        plt.savefig(f"Plots/listed_boxplot/listed_{col}_boxplot.png")
        plt.close()

listed.to_csv('listed_eda.csv', index=False)

# %%
# Week 3

listed = pd.read_csv("listed_eda.csv", low_memory=False)

listed["CloseDate"] = pd.to_datetime(listed["CloseDate"], errors="coerce")
listed["ListingContractDate"] = pd.to_datetime(listed["ListingContractDate"], errors="coerce")
listed["PurchaseContractDate"] = pd.to_datetime(listed["PurchaseContractDate"], errors="coerce")
listed["ContractStatusChangeDate"] = pd.to_datetime(listed["ContractStatusChangeDate"], errors="coerce")

# Fetch the mortgage rate data from FRED import pandas as pd
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US" 
mortgage = pd.read_csv(url, parse_dates=['observation_date']) 
mortgage.columns = ['Date', 'Rate30YrFixed']

# Resample weekly rates to monthly averages 
mortgage['YrMo'] = mortgage['Date'].dt.to_period('M')
mortgage_monthly = (mortgage.groupby('YrMo')['Rate30YrFixed'].mean().reset_index())

# Create a matching year-month key on the MLS datasets and merge
listed['YrMo'] = listed['ListingContractDate'].dt.to_period('M')
listed = listed.merge(mortgage_monthly, on='YrMo', how='left')

# Validate the merge
print(listed['Rate30YrFixed'].isnull().sum())
print(listed[['ListingContractDate', 'YrMo', 'ListPrice', 'Rate30YrFixed']].head())

listed.to_csv('listed_mortgage.csv', index=False)

# %%
# Weeks 4,5

listed = pd.read_csv("listed_mortgage.csv", low_memory=False)

print("original shape:", listed.shape) #(591452, 86)

#converting date fields to datetime format and proving values are properly changed
date_cols = [
    'CloseDate',
    'ListingContractDate',
    'PurchaseContractDate',
    'ContractStatusChangeDate'
]

date_report = listed[date_cols].dtypes
print(date_report)

listed["CloseDate"] = pd.to_datetime(listed["CloseDate"], errors="coerce")
listed["ListingContractDate"] = pd.to_datetime(listed["ListingContractDate"], errors="coerce")
listed["PurchaseContractDate"] = pd.to_datetime(listed["PurchaseContractDate"], errors="coerce")
listed["ContractStatusChangeDate"] = pd.to_datetime(listed["ContractStatusChangeDate"], errors="coerce")

date_report = listed[date_cols].dtypes
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
    'Rate30YrFixed',
    'Latitude',
    'Longitude'
]

numeric_report = listed[numeric_cols].dtypes
print(numeric_report)

#dropping columns determined in week 2 due to high null
listed = listed.drop(columns=drop_listed)

print("after null drop shape:", listed.shape) #(591452, 73)

#dropping any columns with only one unique value other than those determined to be saved
single_val_listed = [col for col in listed.columns if (listed[col].nunique() <= 1)]
listed = listed.drop(columns=single_val_listed)

print("after single val drop shape:", listed.shape) #(591452, 71)

#dropping duplicates and duplicate columns ending in .1
listed = listed.drop(list(listed.filter(regex='.1$')), axis=1)
listed = listed.drop_duplicates(subset="ListingKey", keep="last")

print("after duplicate drop shape:", listed.shape) #(591317, 61)

#dropping unnecessary and redundant columns
drop_cols = [
    #email not needed
    'ListAgentEmail',
    #use list agent full name
    'ListAgentFirstName',
    'ListAgentLastName',
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

listed = listed.drop(columns=drop_cols)

print("after unnecessary and redundant drop shape:", listed.shape) #(591317, 50)

#finding rows with missing core values and dropping
core_null = (
    (listed['LivingArea'].isnull()) |
    (listed['ListPrice'].isnull()) |
    (listed['ListingKey'].isnull()) |
    (listed['MlsStatus'].isnull()) |
    (listed['DaysOnMarket'].isnull()) |
    (listed['ListingContractDate'].isnull())
)

listed = listed[~core_null]

print("after null core drop shape:", listed.shape) #(590714, 50)

#finding rows with impossible numeric values and dropping
invalid_numeric_values = (
    (listed['ClosePrice'] <= 0) |
    (listed['OriginalListPrice'] <= 0) |
    (listed['ListPrice'] <= 0) |
    (listed['LivingArea'] <= 0) |
    (listed['LotSizeAcres'] < 0) |
    (listed['LotSizeSquareFeet'] < 0) |
    (listed['DaysOnMarket'] < 0) |
    (listed['ParkingTotal'] < 0) |
    (listed['BathroomsTotalInteger'] < 0) |
    (listed['BedroomsTotal'] < 0) |
    (listed['Stories'] < 0) |
    (listed['MainLevelBedrooms'] < 0) |
    (listed['GarageSpaces'] < 0) |
    (listed['AssociationFee'] < 0)
)

listed = listed[~invalid_numeric_values]

print("after impossible numeric values drop shape:", listed.shape) #(590140, 50)

#finding all invalid longitude or latitude values and flagging them with new column in csv
invalid_geo_values = (
    (listed['Latitude'] == 0) | 
    (listed['Longitude'] == 0) |
    (listed['Longitude'] > 0) |
    (listed['Latitude'] < 32) | 
    (listed['Latitude'] > 42) |
    (listed['Longitude'] < -125) | 
    (listed['Longitude'] > -114) |
    (listed['StateOrProvince'] != "CA")
)

listed['InvalidGeoFlag'] = invalid_geo_values
invalid_geo_summary = listed[listed['InvalidGeoFlag'] == True]

print("total rows with invalid coordinates:", len(invalid_geo_summary)) #358

#finding all null longitude or latitude values and flagging them with new column in csv
null_geo_values = (
    (listed['Latitude'].isnull()) | 
    (listed['Longitude'].isnull())
)

listed['NullGeoFlag'] = null_geo_values
null_geo_summary = listed[listed['NullGeoFlag'] == True]

print("total rows with null coordinates:", len(null_geo_summary)) #80649

#finding all invalid postal code values and flagging them with new column in csv pd.to_numeric(df["prices"], errors="coerce")
invalid_postal_values = (
    (pd.to_numeric(listed['PostalCode'], errors="coerce") < 90001) | 
    (pd.to_numeric(listed['PostalCode'], errors="coerce") > 96162)
)

listed['InvalidPostalFlag'] = invalid_postal_values
invalid_postal_summary = listed[listed['InvalidPostalFlag'] == True]

print("total rows with invalid postal codes:", len(invalid_postal_summary)) #298

#finding all invalid dates or timelines and flagging them with new column in csv
invalid_dates = (
    (listed['CloseDate'] < listed['ListingContractDate']) | 
    (listed['CloseDate'] < listed['PurchaseContractDate']) |
    (listed['PurchaseContractDate'] < listed['ListingContractDate']) |
    (listed['ContractStatusChangeDate'] < listed['ListingContractDate'])
)

listed['InvalidDatesFlag'] = invalid_dates
invalid_dates_summary = listed[listed['InvalidDatesFlag'] == True]

print("total rows with invalid dates:", len(invalid_dates_summary)) #554

print("final shape:", listed.shape) #(590140, 54)

listed.to_csv('listed_cleaned.csv', index=False)

# %%
# Week 6

listed = pd.read_csv("listed_cleaned.csv", low_memory=False)

listed['CloseDate'] = pd.to_datetime(listed['CloseDate'], errors="coerce")
listed['ListingContractDate'] = pd.to_datetime(listed['ListingContractDate'], errors="coerce")
listed['PurchaseContractDate'] = pd.to_datetime(listed['PurchaseContractDate'], errors="coerce")
listed['ContractStatusChangeDate'] = pd.to_datetime(listed['ContractStatusChangeDate'], errors="coerce")

#creating new columns through feature engineering
listed['PriceRatio'] = listed['ClosePrice'] / listed['ListPrice']
listed['PricePerSqFt'] = listed['ClosePrice'] / listed['LivingArea']
listed['CloseToOrigListRatio'] = listed['ClosePrice'] / listed['OriginalListPrice']

listed['Year'] = listed['CloseDate'].dt.year
listed['Month'] = listed['CloseDate'].dt.month

listed['ListingToContractDays'] = (listed['PurchaseContractDate'] - listed['ListingContractDate']).dt.days
listed['ContractToCloseDays'] = (listed['CloseDate'] - listed['PurchaseContractDate']).dt.days

#sample output showing that the new columns are correctly populated
sample = [
    'ClosePrice', 
    'PriceRatio', 
    'LivingArea', 
    'OriginalListPrice', 
    'PurchaseContractDate', 
    'ListingContractDate', 
    'CloseDate', 
    'PricePerSqFt', 
    'CloseToOrigListRatio', 
    'DaysOnMarket', 
    'Year', 'Month', 'YrMo', 
    'ListingToContractDays', 
    'ContractToCloseDays'
]

print(listed[sample].head())

#generating statistic summaries for columns and each group within them and creating csv files
features = [
    'PriceRatio',  
    'PricePerSqFt', 
    'CloseToOrigListRatio', 
    'DaysOnMarket', 
    'Year', 'Month', 
    'ListingToContractDays', 
    'ContractToCloseDays'
]

segments = [
    'PropertySubType', 
    'CountyOrParish', 
    'MLSAreaMajor', 
    'ListOfficeName', 
    'BuyerOfficeName'
]

for seg in segments:
    summary = listed.groupby(seg)[features].agg(['count', 'mean', 'median', 'min', 'max'])
    summary.columns = [f"{feat}_{stat}" for feat, stat in summary.columns]
    summary = summary.reset_index()
    summary.to_csv((f"Summaries/listed_{seg}_summary.csv"), index=False)

listed.to_csv('listed_features.csv', index=False)

# %%
# Week 7

listed = pd.read_csv("listed_features.csv", low_memory=False)

print('original shape:', listed.shape) #(590140, 61)

#columns to filter for outliers
cols = [
    'ClosePrice', 
    'LivingArea', 
    'LotSizeSquareFeet', 
    'DaysOnMarket', 
    'ListPrice', 
    'OriginalListPrice', 
    'ListingToContractDays', 
    'ContractToCloseDays'
]

#creating new copy of csv for filtered and flagged csv
listed_clean = listed.copy()

#finding all outlier values for each column and creating new flag column for each
for col in cols:
    print(f'{col} median:', listed[col].median())
    print(f'{col} mean:', listed[col].mean())
    if col == ('DaysOnMarket', 'ListingToContractDays', 'ContractToCloseDays', 'LotSizeSquareFeet'):
        upper = listed[col].quantile(0.975)
        outliers = ((listed[col] > upper))
        listed[f'Outlier{col}Flag'] = outliers
    else:
        lower = listed[col].quantile(0.005)
        upper = listed[col].quantile(0.975)
        outliers = ((listed[col] < lower) | (listed[col] > upper))
        listed[f'Outlier{col}Flag'] = outliers

#creating filtered csv with all rows with any outlier value being removed
listed_clean = listed[
    (listed[f'OutlierClosePriceFlag'] == False) & 
    (listed[f'OutlierLivingAreaFlag'] == False) & 
    (listed[f'OutlierLotSizeSquareFeetFlag'] == False) &
    (listed[f'OutlierDaysOnMarketFlag'] == False) & 
    (listed[f'OutlierListPriceFlag'] == False) & 
    (listed[f'OutlierOriginalListPriceFlag'] == False) &
    (listed['OutlierListingToContractDaysFlag'] == False) & 
    (listed['OutlierContractToCloseDaysFlag'] == False) &
    (listed['InvalidDatesFlag'] == False) &
    (listed['InvalidGeoFlag'] == False) &
    (listed['InvalidPostalFlag'] == False)
]

#comparing cleaned csv to flagged csv
print('cleaned shape:', listed_clean.shape) #(530447, 69)
print('change in shape:', (listed_clean.shape[0] - listed.shape[0])) #59693

for col in cols:
    print(f'{col} cleaned median:', listed_clean[col].median())
    print(f'{col} change in median:', (listed_clean[col].median() - listed[col].median()))
    print(f'{col} cleaned mean:', listed_clean[col].mean())
    print(f'{col} change in mean:', (listed_clean[col].mean() - listed[col].mean()))

listed.to_csv('listed_outlier_flag.csv', index=False)
listed_clean.to_csv('listed_outlier_filtered.csv', index=False)
# %%
