from typing import Collection

class competition:
    def __init__(self, title, competition, location_info, additional_info, column_headers, comp_id, contest_notes):
        self.comp_id = comp_id
        self.title = title
        self.competition = competition
        self.location = getLocation(location_info)
        self.dates = getDates(location_info)
        self.grouped = is_grouped(title, competition, additional_info)
        self.final = is_final(title, competition)
        self.qualifier = is_qualifier(title, competition, additional_info)
        self.column_headers = parse_column_headers(column_headers)
        self.contest_notes = contest_notes

def getLocation(location_info):
    splitter = location_info.split(',')
    splitter.remove(splitter[-1])
    mystring = ""
    for s in splitter:
        mystring = mystring + s
    return mystring

@staticmethod
def getDates(location_info):
    return location_info.split(',')[-1].strip()

def containsWord(word, input):
    word = word.lower()
    if isinstance(input, str):
        input = input.lower()
        if word in input: return True
        return False
    if isinstance(input, Collection):
        for element in input:
            element = element.lower()
            if word in element: return True
        return False

def is_final(title, competition):
    return (containsWord('Final', title) \
            or containsWord('Final', competition) )

def is_grouped(title, competition, additional_info):
    return (containsWord('Group', title)  \
            or containsWord('Group', competition)  \
            or containsWord('Group', additional_info) )

def is_qualifier(title, competition, additional_info):
    return (containsWord('Qualif', title)  \
            or containsWord('Qualif', competition)  \
            or containsWord('Qualif', additional_info) )

def parse_column_headers(column_headers):
    event_types = []

    for header in column_headers:
        if ('#' in header):
            continue
        if containsWord('Competitor', header):
            continue
        if containsWord('Country', header):
            continue
        if containsWord('Pts', header):
            continue
        event_types.append(header)

    return event_types

class competitor:
    def __init__(self, ranking, name, abbreviation, link, country, total_points, events):
        self.ranking = ranking
        self.name = name
        self.abbreviation = abbreviation
        self.link = link
        self.country = country
        self.total_points = total_points
        self.events = events

    def __eq__(self, other):
        return self.ranking == other.ranking \
            and self.name == other.name \
            and self.country == other.country \
            and self.total_points == other.total_points \
            and self.events == other.events \
            and self.abbreviation == other.abbreviation \
            and self.link == other.link

class event:
    def __init__(self, event_type, performance, points, info):
        self.event_name = event_type
        self.performance = performance
        self.points = points
        self.info = info

    def __eq__(self, other):
        return self.event_type == other.event_type \
            and self.performance == other.performance \
            and self.points == other.points \
            and self.info == other.info
            
class EmptyPageError(Exception):
 
    # Constructor or Initializer
    def __init__(self, value):
        self.value = value
 
    # __str__ is to print() the value
    def __str__(self):
        return(repr(self.value))

@staticmethod
def prettifyEntry(element):
    entry = element.split('\r\n')
    entry = list(map(lambda a: a.strip(), entry))
    entry = list(filter(lambda a: a != '', entry))            
    return entry

