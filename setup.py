from setuptools import setup, find_packages

setup(
    name="airflow_project",
    version="0.1",
    packages=find_packages(include=["etl", "etl.*", "plugins", "plugins.*"]),
    install_requires=[
        "requests", "pandas"
    ],
)
