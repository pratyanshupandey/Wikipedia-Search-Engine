import re
from collections import defaultdict

class Encoder:
    def __init__(self):
        self.base = 52
        self.remainders = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        self.mapping = ['a']
        self.max_mapping = 53000
        self.create_mapping()

    def create_mapping(self):
        for i in range(1,53001):
            basex = ""
            while i:
                basex += self.remainders[i % 52]
                i //= 52
            self.mapping.append(basex)

    def mapper(self, num):
        if num <= self.max_mapping:
            return self.mapping[num]
        basex = ""
        while num:
            basex += self.remainders[num % 52]
            num //= 52
        return basex

    def encode(self, posting):
        encoded = self.mapper(posting[0])
        for i in range(1,7):
            if posting[i]:
                encoded += str(i) + self.mapper(posting[i])
        return encoded



class Decoder:
    def __init__(self):
        self.base = 52
        self.remainders = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
                           's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                           'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        self.rev_map = defaultdict(lambda: -1)
        self.create_rev_map()
        self.num_regex = re.compile("[0-9]")
        self.max_mapping = 53000

    def create_rev_map(self):
        for i in range(1,53001):
            basex = ""
            temp = i
            while i:
                basex += self.remainders[i % 52]
                i //= 52
            self.rev_map[basex] = temp

    def mapper(self, string):
        if self.rev_map[string] != -1:
            return self.rev_map[string]
        multiplier = 1
        num = 0
        for char in string:
            num += self.rev_map[char] * multiplier
            multiplier *= self.base
        return num

    def decode(self, posting_string):
        nums = [self.mapper(num) for num in self.num_regex.split(posting_string)]
        posting = [nums[0], 0,0,0,0,0,0]
        j = 1
        for char in posting_string:
            if char in ['1', '2', '3', '4', '5', '6']:
                posting[int(char)] = nums[j]
                j += 1
        return posting


if __name__ == '__main__':
    encoder = Encoder()
    init = [9098267829,343,232,3434,0,432,1]
    print(init)
    encoded = encoder.encode(init)
    decoder = Decoder()
    decoded = decoder.decode(encoded)
    print(encoded, decoded)