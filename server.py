from itertools import groupby
from collections import Counter
from typing import List
from flask import Flask, render_template, request, url_for

from api import Thesaurus, Abbreviations

thesaurus_ = Thesaurus()
abbreviations_ = Abbreviations()


def get_sorted_synonyms(word: str, include_spaces: bool = True):
    synonyms = thesaurus_.get(word)

    if not include_spaces:
        synonyms = filter(lambda x: not (' ' in x or '-' in x), synonyms)  # remove all synonyms with spaces or dashe

    return sorted(synonyms, key=lambda synonym: (len(synonym), synonym))


app = Flask(__name__, template_folder="./templates")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get/<words>')
def result(words: str):
    words: List[str] = words.lower().replace(",", " ").split()
    include_spaces: bool = request.args.get('disable_spaces') == 'false'
    include_partial_rows: bool = request.args.get('hide_partial_rows') == 'false'

    # get synonyms
    sorted_synonyms = {word: get_sorted_synonyms(word, include_spaces) for word in words}

    # get abbreviations for each single synonyms of each word
    # abbreviations = {word: sorted(
    #     list({abbr for synonym in sorted_synonyms[word] for abbr in abbreviations_.get(synonym)}
    #          ), key=lambda abbr: (len(abbr), abbr))
    #     for word in words}
    # print(abbreviations)

    # sort synonyms by length groups for table
    keys = []  # keeps different lengths for table and partial rows feature

    def append_key(item: object):
        keys.append(item)
        return item

    synonyms_table = {word: {append_key(k): list(g) for k, g in groupby(sorted_synonyms[word], len)} for word in words}

    # partial rows
    if not include_partial_rows:
        counted = Counter(keys)
        keys = [el for el in keys if counted[el] >= len(words)]

    return render_template('result.html',
                           words=words,
                           synonyms_table=synonyms_table,
                           keys=sorted(list(dict.fromkeys(keys))),
                           include_partial_rows=include_partial_rows,
                           include_spaces=include_spaces,
                           )


if __name__ == '__main__':
    app.run(debug=True)
