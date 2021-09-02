from collections import defaultdict
import heapq
from preprocessor import TextProcessor
from encoder import Encoder
from html import unescape
import sys
import os

class Index:
    def __init__(self, xml_path, index_path, stats_path):

        # dump specific data
        super().__init__()
        self.xml_path = xml_path
        if index_path[-1] != '/':
            index_path += '/'
        self.index_path = index_path
        self.stats_path = stats_path
        self.all_tokens = set([])
        self.index_num = 0

        # document specific data
        self.body = ""
        self.cur_tag = ""
        self.title = ""
        self.cur_doc = 0

        # current block specific data
        self.map = defaultdict(lambda: [])
        self.local_postings = 0
        self.MAX_LOCAL_POSTINGS = 10000000

        # Setting up the text preprocessor
        self.text_preprocessor = TextProcessor()

        # setting up parsing
        self.data_file = open(self.xml_path, 'r')

        # posting encoder
        self.encoder = Encoder()

    def start_parsing(self):
        self.parse()

    def parse(self):
        while True:
            line = self.data_file.readline()
            if line.find("<page>") != -1:
                title = True
                body = True
                while True:
                    line = self.data_file.readline()
                    if title:
                        pos = line.find("<title>")
                        if pos != -1:
                            self.title = line[pos + 7: line.find("</title>")]
                            title = False
                    if body:
                        pos = line.find("<text")
                        if pos != -1:
                            while line[pos] != ">":
                                pos += 1
                            if line[pos - 1] == "/":
                                self.process_data()
                                break
                            pos += 1
                            end = line.find('</text>')
                            if end != -1:
                                self.body += line[pos:end]
                                self.process_data()
                                break
                            else:
                                self.body += line[pos:]

                            while True:
                                line = self.data_file.readline()
                                end = line.find("</text>")
                                if end != -1:
                                    self.body += line[:end]
                                    self.process_data()
                                    break
                                else:
                                    self.body += line
                            break
            if not line:
                break

    def process_data(self):
        self.title = unescape(self.title.lower())
        self.body = unescape(self.body.lower())

        for tok in self.body.split(" "):
            self.all_tokens.add(tok)
        for tok in self.title.split(" "):
            self.all_tokens.add(tok)

        self.index_content()
        # print(self.cur_doc)
        self.cur_doc += 1
        self.title = ""
        self.body = ""

    def index_content(self):
        # Title, Infobox, Body, Category, Links and References
        title_tokens, body_tokens, references_tokens, category_tokens, infobox_tokens, links_tokens = self.text_preprocessor.process(
            self.title, self.body)
        self.update_map_with(title_tokens, 1)
        self.update_map_with(infobox_tokens, 2)
        self.update_map_with(body_tokens, 3)
        self.update_map_with(category_tokens, 4)
        self.update_map_with(links_tokens, 5)
        self.update_map_with(references_tokens, 6)

        if self.local_postings > self.MAX_LOCAL_POSTINGS:
            self.write_to_file()

    def finish_indexing(self):
        if self.local_postings > 0:
            self.write_to_file()
        self.data_file.close()

    def write_to_file(self):
        # print("creating index" + str(self.index_num) + "...")
        file = open(self.index_path + "index", 'w+')

        for tokenid in sorted(self.map.keys()):
            posting_list = str(tokenid)
            for posting in self.map[tokenid]:
                posting_list += " " + self.encoder.encode(posting)
            posting_list += '\n'

            file.write(posting_list)

        file.close()
        self.index_num += 1

        stat_file = open(self.stats_path, "w+")
        stat_file.write(str(len(self.all_tokens)) + "\n" + str(len(self.map)) + "\n")
        stat_file.close()

        self.map = defaultdict(lambda: [])
        self.all_tokens = set()
        self.local_postings = 0

    def update_map_with(self, tokens, pos):
        for token in tokens:
            if not self.map[token]:
                self.map[token] = [[self.cur_doc, 0, 0, 0, 0, 0, 0]]
                self.local_postings += 1
            elif self.map[token][-1][0] != self.cur_doc:
                self.map[token].append([self.cur_doc, 0, 0, 0, 0, 0, 0])
                self.local_postings += 1

            self.map[token][-1][pos] += 1

    def reset_xmlread(self):
        self.body = ""
        self.cur_tag = ""
        self.title = ""

    def merge(self):
        files = []
        min_heap = []
        listings = []
        finalIndex = open(self.index_path + "finalindex", "w+")
        for i in range(self.index_num):
            files.append(open(self.index_path + "index" + str(i), "r"))
            listing = files[i].readline().split(" ")
            listings.append(listing)
            heapq.heappush(min_heap, [listing[0], i])

        while (True):
            token, i = heapq.heappop(min_heap)
            while (min_heap[0][0] == token):
                pass


if __name__ == '__main__':
    if not os.path.exists(sys.argv[1]):
        print("Invalid path to dump")
    else:
        if not os.path.exists(sys.argv[2]):
            os.makedirs(sys.argv[2])
        index = Index(sys.argv[1], sys.argv[2], sys.argv[3])
        index.start_parsing()
        index.finish_indexing()
