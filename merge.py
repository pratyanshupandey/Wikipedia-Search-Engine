import heapq
import json


def merge(index_path, info_path, range_path):
    token_count = 0
    postings_len = 0
    index_num = 0
    cur_doc = 21384756
    temp_num = 24318
    MAX_INDEX_POSTINGS = 1000000

    temp_files = [open(index_path + "temp" + str(val), 'r') for val in range(temp_num)]
    index_file = open(index_path + "index" + str(index_num), "w+")

    token_min_heap = []
    heapq.heapify(token_min_heap)
    postings = ["" for _ in range(temp_num)]

    for i in range(len(temp_files)):
        line = temp_files[i].readline().split(" ", 1)
        heapq.heappush(token_min_heap, [line[0], i])
        postings[i] = line[1].rstrip("\n")

    popped = []
    cur_token = token_min_heap[0][0]
    term_range = [[cur_token, ""]]
    cur_file = 0
    cur_posting = ""

    while len(token_min_heap):
        if token_min_heap[0][0] != cur_token:
            index_file.write(cur_token + cur_posting + "\n")
            postings_len += len(cur_token) + len(cur_posting) + 2
            token_count += 1
            cur_posting = ""
            if term_range[-1][1] != "":
                term_range.append([cur_token, ""])
            if postings_len >= MAX_INDEX_POSTINGS:
                postings_len = 0
                index_file.close()
                print(index_num)
                term_range[-1][1] = cur_token
                index_num += 1
                index_file = open(index_path + "index" + str(index_num), "w+")

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

    info_file = open(info_path, "w+")
    info_file.write(str(cur_doc) + "\n")
    info_file.write(str(token_count) + "\n")
    info_file.write(str(index_num) + "\n")
    info_file.close()

    range_file = open(range_path, "w+")
    json.dump({"ranges": term_range}, range_file)
    range_file.close()


merge("index/", "index/info", "index/range")
