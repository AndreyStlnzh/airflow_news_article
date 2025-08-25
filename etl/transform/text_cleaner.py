import re
import pandas as pd
import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

class TextCleaner:
    """
    Класс для предобработки текста новостей: удаление дубликатов, очистка текста,
    фильтрация данных, обработка дат.
    """
    # Компилируем регулярки заранее (ускоряет работу)
    _whitespace_re = re.compile(r"\s+")
    _chars_re = re.compile(r"\[\+\d+ chars\]")
    _non_alnum_re = re.compile(r"[^a-zA-Z0-9]")

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.data = None

    def preprocess_data(
        self,
        data: pd.DataFrame,
    ):
        self.data = data
        self._drop_nans()
        self._drop_duplicates()
        self._text_preprocessing()
        self._date_preprocessing()
        self._filter_data()


    def _drop_nans(
        self,
    ) -> None:
        """Удаляем строки с NaN в важных колонках"""
        self.data.dropna(subset=["title", "content"], inplace=True)
        self.data.dropna(subset=["author"], inplace=True)


    def _drop_duplicates(
        self,
    ) -> None:
        """Удаляем дубликаты по 'title' и 'content'"""
        self.data.drop_duplicates(subset=["title", "content"], inplace=True)


    def _text_preprocessing(
        self,
    ) -> None:
        """Очищаем текст в 'title', 'description' и 'content'"""
        for col in ["title", "description", "content"]:
            self.data[col] = self.data[col].astype(str).apply(self._clean_text)

    def _clean_text(
        self, 
        text: str
    ) -> str:
        """
        Функция очистки текста
        Удаляет лишние пробелы и символы переноса строк и табуляции
        Оставляет только буквы и цифры

        Args:
            text (str): Исходный текст

        Returns:
            str: Очищенный текст
        """

        text = self._whitespace_re.sub(" ", text) # удаляем символы табуляции и переносов строк
        text = self._chars_re.sub(" ", text) # удаляем [+123 chars] (есть в каждом content)
        text = self._non_alnum_re.sub(" ", text)  # оставляем только буквы и цифры
        
        text = text.lower()
        words = word_tokenize(text)  # Токенизация
        words = [self.lemmatizer.lemmatize(word) for word in words if word not in self.stop_words]  # Лемматизация
        return " ".join(words)
    

    def _date_preprocessing(
        self,
    ) -> None:
        """Обрабатываем даты и создаем колонки 'date' и 'time'"""
        self.data['publishedAt'] = pd.to_datetime(self.data['publishedAt'], errors='coerce')
        self.data['date'] = self.data['publishedAt'].dt.date
        self.data['time'] = self.data['publishedAt'].dt.time
        self.data.rename(columns={'publishedAt': 'published_at'}, inplace=True)


    def _filter_data(
        self,
    ) -> None:
        """Удаляем ненужные колонки"""
        self.data.drop(columns=["urlToImage", "source.id", "source.name"], inplace=True)
