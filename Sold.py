# %%

import pandas as pd
import glob
import matplotlib.pyplot as plt

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

sold["CloseDate"] = pd.to_datetime(sold["CloseDate"], errors="coerce")
sold["ListingContractDate"] = pd.to_datetime(sold["ListingContractDate"], errors="coerce")
sold["PurchaseContractDate"] = pd.to_datetime(sold["PurchaseContractDate"], errors="coerce")

null_sold = sold.isnull().sum()
pct_sold = (null_sold / len(sold)) * 100

sold_report = pd.DataFrame({'total null': null_sold, 'perecnt null': pct_sold})

high_null_sold = sold_report[sold_report['perecnt null'] > 90]

print("possible sold columns to drop:\n", high_null_sold)

save_list = ['WaterfrontYN', 'BasementYN']
single_val_sold = [col for col in sold.columns if (sold[col].nunique() <= 1) & (col not in save_list)]

print("single val drops:\n", single_val_sold)

drop_sold = [col for col in high_null_sold.index.tolist() if col not in save_list]
drop_sold = list(set(drop_sold + single_val_sold))

print("listed columns to drop:\n", drop_sold)
print("before drop shape:", sold.shape)

sold = sold.drop(columns=drop_sold)

print("after drop shape:", sold.shape)

sold = sold.drop(list(sold.filter(regex='.1$')), axis=1)
sold = sold.drop_duplicates(subset="ListingKey", keep="last")

print("after duplicate drop shape:", sold.shape)

sold = sold[sold['CloseDate'] >= sold['ListingContractDate']]
sold = sold[sold['CloseDate'] >= sold['PurchaseContractDate']]
sold = sold[sold['PurchaseContractDate'] >= sold['ListingContractDate']]

print("after date drop shape:", sold.shape)

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

for col in cols:
    if col in sold.columns:
        plt.figure(figsize = (10,6))
        sold[col].hist(bins = 50)
        plt.title(f"Sold Distribution of {col}")
        plt.xlabel(col)
        plt.ylabel("Frequency")
        plt.savefig(f"Plots/sold_histogram/sold_{col}_histogram.png")
        plt.show()
        plt.close()

        plt.figure(figsize = (10,6))
        sold.boxplot(column = col)
        plt.title(f"Sold Boxplot of {col}")
        plt.savefig(f"Plots/sold_boxplot/sold_{col}_boxplot.png")
        plt.show()
        plt.close()

sold.to_csv('sold_eda.csv', index=False)

# %%
# Week 3

sold = pd.read_csv("sold_eda.csv", low_memory=False)

sold["CloseDate"] = pd.to_datetime(sold["CloseDate"], errors="coerce")
sold["ListingContractDate"] = pd.to_datetime(sold["ListingContractDate"], errors="coerce")
sold["PurchaseContractDate"] = pd.to_datetime(sold["PurchaseContractDate"], errors="coerce")

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
