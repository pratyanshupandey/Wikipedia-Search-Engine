from encoder import Decoder
from queryprocessor import QueryProcessor
from collections import defaultdict
import json

class Search:
    def __init__(self, path):

        self.index_path = path

        self.query_processor = QueryProcessor()

        self.decoder = Decoder()

        self.answer = defaultdict(lambda: {})

    def reset(self):
        self.answer = defaultdict(lambda: {})

    def search(self, query_string):
        parts = query_string.split(" ")
        qtokens = []
        for query in parts:
            tokens = self.query_processor.process(query)
            for tok in tokens:
                qtokens.append([tok, query])
        qtokens.sort()
        self.print_result(qtokens, self.find(qtokens))
        self.reset()

    def find(self, qtokens):
        ind = 0
        length = len(qtokens)
        cur_len = len(qtokens[ind][0])
        postings_list = []

        file = open(self.index_path, "r")

        while(ind < length):
            line = file.readline().strip("\n")
            if qtokens[ind][0] == line[:cur_len]:
                postings_list.append(line)
                ind += 1
                if ind < length:
                    cur_len = len(qtokens[ind][0])
        file.close()
        return postings_list

    def print_result(self, qtokens, postings_list):
        for i in range(len(qtokens)):
            query = qtokens[i][1]
            posting = postings_list[i]
            self.add(query, posting)
        print(json.dumps(self.answer, indent=4))

    def add(self,query, posting):
        if self.answer[query] == {}:
            self.answer[query] = {
                "title": [],
                "body": [],
                "infobox": [],
                "categories": [],
                "references": [],
                "links": []
            }
        for ele in posting.split(" ")[1:]:
            doc = self.decoder.decode(ele)
            if doc[1]:
                self.answer[query]["title"].append(doc[0])
            if doc[2]:
                self.answer[query]["infobox"].append(doc[0])
            if doc[3]:
                self.answer[query]["body"].append(doc[0])
            if doc[4]:
                self.answer[query]["categories"].append(doc[0])
            if doc[5]:
                self.answer[query]["links"].append(doc[0])
            if doc[6]:
                self.answer[query]["references"].append(doc[0])

if __name__ == '__main__':
    search = Search("index/index0")
    search.search("lake")




