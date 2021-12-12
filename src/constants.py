from enum import IntEnum, Enum


class LabelConstant:
    class Label(IntEnum):
        A = 0
        B = 1

    @staticmethod
    def map_labels_to_int(label: str) -> int:
        if label == "A":
            return LabelConstant.Label.A
        elif label == "B":
            return LabelConstant.Label.B
        else:
            return -1


class ModelConstant:
    WEIGHTS = [0.5, 0.6, 0.7]
