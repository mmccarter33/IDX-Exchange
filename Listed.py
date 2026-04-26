# %%
import pandas as pd
import glob
import matplotlib.pyplot as plt

# %%
# Week 1

files = glob.glob('raw/CRMLSListing*.csv')
data = []
count1 = 0

for f in files:
    file = pd.read_csv(f)
    count1 += len(file)
    data.append(file)
combined_listed = pd.concat(data, ignore_index=True)
print(count1)
##Before concat count = 852963

count2 = len(combined_listed)
print(count2)
##After concat count = 852963

combined_listed = combined_listed[combined_listed['PropertyType'] == 'Residential']

count3 = len(combined_listed)
print(count3)
##After filter count = 540183

combined_listed.to_csv('listed.csv', index=False)

# %%
# Week 2

listed = pd.read_csv("listed.csv", low_memory=False)

listed["ListingContractDate"] = pd.to_datetime(listed["ListingContractDate"], errors="coerce")
listed["ContractStatusChangeDate"] = pd.to_datetime(listed["ContractStatusChangeDate"], errors="coerce")

null_listed = listed.isnull().sum()
pct_listed = (null_listed / len(listed)) * 100

listing_report = pd.DataFrame({'total null': null_listed, 'perecnt null': pct_listed})
high_null_listing = listing_report[listing_report['perecnt null'] > 90]

print("possible listed columns to drop:\n", high_null_listing)

single_val_listed = [col for col in listed.columns if (listed[col].nunique() <= 1)]

print("single val drops:\n", single_val_listed)

drop_listed = high_null_listing.index.tolist()
drop_listed = list(set(drop_listed + single_val_listed))

print("listed columns to drop:\n", drop_listed)
print("before drop shape:", listed.shape)

listed = listed.drop(columns=drop_listed)

print("after drop shape:", listed.shape)

listed = listed.drop(list(listed.filter(regex='.1$')), axis=1)
listed = listed.drop_duplicates(subset="ListingKey", keep="last")

print("after duplicate drop shape:", listed.shape)

listed = listed[listed['ContractStatusChangeDate'] >= listed['ListingContractDate']]

print("after date drop shape:", listed.shape)

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
        listed[col].hist(bins = 50)
        plt.title(f"Listed Distribution of {col}")
        plt.xlabel(col)
        plt.ylabel("Frequency")
        plt.savefig(f"Plots/listed_histogram/listed_{col}_histogram.png")
        plt.show()
        plt.close()

        plt.figure(figsize = (10,6))
        listed.boxplot(column = col)
        plt.title(f"Listed Boxplot of {col}")
        plt.savefig(f"Plots/listed_boxplot/listed_{col}_boxplot.png")
        plt.show()
        plt.close()

listed.to_csv('listed_eda.csv', index=False)

# %%
# Week 3

listed = pd.read_csv("listed_eda.csv", low_memory=False)

listed["ListingContractDate"] = pd.to_datetime(listed["ListingContractDate"], errors="coerce")
listed["ContractStatusChangeDate"] = pd.to_datetime(listed["ContractStatusChangeDate"], errors="coerce")

# Fetch the mortgage rate data from FRED import pandas as pd
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US" 
mortgage = pd.read_csv(url, parse_dates=['observation_date']) 
mortgage.columns = ['date', 'rate_30yr_fixed']

# Resample weekly rates to monthly averages 
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (mortgage.groupby('year_month')['rate_30yr_fixed'].mean().reset_index())

# Create a matching year_month key on the MLS datasets and merge
listed['year_month'] = listed['ListingContractDate'].dt.to_period('M')
listed = listed.merge(mortgage_monthly, on='year_month', how='left')

# Validate the merge
print(listed['rate_30yr_fixed'].isnull().sum())
print(listed[['ListingContractDate', 'year_month', 'ListPrice', 'rate_30yr_fixed']].head())

listed.to_csv('listed_mortgage.csv', index=False)

# %%
