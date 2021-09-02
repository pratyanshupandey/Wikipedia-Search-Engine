import re
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import time
# import nltk
# >>> nltk.download('wordnet')
# >>> nltk.download('stopwords')

class TextProcessor:
    def __init__(self):
        # regex specific data
        self.title_regex = re.compile(r"[a-zA-Z0-9]+")
        self.token_regex = re.compile(r"[a-zA-Z0-9]+")
        self.remove_regex = re.compile(r"[0-9]+[a-z]+[a-z0-9]*")
        self.infobox_regex = re.compile(r"{{infobox")
        self.body_regex = re.compile(r"[a-zA-Z0-9]+")
        self.links_regex = re.compile(r"(http|https)://\S+")
        self.categories_regex = re.compile(r"\[\[category:(.*)\]\]")
        self.external_regex = re.compile(r"=+external links=+")
        self.reference_regex = re.compile(r"=+references=+|=+notes=+|=+footnotes=+")
        self.citation_regex = re.compile(r"\{\{cite(.*)\}\}")

        # stopwords
        self.stopwords = set(stopwords.words('english'))

        # stemmer
        self.stemmer = SnowballStemmer('english')
        self.lem = WordNetLemmatizer()

        # sections processed under other already
        self.already_proc = []

    def reset(self):
        self.already_proc = []

    def process(self, title, body):

        title = title.lower()
        title_tokens = self.title_tokens(title)




        body = body.lower()
        body_len = len(body)


        infobox_tokens = self.infobox_tokens(body, body_len)




        category_tokens = self.categories_tokens(body)


        reference_tokens = self.reference_tokens(body, body_len)



        external_links_tokens = self.external_links_tokens(body, body_len)



        self.already_proc.sort()
        body_tokens = self.body_tokens(body, body_len)


        self.reset()

        return title_tokens, body_tokens, reference_tokens, category_tokens, infobox_tokens, external_links_tokens

    def stopwords_stemmer(self, tokens):
        tokens = [token for token in tokens if token not in self.stopwords]
        # print("start",time.time())
        # tokens2 = [self.stemmer.stem(token) for token in tokens]
        # print("stem done",time.time())
        # tokens3 = [self.lem.lemmatize(token) for token in tokens]
        # print("lem done", time.time())
        return tokens

    def title_tokens(self, title):
        tokens = self.title_regex.findall(title)
        tokens = self.stopwords_stemmer(tokens)
        return tokens

    def categories_tokens(self, body):
        list = self.categories_regex.findall(body)
        tokens = []
        for element in list:
            tokens.extend(self.token_regex.findall(element))
        tokens = self.stopwords_stemmer(tokens)
        return tokens

    def infobox_tokens(self, body, body_len):
        list = [(m.start(0), m.end(0)) for m in self.infobox_regex.finditer(body)]
        tokens = []
        for start, end in list:
            depth = 0
            temp = start
            while (True):
                if temp + 1 < body_len and body[temp] == "{" and body[temp + 1] == "{":
                    temp += 1
                    depth += 1
                elif temp + 1 < body_len and body[temp] == "}" and body[temp + 1] == "}":
                    temp += 1
                    depth -= 1
                if depth == 0 or temp >= body_len:
                    if temp > body_len:
                        temp = body_len
                    self.already_proc.append((start, temp))
                    tokens.extend(self.token_regex.findall(body[end:temp]))
                    break
                temp += 1

        tokens = self.stopwords_stemmer(tokens)
        return tokens

    def external_links_tokens(self, body, body_len):
        tokens = []
        list = [(m.start(0), m.end(0)) for m in self.external_regex.finditer(body)]
        for start, end in list:
            temp = end
            while (True):
                if temp + 1 >= body_len or ((body[temp] == "=" and body[temp + 1] == "=") or (
                        body[temp] == "\n" and body[temp + 1] == "\n")):
                    temp += 1
                    if temp + 1 >= body_len:
                        temp = body_len
                    self.already_proc.append((start, temp))
                    split_by_links = self.links_regex.split(body[end:temp])
                    for section in split_by_links:
                        tokens.extend(self.token_regex.findall(section))
                    break
                temp += 1

        tokens = self.stopwords_stemmer(tokens)
        return tokens

    def reference_tokens(self, body, body_len):
        # in form of citations
        list = self.citation_regex.findall(body)
        tokens = []
        for element in list:
            tokens.extend(self.token_regex.findall(element))

        # as list under references
        list = [(m.start(0), m.end(0)) for m in self.reference_regex.finditer(body)]
        for start, end in list:
            temp = end
            while (True):
                if temp + 1 >= body_len or ((body[temp] == "=" and body[temp + 1] == "=") or (
                        body[temp] == "\n" and body[temp + 1] == "\n")):
                    temp += 1
                    if temp + 1 >= body_len:
                        temp = body_len
                    self.already_proc.append((start, temp))
                    tokens.extend(self.token_regex.findall(body[end:temp]))
                    break
                temp += 1

        tokens = self.stopwords_stemmer(tokens)
        return tokens

    def body_tokens(self, body, body_len):
        tokens = []
        aplen = len(self.already_proc)

        if aplen < 1:
            tokens = self.token_regex.findall(body)
        else:
            tokens.extend(self.title_regex.findall(body, 0, self.already_proc[0][0]))
            for i in range(1,aplen):
                if self.already_proc[i][0] > self.already_proc[i-1][1] and self.already_proc[i-1][1] < body_len:
                    tokens.extend(self.title_regex.findall(body, self.already_proc[i-1][1],self.already_proc[i][0]))
            tokens.extend(self.title_regex.findall(body, self.already_proc[-1][1], body_len))

        tokens = self.stopwords_stemmer(tokens)
        return tokens


