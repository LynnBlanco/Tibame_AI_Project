import urllib.request
import os
import pandas as pd
from datetime import datetime, timezone, timedelta
import numpy as np
import time
from sklearn.preprocessing import OneHotEncoder

# 所有城市對照英文代碼
city = {
    '基隆市':'KLU',
    '臺北市':'TPE',
    '新北市':'TPH',
    '桃園市':'TYC',
    '新竹市':'HSC',
    '新竹縣':'HSH',
    '苗栗縣':'MAL',
    '臺中市':'TXG',
    '彰化縣':'CWH',
    '南投縣':'NTO',
    '雲林縣':'YLH',
    '嘉義市':'CYI',
    '嘉義縣':'CHY',
    '臺南市':'TNN',
    '高雄市':'KHH',
    '屏東縣':'IUH',
    '宜蘭縣':'ILN',
    '花蓮縣':'HWA',
    '臺東縣':'TTT'
}

# 農作物  (順序與colab有變動)
crop_dict = {
    1 : ['cabbage', '高麗菜', '(LA1 甘藍 初秋)'],
    2 : ['carrot', '胡蘿蔔', '(SB2 胡蘿蔔 清洗)'],
    3 : ['beeftomato', '牛番茄', '(FJ3 番茄 牛蕃茄)'],
    4 : ['cucumber', '胡瓜', '(FD1 花胡瓜)'],
    5 : ['loofah', '絲瓜', '(FF1 絲瓜)'],
    6 : ['cabbage2', '包心白菜', '(LC1 包心白 包白)'],
    7 : ['shallots', '青蔥', '(SE6 青蔥 粉蔥)'],
    8 : ['bittergourd', '苦瓜', '(FG1 苦瓜 白大米)'],
    9 : ['onion', '洋蔥', '(SD1 洋蔥 本產)'],
    10 : ['waterspinach', '空心菜', '(LF2 蕹菜 小葉)'],

    11 : ['guava', '番石榴', '(P1 番石榴 珍珠芭)'],
    12 : ['pineapple', '鳳梨', '(B2 鳳梨 金鑽鳳梨)'],
    13 : ['papaya', '木瓜', '(I1 木瓜 網室紅肉)'],
    14 : ['watermelon', '西瓜', '(T1 西瓜 大西瓜)'],
    15 : ['banana', '香蕉', '(A1 香蕉)'],
    16 : ['apple', '蘋果', '(X69 蘋果 富士進口)'],
    17 : ['pear', '梨子', '(O4 梨 新興梨)'],
    18 : ['grape', '葡萄', '(S1 葡萄 巨峰)'],
    19 : ['dragonfruit', '火龍果', '(812 火龍果 紅肉)'],
    20 : ['mango', '芒果', '(R1 芒果 愛文)'],
    21 : ['pakchoy', '青江菜', '(LD1 青江白菜 小梗)'], # 此處與colab有變動
    22 : ['cauliflower', '花椰菜', '(FB11 花椰菜 青梗 留梗炳)'],
    23 : ['lemon', '檸檬', '(F1 雜柑 檸檬)'],
    24 : ['tomato', '小番茄', '(74 小番茄 玉女)'], # 此處與colab有變動
}

# # 市場選定
# market_dict = {
#     1 : '台北一'
# }

# 只要中文一樣就可以，不用分蔬菜還是水果的市場
market_dict = {
    1 : ['南投市', '蔬菜'],
    2 : ['屏東市', '蔬菜'],
    3 : ['永靖鄉', '蔬菜'],
    4 : ['西螺鎮', '蔬菜'],
    5 : ['高雄市', '蔬菜'],
    6 : ['鳳山區', '蔬菜'],
    7 : ['台中市', '蔬菜'],
    8 : ['台北一', '蔬菜'],
    9 : ['台北二', '蔬菜'],
    10 : ['台東市', '蔬菜'],
    11 : ['溪湖鎮', '蔬菜'],
    12 : ['花蓮市', '蔬菜'],
    13 : ['三重區', '蔬菜'],
    14 : ['桃　農', '蔬菜'],
    15 : ['宜蘭市', '蔬菜'],
    16 : ['豐原區', '蔬菜'],
    17 : ['板橋區', '蔬菜'],
    18 : ['三重區', '水果'],
    19 : ['嘉義市', '水果'],
    20 : ['高雄市', '水果'],
    21 : ['鳳山區', '水果'],
    22 : ['台中市', '水果'],
    23 : ['台北一', '水果'],
    24 : ['台北二', '水果'],
    25 : ['台東市', '水果'],
    26 : ['東勢區', '水果'],
    27 : ['桃　農', '水果'],
    28 : ['宜蘭市', '水果'],
    29 : ['豐原區', '水果'],
    30 : ['板橋區', '水果']
}

dataset_folder = './mDataset/'

