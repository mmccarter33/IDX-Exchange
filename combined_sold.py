import pandas as pd
import glob

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
