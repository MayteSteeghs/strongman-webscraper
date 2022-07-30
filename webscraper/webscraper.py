import requests
import json
import lxml.html

from utils import competitor
from utils import competition
from utils import event
from utils import event_type

class competitionScraper:
    
    API_url = 'https://strongmanarchives.com/fetchContestResult.php'
    scraped_competitors = []
    
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
        element = lxml.html.fromstring(html.content)

        title = element.xpath('/html/head/title')[0].text
        
        header_information = []

        # Usually the header information is formatted into a table
        header = element.xpath('/html/body/center/div/table/thead/tr/th/center/*')
        for item in header:
            header_information.append(item.text_content())

        # Sometimes it's formatted as a random piece of text for some ungodly reason
        if (len(header_information) == 0):
            header = element.xpath('/html/body/center/div/*')

            for item in header:
                if (item.tag == 'br'):
                    break
                header_information.append(item.text_content())
        
        # Summarize extra header content
        header_additional = ",".join(header_information[2:])

        # Now time to extract the column names and pray so we can splice together our two information sources
        table = element.cssselect('thead')
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
            entry = row.split('\r\n')
           
            for item in entry:
                item.strip()
                if item == "":
                    entry.remove(item)

            column_labelset.append(entry)
        
        info = {
            'title': title,
            'competition': header_information[0],
            'location': header_information[1],
            'additional_header_information': header_additional,
            'column_headers': column_labelset
        }

        return info

    def parse_total_dataset(self, competitor_data, competition_data):
        # parse event_types
        comp = competition(competition_data.title, competition_data.competition,\
                           competition_data.location, competition_data.additional_header_information, \
                           competition_data.column_headers)

        event_types = comp.event_types

        # loop through competitors and extract info
        for line in competitor_data['data']:
            strongman = None
            self.scraped_competitors.append(strongman)

    # Run the script
    def run(self):
        competitor_data = self.get_comp_info(1305)
        competition_data = self.parse_competition(1305)
        self.parse_total_dataset(competitor_data, competition_data)

        self.save_data()

    # save the data into a json file
    def save_data(self):
        with open('competition_file.json', 'w') as json_file:
            json.dump(self.scraped_competitors, json_file, indent=4)