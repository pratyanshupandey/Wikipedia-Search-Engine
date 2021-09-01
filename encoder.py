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
            encoded += str(i) + self.mapper(posting[i])
        return encoded



class Decoder:
    def __init__(self):
        self.base = 26
        self.mapping = []
        self.create_mapping()

    def create_mapping(self):
        pass

    def decode(self, posting):
        pass

if __name__ == '__main__':
    encoder = Encoder()
    print(encoder.encode([12,3,4,5,0,9,4]))