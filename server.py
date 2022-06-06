from itertools import groupby
from collections import Counter
from typing import List
from flask import Flask, render_template, request, url_for

from thesaurus import Thesaurus


def get_sorted_synonyms(word: str, include_spaces: bool = True):
    synonyms = Thesaurus.get_synonyms(word)

    if not include_spaces:
        synonyms = filter(lambda x: not (' ' in x or '-' in x), synonyms) # remove all synonyms with spaces or dashe

    return sorted(synonyms, key=len)



app = Flask(__name__, template_folder="./templates")


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/synonyms/<words>')
def synonyms(words):
    
    words: List[str] = words.split()
    include_spaces: bool = request.args.get('disable_spaces') == 'false'
    include_partial_rows: bool = request.args.get('hide_partial_rows') == 'false'

    # get synonyms
    sorted_synonyms = {word: get_sorted_synonyms(word, include_spaces) for word in words}

    # sort synonyms by length groups for table
    
    keys = [] # keeps different lengths for table and partial rows feature

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
                           keys=list(dict.fromkeys(keys))
                           )



if __name__ == '__main__':
    app.run(debug=True)
