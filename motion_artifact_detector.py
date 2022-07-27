from cmath import nan
import pandas as pd
import math
import numpy as np
from Pan_Tompkins_QRS import *
import matplotlib.pyplot as plt

threshold = 15
gap = 5
fs = 200

file_number = 19
df = pd.read_csv('BW_ (' + str(file_number) + ').csv')

ECG_data = list([float(x) for x in df['dataPoint']])
for i in range(len(ECG_data)):
    ECG_data[i] = math.floor(ECG_data[i] * 400)

QRS_detector = Pan_Tompkins_QRS()
input_signal = pd.DataFrame(np.array([list(range(len(ECG_data))), ECG_data]).T, columns=['TimeStamp', 'ecg'])
output_signal = QRS_detector.solve(input_signal)

signal = np.array(ECG_data)
hr = heart_rate(signal, fs)
result = hr.find_r_peaks()
result = np.array(result)
result = result[result > 0]

print(result)

R_peak_index = result.copy()
is_motion_artifact = [0] * (len(R_peak_index) - 1)

for i in range(len(R_peak_index) - 1):
    section = ECG_data[R_peak_index[i] + gap: R_peak_index[i + 1] - gap].copy()
    v = np.var(section) ** 0.5
    if v > threshold:
        is_motion_artifact[i] = 1
    else:
        is_motion_artifact[i] = 0

print(is_motion_artifact)


