from typing import Collection

class competition:
    def __init__(self, title, competition, location_info, additional_info, column_headers):
        self.title = title
        self.competition = competition
        self.location = getLocation(location_info)
        self.dates = getDates(location_info)
        self.grouped = is_grouped(title, competition, additional_info)
        self.final = is_final(title, competition)
        self.column_headers = parse_column_headers(column_headers)

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