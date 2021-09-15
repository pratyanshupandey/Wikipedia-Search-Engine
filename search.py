from encoder import Decoder
from queryprocessor import QueryProcessor
from collections import defaultdict
import json
import sys
import os


class Search:
    def __init__(self, index_path, range_path, doc_nums, length_path):
        if index_path[-1] != "/":
            index_path += "/"
        self.index_path = index_path + "index"
        range_file = open(range_path, "r")
        dict = json.load(range_file)
        self.ranges = dict["ranges"]
        self.doc_nums = doc_nums
        self.length_avg = [length / doc_nums for length in dict["length_sums"]]
        self.lengths = []
        self.load_length(length_path)

        self.weights = [5,2,1,1,1,1]

        self.query_processor = QueryProcessor()

        self.decoder = Decoder()

        self.answer = defaultdict(lambda: {})

        self.b_c = 1
        self.k_1 = 1.2

        self.TITLES = 10000

        self.doc_scores = defaultdict(lambda: 0)
        self.MAX_RESULT = 10

    def reset(self):
        self.doc_scores = defaultdict(lambda: 0)

    def get_qtokens(self, query_string):
        qtokens = self.query_processor.process(query_string)
        qtokens = list(set(qtokens))
        qtokens.sort()
        return qtokens

    def search(self, query_string):
        qtokens = self.get_qtokens(query_string)
        posting_list = self.find_in_index(qtokens)          # posting list for every qtoken undecoded
        self.calc_tf_idf(posting_list)

        result_docs = [doc_id for doc_id,score in sorted(self.doc_scores.items(), key=lambda x: x[1], reverse = True)[:self.MAX_RESULT]]
        self.print_result(result_docs)

    def get_title(self, doc_id):
        title_file = doc_id // self.TITLES
        file = open(self.index_path + "titles" + str(title_file))
        while True:
            line = file.readline()
            if line is None:
                break
            if str(doc_id) == line[:len(str(doc_id))]:
                file.close()
                return line.rstrip("\n").split(" ", 1)[1]
        return ""

    def calc_tf_idf(self, posting_list):
        # posting_list can be "" to denote no tokens found

        for posting in posting_list: ## or qtok in qtokens
            if posting == "":
                continue
            docs = posting.split(" ")
            idf_score = (self.doc_nums - len(docs) + 0.5)/(len(docs) + 0.5) + 1

            for doc in docs:    # docid t i b c l r
                post = self.decoder.decode(doc)
                doc_id = post[0]
                tf_score = 0
                for i in range(1,7):
                    tf_score += self.weights[i-1] * ( post[i] / (1 + self.b_c * (self.lengths[doc_id][i-1]/self.length_avg[i-1] - 1)))
                if self.doc_scores[doc_id] == 0:
                    self.doc_scores[doc_id] = (tf_score * idf_score)/ (self.k_1 + tf_score)
                else:
                    self.doc_scores[doc_id] += (tf_score * idf_score)/ (self.k_1 + tf_score)



    def binary_search(self, target, low, high):
        while high - low > 1:
            mid = (low + high) // 2
            if self.ranges[mid][0] <= target <= self.ranges[mid][1]:
                return mid
            elif target < self.ranges[mid][0]:
                high = mid - 1
            else:
                low = mid + 1
        if self.ranges[low][0] <= target <= self.ranges[low][1]:
            return low
        elif self.ranges[high][0] <= target <= self.ranges[high][1]:
            return high
        else:
            return -1

    def find_in_index(self, qtokens):
        posting_list = []
        low = 0
        high = len(self.ranges) - 1

        i = 0
        while i < len(qtokens):
            ind = self.binary_search(qtokens[i],low, high)

            if ind == -1:
                posting_list.append("")
                i += 1
                continue

            low = ind
            index_file = open(self.index_path + "index" + str(ind), 'r')
            while qtokens[i] <= self.ranges[ind][1]:
                while True:
                    line = index_file.readline()
                    if qtokens[i] <= line[:len(qtokens[i])]:
                        if qtokens[i] == line[:len(qtokens[i])]:
                            posting_list.append(line.rstrip("\n").split(" ", 1)[1])
                            i += 1
                            break
                        else:
                            posting_list.append("")
                            i += 1
                            if qtokens[i] == line[:len(qtokens[i])]:
                                posting_list.append(line.rstrip("\n").split(" ", 1)[1])
                                i += 1
                            break

            index_file.close()

        return posting_list

    def print_result(self, result_docs):
        for doc_id in result_docs:
            title = self.get_title(doc_id)
            print(str(doc_id) + ", " + title)


    def load_length(self, length_path):
        length_file = open(length_path, 'r')
        while True:
            line = length_file.readline()
            if line is None:
                break
            self.lengths.append(json.loads(line.split(" ", 1)[1]))


if __name__ == '__main__':
    search = Search("prev_data", 44, 52612, "prev_data/lengths")
    search.search(input())
    while True:
        more = input("More searching:")
        if more == 'n':
            break
        search.search(input())
