import math
import numpy as np

def clean_up(input_signal):
    l = len(input_signal)  # length of the signal
    m = np.mean(input_signal)
    for i in range(len(input_signal)):
        if input_signal[i] < m / 2:
            input_signal[i] = m

    output_signal = input_signal.copy()
    for i in range(l):
        if math.isnan(output_signal[i]):  # checking if the input is nan
            j = 1
            while i + j < l:
                if math.isnan(output_signal[i + j]):
                    j = j + 1
                else:
                    break
            step = 0
            if i + j == l:
                step = output_signal[i - 1] - output_signal[i - 2]  # fixing the end of the signal
            elif i == 0:
                step = output_signal[i + j + 1] - output_signal[i + j]  # fixing the start of the signal
            elif i == 0 and i + j == l:
                return -1  # the whole signal is nan
            else:
                step = (output_signal[i + j] - output_signal[i - 1]) / (j + 1)  # fixing the middle of the signal
            for k in range(j):
                output_signal[i + k] = int(round(output_signal[i - 1] + step * (k + 1), 0))  # rounding to the closest integer
    return output_signal
