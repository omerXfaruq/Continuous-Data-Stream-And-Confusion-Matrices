from math import ceil
import asyncio

from .db import read_csv_by_chunks, create_db_and_tables, get_all_entries


class ContinuousLearning:
    def __init__(
        self,
        input_path: str = "/test/data/data_small.csv",
        sleep_between_reads: float = 1,
        chunk_size: int = 300,
        close_after_time: int = 400,
    ) -> "MainEvent":
        """
        Runs simulated continuous data source and continuous learning concurrently.

        Args:
            input_path:
            sleep_between_reads:
            chunk_size:
            write_to_db:
        """
        self.loop = asyncio.get_event_loop()
        self.new_data_arrived = False
        self.stop = False
        self.lock = asyncio.Lock()
        create_db_and_tables()

        # Run tasks concurrently
        self.loop.create_task(
            read_csv_by_chunks(
                input_path=input_path,
                sleep_between_reads=sleep_between_reads,
                chunk_size=chunk_size,
                write_to_db=True,
                caller_main_event=self,
            )
        )
        self.loop.create_task(self.update_data_with_confusion_matrix())
        self.loop.run_until_complete(self.countdown_stop(close_after_time))
        self.loop.close()

    async def mark_new_data_arrived(self):
        async with self.lock:
            self.new_data_arrived = True

    def close(self):
        self.stop = True

    async def countdown_stop(self, countdown: float) -> None:
        countdown = max(0, ceil(countdown - 10))
        await asyncio.sleep(countdown)
        self.close()
        await asyncio.sleep(10)

    async def update_data_with_confusion_matrix(
        self, sleep_interval: float = 10
    ) -> None:
        """
        Update data with the confusion matrix when new_data arrives.

        Args:
            sleep_interval:
        """
        while self.stop is False:
            await asyncio.sleep(sleep_interval)
            async with self.lock:
                flag = self.new_data_arrived
                self.new_data_arrived = False
            if flag is True:
                print(get_all_entries())
                # TODO:
