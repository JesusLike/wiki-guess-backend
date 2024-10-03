'''
Tools for scrapping wiki pages
'''

import re
from io import StringIO

import requests
import pandas
from bs4 import BeautifulSoup

def get_wiki_page(page):
    '''
    Get page html content via MediaWiki api endpoint 
    https://www.mediawiki.org/wiki/API:Get_the_contents_of_a_page
    '''
    wiki_page_api_template = 'https://en.wikipedia.org/w/api.php?action=parse&prop=text&format=json&redirects=true&page={page}'
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


def get_country_info(country_page):
    '''
    Parse country page to get the needed data
    '''
    print(f'Retrieving page: {country_page}')
    content = get_wiki_page(country_page)
    info_table_contents = extract_info_table(content)

    df = pandas.read_html(StringIO(info_table_contents))[0]
    df.columns = ['Group', 'Property', 'Value']
    df.dropna(inplace=True)

    return df


def insert_group_name(row, group_name, soup):
    '''
    Handle grouping in source table by adding one more cell to data row
    containing group name or marking abscense of it
    '''
    data_label = row.find('th', 'infobox-label')
    if data_label:
        new_cell = soup.new_tag('th')
        new_cell.string = group_name
        data_label.insert_before(new_cell)


def process_group(soup, subheader, group_name):
    '''
    Transform groups with header row for pandas to parse correctly
    '''
    subheader_row = subheader.find_parent('tr')
    data_row = subheader_row.find_next_sibling('tr')
    allowed_classes = ['mergedrow', 'mergedbottomrow']

    while data_row and 'class' in data_row.attrs and any(x in ' '.join(data_row['class']) for x in allowed_classes):
        insert_group_name(data_row, group_name, soup)
        data_row = data_row.find_next_sibling('tr')

    subheader_row.decompose()
    return data_row


def extract_info_table(page_content):
    '''
    Extract the table with country props from the page
    and prepares it to be consumed by pandas
    '''
    soup = BeautifulSoup(page_content, 'html.parser')
    info_table = soup.find('table', 'infobox')

    for x in info_table.find_all('sup', 'reference'):
        x.decompose()

    row = info_table.find('tr')
    while row:
        subheader = row.find('th', 'infobox-header')
        if subheader:
            row = process_group(soup, subheader, subheader.get_text())
        else:
            try:
                subheader = row.find(string=re.compile('GDP')).find_parent('th')
            except AttributeError:
                pass
            if subheader:
                row = process_group(soup, subheader, subheader.get_text())
            else:
                insert_group_name(row, 'No Group', soup)
                row = row.find_next_sibling('tr')

    table_contents = str(info_table).replace("\u2022", "").replace("\u00a0", " ").replace("\u00B7", ", ").replace("\u2013", "-")
    #.replace("\u2007", "; ") - this one is used to align single-digits with two-digits
    return table_contents


def serialize_country_info(df):
    '''
    Transform DataFrame with country props to JSON with hierarchical groups
    '''
    return df.groupby('Group').apply(lambda x: x.to_dict(orient='records'), include_groups=False).to_json()
