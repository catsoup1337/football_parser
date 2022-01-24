import requests
from bs4 import BeautifulSoup
import csv

# url = 'https://www.sports.ru/football/match/brentford-vs-wolves/'
url = 'https://www.sports.ru/football/match/norwich-city-vs-watford/'

order = [
    'Голы',
    'bebra']

filename = 'vv.csv'

def create_csv(filename, order):
    with open(filename, 'w', encoding='utf-8', newline='') as file:
        csv.DictWriter(file, fieldnames=order).writeheader()


def write_csv(filename, data):
    with open(filename, 'a', encoding='utf-8', newline='') as file:
        csv.DictWriter(file, quotechar=" " ,fieldnames=list(data)).writerow(data)


create_csv(filename, order)
r  = requests.get(url).text
soup = BeautifulSoup(r, 'lxml')
t = soup.find_all(class_='event-container')
goals = []
data = dict.fromkeys(order)
for i in range(len(t)):
    tt = t[i].text.split(' ')
    if 'Гол!' in tt:
        if tt[0] == 'Гол!':
            goals.append('1')
        if tt[2] == 'Гол!':
            goals.append('-1')
    if 'Автогол!' in tt:
        if tt[4] == 'Автогол!':
            goals.append('-1')
        if tt[0] == 'Автогол!':
            goals.append('1')
data['bebra'] = 'bebra'
data['Голы'] = ','.join(goals)
write_csv(filename, data)

# print(goals)

