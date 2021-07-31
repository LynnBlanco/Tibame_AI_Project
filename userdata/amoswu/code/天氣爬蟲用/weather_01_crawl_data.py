from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import util_mysql
from datetime import datetime, timedelta
import urllib

ssl._create_default_https_context = ssl._create_unverified_context

current_year_full = (datetime.now() - timedelta(days=1)).strftime('%Y')
current_month = (datetime.now() - timedelta(days=1)).strftime('%m')
current_day = (datetime.now() - timedelta(days=1)).strftime('%d')

now_year_month = str(current_year_full) + '-' + str(current_month)
now_day = current_day

# 手動補資料範例，要於今天12:00後輸入昨天的日期，可以直接補資料，如果已經有資料會更新現有的資料
# now_year_month = '2021-06'
# now_day = '08'

#################SQL statement###################

queryFetchStationSQL = "CALL fetch_station(1,NULL)"
queryFetchDailyDateSQL = "CALL fetch_daily_date (1, 199601, 200912)"
insertDailySQL = '''
INSERT INTO `tbl_weather_raw` (
`ObsTime`, `StnPres`, `SeaPres`, `StnPresMax`, `StnPresMaxTime`, `StnPresMin`, `StnPresMinTime`,
`Temperature`, `TMax`, `TMaxTime`, `TMin`, `TMinTime`, `TdDewPoint`, `RH`, `RHMin`, `RHMinTime`,
`WS`, `WD`, `WSGust`, `WDGust`, `WGustTime`, `Precp`, `PrecpHour`, `PrecpMax10`, `PrecpMax10Time`,
`PrecpMax60`, `PrecpMax60Time`, `SunShine`, `SunShineRate`, `GloblRad`, `VisbMean`, `EvapA`, `UVIMax`,
`UVIMaxTime`, `CloudAmount`, `_id`, `code`, `name`, `date`, `city`) 
VALUES (
%(ObsTime)s, %(StnPres)s, %(SeaPres)s, %(StnPresMax)s, %(StnPresMaxTime)s, %(StnPresMin)s, %(StnPresMinTime)s,
%(Temperature)s, %(TMax)s, %(TMaxTime)s, %(TMin)s, %(TMinTime)s, %(TdDewPoint)s, %(RH)s, %(RHMin)s, %(RHMinTime)s,
%(WS)s, %(WD)s, %(WSGust)s, %(WDGust)s, %(WGustTime)s, %(Precp)s, %(PrecpHour)s, %(PrecpMax10)s, %(PrecpMax10Time)s,
%(PrecpMax60)s, %(PrecpMax60Time)s, %(SunShine)s, %(SunShineRate)s, %(GloblRad)s, %(VisbMean)s, %(EvapA)s, %(UVIMax)s,
%(UVIMaxTime)s, %(CloudAmount)s, %(_id)s, %(code)s, %(name)s, %(date)s, %(city)s
)
ON DUPLICATE KEY UPDATE 
`ObsTime` = %(ObsTime)s, `StnPres` = %(StnPres)s, `SeaPres` = %(SeaPres)s, `StnPresMax` = %(StnPresMax)s, `StnPresMaxTime` = %(StnPresMaxTime)s, `StnPresMin` = %(StnPresMin)s, `StnPresMinTime` = %(StnPresMinTime)s,
`Temperature` = %(Temperature)s, `TMax` = %(TMax)s, `TMaxTime` = %(TMaxTime)s, `TMin` = %(TMin)s, `TMinTime` = %(TMinTime)s, `TdDewPoint` = %(TdDewPoint)s, `RH` = %(RH)s, `RHMin` = %(RHMin)s, `RHMinTime` = %(RHMinTime)s,
`WS` = %(WS)s, `WD` = %(WD)s, `WSGust` = %(WSGust)s, `WDGust` = %(WDGust)s, `WGustTime` = %(WGustTime)s, `Precp` = %(Precp)s, `PrecpHour` = %(PrecpHour)s, `PrecpMax10` = %(PrecpMax10)s, `PrecpMax10Time` = %(PrecpMax10Time)s,
`PrecpMax60` = %(PrecpMax60)s, `PrecpMax60Time` = %(PrecpMax60Time)s, `SunShine` = %(SunShine)s, `SunShineRate` = %(SunShineRate)s, `GloblRad` = %(GloblRad)s, `VisbMean` = %(VisbMean)s, `EvapA` = %(EvapA)s, `UVIMax` = %(UVIMax)s,
`UVIMaxTime` = %(UVIMaxTime)s, `CloudAmount` = %(CloudAmount)s, `_id` = %(_id)s, `code` = %(code)s, `name` = %(name)s, `date` = %(date)s, `city` = %(city)s
'''
reportDailyColumnList = [
'ObsTime', 'StnPres', 'SeaPres', 'StnPresMax', 'StnPresMaxTime', 'StnPresMin', 'StnPresMinTime',
'Temperature', 'TMax', 'TMaxTime', 'TMin', 'TMinTime', 'TdDewPoint', 'RH', 'RHMin', 'RHMinTime',
'WS', 'WD', 'WSGust', 'WDGust', 'WGustTime', 'Precp', 'PrecpHour', 'PrecpMax10', 'PrecpMax10Time',
'PrecpMax60', 'PrecpMax60Time', 'SunShine', 'SunShineRate', 'GloblRad', 'VisbMean', 'EvapA', 'UVIMax',
'UVIMaxTime', 'CloudAmount', '_id', 'code', 'name', 'date', 'city'
]
#################爬蟲相關###################

