from abc import abstractmethod

import requests
from lxml import html
from typing import List, Tuple, Dict
import dill as pickle

MIN_ABBR_LEN = 2


def request_http(url: str) -> Tuple[int, bytes]:
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    return (response.status_code, response.content)


class LazyFetcher:
    cache_file_name: str
    local_cache: Dict[str, List[str]]

    def __init__(self, file_name: str):
        self.cache_file_name = file_name

        try:
            with open(file_name, 'rb') as f:
                self.local_cache = pickle.load(f)
        except FileNotFoundError:
            self.local_cache = {}

    def store_cache(self):
        with open(self.cache_file_name, 'wb') as f:
            pickle.dump(self.local_cache, f)

    @abstractmethod
    def fetch(self, word: str):
        pass

    def get(self, word: str):
        if word in self.local_cache:
            return self.local_cache[word]

        res = self.fetch(word)
        self.local_cache[word] = res
        self.store_cache()

        return res


class Thesaurus(LazyFetcher):
    def __init__(self):
        super().__init__("synonym.cache.pkl")

    def fetch(self, word: str):
        status, content = request_http(f'https://www.thesaurus.com/browse/{word}')

        if status == 404:
            return []

        tree = html.fromstring(content)

        # Fetched on 2024-11-8
        xpath = '//*[@id="root"]/div/main/div[2]/div[2]/div[2]/section/div[1]/div[2]/div[2]//a/text()' 
        elements = tree.xpath(xpath)

        return elements


class Abbreviations(LazyFetcher):
    def __init__(self):
        super().__init__("abbr.cache.pkl")

    def fetch(self, word: str) -> List[str]:
        status, content = request_http(f'https://www.abbreviations.com/abbreviation/{word}')

        if status == 404:
            return []

        tree = html.fromstring(content)

        # Fetched on 2024-11-8
        xpath = '//*[@id="content-body"]/div[1]/div[3]/div/table//*[contains(@class, "tal tm fsl")]/a/text()' 
        elements = tree.xpath(xpath)
        abbrs_ = [abbr.lower().replace('.', '') for abbr in elements]

        return list({abbr for abbr in abbrs_ if MIN_ABBR_LEN <= len(abbr) and abbr != word.lower()})
