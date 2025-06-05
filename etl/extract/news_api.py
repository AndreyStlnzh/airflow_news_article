import requests
import pandas as pd

from pandas import json_normalize

class NewsApi:
    """
    API для полученя новостных статей
    Можно было использовать NewsApiClient с библиотеки newsapi, но можно и обычными requests

    Returns:
        _type_: _description_
    """
    _news_api_url = "https://newsapi.org/v2/everything"

    def __init__(self) -> None:
        pass

    def get_articles(
        self,
        api_key: str,
        keyword: str,
        date_from: str,
        date_to: str,
        save_csv: bool=False
    ): 
        """
        Функция получения статей с NewsApi

        Args:
            api_key (str): ключ API
            keyword (str): ключевое слово или фраза, статьи по которым необходимо найти
            date_from (str): фильтрация статей по дате
            date_to (str): фильтрация статей по дате

        Returns:
            _type_: _description_
        """
        data_df = None
        page = 1
        while True:
            print("Page: ", page)
            params = {
                "q": keyword,
                "from": date_from,
                "to": date_to,
                "page": page,
                "apiKey": api_key,
            }
            print(f"Обращаемся по адресу {self._news_api_url}")
            response = requests.get(self._news_api_url, params=params)
            print(response.status_code)
            if response.status_code != 200:
                print(f"Получили {response.status_code}")
                if save_csv:
                    data_df.to_csv(f"data_{keyword}.csv")
                    print(f"Сохранили данные в data_{keyword}.csv")
                return data_df
            
            print("Приняли результат, начинаем обработку")
            data = response.json()
            # print(f"Всего {data["totalResults"]} новостных статей по данному запросу")

            data_df = pd.concat([data_df, json_normalize(data["articles"])], ignore_index=True)
            page += 1
