from cmath import nan
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt

threshold = 0.115
gap = 5

file_number = 23
df = pd.read_csv('BW_ (' + str(file_number) + ').csv')

ECG_data = list([float(x) for x in df['dataPoint']])
print(ECG_data[100])
R_peak_index = [98,243,384,456,639,763,885,1009,1134,1260,1381,1498,1610,1724,1848,1996] # this array is given by pan tompkins
is_motion_artifact = [0] * (len(R_peak_index) - 1)

# filling the gaps

for i in range(len(ECG_data)):
    if ECG_data[i] == nan:
        j = 1
        while ECG_data[i + j] == nan:
            j = j + 1
        step = (ECG_data[i + j] - ECG_data[i - 1]) / (j + 1)
        for k in range(j):
            ECG_data[i + k] = ECG_data[i -1] + step * (k + 1)
        i = i + j

m = np.mean(ECG_data)

for i in range(len(R_peak_index) - 1):
    section  = ECG_data[R_peak_index[i] + gap : R_peak_index[i+1] - gap].copy()
    v = np.var(section)**0.5    
    #print(v)    
    if v > threshold:
        is_motion_artifact[i] = 1
    else:
        is_motion_artifact[i] = 0

print(is_motion_artifact)



