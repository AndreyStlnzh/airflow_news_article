import logging

from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.models import Variable
from etl.extract.news_api import NewsApi
from plugins.io.serializers.dataframe import dataframe_to_bytes, bytes_to_dataframe
from plugins.io.s3_client import uploud_to_minio, download_from_minio
# from .functions import download_dataset, convert_to_parquet

default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 3, 15),
    # "retries": 2,
    # "retry_delay": dt.timedelta(seconds=10),
}

@dag(
    default_args=default_args,
    start_date=datetime(2025, 4, 4),
    schedule_interval="@monthly",
)
def news_article_dag():
    keyword = "apple"
    date_from = (datetime.now() - timedelta(days=3)).date().isoformat()
    date_to = (datetime.now()).date().isoformat()
    page=1

    api_key = Variable.get("news_api_key")

    minio_bucket = Variable.get("minio_bucket")

    endpoint_to_check_data=f"?q={keyword}&from={date_from}" \
                           f"&to={date_to}&page={page}&apiKey={api_key}"

    
    check_data = SimpleHttpOperator(
        method="GET",
        endpoint=endpoint_to_check_data,
        task_id="check_data",
        http_conn_id="news_article_id"
    )

    @task
    def get_articles():
        logging.info("Начало извлечения данных")
        
        news_api = NewsApi()
        context = get_current_context()
        
        # Беру данные за дату выполнения и предыдущий денья
        date_from = (context["execution_date"] - timedelta(days=1)).date().isoformat()
        date_to = (context["execution_date"]).date().isoformat()

        articles_df = news_api.get_articles(api_key, "apple", date_from, date_to=date_to, save_csv=False)
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

    @task
    def prepare_data(minio_path: str):
        logging.info("Начало трансформации данных")
        
        file_bytes = download_from_minio(
            minio_path=minio_path,
            minio_bucket=minio_bucket,
            format="parquet",
        )
        logging.info("Данные загружены в минио. Начало десериализации")
        data_df = bytes_to_dataframe(file_bytes=file_bytes, format="parquet")
        logging.info("Данные десериализованы. Начало трансформации")

        

    minio_path = get_articles()

    check_data >> minio_path

news_dag = news_article_dag()
