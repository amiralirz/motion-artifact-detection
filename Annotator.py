import argparse
from MotionArtifactDetector import *

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True, help="input file directory")
parser.add_argument("-o", "--output", required=False, help="output file directory. the default is the input file "
                                                           "directory")
parser.add_argument("-t", "--threshold", required=False,
                    help="Threshold used for Artifact detection. default is 62 and the normal range is (40 90)")
parser.add_argument("-g", "--gap", required=False,
                    help="The number of samples ignored around R peaks. default is (fs * 0.2) and the normal range is ("
                         "10 100)")
parser.add_argument("-m", "--margin", required=False, help="the number of R peaks before and after an artifact that "
                                                           "will be included in the episodes. default is 5 and the "
                                                           "normal range is (1 7)")
args = vars(parser.parse_args())

input_directory = args["input"]
output_directory = args["output"] or input_directory[:input_directory.rfind("\\")]
file_name = input_directory[input_directory.rfind("\\") + 1:]
g = int(str(30) or args["gap"])
output_directory = args["output"] or output_directory
t = int(args["threshold"] or '62')
m = int(args["margin"] or '5')

detector = MotionArtifactDetector(input_directory)
ann = detector.annotate(t, g, m)
ann.wrann(True, output_directory)

