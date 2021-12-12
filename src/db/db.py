from typing import List, Union
from sqlmodel import Session, SQLModel, create_engine, select
from .models import (
    Entry,
    create_entry_from_array,
    ConfusionMatrix,
    create_confusion_matrix_from_array,
)

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def create_entry(
    entry: Entry,
    session: Session = next(get_session()),
) -> Entry:
    try:
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return entry

    except Exception as ex:
        raise ex


def create_entry_list_coming_from_csv(
    entry_list: List[List[Union[int, str]]],
    session: Session = next(get_session()),
) -> None:
    try:
        for array in entry_list:
            entry = create_entry_from_array(array)
            session.add(entry)
        session.commit()

    except Exception as ex:
        raise ex


def get_entry_by_id(
    id: int,
    session: Session = next(get_session()),
) -> Entry:
    selected_item = session.exec(select(Entry).where(Entry.id == id)).first()
    return selected_item


def get_all_entries(
    start_index: int = 1,
    end_index: int = 1000,
    session: Session = next(get_session()),
) -> List[Entry]:
    try:
        offset = max(0, start_index - 1)
        number_of_elements = end_index - start_index + 1
        entries = session.exec(
            select(Entry).offset(offset).limit(number_of_elements)
        ).all()
    except Exception as ex:
        raise ex
    return entries


def get_entry_count(session: Session = next(get_session())) -> int:
    try:
        entry_count = session.query(Entry).count()

    except Exception as ex:
        raise ex
    return entry_count


def delete_entry_by_id(
    id: int,
    session: Session = next(get_session()),
) -> None:
    try:
        entry = session.get(Entry, id)
        if entry is not None:
            session.delete(entry)
            session.commit()
    except Exception as ex:
        raise ex


def write_confusion_matrix_to_db(
    confusion_matrices: List[ConfusionMatrix],
    session: Session = next(get_session()),
) -> None:
    try:
        for confusion_matrix in confusion_matrices:
            session.add(confusion_matrix)
        session.commit()

    except Exception as ex:
        raise ex


def get_confusion_matrices(
    start_index: int = 1,
    end_index: int = 1000,
    session: Session = next(get_session()),
) -> List[ConfusionMatrix]:
    try:
        offset = max(0, start_index - 1)
        number_of_elements = end_index - start_index + 1
        matrices = session.exec(
            select(ConfusionMatrix).offset(offset).limit(number_of_elements)
        ).all()
        return matrices
    except Exception as ex:
        raise ex


def get_confusion_matrix_count(session: Session = next(get_session())) -> int:
    try:
        confusion_matrix_count = session.query(ConfusionMatrix).count()
        return confusion_matrix_count

    except Exception as ex:
        raise ex
