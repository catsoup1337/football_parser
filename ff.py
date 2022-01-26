import requests
from bs4 import BeautifulSoup
import csv
from pyexcel.cookbook import merge_all_to_a_book
import glob
import time
from fake_useragent import UserAgent


ua = UserAgent()

ORDER = [
    'Дата',
    'Событие',
    '№ Тура',
    'Команда 1',
    'Голы Команда 1',
    'Голы Команда 2',
    'Команда 2',
    'Голы']

FILENAME_CSV = 'vv.csv'
FILENAME_XLSX = 'vv.xlsx'

def create_csv(filename, order):
    with open(filename, 'w', encoding='utf-8', newline='') as file:
        csv.DictWriter(file, fieldnames=order).writeheader()


def write_csv(filename, data):
    with open(filename, 'a', encoding='utf-8', newline='') as file:
        csv.DictWriter(file, quotechar=" " ,fieldnames=list(data)).writerow(data)

# sportbox ru



PERIODS = [ 
    '1999-00',
    '2000',
    '2000-01',
    '2001',
    '2001-02',
    '2002',
    '2002-03',
    '2003',
    '2003-04',
    '2004',
    '2004-05',
    '2005',
    '2005-06',
    '2006',
    '2006-07',
    '2007',
    '2007-08',
    '2008',
    '2008-09',
    '2009',
    '2009-10',
    '2010',
    '2010-11',
    '2011'
    '2011-12',
    '2012',
    '2012-13',
    '2013',
    '2013-14',
    '2014'
    '2014-15',
    '2015',
    '2015-16',
    '2016',
    '2016-17',
    '2017',
    '2017-18',
    '2018',
    '2018-19',
    '2019',
    '2019-20',
    '2020',
    '2020-21',
    '2021',
    '2021-22',
    '2022'
    ]

def get_html(url, attempts = 4):
    html = None
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(
                url=url,
                headers={'user-agent': f'{ua.random}'},
                timeout=24)
        except Exception as error:
            print('Ошибка загрузки страницы:', error)
            print('Пауза 12 сек.')
            time.sleep(12)
            continue

        if response.status_code == 200:
            html = response.text
            break

        print('Пауза 6 сек.')
        time.sleep(6)

    return html

def get_tournaments(url):
    r  = get_html(url)
    soup = BeautifulSoup(r, 'lxml')
    tournament_links = []
    table = soup.find(class_='b-table b-table-js').find('table').find_all('a')
    for i in range(len(table)-1):
        title = table[i].get('title').split('. ')[-1].split(' ')[-1].strip(' ')
        if title in PERIODS:
            link = f"https://news.sportbox.ru{table[i].get('href')}"
            tournament_links.append(link)
    tournament_links = list(reversed(tournament_links))
    # print(len(tournament_links))
    get_matchs(tournament_links)

def get_matchs(tournament_links):
    for n in range(len(tournament_links)-1):
        req_tour = get_html(url = tournament_links[n])
        print(tournament_links[n])
        soup_tournament = BeautifulSoup(req_tour, 'lxml')
        table_tours = soup_tournament.find(class_='calendar-cutting-js').find('tbody').find_all('a')
        for j in range(1,len(table_tours)):
            try:
                link_game = f"https://news.sportbox.ru{table_tours[j].get('href')}"
                print(link_game)
                get_score(link_game)
            except:
                print('skip')
            # if j>3 and table_tours[j].get('href').split('/')[5] == table_tours[j-1].get('href').split('/')[5]:
            #     link_game = f"https://news.sportbox.ru{table_tours[j].get('href')}"
            #     get_score(link_game)

