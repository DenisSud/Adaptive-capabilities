import os
import json
import numpy as np
import pandas as pd

with open('results.json', encoding="utf8") as json_file:
    results = json.load(json_file)

# Specify the directory containing the combined CSV file
directory = 'pupil_data/'

# Read the combined CSV file into a dataframe
combined_df = pd.read_csv(os.path.join(directory, 'combined.csv'))

for column in combined_df.columns:

    if any(column in d['name'] for d in results):
        print("уже посчитан(a): " + column)
        continue
    # Get the data array from the column
    data_array = combined_df[column]

    file_name = column.split('/')[-1]

    # Ask user for 4 values
    val1, val3 = input(f'\nPlease enter the values for the file: {column}: ').split()
    val1 = int(val1)
    val3 = int(val3)
    val2 = val1 + 50
    val4 = val3 + 50
    print(f"{val1} {val2} {val3} {val4}")

    # print(f'\nThe values for the person: {column}: are:\n\t{val1}\n\t{val2}\n{val3}\n\t{val4}')

    # Calculate 3 averages
    end = len(data_array)
    # TODO find the end of the data array (find when NaN values appear) then 

    print(data_array[:val1])
    print((data_array[val2:val3]))
    print(data_array[val4:])
    avg1 = int((data_array[:val1]).sum()/len(data_array[:val1]))
    avg2 = int((data_array[val2:val3]).sum()/len(data_array[val2:val3]))
    avg3 = int((data_array[val4:end]).sum()/len(data_array[val4:]))

    d1 = avg2 - avg1
    if avg1 >= avg3:
        d2 = avg1 - avg3
    else:
        d2 = avg3 - avg1

    speed1 = (sum(data_array[val2:val2+5])- sum(data_array[val1:val1+5]))/(val2-val1) 
    speed2 = (sum(data_array[val3:val3+5])- sum(data_array[val4:val4+5]))/(val4-val3)

    result = {
        'name': file_name,
        'averages': [avg1, avg2, avg3],
        'differences': [d1, d2],
        'speeds': [speed1, speed2]
    }

    results.append(result)

    output_file = 'results.json'
    with open(output_file, 'w', encoding="utf8") as json_file:
        json.dump(results, json_file, indent=4, ensure_ascii=False)


# # Save results to a JSON file
# output_file = 'results.json'
# with open(output_file, 'w') as json_file:
#    json.dump(results, json_file, indent=4)

print(results)

print('Results saved to', output_file)
