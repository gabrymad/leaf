import datetime

d0 = datetime.datetime(2021, 5, 22, 13, 33)
d1 = datetime.datetime(2023, 5, 22, 13, 45)

delta = d1 - d0
print('Device connected for', delta.days, 'days and', datetime.timedelta(seconds=delta.seconds), 'hours')