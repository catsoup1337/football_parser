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

ATTEMPTS = 3
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
PERIODS = [ 
    '2000-2001',
    '2001-2002',
    '2002-2003',
    '2003-2004',
    '2004-2005',
    '2005-2006',
    '2006-2007',
    '2007-2008',
    '2008-2009',
    '2009-2010',
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
    '2021-2022'
    ]

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,'Привет, напиши название команды на латинице')

@bot.message_handler(content_types='text')
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
        now = datetime.datetime.now().strftime("%d%m%Y%H%M")
        y.upload(src_t, f'/documents/{now}{FILENAME_XLSX}')
        d_link = y.get_download_link(f'/documents/{now}{FILENAME_XLSX}')
        bot.reply_to(message, f"Всё готово, вот ссылка на скачивание {d_link}")




def create_csv(filename, order):
    with open(filename, 'w', encoding='utf-8', newline='') as file:
        csv.DictWriter(file, fieldnames=order).writeheader()


def write_csv(filename, data):
    with open(filename, 'a', encoding='utf-8', newline='') as file:
        csv.DictWriter(file, fieldnames=list(data)).writerow(data)


def get_html(url, attempts):
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
    html = get_html(url=url, attempts=ATTEMPTS)
    if html:
        tree = HTMLParser(html)
        data = dict.fromkeys(order)

        match_date = tree.css_first('time[itemprop="startDate"]').attributes['datetime'][:10].split('-')
        match_date = '{2}.{1}.{0}'.format(*match_date)
        data['Дата'] = match_date

        tour_n = tree.css_first('.top__tournament-round').text()
        tour_n = tour_n.replace('Групповой этап', 'Regular Season')
        data['№ тура'] = tour_n

        tour = tree.css_first('.top__tournament-name').text().strip('.')
        tour = tour.replace('тур', 'tour')
        data['Тур'] = tour

        team_info_home = tree.css_first('.match-summary__team-info--home')
        team_home_slag = team_info_home.css_first('a[itemprop="name"]').attributes['href'][1:-1]
        team_home_name = team_info_home.css_first('a[itemprop="name"]').text()

        team_info_away = tree.css_first('.match-summary__team-info--away')
        team_away_slag = team_info_away.css_first('a[itemprop="name"]').attributes['href'][1:-1]
        team_away_name = team_info_away.css_first('a[itemprop="name"]').text()

        matchboard = tree.css_first('.matchboard').css('.matchboard__card')
        goal_home = matchboard[0].css_first('.matchboard__card-game').text().strip()
        goal_away = matchboard[1].css_first('.matchboard__card-game').text().strip()

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
        # print(data['Дата'], data['Тур'], data['Команда 2'])


def get_matchs(period_url, FILENAME_CSV):
    html = get_html(url=period_url, attempts=ATTEMPTS)
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
    html = get_html(url=f'{team_url}calendar/', attempts=ATTEMPTS)
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
    html = get_html(url=championship_url, attempts=ATTEMPTS)
    tree = HTMLParser(html)
    table = tree.css_first('.stat > table > tbody')
    teams = table.css('tr')
    for team in teams:
        team_url = team.css_first('a.name').attributes['href']
        print(team_url)
        get_calendar(team_url)

bot.infinity_polling()