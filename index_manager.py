from collections import defaultdict
import heapq
from preprocessor import TextProcessor
from encoder import Encoder
from html import unescape
import sys
import os

class Index:
    def __init__(self, xml_path, index_path, stats_path, title_path, len_path, info_path):

        # dump specific data
        super().__init__()
        self.xml_path = xml_path
        if index_path[-1] != '/':
            index_path += '/'
        self.index_path = index_path
        self.stats_path = stats_path
        self.title_file = open(title_path, "w+")
        self.size_file = open(len_path, "w+")
        self.info_path = info_path

        self.index_num = 0
        self.temp_num = 0
        self.MAX_INDEX_POSTINGS = 1000000

        # stats forBM25
        self.length_sum = [0, 0, 0, 0, 0, 0]

        # document specific data
        self.body = ""
        self.cur_tag = ""
        self.title = ""
        self.cur_doc = 0

        # current block specific data
        self.map = defaultdict(lambda: [])
        self.local_postings = 0
        self.MAX_LOCAL_POSTINGS = 100000

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

        self.title_file.write(str(self.cur_doc) + " " + self.title + "\n")

        self.title = unescape(self.title.lower())
        self.body = unescape(self.body.lower())

        self.index_content()
        print(self.cur_doc)
        self.cur_doc += 1
        self.title = ""
        self.body = ""

    def index_content(self):
        # Title, Infobox, Body, Category, Links and References
        title_tokens, body_tokens, references_tokens, category_tokens, infobox_tokens, links_tokens = self.text_preprocessor.process(
            self.title, self.body)

        # adding lenghts and storing lengths for each document
        self.size_file.write(str(self.cur_doc) + " " + str([len(title_tokens), len(infobox_tokens), len(body_tokens), len(category_tokens), len(links_tokens), len(references_tokens)]) + "\n")

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
        self.size_file.close()
        self.title_file.close()
        self.merge()


    def write_to_file(self):
        # print("creating index" + str(self.index_num) + "...")
        file = open(self.index_path + "temp" + str(self.temp_num), 'w+')

        for tokenid in sorted(self.map.keys()):
            posting_list = str(tokenid)
            for posting in self.map[tokenid]:
                posting_list += " " + self.encoder.encode(posting)
            posting_list += '\n'

            file.write(posting_list)

        file.close()
        self.temp_num += 1

        self.map = defaultdict(lambda: [])
        self.local_postings = 0

    def update_map_with(self, tokens, pos):

        self.length_sum[pos-1] += len(tokens)

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
        token_count = 0
        postings_len = 0

        temp_files = [open(self.index_path + "temp" + str(val), 'r') for val in range(self.temp_num)]
        index_file = open(self.index_path + "index" + str(self.index_num), "w+")

        token_min_heap = []
        heapq.heapify(token_min_heap)
        postings = ["" for _ in range(self.temp_num)]

        for i in range(len(temp_files)):
            line = temp_files[i].readline().split(" ", 1)
            heapq.heappush(token_min_heap, [line[0], i])
            postings[i] = line[1].rstrip("\n")

        popped = []
        cur_token = token_min_heap[0][0]
        cur_file = 0
        cur_posting = ""

        while len(token_min_heap):
            if token_min_heap[0][0] != cur_token:
                index_file.write(cur_token + cur_posting + "\n")
                postings_len += len(cur_token) + len(cur_posting) + 2
                token_count += 1
                cur_posting = ""
                if postings_len >= self.MAX_INDEX_POSTINGS:
                    postings_len = 0
                    index_file.close()
                    self.index_num += 1
                    index_file = open(self.index_path + "index" + str(self.index_num), "w+")

            popped = heapq.heappop(token_min_heap)
            cur_token = popped[0]
            cur_file = popped[1]
            cur_posting += " " + postings[cur_file]

            if temp_files[cur_file] is not None:
                line = temp_files[cur_file].readline()
                if line is None:
                    temp_files[cur_file].close()
                    temp_files[cur_file] = None
                else:
                    line = line.split(" ", 1)
                    if len(line) > 1:
                        heapq.heappush(token_min_heap, [line[0], cur_file])
                        # print(line)
                        postings[cur_file] = line[1].rstrip("\n")

        index_file.write(cur_token + " " + cur_posting + "\n")
        token_count += 1
        index_file.close()

        info_file = open(self.info_path , "w+")
        info_file.write(str(self.cur_doc) + "\n")
        info_file.write(str(token_count) + "\n")
        info_file.write(str(self.index_num) + "\n")
        info_file.close()

if __name__ == '__main__':
    index = Index("enwiki-20210720-pages-articles-multistream.xml", "index", "invertedindex_stat.txt", "index/titles", "index/lengths", "index/info")
    index.start_parsing()
    index.finish_indexing()
