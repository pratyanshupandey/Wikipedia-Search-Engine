import re
from nltk.corpus import stopwords
import Stemmer

class TextProcessor:
    def __init__(self):
        # regex specific data
        self.title_regex = re.compile(r"[a-zA-Z0-9]+")
        self.token_regex = re.compile(r"[a-zA-Z0-9]+")
        self.infobox_regex = re.compile(r"{{infobox")
        self.links_regex = re.compile(r"(http|https)://\S+")
        self.categories_regex = re.compile(r"\[\[category:(.*)\]\]")
        self.external_regex = re.compile(r"=+external links=+")
        self.reference_regex = re.compile(r"=+references=+|=+notes=+|=+footnotes=+")
        self.citation_regex = re.compile(r"\{\{cite(.*)\}\}")

        # stopwords
        self.stopwords = set(stopwords.words('english'))

        # stemmer
        self.stemmer = Stemmer.Stemmer('english')

        # sections processed under other already
        self.already_proc = []

    def reset(self):
        self.already_proc = []

    def process(self, title, body):
        title_tokens = self.title_tokens(title)
        body_len = len(body)
        infobox_tokens = self.infobox_tokens(body, body_len)
        category_tokens = self.categories_tokens(body)
        reference_tokens = self.reference_tokens(body, body_len)
        external_links_tokens = self.external_links_tokens(body, body_len)
        self.already_proc.sort()
        body_tokens = self.body_tokens(body, body_len)
        self.reset()

        return title_tokens, body_tokens, reference_tokens, category_tokens, infobox_tokens, external_links_tokens

    def stopwords_stemmer(self, tokens):
        tokens = [token for token in tokens if token not in self.stopwords and len(token) > 1]
        tokens = self.stemmer.stemWords(tokens)
        return tokens

    def title_tokens(self, title):
        tokens = self.title_regex.findall(title)
        tokens = self.stopwords_stemmer(tokens)
        return tokens

    def categories_tokens(self, body):
        list = self.categories_regex.findall(body)
        tokens = []
        for element in list:
            tokens.extend(self.token_regex.findall(element))
        tokens = self.stopwords_stemmer(tokens)
        return tokens

    def infobox_tokens(self, body, body_len):
        list = [(m.start(0), m.end(0)) for m in self.infobox_regex.finditer(body)]
        tokens = []
        for start, end in list:
            depth = 0
            temp = start
            while True:
                if temp + 1 < body_len and body[temp] == "{" and body[temp + 1] == "{":
                    temp += 1
                    depth += 1
                elif temp + 1 < body_len and body[temp] == "}" and body[temp + 1] == "}":
                    temp += 1
                    depth -= 1
                if depth == 0 or temp >= body_len:
                    if temp > body_len:
                        temp = body_len
                    self.already_proc.append((start, temp))
                    tokens.extend(self.token_regex.findall(body[end:temp]))
                    break
                temp += 1

        tokens = self.stopwords_stemmer(tokens)
        return tokens

    def external_links_tokens(self, body, body_len):
        tokens = []
        list = [(m.start(0), m.end(0)) for m in self.external_regex.finditer(body)]
        for start, end in list:
            temp = end
            while (True):
                if temp + 1 >= body_len or ((body[temp] == "=" and body[temp + 1] == "=") or (
                        body[temp] == "\n" and body[temp + 1] == "\n")):
                    temp += 1
                    if temp + 1 >= body_len:
                        temp = body_len
                    self.already_proc.append((start, temp))
                    split_by_links = self.links_regex.split(body[end:temp])
                    for section in split_by_links:
                        tokens.extend(self.token_regex.findall(section))
                    break
                temp += 1

        tokens = self.stopwords_stemmer(tokens)
        return tokens

    def reference_tokens(self, body, body_len):
        # in form of citations
        list = self.citation_regex.findall(body)
        tokens = []
        for element in list:
            tokens.extend(self.token_regex.findall(element))

        # as list under references
        list = [(m.start(0), m.end(0)) for m in self.reference_regex.finditer(body)]
        for start, end in list:
            temp = end
            while True:
                if temp + 1 >= body_len or ((body[temp] == "=" and body[temp + 1] == "=") or (
                        body[temp] == "\n" and body[temp + 1] == "\n")):
                    temp += 1
                    if temp + 1 >= body_len:
                        temp = body_len
                    self.already_proc.append((start, temp))
                    tokens.extend(self.token_regex.findall(body[end:temp]))
                    break
                temp += 1

        tokens = self.stopwords_stemmer(tokens)
        return tokens

    def body_tokens(self, body, body_len):
        tokens = []
        aplen = len(self.already_proc)

        if aplen < 1:
            tokens = self.token_regex.findall(body)
        else:
            tokens.extend(self.title_regex.findall(body, 0, self.already_proc[0][0]))
            for i in range(1,aplen):
                if self.already_proc[i][0] > self.already_proc[i-1][1] and self.already_proc[i-1][1] < body_len:
                    tokens.extend(self.title_regex.findall(body, self.already_proc[i-1][1],self.already_proc[i][0]))
            tokens.extend(self.title_regex.findall(body, self.already_proc[-1][1], body_len))

        tokens = self.stopwords_stemmer(tokens)
        return tokens
