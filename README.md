# Analysis of news articles

ETL-pipeline implementation orchestrated by Airflow. <u>Fundamentals of Data Engineering</u>

This project is refined and adapted to <u>Airflow</u> "news-article-analysis" project

## Task
Collect, process, and save data from news sites to analyze the most popular topics.
 
The ETL process should be performed once a week to ensure fresh data.

## ETL-pipeline

1) **Extract**
    - Using the API of the news aggregator;
    - Uploading articles on the specified topics (for example, "technology", "science", "apple").
2) **Transform**
    - Text preprocessing (stop words, extra characters);
    - Sentiment analysis;
    - Identifying the main topics (TF-IDF).
3) **Load**
    - PostgreSQL: SQLAlchemy hooks
    - MinIO: S3Hook integration
        - Parquet for analytics
        - CSV for raw backups

## Technologies used

- Apache Airflow
- SQLAlchemy (PostgreSQL)
- MinIO
- requests
- pandas, nltk
- pydantic
- parquet

## Project Structure
```
airflow-project/
├── dags/                       # Main DAG definitions
│   └── news_article_dag.py     # Primary pipeline
├── etl/                        # Core business logic
│   ├── extract/
│   ├── transform/              # NLP processing
│   └── load/                   # DB/MinIO utils
├── plugins/
│   ├── io/                     # dataframe ⇄ bytes
│   └── s3_client/              # Custom operators/hooks
└── config/                     # Environment configs
```

## Run
...