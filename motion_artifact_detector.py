from cmath import nan
import pandas as pd
import math
import numpy as np
from Pan_Tompkins_QRS import *
from Data_cleaner import *
import matplotlib.pyplot as plt

threshold = 40
gap = 10
fs = 200

file_number = 17
df = pd.read_csv('BW_ (' + str(file_number) + ').csv')  # reading the CSV file

ECG_data = list([float(x) for x in df['dataPoint']])  #

ECG_data = clean_up(ECG_data)  # cleaning the gaps in the data using extrapolation

for i in range(len(ECG_data)):
    ECG_data[i] = math.floor(ECG_data[i] * 400)  # converting the data to io int type with minimum loss

QRS_detector = Pan_Tompkins_QRS()
# converting the datatype to pandas dataframe
input_signal = pd.DataFrame(np.array([list(range(len(ECG_data))), ECG_data]).T, columns=['TimeStamp', 'ecg'])

output_signal = QRS_detector.solve(input_signal)  # this output is not used
signal = np.array(ECG_data)  # converting to numpy array
hr = heart_rate(signal, fs)  # this class has a method for peak detection
result = hr.find_r_peaks()  # finding the index of R peaks
result = np.array(result)  # converting the output to a numpy array
result = result[result > 0]  # cleaning up the training data
R_peak_index = result.copy()

is_motion_artifact = [0] * (len(R_peak_index) - 1)  # this is the primary output of the code
fig = [0] * len(ECG_data)  # this array is only used for presentation

for i in range(len(R_peak_index) - 1):
    section = ECG_data[R_peak_index[i] + gap: R_peak_index[i + 1] - gap].copy()  # dividing the data into sections
    v = np.var(section) ** 0.5  # calculating the standard deviation of each section
    fig[R_peak_index[i] + gap: R_peak_index[i + 1] - gap] = [v * 10] * len(section)  # this is only for presentation
    if v > threshold:
        is_motion_artifact[i] = 1
    else:
        is_motion_artifact[i] = 0

print(is_motion_artifact)  # main output of the code

plt.figure(figsize=(18, 8), dpi=100)
plt.plot(ECG_data)
plt.plot(fig)
plt.scatter(result, signal[result], color='red', s=50,  marker='*')
plt.title('file no.' + str(file_number))
plt.xlabel('samples')
plt.show()


