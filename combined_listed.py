import pandas as pd
import glob

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