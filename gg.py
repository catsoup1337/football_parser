from bs4 import BeautifulSoup
import requests


link_game = 'https://news.sportbox.ru/Vidy_sporta/Futbol/Evropejskie_chempionaty/Angliya/stats/turnir_5350/game_1340022146'
dict_goals = {}
req_game = requests.get(url = link_game).text
soup_game = BeautifulSoup(req_game, 'lxml')
time_lane_right = []
try:
    time_lane_right_goals = soup_game.find_all(class_='event_right_command stats_pict stats_pict_gol')
    for _ in range(len(time_lane_right_goals)+1):
        time_lane_right.append(time_lane_right_goals[_])
except:
    ...
try:
    time_lane_right_pin = soup_game.find_all(class_='event_right_command stats_pict stats_pict_pin')
    for _ in range(len(time_lane_right_pin)+1):
        time_lane_right.append(time_lane_right_pin[_])
except:
    ...
try:
    time_lane_right_pin = soup_game.find_all(class_='event_right_command stats_pict stats_pict_autogol')
    for _ in range(len(time_lane_right_pin)+1):
        time_lane_right.append(time_lane_right_pin[_])
except:
    ...
for i in range(len(time_lane_right)):
    minutes = time_lane_right[i].get('attr-min')
    value = '-1'
    if dict_goals.get(minutes): 
        dict_goals[minutes].append(value)
    else:
        dict_goals.update({minutes: [value]})

time_lane_left = []
try:
    time_lane_left_goals = soup_game.find_all(class_='event_left_command stats_pict stats_pict_gol')
    for _ in range(len(time_lane_left_goals)+1):
        time_lane_left.append(time_lane_left_goals[_])
except:
    ...
try:
    time_lane_left_pin = soup_game.find_all(class_='event_left_command stats_pict stats_pict_pin')
    for _ in range(len(time_lane_left_pin)+1):
        time_lane_left.append(time_lane_left_pin[_])
except:
    ...
try:
    time_lane_left_auto = soup_game.find_all(class_='event_left_command stats_pict stats_pict_autogol')
    for _ in range(len(time_lane_left_auto)+1):
        time_lane_left.append(time_lane_left_auto[_])
except:
    ...
for i2 in range(len(time_lane_left)):
    minutes = time_lane_left[i2].get('attr-min')
    value = '+1'
    if dict_goals.get(minutes): 
        dict_goals[minutes].append(value)
    else:
        dict_goals.update({minutes: [value]})
print(dict_goals)
sorted_di = sorted(dict_goals.items(), key=lambda f: int(f[0]))
# for i in range(len())
print(sorted_di)
final=[]
for x, y in sorted_di:
    for j in range(len(y)):
        final.append(y[j])

print(', '.join(final))
# res = ','.join(sum(sorted_di.values(),()))
# print(res)

# d = {'30': ['Математика'], '26': ['Русский язык'], '7': ['История'], '7': ['История'], '15': ['Музыка'], '33': ['География']}
# key = '7'
# value = 'История'
# if d.get(key): 
#     d[key].append(value)
# else:
#     d.update({key: [value]})
# # sorted_d = dict(sorted(d.items(), key=lambda f: int(f[0])))

# # print(d)
# d = {'6': ['-1'], '30': ['-1'], '53': ['-1'], '63': ['-1'], '9': ['-1'], '40': ['+1'], '50': ['+1'], '81': ['+1', '+1'], '86': ['+1']}
# print(sum(d.values(),[]))