# 檔案下載url   
weather_data_url = 'https://github.com/Yi-Wei-Lin/Tibame_AI_Project/raw/main/userdata/amoswu/dataset/reportdaily_mean_fillna.csv'
typhoon_data_url = 'https://github.com/Yi-Wei-Lin/Tibame_AI_Project/raw/main/userdata/amoswu/dataset/TyphoonDatabase.csv'
dataset_url = 'https://github.com/Yi-Wei-Lin/Tibame_AI_Project/raw/main/userdata/amoswu/dataset/'

# 將檔案下載
def download_data():
    if not os.path.exists('weather.csv'): urllib.request.urlretrieve(weather_data_url, 'weather.csv') 
    if not os.path.exists('typhoon.csv'): urllib.request.urlretrieve(typhoon_data_url, 'typhoon.csv') 
    # if not os.path.exists('mDataset/typhoon.csv'): urllib.request.urlretrieve(typhoon_data_url, 'mDataset/typhoon.csv')
    for i in range(1, 25):
        if not os.path.exists(dataset_folder + crop_dict[i][0] + '.csv'):
            urllib.request.urlretrieve(dataset_url + crop_dict[i][0] + '.csv', dataset_folder + crop_dict[i][0] + '.csv')


# 要移除的 天氣欄位列表
# weather columb全部列表: 'date', 'city', 'StnPres', 'SeaPres', 'StnPresMax', 'StnPresMaxTime', 'StnPresMin', 'StnPresMinTime', 'Temperature', 'TMax', 'TMaxTime', 'TMin', 'TMinTime', 'TdDewPoint', 'RH', 'RHMin', 'RHMinTime', 'WS', 'WD', 'WSGust', 'WDGust', 'WGustTime', 'Precp', 'PrecpHour', 'PrecpMax10', 'PrecpMax10Time', 'PrecpMax60', 'PrecpMax60Time', 'SunShine', 'SunShineRate', 'GloblRad', 'VisbMean', 'EvapA', 'UVIMax', 'UVIMaxTime', 'CloudAmount'
weather_drop_columns = [
              'StnPres', 'SeaPres', 'StnPresMax', 'StnPresMaxTime', 
              'StnPresMin', 'StnPresMinTime', 'RHMin',  'WSGust', 
              'GloblRad', 'VisbMean', 'UVIMax', 'UVIMaxTime', 'CloudAmount'
]

# 讀取天氣資料
def getWeatherDf():
    df = pd.read_csv('weather.csv', encoding='utf-8')
    # 移除不必要的欄位
    df = df.drop(weather_drop_columns, axis=1)  
    # 使用index做merge，將df表格依日期拉平
    df_date = df['date'].drop_duplicates().to_frame().set_index('date')

    for cityname, citycode in city.items():
        df_city = df.loc[df['city'] == cityname].add_suffix('_' + citycode).set_index('date' + '_' + citycode)
        df_date = pd.merge(df_date, df_city, how='left', left_index = True, right_index = True)
    # 將城市名稱欄位移除
    df_date = df_date[df_date.columns.drop(list(df_date.filter(regex='city')))]
    df_weather = df_date
    return df_weather

# 要移除的城市名單
# city_drop = ['KLU', 'TPE', 'TPH', 'TYC', 'HSC', 'HSH', 'MAL', 'TXG', 'CWH', 
#         'NTO', 'YLH', 'CYI', 'CHY', 'TNN', 'KHH', 'IUH', 'ILN', 'HWA', 'TTT']
city_drop_list = ['KLU', 'TPH', 'TYC', 'HSC', 'HSH', 'MAL', 'TXG', 'CYI']

# 移除城市
def weather_city_left():
    city_drop_columns = []
    for i in city_drop_list:
        city_drop_columns.append([s for s in list(getWeatherDf().columns) if s.__contains__(i)])
    city_drop_columns = list(np.array(city_drop_columns).reshape(-1))
    return city_drop_columns
    df_weather = getWeatherDf().drop(city_drop_columns, axis=1)
    return df_weather

# 計算兩個日期間隔多少天
def daysBetweenDate(startdate: str, enddate: str) -> int:
    startdate = datetime.strptime(startdate, "%Y-%m-%d")
    enddate = datetime.strptime(enddate, "%Y-%m-%d")
    days = (enddate - startdate).days + 1
    return days

# 日期調整
def dateShift(startdate: str, shiftday: int) -> str:
    startdate = datetime.strptime(startdate, "%Y-%m-%d")
    targetdate = startdate + timedelta(days=shiftday)
    return datetime.strftime(targetdate, "%Y-%m-%d")

def getTyphoonDf():
    # 讀取颱風資料庫
    df_typhoon = pd.read_csv('typhoon.csv', encoding='utf-8')

    # 將Warning的日期文字轉為4個欄位'startdate','starttime','enddate','endtime'
    df_typhoon[['startdate','starttime','enddate','endtime']] = df_typhoon['Warning'].str.split().tolist()
    # 將最前面塞入date欄位
    df_typhoon_new = pd.DataFrame(columns=df_typhoon.columns.insert(0, 'date'))

    # 將所有颱風按日期列出
    # 使用iterrows
    start_time = time.time()
    for index, row in df_typhoon.iterrows():
        days = daysBetweenDate(row['startdate'], row['enddate'])
        for day in range(0, days):
            date = dateShift(row['startdate'],day)
            datesr1 = pd.Series(date).append(df_typhoon.iloc[index]).rename({0: 'date'})
            df_typhoon_new = df_typhoon_new.append(datesr1, ignore_index=True)

    # 將相同日期的去除並暫時只留WarnMark欄位
    df_typhoon_wm = pd.DataFrame(df_typhoon_new, columns=['date'])
    df_typhoon_wm['WarnMark'] = 1
    df_typhoon_wm = df_typhoon_wm.drop_duplicates().reset_index().drop(columns=['index'])
    df_typhoon = df_typhoon_wm.set_index('date')

    return df_typhoon