if __name__ == '__main__':
    tp = TextProcessor()
    title = "Vickers Vagabond"
    body = """&lt;!-- This article is a part of [[Wikipedia:WikiProject Aircraft]]. Please see [[Wikipedia:WikiProject Aircraft/page content]] for recommended layout. --&gt;
{{Use dmy dates|date=September 2017}}
{{Use British English|date=September 2017}}
{|{{Infobox Aircraft Begin
 | name=Vagabond
 | image=Vickers Vagabond.jpg
 | caption=
}}{{Infobox Aircraft Type
 | type=Two-seat light aircraft
 | national origin=[[United Kingdom]]
 | manufacturer=[[Vickers]]
 | designer=[[Rex Pierson|R.K. Pierson]]
 | first flight=1924
 | introduced=
 | retired=
 | status=
 | primary user=
 | number built=1
 | developed from= 
 | variants with their own articles=
}}
|}
The '''Vickers Vagabond''' was [[Vickers]]' entrant for the second Lympne light aircraft competition, held in 1924.  It was a conventional small [[biplane]], with a very unusual method of trimming.  It was eliminated from the trials at an early stage and only one was built.

==Development==
Following the first Lympne trials held in 1923 for single-seat motor-gliders, the [[Air Ministry]] organised a similar event in 1924, this time for low-powered two-seat aircraft.  The engine capacity limit was set at 1,100 cc. and, as before, the wings had to fold for easy transport and storage.  The trials took place between 29 September and 4&amp;nbsp;October.  Several companies built aircraft for them, including the [[Blackburn Bluebird]], [[Hawker Cygnet]], [[Supermarine Sparrow]] and two from Westland, the [[Westland Woodpigeon|Woodpigeon]] and [[Westland Widgeon (fixed wing)|Widgeon]].

The Type 98 Vagabond was Vickers' entry. It was a single-bay, wire-braced biplane with wings of constant chord except towards the rounded trailing tips.  The wings had equal span and carried marked stagger. There were ailerons on both upper and lower wings, with flaps inboard on the lower wings which could be folded to assist wing-folding.  The pilot and passenger sat in open cockpits, the latter under the upper wing.  The pilot's upward view was enhanced by a small cutout in the trailing edge of the top wing.  The fuselage had a more rounded cross-section than that of the earlier [[Vickers Viget|Viget]], Vickers' single-seat entry to the 1923 competition, extending a little below the lower wing.  The 32&amp;nbsp;hp (24&amp;nbsp;kW)  [[Bristol Cherub]] III flat twin engine was mounted in a smooth nose with the finned cylinders exposed for air cooling.  The horizontal tail was similar to that of the Viget, but the fin and rudder were much more rounded.  Because of the stagger, the mainwheels were in front of the lower wing, braced to the lower fuselage logeron aft to the front wing spar and forward to a point roughly below the upper wing leading edge.&lt;ref name=&quot;Andrews&quot;&gt;{{Harvnb|Andrews|Morgan|1988|pages=481–82}}&lt;/ref&gt;&lt;ref&gt;{{harvnb|''Flight'' 25 September 1924|pp=617–620}}&lt;/ref&gt;

A most unusual feature of the Vagabond was the method of longitudinal trimming.  Rather than changing the angle of the tailplane with respect to the fuselage, the whole rear part of the fuselage was hinged just ahead of the lower wing's trailing edge.  This was controlled via a handwheel between the two cockpits; the rear fuselage was raised at the start of a landing descent to increase drag and slow the aircraft.&lt;ref name=&quot;Andrews&quot;/&gt;

Early flight trials, with H.J.Pain as pilot revealed a need to stiffen the engine mountings.&lt;ref name=&quot;Andrews&quot;/&gt;  When this was done, the Vagabond, now fitted with a three-cylinder 1,095 cc [[Blackburne Thrush]] radial engine flew well enough at Lympne, but was eliminated in the preliminary rounds.  Only one Vagabond, registered  as ''G-EBJF'' on 1 July 1924&lt;ref&gt;[http://www.caa.co.uk/application.aspx?catid=60&amp;pagetype=65&amp;appid=1&amp;mode=detailnosummary&amp;fullregmark=EBJF  CAA]&lt;/ref&gt; was built.  It was deregistered on 24 January 1928.
&lt;!-- ==Operational history== --&gt;
&lt;!-- ==Variants== --&gt;
&lt;!-- ==Units using this aircraft/Operators (choose)== --&gt;

==Specifications==
[[File:Vickers_Vagabond_3-view_NACA-TM-289.jpg|thumb|Vickers Vagabond 3-view drawing from NACA-TM-289]]
{{Aircraft specs
|ref=&lt;ref&gt;{{Harvnb|Andrews|Morgan|1988|p=482}}&lt;/ref&gt;&lt;!-- the reference for the data given --&gt;
|prime units?=imp
&lt;!--
        General characteristics
--&gt;
|genhide= 

|crew=1
|capacity=1 passenger
|length m=
|length ft=21
|length in=10
|span m=
|span ft=28
|span in=0
|width ft=10&lt;!-- if applicable --&gt;
|width in=0&lt;!-- if applicable --&gt;
|width note=(width wings folded)&lt;ref&gt;{{harvnb|''Flight'' 25 September 1924|p=618}}&lt;/ref&gt;
|height m=
|height ft=
|height in=
|wing area sqm=
|wing area sqft=235
|empty weight kg=
|empty weight lb=527
|gross weight kg=
|gross weight lb=887
|fuel capacity=
&lt;!--
        Powerplant
--&gt;
|eng1 number=1
|eng1 name=[[Bristol Cherub]] III 
|eng1 type=flat twin
|eng1 kw=&lt;!-- prop engines --&gt;
|eng1 hp=32&lt;!-- prop engines --&gt;

|prop blade number=&lt;!-- propeller aircraft --&gt;
|prop name=
|prop dia m=&lt;!-- propeller aircraft --&gt;
|prop dia ft=&lt;!-- propeller aircraft --&gt;
|prop dia in=&lt;!-- propeller aircraft --&gt;

&lt;!--
        Performance
--&gt;
|perfhide=

|max speed kmh=
|max speed mph=77
|max speed kts=
|max speed mach=&lt;!-- supersonic aircraft --&gt;
|cruise speed kmh=&lt;!-- if max speed unknown --&gt;
|cruise speed mph=&lt;!-- if max speed unknown --&gt;
|cruise speed kts=
|range km=
|range miles=
|range nmi=
|ceiling m=
|ceiling ft=
|climb rate ms=
|climb rate ftmin=
|more performance=

|avionics=
}}
&lt;!-- ==See also== --&gt;
{{aircontent
&lt;!-- include as many lines are appropriate. additional lines/entries with carriage return. --&gt;
|see also=
|related=&lt;!-- related developments --&gt;
|similar aircraft=&lt;!-- similar or comparable aircraft --&gt;
|lists=&lt;!-- related lists --&gt;
}}

==References==
{{commons category|Vickers Vagabond}}
===Notes===
{{reflist}}

===Bibliography===
{{refbegin}}
*{{cite book |title= Vickers Aircraft since 1908 |last1= Andrews |first1= CF |last2=Morgan|first2=E.B.|edition= 2nd |year= 1988|publisher= Putnam|location= London|isbn= 0-85177-815-1}}
*{{cite magazine |title=Two-Seater Light 'Plane Competitions at Lympne |magazine=[[Flight International|Flight]] |date=25 September 1924 |volume=XVI |issue=822 |pages=586–626 |url=https://www.flightglobal.com/pdfarchive/view/1924/1924%20-%200586.html |access-date=8 April 2019 |ref={{harvid|''Flight'' 25 September 1924}} }}
{{refend}}

&lt;!-- ==External links== --&gt;
{{Vickers aircraft}}

[[Category:1920s British sport aircraft]]
[[Category:Vickers aircraft|Vagabond]]
[[Category:Biplanes]]
[[Category:Single-engined tractor aircraft]]
[[Category:Aircraft first flown in 1924]]"""
    title_tokens, body_tokens, reference_tokens, category_tokens, infobox_tokens, external_tokens = tp.process(title,
                                                                                                               body)
    # print("title: ", title_tokens)
    # print("infobox: ", infobox_tokens)
    # print("category: ", category_tokens)
    # print("reference: ", reference_tokens)
    # print("external: ", external_tokens)
    # print("body: ", body_tokens)

# Title = title tag in xml
# infobox = infoboxes in wiki
# body - rest of the stuff
# category - category in wiki
# links - External links
# references - {{cite ==refrences ==notes ==Footnotes ==Bibliography
