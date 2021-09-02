import xml.sax

class Index(xml.sax.handler.ContentHandler):
    def __init__(self, xml_path):

        # dump specific data
        super().__init__()
        self.docs = 0
        self.xml_path = xml_path

        # document specific data
        self.body = ""
        self.cur_tag = ""
        self.title = ""
        self.cur_doc = 0

        # setting up parsing
        self.parser = xml.sax.make_parser()
        self.parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        self.parser.setContentHandler(self)


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
            # self.reset_xmlread()
            self.body = ""
            self.title = ""

    def characters(self, content):
        if self.cur_tag == 'title':
            self.title += content
        if self.cur_tag == 'text':
            self.body += content

    def start_parsing(self):
        self.parser.parse(self.xml_path)

    def reset_xmlread(self):
        self.body = ""
        self.cur_tag = ""
        self.title = ""

ind = Index("data")
ind.start_parsing()
