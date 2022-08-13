import requests
import lxml.html

# Helper method to extract country from name
def extractCountry(self, countryRow):
    url = 'https://strongmanarchives.com' + str(countryRow.get('href'))

    html = requests.get(url)
    doc = lxml.html.fromstring(html.content)

    title = doc.xpath('/html/head/title')[0].text
    country = title.split('Strongman Archives -')[1].strip()
    self.country_cache[countryRow.get('title').strip()] = country
    return country

# Gets data from contestID
def get_comp_info(self, contestID):

    data = {
        'contestID': contestID,
        'unitDisplay': 'Metric'
    }

    response = requests.post(self.API_url, data=data)
    return response.json()