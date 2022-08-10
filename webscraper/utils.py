from typing import Collection

class competition:
    def __init__(self, title, competition, location, additional_info, column_headers):
        self.title = title
        self.competition = competition
        self.location = location
        self.grouped = self.is_grouped(title, competition, additional_info)
        self.final = self.is_final(title, competition)
        self.event_types = self.parse_column_headers(column_headers)

    def is_final(self, title, competition):
        return (self.containsWord('Final', title) \
                or self.containsWord('Final', competition) )
    
    def is_grouped(self, title, competition, additional_info):
        return (self.containsWord('Group', title)  \
                or self.containsWord('Group', competition)  \
                or self.containsWord('Group', additional_info) )

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
    
    def parse_column_headers(column_headers):
        event_types = []

        for header in column_headers:
            if ('#' in header):
                pass
            if ('Competitor' or 'competitor' or 'COMPETITOR' in header):
                pass
            if ('Country' or 'COUNTRY' or 'country' in header):
                pass
            if ('pts' or 'PTS' in header):
                pass
            event_types.append(event_type(header))

        return event_types

class competitor:
    def __init__(self, ranking, name, country, total_points, events):
        self.ranking = ranking
        self.name = name
        self.country = country
        self.total_points = total_points
        self.events = events

    def __eq__(self, other):
        return self.ranking == other.ranking \
            and self.name == other.name \
            and self.country == other.country \
            and self.total_points == other.total_points \
            and self.events == other.events

class event:
    def __init__(self, event_type, performance, points, info):
        self.event_type = event_type
        self.performance = performance
        self.points = points
        self.info = info

    def __eq__(self, other):
        return self.event_type == other.event_type \
            and self.performance == other.performance \
            and self.points == other.points \
            and self.info == other.info

class event_type:

    def __init__(self, name):
        self.name = name
        self.unit = self.get_units(name)

    def __eq__(self, other):
        return self.name == other.name
    
    # Milan you get to fill this in <3
    def get_units(name):
        match name:
            case 'Viking Press':
                return Units.reps 
            case 'Herucles Hold':
                return Units.seconds
            case 'Truck Pull':
                return Units.seconds
            case 'Conan\'s wheel':
                return Units.degrees
            case 'Super Yoke':
                return Units.seconds
    
class Units(Enum):
    seconds = 1
    reps = 2
    distance = 3
    degrees = 4
    max_weight = 5
    implements = 6
    height = 7