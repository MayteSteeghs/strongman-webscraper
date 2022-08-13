from operator import contains
from typing import Collection
import lxml.html
from backend import *

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
        if (header.strip() == '#'):
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

def data_interface(self, competitor_data, competition_data):
# parse event_types
    comp = competition(competition_data['title'], competition_data['competition'],\
                    competition_data['location_info'], competition_data['additional_header_information'], \
                    competition_data['column_headers'], competition_data['comp_id'], competition_data['contest_notes'])

    competition_entries = []
    event_types = comp.column_headers

    # loop through competitors and extract info
    for line in competitor_data['data']:
        rank = line[0]

        # Extract name from first row
        nameRow = lxml.html.fromstring(line[1])
        name = nameRow.get('title')
        link = nameRow.get('href')
        abbreviation = nameRow.text_content()

        # Extract country from second row
        countryRow = lxml.html.fromstring(line[2])
        countryKey = countryRow.get('title').strip()
        country = ""
        if countryKey in self.country_cache:
            country = self.country_cache.get(countryKey)
        else:
            country = extractCountry(self, countryRow)

        # Extract performance information
        if isinstance(line[3], str):
            events = processEdgeCaseScores(line[3:], event_types, competition_data['event_info'])
            total_points = -1
        else:
            total_points = line[3]
            events = processScores(line[4:], event_types, competition_data['event_info'])

        competition_entry = competitor(rank, name, abbreviation, link, country, total_points, events)
        competition_entries.append(competition_entry)
    return [comp, competition_entries]

# Helper method to process scores by combining event column headers and athletes performances
@staticmethod
def processScores(scores, event_types, event_info):
    if len(scores) != len(event_types) * 2:
        print("More scores than there are events!")

    scoresIterable = iter(scores)
    events = []
    for ev in event_types:
        performance = next(scoresIterable)
        points = next(scoresIterable)
        info = event_info.get(ev, 'None')
        events.append(event(ev, performance, points, info))
    return events

@staticmethod
def processEdgeCaseScores(scores, event_types, event_info):
    scoresIterable = iter(scores)
    events = []
    for ev in event_types:
        performance = next(scoresIterable)
        info = event_info.get(ev, 'None')
        events.append(event(ev, performance, -1, info))
    return events
        
