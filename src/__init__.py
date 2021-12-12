from sys import argv, exit
from .main import ContinuousLearning

__all__ = [
    "ContinuousLearning",
]

if __name__ == "__main__":
    if len(argv) != 3:
        exit("Please provide an input file and close_after_seconds duration!")

    input_path = argv[1]
    close_after_seconds = int(argv[2])

    ContinuousLearning(
        input_path=input_path,
        close_after_countdown=close_after_seconds,
        confusion_matrix_length=3,
        debug=True,
    )

    from .db import get_confusion_matrices, get_all_entries

    print("Entries:")
    print(get_all_entries())
    print("Confusion Matrices:")
    print(get_confusion_matrices())
    print("Closed the Continuous Learning and finished the program!")
