'''
Tools for scrapping wiki pages
'''

import requests
from bs4 import BeautifulSoup

def get_wiki_page(page):
    '''
    Get page html content via MediaWiki api endpoint 
    https://www.mediawiki.org/wiki/API:Get_the_contents_of_a_page
    '''
    wiki_page_api_template = 'https://en.wikipedia.org/w/api.php?action=parse&prop=text&format=json&page={page}'
    wiki_page_api_endpoint = wiki_page_api_template.format(page=page)
    response = requests.get(wiki_page_api_endpoint, timeout=5000)
    if response.status_code == 404:
        raise RuntimeError(f'API endpoint {wiki_page_api_endpoint} not found')
    if response.status_code == 500:
        raise RuntimeError(f'Internal server error on API endpoint {wiki_page_api_endpoint}')
    if response.status_code != 200:
        raise RuntimeError(f'Unhandled error while calling API endpoint {wiki_page_api_endpoint}')

    json_body = response.json()
    if json_body.get('error'):
        raise RuntimeError(f'Page not found {page}')

    return response.json().get('parse').get('text').get('*')

def get_countries():
    '''
    Parse UN members wiki page and return a list of countries and links to their pages in format:
    
    { 
        "name": "Country Name",
        "page": "Country Page name for API call"
    }
    '''
    content = get_wiki_page('Member_states_of_the_United_Nations')
    soup = BeautifulSoup(content, 'html.parser')
    tables = soup.find_all('table')

    def is_country_table(table):
        '''
        Check whether the table is the list of UN Member States by it's caption
        '''
        table_caption = table.find('caption')
        if not table_caption:
            return False
        if not table_caption.find(string='UN member states'):
            return False
        return True

    def parse_country_cell(cell):
        '''
        Transform cell html into the meaningful dictionary
        '''
        cell_link = cell.find('a')
        country_name = str(cell_link.string)
        country_page = cell_link['href'].replace('/wiki/', '')
        return {
                "name": country_name,
                "page": country_page
                }

    country_table = next((table for table in tables if is_country_table(table)), None)
    country_cells = country_table.find_all('th', attrs={ 'scope': 'row' })
    country_infos = list(map(parse_country_cell, country_cells))
    return country_infos
