import pandas as pd

from typing import Tuple
from collections import Counter

class MostCommonWords:
    def __init__(self):
        pass


    def find_most_common_words(
        self,
        data: pd.DataFrame,
        n: int=10
    ) -> Tuple[list, list]:
        """Функция нахождения самых частых слов

        Args:
            data (pd.DataFrame): датафрейм
            n (int, optional): количество самых частых слов. Defaults to 10.

        Returns:
            Tuple[list, list]: список слов и список их частот
        """
        all_words = [word for sent in data["content"] for word in sent.split()]

        word_count = Counter(all_words)
        most_common = word_count.most_common(n)
        words, count = zip(*most_common)

        return words, count
    