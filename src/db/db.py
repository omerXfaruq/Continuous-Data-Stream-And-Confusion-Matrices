from typing import List
from sqlmodel import Session, SQLModel, create_engine, select
from .models import Entry, create_entry_from_array

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


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
    except Exception as ex:
        raise ex
    return entry


def create_entry_list_coming_from_csv(
    entry_list: "numpy.ndarray",
    session: Session = next(get_session()),
) -> None:
    for array in entry_list:
        entry = create_entry_from_array(array)
        create_entry(entry, session)


def get_entry_by_id(
    id: int,
    session: Session = next(get_session()),
) -> Entry:
    selected_item = session.exec(select(Entry).where(Entry.id == id)).first()
    return selected_item


def get_all_entries(session: Session = next(get_session())) -> List[Entry]:
    try:
        entries = session.exec(select(Entry)).all()
    except Exception as ex:
        raise ex
    return entries


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
