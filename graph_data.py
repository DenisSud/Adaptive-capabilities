import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define path for input and output folders
input_folder = './pupil_data/new_data'
output_folder = './pupil_data/new_plots'

# Function to extract filename without extension from a given filepath
def get_filename(filepath):
    return os.path.splitext(os.path.basename(filepath))[0]

# List all CSV files in the input folder
csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]

# Initialize plot counter and figure size
plot_counter = 1
figsize = (8, 6)

# Create output folder if it does not exist already
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for file in csv_files:
    # Load data from CSV file using Pandas
    df = pd.read_csv(os.path.join(input_folder, file))

    # Create scatter plot using Seaborn's `scatterplot()` function
    sns.lineplot(x=df.iloc[:, 0], y=df.iloc[:, 1])
    # Add a title to the plot
    plt.title(f"{get_filename(file)} Plot")
    plt.gca().set_aspect(0.5)
    # Save the figure using `savefig()`
    plt.savefig(os.path.join(output_folder, get_filename(file) + '.png'), dpi=300)

    # Clear the plot for the next iteration
    plt.clf()

print('All plots have been saved successfully!')
