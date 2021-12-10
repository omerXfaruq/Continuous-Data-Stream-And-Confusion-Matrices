from sys import argv, exit
from .main import ContinuousLearning

if __name__ == "__main__":
    if len(argv) != 3:
        exit("Please provide an input file and close_after_seconds duration!")
    input_path = argv[1]
    close_after_seconds = int(argv[2])
    ContinuousLearning(input_path=input_path, close_after_time=close_after_seconds)
    print("Closed the Continuous Learning and finished the program!")
