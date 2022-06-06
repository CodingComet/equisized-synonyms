import requests
from bs4 import BeautifulSoup
from typing import List, Tuple

def request_http(url: str) -> Tuple[int, bytes]:
    response = requests.get(url)

    return (response.status_code, response.content)

class Thesaurus:
    soup: BeautifulSoup

    @staticmethod
    def get_synonyms(word: str) -> List[str]:
        status, content = request_http(f'https://www.thesaurus.com/browse/{word}')

        if status == 404:
            return []

        Thesaurus.soup = BeautifulSoup(content, 'html.parser')


        # get word container
        div = Thesaurus.soup.find('div', attrs={'data-testid': 'word-grid-container'})
        synonyms_element = div.find('ul').children # get synonyms element

        return [synonym.find('a').text.strip() # extract synonym element and strip the text
                for synonym in synonyms_element] + [word] # create a synonym list out of element