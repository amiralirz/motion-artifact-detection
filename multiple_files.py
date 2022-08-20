import os
from MotionArtifactDetector import *

files_directory = "C:\hmmmmmmmm\Work\Python\\benchmark\Data"
output_directory = "C:\hmmmmmmmm\Work\Python\\benchmark"
no_files = len(os.listdir(files_directory))
# no_files = 1

threshold = 55
gap = 10
margin = 4

for i in range(no_files):
    file_name = os.listdir(files_directory + "/" + str(i+1))[0][:6]
    directory = files_directory + "\\" + str(i+1) + "\\" + file_name
    detector = MotionArtifactDetector(directory)
    ann = detector.annotate(threshold, gap, margin)
    ann.wrann(True, files_directory + f"\\{str(i+1)}")
    print(file_name)



