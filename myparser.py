
class Parser:
    def __init__(self, path):
        self.file = open(path, 'r')
        self.doc_id = 0
        self.title = ""
        self.body = ""

    def parse(self):
        while True:
            line = self.file.readline()
            if 0 < len(line) < 15 and line.find("<page>") != -1:
                title = True
                body = True
                while True:
                    line = self.file.readline()
                    if title:
                        pos = line.find("<title>")
                        if(pos != -1):
                            self.title = line[pos + 7: line.find("</title>")]
                            title = False
                    if body:
                        pos = line.find("<text")
                        if pos != -1:
                            end = line.find("</text>")
                            if end != -1:
                                self.body += line[pos:end]
                                self.doc_id += 1
                                print(self.doc_id)
                                self.title = ""
                                self.body = ""
                            while True:
                                line = self.file.readline()
                                end = line.find("</text>")
                                if end != -1:
                                    self.body += line[pos:end]
                                    self.doc_id += 1
                                    print(self.doc_id)
                                    self.title = ""
                                    self.body = ""
                                    break
                                else:
                                    self.body += line
                            break
            if not line:
                break

Parser("data").parse()
