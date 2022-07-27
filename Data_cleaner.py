import math
from cmath import nan


def clean_up(input_signal):
    l = len(input_signal)  # length of the signal
    output_signal = input_signal.copy()
    for i in range(l):
        if math.isnan(output_signal[i]):
            j = 1
            while i + j < l:
                if math.isnan(output_signal[i + j]):
                    j = j + 1
                else:
                    break
            step = 0
            if i + j == l:
                step = output_signal[i - 1] - output_signal[i - 2]
            elif i == 0:
                step = output_signal[i + j + 1] - output_signal[i + j]
            elif i == 0 and i + j == l:
                return -1
            else:
                step = (output_signal[i + j] - output_signal[i - 1]) / (j + 1)
            for k in range(j):
                output_signal[i + k] = int(round(output_signal[i - 1] + step * (k + 1), 0))  # rounding to the closest integer
    return output_signal
