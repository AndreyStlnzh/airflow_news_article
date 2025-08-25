import logging
from datetime import datetime, timedelta
from typing import List, Tuple

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.models import Variable
import pandas as pd
from etl.extract.news_api import NewsApi
from etl.transform.most_common_words import MostCommonWords
from etl.transform.sentiment_analysis import SentimentAnalysis
from etl.transform.text_cleaner import TextCleaner
from plugins.io.postgres_client import save_article, save_word_stats
from plugins.io.serializers.dataframe import dataframe_to_bytes, bytes_to_dataframe
from plugins.io.s3_client import uploud_to_minio, download_from_minio

default_args = {
    "owner": "airflow",
}

@dag(
    default_args=default_args,
    start_date=datetime(2025, 5, 4),
    schedule_interval="@monthly",
)
def news_article_dag():
    keyword = "apple"
    api_key = Variable.get("news_api_key")
    minio_bucket = Variable.get("minio_bucket")

    @task(execution_timeout=timedelta(seconds=60))
    def get_articles() -> str:
        """Функция извлечения данных

        Returns:
            str: путь до извлеченного датасета
        """
        logging.info("Начало извлечения данных")
        
        news_api = NewsApi()
        context = get_current_context()
        
        # Беру данные за дату выполнения и предыдущий день
        date_from = (context["execution_date"] - timedelta(days=1)).date().isoformat()
        date_to = (context["execution_date"]).date().isoformat()

        logging.info(f"Запрашиваем данные с {date_from} по {date_to}")

        articles_df = news_api.get_articles(api_key, keyword, date_from, date_to=date_to, save_csv=False)
        if articles_df is None:
            logging.error("Извлеченный датафрейм пуст")
            raise AttributeError("No data...")
        
        logging.info("Данные получены, сериализуем данные")
        data_bytes = dataframe_to_bytes(dataframe=articles_df, format="parquet")
        logging.info("Загружаем итоговые данные в minio")
        minio_path = uploud_to_minio(
            data_bytes=data_bytes, 
            minio_bucket=minio_bucket,
            format="parquet"
        )
        logging.info("Данные загружены в minio")
        logging.info(f"Путь в минио: {minio_path}")

        return minio_path

    @task(execution_timeout=timedelta(seconds=60), multiple_outputs=True)
    def prepare_data(minio_path: str) -> Tuple[str, List]:
        """Функция трансформации данных

        Args:
            minio_path (str): путь до исходного датасета в minio

        Returns:
            str: путь до предобработанного датасета в minio
        """
        logging.info("Начало трансформации данных")
        
        file_bytes = download_from_minio(
            minio_path=minio_path,
            minio_bucket=minio_bucket,
        )
        logging.info("Данные загружены с минио. Начало десериализации")
        data_df = bytes_to_dataframe(file_bytes=file_bytes, format="parquet")
        logging.info("Данные десериализованы. Начало трансформации")
        
        text_cleaner: TextCleaner = TextCleaner()
        most_common_words: MostCommonWords = MostCommonWords()
        sentiment_analysis: SentimentAnalysis = SentimentAnalysis()

        text_cleaner.preprocess_data(data_df)
        logging.info("Данные предобработаны")
        most_common: List[Tuple] = most_common_words.find_most_common_words(data_df)
        logging.info("Подсчитаны самые частые слова")
        data_df: pd.DataFrame = sentiment_analysis.process_sentiment_analysis(data_df)
        logging.info("Проведен аналз тональности")
        data_bytes = dataframe_to_bytes(dataframe=data_df, format="parquet")
        minio_path = uploud_to_minio(
            data_bytes=data_bytes, 
            minio_bucket=minio_bucket,
            format="parquet"
        )
        
        print("КОЛОНКИ", data_df.columns)

        logging.info("Данные загружены в minio")
        logging.info(f"Путь в минио: {minio_path}")

        return {
            "prepared_minio_path": minio_path,
            "most_common": most_common
        }


    @task
    def load_results_to_db(
        minio_path: str, 
        most_common: List[Tuple],
    ):
        """Функция загрузки данных"""
        # скачать с минио паркет файл и сохранить все как сохранял в new_article
        logging.info("Начало загрузки данных")
        
        file_bytes = download_from_minio(
            minio_path=minio_path,
            minio_bucket=minio_bucket,
        )
        logging.info("Данные загружены в минио. Начало десериализации")
        data_df = bytes_to_dataframe(file_bytes=file_bytes, format="parquet")
        logging.info("Данные десериализованы. Начало сохранения данных")

        save_article(data_df)
        logging.info("Статьи успешно сохранены в БД")
        save_word_stats(most_common)
        logging.info("Word stats успешно сохранены в БД")

        return 1
    

    minio_path = get_articles()
    prep = prepare_data(minio_path)
    res = load_results_to_db(
        minio_path=prep["prepared_minio_path"],
        most_common=prep["most_common"]
    )
    minio_path >> prep >> res

news_dag = news_article_dag()
