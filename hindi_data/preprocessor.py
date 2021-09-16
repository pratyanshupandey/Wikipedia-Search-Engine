import re
from nltk.corpus import stopwords
import Stemmer

class TextProcessor:
    def __init__(self):
        # regex specific data
        self.title_regex = re.compile(r"\w+")
        self.token_regex = re.compile(r"\w+")
        self.infobox_regex = re.compile(r"{{infobox")
        self.links_regex = re.compile(r"(http|https)://\S+")
        self.categories_regex_en = re.compile(r"\[\[category:(.*)\]\]")
        self.categories_regex_hi = re.compile(r"\[\[श्रेणी:(.*)\]\]")
        self.external_regex = re.compile(r"=+external links=+| बाहरी कड़ियाँ ")
        self.reference_regex = re.compile(r"=+references=+|=+notes=+|=+footnotes=+|=+\s?सन्दर्भ\s?=+|=+\s?इन्हें भी देखें\s?=+")
        self.citation_regex = re.compile(r"\{\{cite(.*)\}\}")

        # stopwords
        self.stopwords = stopwords.words('english')
        self.load_hindi_stopwords()
        self.stopwords = set(self.stopwords)

        # stemmer
        self.stemmer_en = Stemmer.Stemmer('english')
        self.stemmer_hi = Stemmer.Stemmer('hindi')

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
        toks = []
        for token in tokens:
            toks.extend(token.split("_"))

        toks = [token for token in toks if token not in self.stopwords and len(token) > 1]
        toks = [token for token in toks if not token.isnumeric() or len(token) == 4]
        ret = []
        for token in toks:
            if 'a' <= token[0] <='z' or '0' <= token[0] <='9':
                ret.append(self.stemmer_en.stemWord(token))
            else:
                ret.append(self.stemmer_hi.stemWord(token))
        return ret

    def title_tokens(self, title):
        tokens = self.title_regex.findall(title)
        tokens = self.stopwords_stemmer(tokens)
        return tokens

    def categories_tokens(self, body):
        list = self.categories_regex_en.findall(body)
        list.extend(self.categories_regex_hi.findall(body))
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

    def load_hindi_stopwords(self):
        file = open("hindi_stopwords.txt", "r")
        while True:
            line = file.readline()
            if line == "":
                break
            self.stopwords.extend(line.rstrip("\n").split(" "))
        file.close()
