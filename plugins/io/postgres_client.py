import logging
import pandas as pd

from typing import List, Literal
from datetime import datetime
from io import BytesIO
from airflow.providers.postgres.hooks.postgres import PostgresHook


def save_word_stats(
    words: List[str],
    count: List[int],
):
    postgres_hook = PostgresHook(postgres_conn_id="postgres_conn")

    conn = postgres_hook.get_conn()

        