def queryUrl(station, stname, datepicker):
    stname = stname
    stname = urllib.parse.quote_plus(stname)

    queryParams = {"station":station, "stname":stname, "datepicker":datepicker}
    quepyParamsEncoded = urllib.parse.urlencode(queryParams)
    url = 'https://e-service.cwb.gov.tw/HistoryDataQuery/MonthDataController.do?command=viewMain&' + quepyParamsEncoded
    return url

def getTable(_id, station, stname, datepicker, city):
    url = queryUrl(station, stname, datepicker)
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', id="MyTable")
    if table != None:
        table_rows = table.find_all('tr')
        l = []
        for tr in table_rows:
            tds = tr.find_all('td')
            row = [None if (
                    (td.text.replace(u'\xa0', u'') == '...') or
                    (td.text.replace(u'\xa0', u'') == 'T') or
                    (td.text.replace(u'\xa0', u'') == '/') or
                    (td.text.replace(u'\xa0', u'') == 'X') or
                    (td.text.replace(u'\xa0', u'') == '&')
                    ) else td.text.replace(u'\xa0', u'') for td in tds]
            try:
                datepicker_new = datepicker + "_" + row[0]
                row.extend([_id, station, stname, datepicker_new, city])
                if (station[:2] == '46') or (station[:2] == 'C0'):
                    if row[1] != None:
                        l.append(row)
                elif (station[:2] == 'C1'):
                    if row[21] != None:
                        l.append(row)
                else:
                    print("util.py getTable else params:",_id, station, stname, datepicker_new, city)
            except:
                pass

        return l

def getRow(_id, station, stname, datepicker, now_day, city):
    url = queryUrl(station, stname, datepicker)
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', id="MyTable")
    if table != None:
        table_rows = table.find_all('tr')
        l = []
        for tr in table_rows:
            tds = tr.find_all('td')
            row = [None if (
                    (td.text.replace(u'\xa0', u'') == '...') or
                    (td.text.replace(u'\xa0', u'') == 'T') or
                    (td.text.replace(u'\xa0', u'') == '/') or
                    (td.text.replace(u'\xa0', u'') == 'X') or
                    (td.text.replace(u'\xa0', u'') == '&')
                    ) else td.text.replace(u'\xa0', u'') for td in tds]
            try:
                if row[0] == now_day:
                    datepicker_new = datepicker + "_" + row[0]
                    row.extend([_id, station, stname, datepicker_new, city])
                    print(row)
                    if (station[:2] == '46') or (station[:2] == 'C0'):
                        if row[1] != None:
                            l.append(row)
                    elif (station[:2] == 'C1'):
                        if row[21] != None:
                            l.append(row)
                    else:
                        print("util.py getTable else params:",_id, station, stname, datepicker_new, city)
            except:
                pass
        return l

def getParamDict(keylist, valuelist):
	return dict(zip(keylist, valuelist))

#################fetchStation###################

util_mysql.dbConnect()
fetchStation = util_mysql.queryDB(queryFetchStationSQL)
print("共有多少站:", len(fetchStation))
print(fetchStation[0])
# fetchDailyDate = util_mysql.queryDB(queryFetchDailyDateSQL)
# print("共有多少日期:", len(fetchDailyDate))
# print(fetchDailyDate)

# 抓單日的資料
# for i in range(0, len(fetchStation)):
#     print("now quepy station", fetchStation[i][0])
#     _id = str(fetchStation[i][0])
#     station = str(fetchStation[i][1])
#     stname = str(fetchStation[i][2])
#     datepicker = now_year_month
#     city = str(fetchStation[i][3])
#     data = getRow(_id, station, stname, datepicker, now_day, city)
#     if data != None:
#         for k in range(len(data)):
#             sql = insertDailySQL
#             param = getParamDict(reportDailyColumnList, data[k])
#             util_mysql.exeSql(sql, param)

# 抓整個月份的資料
for i in range(0, len(fetchStation)):
    print("now quepy station", fetchStation[i])
    _id = str(fetchStation[i][0])
    station = str(fetchStation[i][1])
    stname = str(fetchStation[i][2])
    datepicker = now_year_month
    city = str(fetchStation[i][3])
    data = getTable(_id, station, stname, datepicker, city)
    if data != None:
        for k in range(len(data)):
            sql = insertDailySQL
            param = getParamDict(reportDailyColumnList, data[k])
            util_mysql.exeSql(sql, param)

util_mysql.dbDisconnect()
