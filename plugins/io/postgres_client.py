import logging
import numpy as np
import pandas as pd

from typing import List, Literal, Tuple
from datetime import datetime
from io import BytesIO
from airflow.providers.postgres.hooks.postgres import PostgresHook


def save_word_stats(
    most_common: List[Tuple],
    table_name: str = "wordstat",
) -> None:
    postgres_hook = PostgresHook(postgres_conn_id="postgres_conn")
    conn = postgres_hook.get_conn()
    cursor = conn.cursor()

    query = f"""
        INSERT INTO {table_name} (word, count)
        VALUES (%s, %s)
    """

    try:
        cursor.executemany(query, most_common)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def save_article(
    df: pd.DataFrame, 
    table_name: str = "article",
) -> None:
    postgres_hook = PostgresHook(postgres_conn_id="postgres_conn")
    conn = postgres_hook.get_conn()
    cursor = conn.cursor()
    
    cols = ", ".join(df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))

    query = f"""
        INSERT INTO {table_name} ({cols})
        VALUES ({placeholders});
    """

    print(query)

    values: List[Tuple] = [tuple(row) for row in df.to_numpy()]

    try:
        cursor.executemany(query, values)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    df = pd.read_csv("data_apple.csv", index_col=0)
    print(df.columns)
    print(df.columns)
    # save_article(df)