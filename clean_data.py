import os
import glob
import pandas as pd
# Specify the directory containing the CSV files
directory = 'pupil_data/'

# Get a list of all CSV files in the directory
csv_files = glob.glob(os.path.join(directory, '*.csv'))

# Create an empty list to store the dataframes
dataframes = []

# Iterate through each CSV file
for csv_file in csv_files:
    # Get the filename without the extension
    filename = os.path.splitext(os.path.basename(csv_file))[0]

    # Read the CSV file into a dataframe
    df = pd.read_csv(csv_file, header=None)

    # Rename the column to the filename
    df.columns = [filename]

    # Append the dataframe to the list
    dataframes.append(df)

combined_df = pd.concat(dataframes, axis=1)
# Write the combined dataframe to a new CSV file
combined_df.to_csv('combined.csv', index=False)
