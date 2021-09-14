import re
import Stemmer
from nltk.corpus import stopwords

class QueryProcessor:
    def __init__(self):
        # regex specific data
        self.token_regex = re.compile(r"[a-zA-Z0-9]+")

        # stopwords
        self.stopwords = set(stopwords.words('english'))

        # stemmer
        self.stemmer = Stemmer.Stemmer('english')

    def process(self, string):
        string = string.lower()
        if string is None:
            return []
        tokens = self.token_regex.findall(string)
        tokens = [token for token in tokens if token not in self.stopwords]
        tokens = self.stemmer.stemWords(tokens)
        return tokens