# 要移除的欄位列表
# market columns 全部列表: 'Date', 'Market', 'Product', 'Up_price', 'Mid_price', 'Low_price', 'Avg_price', 'Volume', 'Month', 'Week_day', 'Year', 'Rest_day'
market_drop_columns = [
              'Product',
              # 'Month', 
              # 'Week_day', 
              'Year', 
              'Rest_day'
]

# 將休市價格填入前後日之平均價格(暫不使用)
def fillna_fb_mean(self):
    df_f = self.fillna(method='ffill')
    df_b = self.fillna(method='bfill')
    df_fb = (df_f+df_b)/2
    return df_fb

# 讀取農產品資料
def getCorpDf(crop_no, market_id, price_na_del=False, ohe=False):
    csv_name = crop_dict[crop_no][0] + '.csv'
    df = pd.read_csv(dataset_folder + csv_name, encoding='utf-8')
    # csv_name = crop_dict[crop_no][0] + '.csv'
    # df = pd.read_csv(csv_name, encoding='utf-8')
    # 移除不需要的欄位
    df = df.drop(market_drop_columns, axis=1)
    # 去除價格空值者
    if price_na_del:
        df = df
    else:
        # 將休市價格填入前一日價格
        df = df.fillna(method="ffill")
    # 只拿出指定市場的資料
    # df = df[df.Market == market_dict[0]]
    df = df[df.Market == market_dict[market_id][0]]

    # 去除空值
    df = df.dropna()
    df_crop = df.reset_index().drop(['index'], axis=1)
    
    if ohe:
        onehotencoder = OneHotEncoder()
        df_crop_month_ohe = onehotencoder.fit_transform(df_crop[["Month"]]).toarray()
        month = pd.DataFrame(df_crop_month_ohe)
        for i in month:
            new = int(i) + 1
            new = str(new)
            month = month.rename(columns={i:new})
        month = month.add_prefix("Month_")
        onehotencoder = OneHotEncoder()
        df_crop_week_ohe = onehotencoder.fit_transform(df_crop[["Week_day"]]).toarray()
        week = pd.DataFrame(df_crop_week_ohe)
        for i in week:
            new = int(i) + 1
            new = str(new)
            week = week.rename(columns={i:new})
        week = week.add_prefix("Week_day_")
        df_crop = df_crop.join(month, how="left")
        df_crop = df_crop.join(week, how="left")
        df_crop = df_crop.drop(['Month', 'Week_day'], axis=1).rename(columns={'Date': 'date'}).set_index('date')

    else:
        df_crop = df_crop.drop(['Month', 'Week_day'], axis=1).rename(columns={'Date': 'date'}).set_index('date')


    return df_crop


def getAllDf(add_weather_data, add_typhoon_data, crop_no, market_id, price_na_del):
    # 下載訓練資料集
    download_data()
    df_weather = weather_city_left()
    df_typhoon = getTyphoonDf()
    df_crop = getCorpDf(crop_no, market_id)

    df_all = df_crop
    # 是否要合併天氣資料
    if add_weather_data:
        df_all = pd.merge(df_all, df_weather, how='inner', left_index = True, right_index = True)
    # 是否要合併颱風資料
    if add_typhoon_data:
        df_all = pd.merge(df_all, df_typhoon, how='left', left_index = True, right_index = True).fillna(0)

    # 把平均價格移到最後1欄
    col_Avg_price = df_all.pop('Avg_price')
    df_all = pd.concat([df_all, col_Avg_price], 1)

    # 將資料複製一份來作業, 將欄位index改為date
    df = df_all.copy()
    df = df.reset_index().rename(columns={'index': 'date'})

    return df


# add_weather_data = False
# add_typhoon_data = True
# price_na_del = True
# train_start_date = '2013-01-02'
# train_end_date = '2020-05-31'
# test_start_date = '2020-06-01'
# test_end_date = '2021-06-18'
# pastDay = 30
# futureDay = 7
# model_no = 3
# repeat_train = True
# LSTM_unit_1 = 10
# LSTM_unit_2 = ''
# batch_size = 30
# epochs = 1
# validation_split = 0.1
# patience = 1
# plotDay = 1
# pic_days = 300
# path = './'
# dev_notes = ''
# market_id = 23
# crop_no = 11

# df = getAllDf(add_weather_data, add_typhoon_data, crop_no, market_id, price_na_del)
# print(df)