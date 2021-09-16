import re
import Stemmer
from nltk.corpus import stopwords
from collections import defaultdict

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
        if string == "":
            return []

        token_field = ["", "", "", "", "", "", ""]
        cur_type = 0
        for i in range(len(string)):
            if string[i:i + 2] in ["t:", "i:", "b:", "c:", "l:", "r:"]:
                cur_type = ["t:", "i:", "b:", "c:", "l:", "r:"].index(string[i:i + 2]) + 1
                i += 1
                token_field[cur_type] += " "
            else:
                token_field[cur_type] += string[i]

        token_field = [self.token_regex.findall(string) for string in token_field]

        tokens_map = defaultdict(lambda: [])
        for i in range(len(token_field)):
            for token in token_field[i]:
                if token not in self.stopwords and len(token) > 1 and (token.isnumeric() == False or len(token) == 4):
                    token = self.stemmer.stemWord(token)
                    if tokens_map[token] == []:
                        tokens_map[token] = [0,0,0,0,0,0,0]
                    tokens_map[token][i] = 1

        return list(tokens_map.items())


if __name__ == "__main__":
    q = QueryProcessor()
    qtokens = q.process("whats hangingt: Hello World b: good i: some good ")
    qtokens.sort()
    print([qtok[0] for qtok in qtokens], [qtok[1] for qtok in qtokens])
