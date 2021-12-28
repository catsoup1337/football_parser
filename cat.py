import datetime
now = datetime.datetime.now().strftime("%d-%m-%Y--%H:%M")
FILENAME_XLSX = 'liverpool.xlms'
d_link = f'/documents/{now}-{FILENAME_XLSX}'
print(d_link)