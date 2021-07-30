import ssl
import util_mysql
from datetime import datetime, timedelta

ssl._create_default_https_context = ssl._create_unverified_context

current_year_full = (datetime.now() - timedelta(days=1)).strftime('%Y')
current_month = (datetime.now() - timedelta(days=1)).strftime('%m')
current_day = (datetime.now() - timedelta(days=1)).strftime('%d')

now_year_month = str(current_year_full) + '-' + str(current_month)
now_day = current_day

util_mysql.dbConnect()

util_mysql.cur.execute("call p_tbl_weather_c('')") # 不帶日期參數，就是會做昨天的日期
# util_mysql.cur.execute("CALL p_tbl_weather_mean ('2021-07-02')") # 指定日期

for data in util_mysql.cur.fetchall():
    print(data)

print('finish..')
util_mysql.dbDisconnect()