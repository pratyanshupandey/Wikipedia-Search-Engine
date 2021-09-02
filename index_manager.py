import sys
import os
import xml.sax
from collections import defaultdict
import heapq
from preprocessor import TextProcessor
import json
from encoder import Encoder


class Index(xml.sax.handler.ContentHandler):
    def __init__(self, xml_path, index_path):

        # dump specific data
        super().__init__()
        self.docs = 0
        self.xml_path = xml_path
        self.index_path = index_path
        self.vocabulary = defaultdict(lambda: [])
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
        self.parser = xml.sax.make_parser()
        self.parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        self.parser.setContentHandler(self)

        # posting encoder
        self.encoder = Encoder()

    def startElement(self, name, attrs):
        self.cur_tag = name

    def endElement(self, name):
        if name == 'page':
            # if self.cur_doc != 28307:
            #     self.index_content()
            self.cur_doc += 1
            # print(self.cur_doc)
            # if self.cur_doc == 28307:
            #     print(self.title)
            self.reset_xmlread()

    def characters(self, content):
        if self.cur_tag == 'title':
            self.title += content
        if self.cur_tag == 'text':
            self.body += content

    def start_parsing(self):
        self.parser.parse(self.xml_path)

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
        # file = open(self.index_path + "vocabulary.json", 'w+')
        # json.dump(self.map, file)
        # file.close()

    def write_to_file(self):
        print("creating index" + str(self.index_num) + "...")
        file = open(self.index_path + "index" + str(self.index_num), 'w+')

        for tokenid in sorted(self.map.keys()):
            posting_list = str(tokenid)
            for posting in self.map[tokenid]:
                posting_list += " " + self.encoder.encode(posting)
                # if posting[1] != 0:
                #     posting_list += "t" + str(posting[1])
                # if posting[2] != 0:
                #     posting_list += "i" + str(posting[2])
                # if posting[3] != 0:
                #     posting_list += "b" + str(posting[3])
                # if posting[4] != 0:
                #     posting_list += "c" + str(posting[4])
                # if posting[5] != 0:
                #     posting_list += "l" + str(posting[5])
                # if posting[6] != 0:
                #     posting_list += "r" + str(posting[6])
            posting_list += '\n'

            file.write(posting_list)

        file.close()
        self.index_num += 1
        self.map = defaultdict(lambda: [])
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
    index = Index("data", "./index/")
    index.start_parsing()
    index.finish_indexing()
    # index.merge()
