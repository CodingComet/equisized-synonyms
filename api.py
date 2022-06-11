from abc import abstractmethod

import requests
from bs4 import BeautifulSoup
from typing import List, Tuple, Dict
import dill as pickle

MIN_ABBR_LEN = 2


def request_http(url: str) -> Tuple[int, bytes]:
    response = requests.get(url)

    return (response.status_code, response.content)


class LazyFetcher:
    soup: BeautifulSoup
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

        Thesaurus.soup = BeautifulSoup(content, 'html.parser')

        # get word container
        div = Thesaurus.soup.find('div', attrs={'data-testid': 'word-grid-container'})
        synonyms_element = div.find('ul').children  # get synonyms element

        return [synonym.find('a').text.strip()  # extract synonym element and strip the text
                for synonym in synonyms_element] + [word]  # create a synonym list out of element


class Abbreviations(LazyFetcher):
    def __init__(self):
        super().__init__("abbr.cache.pkl")

    def fetch(self, word: str) -> List[str]:
        status, content = request_http(f'https://www.abbreviations.com/abbreviation/{word}')

        if status == 404:
            return []

        self.soup = BeautifulSoup(content, 'html.parser')

        # get word container
        abbr_elemets_ = self.soup.find_all('td', attrs={'class': 'tal tm fsl'})
        abbrs_ = (next(abbr.children).text.lower().replace('.', '') for abbr in abbr_elemets_)
        return list({abbr for abbr in abbrs_ if MIN_ABBR_LEN <= len(abbr) and abbr != word.lower()})
