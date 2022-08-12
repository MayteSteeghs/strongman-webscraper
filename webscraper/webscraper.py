import requests
import lxml.html
import pandas as pd
import json
from utils import *

class competitionScraper:
    
    API_url = 'https://strongmanarchives.com/fetchContestResult.php'
    scraped_competitions = []
    country_cache = {}

    # Run the script
    def run(self):
        with open('data\input\country_lookup.json', 'r') as d:
            self.country_cache = json.load(d)

        for id in range (1, 1350):
            competitor_data = self.get_comp_info(id)
            competition_data = self.parse_competition(id)
            self.parse_total_dataset(competitor_data, competition_data)
            self.save_data(id) # move once testing phase is done
        

    # save the data into a csv file
    def save_data(self, id):
        i = self.scraped_competitions[id-1]
        comp_info = vars(i[0])
        del comp_info['column_headers']
        competitors = list(map(lambda a: vars(a), i[1]))
        dataframe = []
        for sm in competitors:
            sm['events'] = list(map(lambda a: vars(a), sm['events']))
            dataframe.append(comp_info | sm)
        df = pd.DataFrame(dataframe)
        name = comp_info['title']
        df.to_csv("data\output\\" + name + ".csv")

        with open('data\input\country_lookup.json', 'w') as w:
            json.dump(self.country_cache, w)
                
    # Gets data from contestID
    def get_comp_info(self, contestID):

        data = {
            'contestID': contestID,
            'unitDisplay': 'Metric'
        }

        response = requests.post(self.API_url, data=data)
        return response.json()

    # Parse the data found from the json response
    def parse_competition(self, contestID):
        url = 'https://strongmanarchives.com/viewContest.php?id=' + str(contestID)

        html = requests.get(url)
        doc = lxml.html.fromstring(html.content)

        title = doc.xpath('/html/head/title')[0].text.split('Strongman Archives -')[1].strip()

        header_information = []

        # Usually the header information is formatted into a table
        header = doc.xpath('/html/body/center/div/table/thead/tr/th/center/*')
        for item in header:
            header_information.append(item.text_content())

        # Sometimes it's formatted as a random piece of text for some ungodly reason
        if (len(header_information) == 0):
            header = doc.xpath('/html/body/center/div/*')

            for item in header:
                if (item.tag == 'br'):
                    break
                header_information.append(item.text_content())
        
        # Summarize extra header content
        header_additional = ",".join(header_information[2:])

        # Find the event information
        event_list = {}
        if (len(doc.find_class('content')) != 0):
            event_info = prettifyEntry(doc.find_class('content')[0].text_content())
            for event in event_info:
                e = list(map(lambda a: a.strip(), event.split(':')))
                event_list[e[0]] = e[1]
                 
        # Now time to extract the column names and pray so we can splice together our two information sources
        table = doc.cssselect('thead')
        column_labels = []
        for item in table:
            column_labels.append(item.text_content())

        # remove labels for the header table because god forbid you could actually use ids
        for item in header_information:
            for label in column_labels:
                if (item in label):
                    column_labels.remove(label)
        
        # prettify entries
        column_labelset = []
        for row in column_labels:
            column_labelset.append(prettifyEntry(row))
        
        info = {
            'title': title,
            'competition': header_information[0],
            'location_info': header_information[1],
            'additional_header_information': header_additional,
            'column_headers': column_labelset[0],
            'event_info': event_list,
            'comp_id': contestID
        }

        return info

    def parse_total_dataset(self, competitor_data, competition_data):
        # parse event_types
        comp = competition(competition_data['title'], competition_data['competition'],\
                           competition_data['location_info'], competition_data['additional_header_information'], \
                           competition_data['column_headers'], competition_data['comp_id'])

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
                country = self.extractCountry(countryRow)

            # Extract performance information
            total_points = line[3]
            events = self.processScores(line[4:], event_types, competition_data['event_info'])

            competition_entry = competitor(rank, name, abbreviation, link, country, total_points, events)
            competition_entries.append(competition_entry)
        self.scraped_competitions.append([comp, competition_entries])

    # Helper method to extract country from name
    def extractCountry(self, countryRow):
        url = 'https://strongmanarchives.com' + str(countryRow.get('href'))

        html = requests.get(url)
        doc = lxml.html.fromstring(html.content)

        title = doc.xpath('/html/head/title')[0].text
        country = title.split('Strongman Archives -')[1].strip()
        self.country_cache[countryRow.get('title').strip()] = country
        return country
       
    # Helper method to process scores by combining event column headers and athletes performances
    def processScores(self, scores, event_types, event_info):
        if len(scores) != len(event_types) * 2:
            print("More scores than there are events!")

        scoresIterable = iter(scores)
        events = []
        for ev in event_types:
            performance = next(scoresIterable)
            points = next(scoresIterable)
            #TODO: Implement information
            info = event_info.get(ev, 'None')
            events.append(event(ev, performance, points, info))
        return events