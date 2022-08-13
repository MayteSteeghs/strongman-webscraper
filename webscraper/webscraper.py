import pandas as pd
import json
from utils import *
from frontend import *
from backend import *

class competitionScraper:
    
    API_url = 'https://strongmanarchives.com/fetchContestResult.php'
    scraped_competition = None
    country_cache = {}

    # Run the script
    def run(self):
        with open('data\input\country_lookup.json', 'r') as d:
            self.country_cache = json.load(d)
            
        for id in range (1, 1400):
            try:
                competition_data = parse_competition(id)
                competitor_data = get_comp_info(self, id)
            except EmptyPageError:
                continue
            self.parse_total_dataset(competitor_data, competition_data)
            self.save_data() # move once testing phase is done

    # save the data into a csv file
    def save_data(self):
        i = self.scraped_competition
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
            w.seek(0)
            json.dump(self.country_cache, w, indent=1)
            w.truncate()

    def parse_total_dataset(self, competitor_data, competition_data):
        self.scraped_competition = (data_interface(self, competitor_data, competition_data))