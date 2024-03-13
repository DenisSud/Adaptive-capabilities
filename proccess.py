import os
import csv
import json
import numpy as np

data_folder = 'pupil_data/'
results = []

for filename in os.listdir(data_folder):
    if filename.endswith('.csv'):
        file_path = data_folder + filename

        # Read CSV into DataFrame
        data = []
        with open(file_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                data.append(float(row[0]))

        # print(data)
        
        # Ask user for 4 values
        val1, val3 = input(f'\nPlease enter the values for the file: {file_path}: ').split()
        val1 = int(val1)
        val3 = int(val3)
        val2 = val1 + 50
        val4 = val3 + 50
    
        # Get data array
        data_array = np.array(data)
        
        # Calculate 3 averages
        avg1 = (np.average(data_array[:val1])).round()
        avg2 = (np.average(data_array[val2:val3])).round() 
        avg3 = (np.average(data_array[val4:]).round())

        d1 = avg2 - avg1
        if avg1 >= avg3:
            d2 = avg1 - avg3
        else:
            d2 = avg3 - avg1

        speed1 = (data_array[val2]- data_array[val1])/(val2-val1) 
        speed2 = (data_array[val3]- data_array[val4])/(val4-val3)
        
        # print('Averages:')
        # print(avg1)
        # print(avg2)
        # print(avg3)

        # print('Differences:')
        # print(d1)
        # print(d2)

        # print('Speeds:')
        # print(speed1)
        # print(speed2)

        result = {
            'file_path': file_path,
            'averages': [avg1, avg2, avg3],
            'differences': [d1, d2],
            'speeds': [speed1, speed2]
        }

        results.append(result)

# Save results to a JSON file
output_file = 'results.json'
with open(output_file, 'w') as json_file:
    json.dump(results, json_file, indent=4)

print('Results saved to', output_file)