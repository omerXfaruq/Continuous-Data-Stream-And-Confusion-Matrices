import time
from copy import deepcopy

import pytest

from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.constants import LabelConstant
from src.db import (
    create_entry_from_array,
    create_db_and_tables,
    create_entry,
    get_all_entries,
    get_entry_count,
    delete_entry_by_id,
    get_confusion_matrices,
    create_entry_list_coming_from_csv,
)
from src.main import ContinuousLearning

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


class MockData:
    entry_array_A_A = create_entry_from_array(
        [
            1,
            "A",
            0.6315429094436551,
            0.3684570905563449,
            0.9881789935400176,
            0.011821006459982408,
            0.7254980531654877,
            0.27450194683451234,
        ]
    )
    entry_array_A_B = create_entry_from_array(
        [
            1,
            "A",
            0.1315429094436551,
            0.8684570905563449,
            0.1881789935400176,
            0.811821006459982408,
            0.1254980531654877,
            0.87450194683451234,
        ]
    )


class TestUnit:
    class TestDb:
        def test_with_realdb(self):
            return
            # Run this function only in this scope/directory. It is intended to do testing without mocked db. Currently, it is closed.
            create_db_and_tables()

            entry = create_entry_from_array([1, "2", 3, 4, 5, 6, 7, 8])
            delete_entry_by_id(1)
            created_entry = create_entry(deepcopy(entry))
            entries = get_all_entries()
            assert entries[0] == created_entry
            entry.id = 1
            assert entries[0] == entry

        def test_create_entries(self, session: Session):
            entries = [
                deepcopy([1, "A", 0.6315429094436551, 0.3684570905563449, 0.9881789935400176, 0.011821006459982408, 0.7254980531654877, 0.27450194683451234, ]),
                deepcopy([1, "A", 0.6315429094436551, 0.3684570905563449, 0.9881789935400176, 0.011821006459982408, 0.7254980531654877, 0.27450194683451234, ]),
                deepcopy([1, "A", 0.6315429094436551, 0.3684570905563449, 0.9881789935400176, 0.011821006459982408, 0.7254980531654877, 0.27450194683451234, ]),
                deepcopy([1, "A", 0.6315429094436551, 0.3684570905563449, 0.9881789935400176, 0.011821006459982408, 0.7254980531654877, 0.27450194683451234, ]),
            ]
            create_entry_list_coming_from_csv(entries, session)
            create_entry_list_coming_from_csv(entries, session)
            create_entry_list_coming_from_csv(entries, session)
            assert 12 == len(get_all_entries(session=session))

        def test_read_entries(self, session: Session):
            entry = deepcopy(MockData.entry_array_A_A)
            session.add(deepcopy(entry))
            session.add(deepcopy(entry))
            session.commit()
            entries = get_all_entries(session=session)

            entry.id = 1
            assert entry == entries[0]
            entry.id = 2
            assert entry == entries[1]

        def test_read_entries_with_start_index(self, session: Session):
            entry = deepcopy(MockData.entry_array_A_A)
            session.add(deepcopy(entry))
            session.add(deepcopy(entry))
            session.add(deepcopy(entry))
            session.add(deepcopy(entry))
            session.add(deepcopy(entry))
            session.add(deepcopy(entry))
            session.add(deepcopy(entry))
            session.commit()
            entries = get_all_entries(start_index=3, end_index=5, session=session)

            assert len(entries) == 3
            entry.id = 3
            assert entry == entries[0]
            assert entries[0].predicted_label == LabelConstant.Label.A
            entry.id = 4
            assert entry == entries[1]
            entry.id = 5
            assert entry == entries[2]

        def test_get_entry_count(self, session: Session):
            entry = deepcopy(MockData.entry_array_A_A)
            session.add(deepcopy(entry))
            session.add(deepcopy(entry))
            session.add(deepcopy(entry))
            session.commit()
            assert get_entry_count(session) == 3

    class TestContinuousLearning:
        def test_calculate_confusion_matrix(self, session: Session):
            entry = deepcopy(MockData.entry_array_A_A)
            session.add(deepcopy(entry))
            session.add(deepcopy(entry))
            session.add(deepcopy(entry))
            session.add(deepcopy(entry))

            entries = get_all_entries(session=session)
            confusion_matrix = ContinuousLearning.calculate_confusion_matrix(entries)
            assert confusion_matrix == [[4, 0], [0, 0]]

        def test_update_confusion_matrix(self, session: Session):
            entry = deepcopy(MockData.entry_array_A_A)
            session.add(deepcopy(entry))
            session.add(deepcopy(entry))
            session.add(deepcopy(entry))
            session.add(deepcopy(entry))

            entries = get_all_entries(session=session)
            confusion_matrix = ContinuousLearning.calculate_confusion_matrix(entries)
            ContinuousLearning.update_confusion_matrix(
                deepcopy(MockData.entry_array_A_A),
                deepcopy(MockData.entry_array_A_B),
                confusion_matrix,
            )

            assert confusion_matrix == [[3, 1], [0, 0]]

        @pytest.mark.asyncio
        async def test_read_csv_by_chunks(self, session: Session):
            current_time = time.time()
            data_input = "test/data/data.csv"
            continuous_learning = ContinuousLearning(
                input_path=data_input,
                sleep_between_reads=0.1,
                chunk_size=10000,
                debug=True,
                auto_start=False,
            )
            await continuous_learning.read_csv_by_chunks(
                session=session,
                write_to_db=False,
            )
            time_difference = time.time() - current_time
            assert time_difference >= 1

        @pytest.mark.asyncio
        async def test_read_csv_by_chunks_and_write(self, session):
            data_input = "test/data/data.csv"

            continuous_learning = ContinuousLearning(
                input_path=data_input,
                sleep_between_reads=0.01,
                chunk_size=300,
                debug=True,
                auto_start=False,
            )
            await continuous_learning.read_csv_by_chunks(
                session=session,
                write_to_db=True,
            )
            entries = get_all_entries(session=session, end_index=100000)
            assert len(entries) == 100000

        @pytest.mark.asyncio
        async def test_trigger_confusion_matrix_update(self, session):
            data_input = "test/data/data_small.csv"

            continuous_learning = ContinuousLearning(
                input_path=data_input,
                sleep_between_reads=0.1,
                chunk_size=10000,
                confusion_matrix_length=3,
                debug=True,
                auto_start=False,
            )
            await continuous_learning.read_csv_by_chunks(
                session=session,
                write_to_db=True,
            )
            entries = get_all_entries(session=session)
            assert len(entries) == 9

            continuous_learning.trigger_confusion_matrix_update(session)

            assert len(get_confusion_matrices(session=session)) == 7
