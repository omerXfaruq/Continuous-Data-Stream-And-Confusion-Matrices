import time
from copy import deepcopy

pytest_plugins = ("pytest_asyncio",)

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.db.csv import read_csv_by_chunks
from src.db.db import (
    create_db_and_tables,
    create_entry,
    get_all_entries,
    delete_entry_by_id,
)
from src.db.models import create_entry_from_array


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


class TestDb:
    def test_with_realdb(self):
        return
        # Run this function only in this scope. It is intented to do testing without mocked db. Currently it is closed.
        create_db_and_tables()

        entry = create_entry_from_array([1, "2", 3, 4, 5, 6, 7, 8])
        delete_entry_by_id(1)
        created_entry = create_entry(deepcopy(entry))
        entries = get_all_entries()
        assert entries[0] == created_entry
        entry.id = 1
        assert entries[0] == entry

    @pytest.mark.asyncio
    async def test_read_csv_by_chunks(self):
        current_time = time.time()
        data_input = "test/data/data.csv"
        await read_csv_by_chunks(
            data_input, 0.1, chunk_size=10000, debug=True, write_to_db=False
        )
        time_difference = time.time() - current_time
        assert time_difference >= 1

    @pytest.mark.asyncio
    async def test_read_csv_by_chunks_and_write(self, session):
        data_input = "test/data/data_small.csv"
        await read_csv_by_chunks(
            data_input, 0.1, chunk_size=10000, debug=True, session=session
        )
        entries = get_all_entries(session)
        assert len(entries) == 9

    def test_read_entries(self, session: Session):
        entry = create_entry_from_array([1, "2", 3, 4, 5, 6, 7, 8])
        session.add(deepcopy(entry))
        session.add(deepcopy(entry))
        session.commit()
        entries = get_all_entries(session)

        entry.id = 1
        assert entry == entries[0]
        entry.id = 2
        assert entry == entries[1]
        print(entries)


def test_temp(session: Session):
    pass
