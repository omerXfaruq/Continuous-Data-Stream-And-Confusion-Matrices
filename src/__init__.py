from sys import argv, exit
from .main import ContinuousLearning
from .db import get_confusion_matrix_count, get_entry_count

__all__ = [
    "ContinuousLearning",
]

if __name__ == "__main__":
    if len(argv) != 5:
        exit(
            "Please provide run as:\npython3 -m src.__init__ [input] [close_after_seconds] [debug]"
        )

    input_path = argv[1]
    close_after_countdown = int(argv[2])
    confusion_matrix_length = int(argv[3])
    debug = "True" == argv[4]

    ContinuousLearning(
        input_path=input_path,
        close_after_countdown=close_after_countdown,
        confusion_matrix_length=confusion_matrix_length,
        debug=debug,
    )

    if debug:
        print("Entry Count:")
        print(get_entry_count())
        print("Confusion Matrices:")
        print(get_confusion_matrix_count())

    print("Closed the Continuous Learning and finished the program!")
