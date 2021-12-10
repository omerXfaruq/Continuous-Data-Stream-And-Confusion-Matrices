from sqlmodel import SQLModel, Field
from typing import Optional
from src.constants import LabelConstant


class Entry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    given_label: int
    model1_A: float
    model1_B: float
    model2_A: float
    model2_B: float
    model3_A: float
    model3_B: float


def map_labels_to_int(label: str) -> int:
    if label == "A":
        return LabelConstant.Label.A
    elif label == "B":
        return LabelConstant.Label.B
    else:
        return -1


def create_entry_from_array(array) -> Entry:
    return Entry(
        given_label=map_labels_to_int(array[1]),
        model1_A=array[2],
        model1_B=array[3],
        model2_A=array[4],
        model2_B=array[5],
        model3_A=array[6],
        model3_B=array[7],
    )
