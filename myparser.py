from html import unescape

class Parser:
    def __init__(self, path):
        self.file = open(path, 'r')
        self.doc_id = 0
        self.title = ""
        self.body = ""
        self.title_write = open("index/titlemy", "w+")
        self.body_write = open("index/bodymy", "w+")

    def parse(self):
        while True:
            line = self.file.readline()
            if line.find("<page>") != -1:
                title = True
                body = True
                while True:
                    line = self.file.readline()
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
                            if line[pos-1] == "/":
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
                                line = self.file.readline()
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
        self.title = unescape(self.title)
        self.body = unescape(self.body)
        self.title_write.write(str(self.doc_id) + " " + self.title + "\n")
        self.body_write.write(str(self.doc_id) + " " + self.body + "\n")
        print(self.doc_id)
        self.doc_id += 1
        self.title = ""
        self.body = ""

ps = Parser("data")
ps.parse()
ps.title_write.close()
ps.body_write.close()

