import json
import pandas as pd

with open('results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create a DataFrame from the list of dicts
df = pd.DataFrame(data)

# Save the DataFrame to a csv file
df.to_csv('people_info.csv', index=False) 