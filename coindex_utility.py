from datetime import datetime
from bs4 import BeautifulSoup
import math
import requests

def date_to_retrieve():
    # return str - index reblancing date to refer to
    date = datetime.now()
    year = str(date.year) # year of the current time 
    Q = math.ceil(date.month/3.) # the quarter of the current time
    '''
    4 quarters in a year - quarter 1 Jan, 2 Apr, 3 Jul, 4 Oct
    '''
    month_ls = ['01','04','07','10']
    to_retrieve = year + '-' + month_ls[Q-1] + '-' + '01'
    return to_retrieve

def date_to_retrieve_inverse():
    date = datetime.now()
    year = str(date.year) # year of the current time 
    Q = math.ceil(date.month/3.) # the quarter of the current time
    '''
    4 quarters in a year - quarter 1 Jan, 2 Apr, 3 Jul, 4 Oct
    '''
    month_ls = ['01','04','07','10']
    to_retrieve = '01' + '-' + month_ls[Q-1] + "-" + year
    return to_retrieve

def rank_list(date_str):
    date = date_str
    url = f'https://coincodex.com/historical-data/crypto/?date={date}T04:00:00Z'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    main_content = soup.find_all("tr", {"class": "coin"})
    rank = []
    for i in range(30):
        obj = main_content[i+1]
        rank.append(obj.td.next_sibling.a.div.div.text)
    return rank

def print_msg_box(msg, indent=1, width=None, title=None):
    """Print message-box with optional title."""
    lines = msg.split('\n')
    space = " " * indent
    if not width:
        width = max(map(len, lines))
    box = f'╔{"═" * (width + indent * 2)}╗\n'  # upper_border
    if title:
        box += f'║{space}{title:<{width}}{space}║\n'  # title
        box += f'║{space}{"-" * len(title):<{width}}{space}║\n'  # underscore
    box += ''.join([f'║{space}{line:<{width}}{space}║\n' for line in lines])
    box += f'╚{"═" * (width + indent * 2)}╝'  # lower_border
    print(box)

def input_date_to_retrieve(date):
    ymd = date.split("-")
    year = ymd[0]
    month = ymd[1]
    Q = math.ceil(float(month)/3.) # the quarter of the current time
    '''
    4 quarters in a year - quarter 1 Jan, 2 Apr, 3 Jul, 4 Oct
    '''
    month_ls = ['01','04','07','10']
    to_retrieve = year + '-' + month_ls[Q-1] + '-' + '01'
    return to_retrieve