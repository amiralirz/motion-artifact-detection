import pandas as pd
import wfdb
from Pan_Tompkins_QRS import *
from Data_cleaner import *
import bisect
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True, help="input file directory")
parser.add_argument("-o", "--output", required=False, help="output file directory. default is the input file directory")
parser.add_argument("-t", "--threshold", required=False, help="Threshold used for Artifact detection. default is 62. normal range is (40 90)")
parser.add_argument("-g", "--gap", required=False, help="The number of samples ignored around R peaks. default is (fs * 0.2). normal range is (10 100)")
args = vars(parser.parse_args())

input_directory = args["input"]
output_directory = args["output"] or input_directory[:input_directory.rfind("\\")]
file_name = input_directory[input_directory.rfind("\\") + 1:]

output_directory = args["output"] or output_directory
threshold = int(args["threshold"] or '62')

record = wfdb.rdrecord(input_directory)
ECG_data = record.p_signal[:, 0]

fs = record.fs
gap = int(str(int(2 / 10 * fs)) or args["gap"])

ECG_data = clean_up(ECG_data)  # cleaning the gaps in the data using extrapolation
data_length = len(ECG_data)

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

ann_sample = R_peak_index.copy().tolist()
ann_symbol = ["N"] * len(R_peak_index)
ann_subtype = [0] * len(R_peak_index)

is_motion_artifact = [0] * (len(R_peak_index) - 1)  # this is the primary output of the code

for i in range(len(R_peak_index) - 1):
    if R_peak_index[i] != R_peak_index[i + 1]:
        section = ECG_data[R_peak_index[i] + gap: R_peak_index[i + 1] - gap].copy()  # dividing the data into sections
        if len(section) == 0:
            continue
        v = np.var(section) ** 0.5  # calculating the standard deviation of each section
        if v > threshold:
            is_motion_artifact[i] = 1
        else:
            is_motion_artifact[i] = 0

noise_episode_start_index = 0
noise_episode_end_index = 0
noise_episode_started = False
noise_episode_margin = 5
noise_episode_margin_counter = noise_episode_margin
noise_episode_starts = []
noise_episode_ends = []
noise_episodes = 0

for i in range(len(is_motion_artifact)):  # finding and storing the index of noise episodes
    if is_motion_artifact[i] == 1:
        noise_episode_margin_counter = noise_episode_margin
        if not noise_episode_started:
            noise_episode_started = True
            noise_episode_start_index = max(0, R_peak_index[max(0, i - noise_episode_margin_counter)] - gap)
            if i < noise_episode_margin:
                noise_episode_start_index = 0
    else:
        if noise_episode_started:
            noise_episode_margin_counter -= 1
            if noise_episode_margin_counter == 0:
                noise_episode_margin_counter = noise_episode_margin
                noise_episode_started = False
                last_index = len(R_peak_index) - 1
                noise_episode_end_index = min(R_peak_index[min(i + 1, last_index)] + gap, data_length - 1)
                noise_episode_ends.append(noise_episode_end_index)
                noise_episode_starts.append(noise_episode_start_index)
                noise_episodes += 1
    if i == len(is_motion_artifact) - 1 and noise_episode_started:
        noise_episode_end_index = data_length - 1
        noise_episode_ends.append(noise_episode_end_index)
        noise_episode_starts.append(noise_episode_start_index)
        noise_episodes += 1

if noise_episodes > 1:
    i = 0
    while i < noise_episodes:  # merging noise episodes that overlap
        if i > 0:
            if noise_episode_starts[i] < noise_episode_ends[i - 1]:
                noise_episode_starts.remove(noise_episode_starts[i])
                noise_episode_ends.remove(noise_episode_ends[i - 1])
                noise_episodes -= 1
        i += 1

for i in range(noise_episodes):  # adding the episodes to tha annotation file

    bisect.insort(ann_sample, noise_episode_starts[i])  # adding the start index
    insertion_index = ann_sample.index(noise_episode_starts[i])
    ann_symbol.insert(insertion_index, '~')
    ann_subtype.insert(insertion_index, 1)

    bisect.insort(ann_sample, noise_episode_ends[i])  # adding the end index
    insertion_index = ann_sample.index(noise_episode_ends[i])
    ann_symbol.insert(insertion_index, '~')
    ann_subtype.insert(insertion_index, 0)

wfdb.wrann(file_name, 'atr', np.array(ann_sample), ann_symbol, np.array(ann_subtype), np.array([0] * len(ann_sample)),
           np.array([0] * len(ann_sample)),
           [''] * len(ann_sample), fs=record.fs,
           write_dir=output_directory)
