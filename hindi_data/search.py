from encoder import Decoder
from queryprocessor import QueryProcessor
from collections import defaultdict
import json
import math


class Search:
    def __init__(self, config_path):

        config_file = open(config_path, "r")
        paths = json.load(config_file)
        config_file.close()

        self.index_path = paths["index_path"] + "index"
        self.info_path = paths["info_path"]
        file = open(paths["info_path"] + "doc_info.json", "r")
        doc_info = json.load(file)
        file.close()
        self.lengths = doc_info["lengths"]
        self.length_avg = [l_sum / doc_info["docs"] for l_sum in doc_info["length_sum"]]
        self.MAX_TITLES = doc_info["max_titles"]
        self.doc_nums = doc_info["docs"]

        file = open(paths["info_path"] + "index_info.json", "r")
        index_info = json.load(file)
        self.ranges = index_info["term_ranges"]
        file.close()

        self.weights = [5, 2, 1, 1, 1, 1]
        self.boost = 10

        self.query_processor = QueryProcessor()

        self.decoder = Decoder()

        self.answer = defaultdict(lambda: {})

        self.b_c = 0.75
        self.k_1 = 1.2

        self.doc_scores = defaultdict(lambda: 0.0)
        self.MAX_RESULT = 10

    def reset(self):
        self.doc_scores = defaultdict(lambda: 0)

    def get_qtokens(self, query_string):
        qtokens = self.query_processor.process(query_string)
        qtokens.sort()
        return [qtok[0] for qtok in qtokens], [qtok[1] for qtok in qtokens]

    def search(self, query_string):
        qtokens, qtok_types = self.get_qtokens(query_string)
        if qtokens  == []:
            print("No results for this query")
            return

        posting_list = self.find_in_index(qtokens)  # posting list for every qtoken undecoded
        self.calc_tf_idf(posting_list, qtok_types)

        result_docs = [doc_id for doc_id, score in sorted(self.doc_scores.items(), key=lambda x: x[1], reverse=True)][
                      :self.MAX_RESULT]
        self.print_result(result_docs)
        self.reset()

    def get_title(self, doc_id):
        title_file = doc_id // self.MAX_TITLES
        file = open(self.info_path + "titles/" + str(title_file))
        offset = doc_id % self.MAX_TITLES
        i = 0
        while True:
            line = file.readline()
            if line == "":
                break
            if i == offset:
                if str(doc_id) == line[:len(str(doc_id))]:
                    file.close()
                    return line.rstrip("\n").split(" ", 1)[1]
                else:
                    print("Error in getting title")
                    return ""
            i += 1

        file.close()
        return ""

    def calc_tf_idf(self, posting_list, qtok_types):
        # posting_list can be "" to denote no tokens found

        for posting,qtok_type in zip(posting_list, qtok_types):  # or qtok in qtokens
            if posting == "":
                continue
            docs = posting.split(" ")
            idf_score = math.log(((self.doc_nums - len(docs) + 0.5) / (len(docs) + 0.5)) + 1)

            for doc in docs:  # docid t i b c l r
                post = self.decoder.decode(doc)
                doc_id = post[0]
                tf_score = 0
                for i in range(1, 7):
                    if qtok_type[i]:
                        tf_score += self.boost * self.weights[i - 1] * (
                                post[i] / (1 + self.b_c * (self.lengths[doc_id][i - 1] / self.length_avg[i - 1] - 1)))
                    else:
                        tf_score += self.weights[i - 1] * (
                                post[i] / (1 + self.b_c * (self.lengths[doc_id][i - 1] / self.length_avg[i - 1] - 1)))

                if self.doc_scores[doc_id] == 0.0:
                    self.doc_scores[doc_id] = (tf_score * idf_score) / (self.k_1 + tf_score)
                else:
                    self.doc_scores[doc_id] += (tf_score * idf_score) / (self.k_1 + tf_score)

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
            ind = self.binary_search(qtokens[i], low, high)

            if ind == -1:
                posting_list.append("")
                i += 1
                continue

            low = ind
            index_file = open(self.index_path + str(ind), 'r')
            while i < len(qtokens) and qtokens[i] <= self.ranges[ind][1]:
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
                            if i < len(qtokens) and qtokens[i] == line[:len(qtokens[i])]:
                                posting_list.append(line.rstrip("\n").split(" ", 1)[1])
                                i += 1
                            break

            index_file.close()

        return posting_list

    def print_result(self, result_docs):
        if result_docs == []:
            print("No search results for this query.")
            return
        for doc_id in result_docs:
            title = self.get_title(doc_id)
            print(str(doc_id) + ", " + title)


if __name__ == '__main__':
    config_path = "config.json"
    query_path = "queries.txt"

    search_engine = Search(config_path)

    while True:
        query = input("Q: ")
        search_engine.search(query)

    # queries = open(query_path, "r")
    # query_list = queries.readlines()
    # for query in query_list:
    #     query = query.rstrip("\n")
    #     print("Query: ")
    #     print("Results: ")
    #     search_engine.search(query)
    #     print("\n\n\n")
