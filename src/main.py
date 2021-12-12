from math import ceil
import asyncio

from typing import List
import pandas as pd

from .db import (
    create_entry_list_coming_from_csv,
    create_db_and_tables,
    get_all_entries,
    get_entry_by_id,
    get_entry_count,
    Entry,
    write_confusion_matrix_to_db,
    get_session,
    Session,
    get_confusion_matrices,
)


class ContinuousLearning:
    def __init__(
        self,
        input_path: str = "/test/data/data_small.csv",
        sleep_between_reads: float = 1,
        chunk_size: int = 300,
        close_after_countdown: int = 400,
        confusion_matrix_length: int = 1000,
        debug: bool = False,
        auto_start: bool = True,
    ) -> "ContinuousLearning":
        """
        Runs simulated continuous data source and continuous learning concurrently.

        Args:
            input_path:
            sleep_between_reads:
            chunk_size:
            write_to_db:
        """
        self.loop = asyncio.get_event_loop()
        self.lock = asyncio.Lock()
        self.new_data_arrived = False
        self.stop = False
        self.last_calculated_confusion_matrix_starting_index = 0

        self.countdown = close_after_countdown
        self.confusion_matrix_length = confusion_matrix_length
        self.debug = debug
        self.input_path = input_path
        self.sleep_between_reads = sleep_between_reads
        self.chunk_size = chunk_size

        create_db_and_tables()

        if auto_start:
            self.start()

    def start(self):
        # Run tasks concurrently

        self.loop.create_task(self.read_csv_by_chunks())
        self.loop.create_task(self.calculate_and_write_confusion_matrices())
        self.loop.run_until_complete(self.countdown_stop())
        self.loop.close()

    async def mark_new_data_arrived(self):
        async with self.lock:
            self.new_data_arrived = True

    def close(self):
        self.stop = True

    async def countdown_stop(self) -> None:
        countdown = max(0, ceil(self.countdown - 10))
        await asyncio.sleep(countdown)
        self.close()
        await asyncio.sleep(10)

    async def calculate_and_write_confusion_matrices(
        self,
        sleep_interval: float = 1,
        session: "Session" = next(get_session()),
    ) -> None:
        """
        Calculate and write new confusion matrices with incoming data.

        Args:
            sleep_interval:
            session:

        """
        while self.stop is False:
            await asyncio.sleep(sleep_interval)
            async with self.lock:
                flag = self.new_data_arrived
                self.new_data_arrived = False
            if flag is True:
                self.trigger_confusion_matrix_update(session)
                if self.debug:
                    print(
                        f"Triggered confusion_matrix_update; last_calculated_confusion_matrix_starting_index:{self.last_calculated_confusion_matrix_starting_index}"
                    )
            else:
                if self.debug:
                    print(
                        f"Confusion Matrices:{get_confusion_matrices(session=session)}"
                    )

    def trigger_confusion_matrix_update(self, session: Session) -> None:
        """
        Calculates new confusion matrices starting from the last calculated point, and writes them to the database.

        Args:
            session:

        Returns:

        """
        number_of_entries = get_entry_count(session)
        if self.debug:
            print(f"trigger_confusion_matrix_update, numberOfEntries: {number_of_entries}")
        if number_of_entries < self.confusion_matrix_length:
            return

        start_index = self.last_calculated_confusion_matrix_starting_index + 1
        index_difference = max(0, self.confusion_matrix_length)
        end_index = start_index + index_difference

        entries = get_all_entries(
            start_index=start_index, end_index=end_index, session=session
        )

        confusion_matrix = self.calculate_confusion_matrix(entries)
        write_confusion_matrix_to_db(confusion_matrix, start_index, end_index, session)

        while end_index < number_of_entries:
            start_index += 1
            end_index += 1
            old_item = entries.pop(0)
            new_item = get_entry_by_id(end_index, session)
            entries.append(new_item)
            # There is no need to calculate all the confusion matrices from scratch.
            self.update_confusion_matrix(old_item, new_item, confusion_matrix)
            written_confusion_matrix = write_confusion_matrix_to_db(
                confusion_matrix, start_index, end_index, session
            )
            if self.debug:
                print(
                    f"Wrote the confusion matrix to the db:{written_confusion_matrix}"
                )

        self.last_calculated_confusion_matrix_starting_index = start_index

    @staticmethod
    def calculate_confusion_matrix(entries: List[Entry]) -> List[List[int]]:
        confusion_matrix = [[0, 0], [0, 0]]
        for entry in entries:
            confusion_matrix[entry.given_label][entry.predicted_label] += 1
        return confusion_matrix

    @staticmethod
    def update_confusion_matrix(
        old_item: Entry, new_item: Entry, confusion_matrix: List[List[int]]
    ) -> None:
        confusion_matrix[old_item.given_label][old_item.predicted_label] += -1
        confusion_matrix[new_item.given_label][new_item.predicted_label] += 1

    async def read_csv_by_chunks(
        self,
        session: Session = next(get_session()),
        write_to_db: bool = True,
    ) -> None:
        """
        Read csv chunk by chunk and write to the database with periodic sleeps.

        Args:
            session:
            write_to_db:

        Returns: None

        """

        df_iter = pd.read_csv(self.input_path, chunksize=self.chunk_size, iterator=True)

        for iter_num, chunk in enumerate(df_iter, 1):
            await asyncio.sleep(self.sleep_between_reads)

            item_array = chunk.to_numpy()

            if write_to_db:
                create_entry_list_coming_from_csv(item_array, session)
                await self.mark_new_data_arrived()
                if self.debug:
                    print(f"Wrote chunk to the db, iteration_no:{iter_num}")

            if self.stop is True:
                break
