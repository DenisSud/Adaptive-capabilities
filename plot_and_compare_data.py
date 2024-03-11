import os
import csv
import matplotlib.pyplot as plt
import seaborn as sns

data_folder = 'pupil_data'

plt.figure()
ax = plt.gca()

for filename in os.listdir(data_folder):
    if filename.endswith('.csv'):
        print(f'Reading {filename}')
        
        with open(os.path.join(data_folder, filename)) as f:
            reader = csv.reader(f)
            next(reader) # skip header
            
            x = []
            y = []
            for row in reader:
                x.append(int(row[0])) 
                y.append(float(row[1]))
                
        sns.lineplot(x=x, y=y, label=filename, ax=ax)
        
ax.set_xlabel('Frame Number')
ax.set_ylabel('Radius (pixels)')
ax.legend()
plt.title('Radius Over Time')
plt.tight_layout()
plt.show()
