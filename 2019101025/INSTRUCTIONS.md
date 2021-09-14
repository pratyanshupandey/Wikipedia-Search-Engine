### Name: Pratyanshu Pandey
### Roll No: 2019101025

<hr>

### Dependencies:
* nltk
* PyStemmer

### Installation Commands
```shell
$ pip3 install PyStemmer
$ pip3 install nltk
$ python3
>>> import nltk
>>> nltk.download('stopwords')
>>> exit()
$
```
### How to Run
Code can be run using any of the 2 methods:
```shell
$ bash index.sh <path_to_wiki_dump> <path_to_inverted_index> invertedindex_stat.txt
$ bash search.sh <path_to_inverted_index> <query_string>
```

#### OR

```shell
$ python3 index_manager.py <path_to_wiki_dump> <path_to_inverted_index> invertedindex_stat.txt
$ python3 search.py <path_to_inverted_index> <query_string>
```

