import telebot
from tqdm.contrib.telegram import tqdm, trange
import os
from dotenv import load_dotenv

import yadisk

import requests
import csv
import time
import datetime
from fake_useragent import UserAgent

from selectolax.parser import HTMLParser
from bs4 import BeautifulSoup
from transliterate import translit

from pyexcel.cookbook import merge_all_to_a_book
import glob

load_dotenv()
y = yadisk.YaDisk(token="AQAAAAAeeuFqAAeVCjRRWT3G8khEv1eCtEu6uY4")

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PROXY = os.getenv('PROXY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
ua = UserAgent()

proxies = {
    "http":PROXY
}


ORDER = [
    'Дата',
    '№ тура',
    'Тур',
    'Команда 1',
    'Голы Команда 1',
    'Голы Команда 2',
    'Команда 2',
    'Данные 1',
    'Данные 2']

ORDER2= [
    'Дата',
    'Событие',
    '№ Тура',
    'Команда 1',
    'Голы Команда 1',
    'Голы Команда 2',
    'Команда 2',
    'Голы']

PERIODS = [ 
    # '2000',
    '2000-2001',
    # '2001',
    '2001-2002',
    # '2002',
    '2002-2003',
    # '2003',
    '2003-2004',
    # '2004',
    '2004-2005',
    # '2005',
    '2005-2006',
    # '2006',
    '2006-2007',
    # '2007',
    '2007-2008',
    # '2008',
    '2008-2009',
    # '2009',
    '2009-2010',
    # '2010',
    '2010-2011',
    '2011-2012',
    '2012-2013',
    '2013-2014',
    '2014-2015',
    '2015-2016',
    '2016-2017',
    '2017-2018',
    '2018-2019',
    '2019-2020',
    '2020-2021',
    '2021-2022',
    'calendar//',
    ]

PERIODS2 = [ 
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


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,'Привет, выбери в меню нужную функцию')

@bot.message_handler(commands=['sports'])
def start_message(message):
    msg = bot.send_message(message.chat.id,'Привет, напиши название команды на латинице')
    bot.register_next_step_handler(msg, handle_team)

@bot.message_handler(commands=['sport_box'])
def start_message(message):
    msg = bot.send_message(message.chat.id,'Привет, введи ссылку на команду')
    bot.register_next_step_handler(msg, handle_team_sportbox)

def handle_team(message):
    try:
        bot.reply_to(message, "Обрабатываю запрос")
        name_site = message.text
        bot.reply_to(message, "Начал парсинг")
        url_first =f'https://www.sports.ru/{name_site}/'
        FILENAME_CSV = f'{name_site}.csv'
        FILENAME_XLSX = f'{name_site}.xlsx' 
        create_csv(FILENAME_CSV, ORDER)
        get_calendar(url_first , message, FILENAME_CSV)
    except Exception as e:
        bot.reply_to(message, e)
    finally:
        merge_all_to_a_book(glob.glob(FILENAME_CSV), FILENAME_XLSX)
        src_t = f'/app/{FILENAME_XLSX}' 
        # src_t = f'{FILENAME_XLSX}' 
        now = datetime.datetime.now().strftime("%d%m%Y%H%M")
        y.upload(src_t, f'/documents/{now}{FILENAME_XLSX}')
        d_link = y.get_download_link(f'/documents/{now}{FILENAME_XLSX}')
        bot.reply_to(message, f"Всё готово, вот ссылка на скачивание {d_link}")


def create_csv(filename, order):
    with open(filename, 'w', encoding='utf-8', newline='') as file:
        csv.DictWriter(file, fieldnames=order).writeheader()


def write_csv(filename, data):
    with open(filename, 'a', encoding='utf-8', newline='') as file:
        csv.DictWriter(file, quotechar=" " ,fieldnames=list(data)).writerow(data)


def get_html(url, attempts = 4):
    html = None
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(
                url=url,
                headers={'user-agent': f'{ua.random}'},
                proxies = proxies,
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


def get_stats(match_info, order, FILENAME_CSV):
    url = match_info['match_url']
    html = get_html(url=url)
    if html:
        soup = BeautifulSoup(html, 'lxml')
        tree = HTMLParser(html)
        data = dict.fromkeys(order)
        # time.sleep(1)
        match_date = tree.css_first('time[itemprop="startDate"]').attributes['datetime'][:10].split('-')
        # print(match_date)
        match_date = '{2}.{1}.{0}'.format(*match_date)
        data['Дата'] = match_date

        tour_n = tree.css_first('.top__tournament-round').text()
        tour_n = tour_n.replace('Групповой этап', 'Regular Season')
        # tour_n = tour_n.replace('тур', 'tour')
        data['№ тура'] = tour_n

        tour = soup.find(class_="top__tournament-name").text.strip('.')
        data['Тур'] = tour
        try:
            team_home_slag = soup.find(class_="match-summary__team-name match-summary__team-name--home").find('a').get('href').strip('/')
            if team_home_slag.split('/')[0]=='tags':
                team_home_slag = soup.find(class_="match-summary__team-name match-summary__team-name--home").text
                team_home_slag = translit(team_home_slag, "ru", reversed=True).lower()
        except:
            team_home_slag = soup.find(class_="match-summary__team-name match-summary__team-name--home").text
            team_home_slag = translit(team_home_slag, "ru", reversed=True).lower()
        try:
            team_away_slag = soup.find(class_="match-summary__team-name match-summary__team-name--away").find('a').get('href').strip('/')
            if team_away_slag.split('/')[0]=='tags':
                team_away_slag = soup.find(class_="match-summary__team-name match-summary__team-name--away").text
                team_away_slag = translit(team_away_slag, "ru", reversed=True).lower()
        except:
            team_away_slag = soup.find(class_="match-summary__team-name match-summary__team-name--away").text
            team_away_slag = translit(team_away_slag, "ru", reversed=True).lower()
        goal_home = str(soup.find_all(class_="matchboard__card")[0].text)
        goal_away = str(soup.find_all(class_="matchboard__card")[1].text)
        # print(goal_home,'-',goal_away)
        print(team_home_slag,team_away_slag)

        if 'В гостях' in match_info['place']:
            team_1_slag = team_away_slag
            team_2_slag = team_home_slag
            goal_1 = goal_away
            goal_2 = goal_home
        else:
            team_1_slag = team_home_slag
            team_2_slag = team_away_slag
            goal_1 = goal_home
            goal_2 = goal_away

        data['Команда 1'] = team_1_slag
        data['Команда 2'] = team_2_slag

        data['Голы Команда 1'] = goal_1
        data['Голы Команда 2'] = goal_2

        data['Данные 1'] = f'{team_home_slag.capitalize()} {goal_home}'
        data['Данные 2'] = f'{team_away_slag.capitalize()} {goal_away}'

        write_csv(filename=FILENAME_CSV, data=data)


def get_matchs(period_url, FILENAME_CSV):
    html = get_html(url=period_url)
    tree = HTMLParser(html)
    stat_table = tree.css_first('table.stat-table').css('tbody > tr')
    matchs = []
    for match in stat_table:
        match_info = {}
        tds = match.css('td')
        place = tds[3].text()
        match_info['place'] = place
        match_info['tournament'] = tds[1].text().strip()
        match_info['date'] = tds[0].text().strip()
        score = tds[4].text().strip()
        if 'превью' not in score:
            match_url = tds[4].css_first('.score').attributes['href']
            if match_url:
                if 'https://www.sports.ru' in match_url:
                    match_info['match_url'] = match_url
                else:
                    match_info['match_url'] = f'https://www.sports.ru{match_url}'
        matchs.append(match_info)
    for match_info in matchs:
        if 'перенесен' not in match_info['date']:
            tournament = match_info['tournament'].lower()
            if 'кубок' in tournament or 'лига' in tournament or 'серия' in tournament:
                get_stats(match_info, ORDER , FILENAME_CSV)


def get_calendar(team_url, message, FILENAME_CSV):
    html = get_html(url=f'{team_url}calendar/')
    tree = HTMLParser(html)

    period_urls = []
    periods = tree.css('.options')[0].css('.option')
    for item in periods:
        period_url = item.attributes['href']
        for period in PERIODS:
            if period in period_url:
                period_urls.append(period_url)

    counter = len(period_urls)

    period_urls = list(reversed(period_urls))
    for i in trange(counter, token=TELEGRAM_TOKEN, chat_id=message.chat.id):
        period_url = period_urls[i]
        get_matchs(period_url, FILENAME_CSV)


def get_teams(championship_url):
    html = get_html(url=championship_url)
    tree = HTMLParser(html)
    table = tree.css_first('.stat > table > tbody')
    teams = table.css('tr')
    for team in teams:
        team_url = team.css_first('a.name').attributes['href']
        get_calendar(team_url)

#################################################################################
def handle_team_sportbox(message):
    global FILENAME2_CSV,FILENAME2_XLSX
    try:
        bot.reply_to(message, "Обрабатываю запрос")
        url = message.text
        bot.reply_to(message, "Начал парсинг")
        
        FILENAME2_CSV = f"{url.split('/')[-1]}.csv"
        FILENAME2_XLSX = f"{url.split('/')[-1]}.xlsx"

        create_csv(FILENAME2_CSV, ORDER2)
        get_tournaments(url,message)

    except Exception as e:
        bot.reply_to(message, e)
        print(e)
    finally:
        merge_all_to_a_book(glob.glob(FILENAME2_CSV), FILENAME2_XLSX)
        src_t = f'/app/{FILENAME2_XLSX}' 
        # src_t = f'{FILENAME2_XLSX}' 
        now = datetime.datetime.now().strftime("%d%m%Y%H%M")
        y.upload(src_t, f'/documents/{now}{FILENAME2_XLSX}')
        d_link = y.get_download_link(f'/documents/{now}{FILENAME2_XLSX}')
        bot.reply_to(message, f"Всё готово, вот ссылка на скачивание {d_link}")


def get_tournaments(url,message):
    r = get_html(url)
    soup = BeautifulSoup(r, 'lxml')
    tournament_links = []
    table = soup.find(class_='b-table b-table-js').find('table').find_all('a')
    for i in range(len(table)-1):
        title = table[i].get('title').split('. ')[-1].split(' ')[-1].strip(' ')
        if title in PERIODS2:
            link = f"https://news.sportbox.ru{table[i].get('href')}"
            tournament_links.append(link)
    tournament_links = list(reversed(tournament_links))
    get_matchs(tournament_links,message)

def get_matchs(tournament_links,message):
    counter = len(tournament_links)-1
    for n in trange(counter, token=TELEGRAM_TOKEN, chat_id=message.chat.id):
        req_tour = get_html(url = tournament_links[n])
        soup_tournament = BeautifulSoup(req_tour, 'lxml')
        table_tours = soup_tournament.find(class_='calendar-cutting-js').find('tbody').find_all('a')
        for j in range(1,len(table_tours)):
            try:
                link_game = f"https://news.sportbox.ru{table_tours[j].get('href')}"
                get_score(link_game)
            except:
                print('skip')

def get_score(link_game):
    dict_goals = {}
    data = dict.fromkeys(ORDER2)
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
    print(f'"{team1}","{team2}"')
    count = top.find(class_='b-match__monitor__count').text.replace('\n','').split(':')
    count1 = count[0].strip()
    count2 = count[1].strip()
    data['Дата'] = date.replace('\n','').strip().split(' ')[0]
    data['Событие'] = event_name.replace(' ','_').strip()
    data['№ Тура'] = event_num.replace(' ','_').strip()
    data['Команда 1'] = team1
    data['Голы Команда 1'] = count1
    data['Голы Команда 2'] = count2
    data['Команда 2'] = team2
    data['Голы'] = res
    write_csv(FILENAME2_CSV, data)


bot.infinity_polling()