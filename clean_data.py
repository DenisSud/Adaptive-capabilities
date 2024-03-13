import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

# def remove_first_column_from_all_csv_files(directory):
#     try:
#         # Get a list of all CSV files in the directory
#         csv_files = glob.glob(os.path.join(directory, '*.csv'))
        
#         # Loop over each CSV file
#         for csv_file in csv_files:
#             # Read the csv file into a DataFrame
#             df = pd.read_csv(csv_file)
            
#             # Check if there's more than one column in the DataFrame
#             if df.shape[1] > 1:
#                 # Remove the first column
#                 df = df.iloc[:, 1:df.shape[1]]
                
#                 # Write the modified DataFrame back to the csv file
#                 df.to_csv(csv_file, index=False)
#             else:
#                 print(f"Cannot remove the first column as there is only one column in the CSV file: {csv_file}")
        
#     except Exception as e:
#         print(f"An error occurred while trying to process the CSV files in the directory: {str(e)}")

# Usage
# remove_first_column_from_all_csv_files('pupil_data')

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


# Combine all dataframes into a single dataframe
combined_df = pd.concat(dataframes, axis=1)
# Iterate over the columns in the combined dataframe
for column in combined_df.columns:
    # Create a figure with a custom size
    plt.figure(figsize=(100, 10))

    # Plot the data from the current column
    combined_df[column].plot()

    # Save the figure as a PNG file with the column name as the filename
    plt.savefig(f'{column}.png', dpi=60)

    # Show the figure
    # plt.show()

