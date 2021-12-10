import pandas as pd
import asyncio
from .db import create_entry_list_coming_from_csv


async def read_csv_by_chunks(
    input_path: str,
    sleep_between_reads: float,
    *,
    chunk_size: int = 10000,
    debug: bool = False,
    write_to_db=True,
    session: "Session" = None,
    caller_main_event: "MainEvent" = None,
) -> None:
    """
    Read csv chunk by chunk and write to the database with periodic sleeps.

    Args:
        input_path:
        sleep_between_reads:
        chunk_size:
        debug:
        write_to_db:
        session:

    Returns: None

    """

    df_iter = pd.read_csv(input_path, chunksize=chunk_size, iterator=True)

    for iter_num, chunk in enumerate(df_iter, 1):
        if debug:
            print(f"Processing iteration {iter_num}")
        await asyncio.sleep(sleep_between_reads)

        if write_to_db:
            item_array = chunk.to_numpy()

            # Use given database session, mainly for testing
            if session is not None:
                create_entry_list_coming_from_csv(item_array, session)
            else:  # pragma: no cover
                create_entry_list_coming_from_csv(item_array)

            if caller_main_event is not None:
                await caller_main_event.mark_new_data_arrived()

        if caller_main_event is not None:
            if caller_main_event.stop is True:
                break
