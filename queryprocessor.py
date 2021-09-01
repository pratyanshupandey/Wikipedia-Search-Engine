import re
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords

class QueryProcessor:
    def __init__(self):
        # regex specific data
        self.token_regex = re.compile(r"[a-zA-Z0-9]+")

        # stopwords
        self.stopwords = set(stopwords.words('english'))

        # stemmer
        self.stemmer = SnowballStemmer('english')

    def process(self, string):
        string = string.lower()
        if len(string) >= 2 and string[0] in ['t', 'i', 'b', 'c', 'l', 'r'] and string[1] == ":":
            string = string[2:]
        if string is None:
            return []
        tokens = self.token_regex.findall(string)
        tokens = [token for token in tokens if token not in self.stopwords]
        tokens = [self.stemmer.stem(token) + " " for token in tokens]
        return tokens