def get_score(link_game):
    dict_goals = {}
    filename = 'vv.csv'
    data = dict.fromkeys(ORDER)
    req_game = get_html(url = link_game)
    soup_game = BeautifulSoup(req_game, 'lxml')

    top = soup_game.find(class_='b-match')
    res = 'Данных нет'
    if top.find(class_='b-match__monitor__count').text != ' - : - ':
        time_lane_right = []
        try:
            time_lane_right_goals = soup_game.find_all(class_='event_right_command stats_pict stats_pict_gol')
            for _ in range(len(time_lane_right_goals)):
                time_lane_right.append(time_lane_right_goals[_])
        except:
            ...
        try:
            time_lane_right_pin = soup_game.find_all(class_='event_right_command stats_pict stats_pict_pin')
            for _ in range(len(time_lane_right_pin)):
                time_lane_right.append(time_lane_right_pin[_])
        except:
            ...
        try:
            time_lane_right_pin = soup_game.find_all(class_='event_right_command stats_pict stats_pict_autogol')
            for _ in range(len(time_lane_right_pin)):
                time_lane_right.append(time_lane_right_pin[_])
        except:
            ...
        for i in range(len(time_lane_right)):
            minutes = time_lane_right[i].get('attr-min')
            value = '-1'
            dict_goals[minutes] = value

        time_lane_left = []
        try:
            time_lane_left_goals = soup_game.find_all(class_='event_left_command stats_pict stats_pict_gol')
            for _ in range(len(time_lane_left_goals)):
                time_lane_left.append(time_lane_left_goals[_])
        except:
            ...
        try:
            time_lane_left_pin = soup_game.find_all(class_='event_left_command stats_pict stats_pict_pin')
            for _ in range(len(time_lane_left_pin)):
                time_lane_left.append(time_lane_left_pin[_])
        except:
            ...
        try:
            time_lane_left_auto = soup_game.find_all(class_='event_left_command stats_pict stats_pict_autogol')
            for _ in range(len(time_lane_left_auto)):
                time_lane_left.append(time_lane_left_auto[_])
        except:
            ...
        for i2 in range(len(time_lane_left)):
            minutes = time_lane_left[i2].get('attr-min')
            value = '+1'
            dict_goals[minutes] = value

        sorted_di = dict(sorted(dict_goals.items(), key=lambda f: int(f[0])))
        res = ','.join(list(sorted_di.values()))

    team1 = top.find(class_='b-match__side b-match__side_left one_player').find(class_='b-match__team-logo').get('title').replace(' ','-').strip()
    team2 = top.find(class_='b-match__side b-match__side_right one_player').find(class_='b-match__team-logo').get('title').replace(' ','-').strip()
    event = soup_game.find(class_='col-lg-8 col-md-8 col-sm-7 col-xs-12').find(class_='b-tournaments-top-menus')
    event_name = event.find(class_='tournaments-selector dropdown tournaments-main').find('a').text
    event_num = event.find_all(class_='tournaments-selector dropdown')[1].find('a').text
    date = top.find(class_='match_count_date').text.strip()
    print(date,event_name,event_num)
    print(f'"{team1}","{team2}"')
    count = top.find(class_='b-match__monitor__count').text.replace('\n','').split(':')
    count1 = count[0].strip()
    count2 = count[1].strip()
    print(count1)
    print(count2)
    data['Дата'] = date.replace('\n','').strip()
    data['Событие'] = event_name.replace(' ','_').strip()
    data['№ Тура'] = event_num.replace(' ','_').strip()
    data['Команда 1'] = team1
    data['Голы Команда 1'] = count1
    data['Голы Команда 2'] = count2
    data['Команда 2'] = team2
    data['Голы'] = res
    write_csv(FILENAME_CSV, data)


def main():
    url = 'https://news.sportbox.ru/Vidy_sporta/Futbol/Evropejskie_chempionaty/Ispaniya/fcbarcelona'
    # url = 'https://news.sportbox.ru/Vidy_sporta/Futbol/Russia/krylya_sovetov_samara/turnir_18858'
    create_csv(FILENAME_CSV, ORDER)
    get_tournaments(url)
    merge_all_to_a_book(glob.glob(FILENAME_CSV), FILENAME_XLSX)


if __name__ =='__main__':
    main()

# print(table)



# sports ru

# goals = []
# data = dict.fromkeys(order)
# for i in range(len(t)):
#     tt = t[i].text.split(' ')
#     if 'Гол!' in tt:
#         if tt[0] == 'Гол!':
#             goals.append('1')
#         if tt[2] == 'Гол!':
#             goals.append('-1')
#     if 'Автогол!' in tt:
#         if tt[4] == 'Автогол!':
#             goals.append('-1')
#         if tt[0] == 'Автогол!':
#             goals.append('1')
# data['bebra'] = 'bebra'
# data['Голы'] = ','.join(goals)
# write_csv(filename, data)

# print(goals)

