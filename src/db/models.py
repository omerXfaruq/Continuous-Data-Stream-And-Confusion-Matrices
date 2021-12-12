from sqlmodel import SQLModel, Field
from typing import Optional, List, Union
from src.constants import LabelConstant, ModelConstant


class Entry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    given_label: int
    predicted_label: int
    model1_A: float
    model1_B: float
    model2_A: float
    model2_B: float
    model3_A: float
    model3_B: float


def calculate_label(model_1: float, model_2: float, model_3: float) -> int:
    """
    Calculates the label according to the combination of ML models probability of being A outputs.

    Args:
        model_1:
        model_2:
        model_3:

    Returns: label(0: A, 1: B)
    """
    weighted_average = (
        model_1 * ModelConstant.WEIGHTS[0]
        + model_2 * ModelConstant.WEIGHTS[1]
        + model_3 * ModelConstant.WEIGHTS[2]
    )
    total_sum = (
        ModelConstant.WEIGHTS[0] + ModelConstant.WEIGHTS[1] + ModelConstant.WEIGHTS[2]
    )
    if weighted_average > total_sum / 2:
        return LabelConstant.Label.A
    else:
        return LabelConstant.Label.B


def create_entry_from_array(array: List[Union[int, str]]) -> Entry:
    return Entry(
        given_label=LabelConstant.map_labels_to_int(array[1]),
        predicted_label=calculate_label(array[2], array[4], array[6]),
        model1_A=array[2],
        model1_B=array[3],
        model2_A=array[4],
        model2_B=array[5],
        model3_A=array[6],
        model3_B=array[7],
    )


class ConfusionMatrix(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Actual _ Predicted
    A_A: int
    A_B: int
    B_A: int
    B_B: int
    start_index: int
    end_index: int


def create_confusion_matrix_from_array(
    array: List[List[int]], start_index: int, end_index: int
) -> ConfusionMatrix:
    return ConfusionMatrix(
        A_A=array[LabelConstant.Label.A][LabelConstant.Label.A],
        A_B=array[LabelConstant.Label.A][LabelConstant.Label.B],
        B_A=array[LabelConstant.Label.B][LabelConstant.Label.A],
        B_B=array[LabelConstant.Label.B][LabelConstant.Label.B],
        start_index=start_index,
        end_index=end_index,
    )
