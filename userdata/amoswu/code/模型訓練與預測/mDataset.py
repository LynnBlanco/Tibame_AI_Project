import urllib.request
import os
import ssl
import pandas as pd
import datetime
import mConfig

ssl._create_default_https_context = ssl._create_unverified_context

crop_dict = mConfig.crop_dict
market_dict = mConfig.market_dict
dataset_folder = mConfig.dataset_folder
city_dict = mConfig.city_dict

# 檔案下載url
weather_data_url = 'https://github.com/Yi-Wei-Lin/Tibame_AI_Project/raw/main/userdata/amoswu/dataset/reportdaily_mean_fillna.csv'
typhoon_data_url = 'https://github.com/Yi-Wei-Lin/Tibame_AI_Project/raw/main/userdata/amoswu/dataset/TyphoonDatabase.csv'
dataset_url = 'https://github.com/Yi-Wei-Lin/Tibame_AI_Project/raw/main/userdata/amoswu/dataset/'

# 檔案下載
def downloadDataset():
    if not os.path.exists(dataset_folder): os.mkdir(dataset_folder)
    if not os.path.exists('mDataset/weather.csv'): urllib.request.urlretrieve(weather_data_url, 'mDataset/weather.csv')
    if not os.path.exists('mDataset/typhoon.csv'): urllib.request.urlretrieve(typhoon_data_url, 'mDataset/typhoon.csv')
    for i in range(1, 25):
        if not os.path.exists(dataset_folder + crop_dict[i][0] + '.csv'):
            urllib.request.urlretrieve(dataset_url + crop_dict[i][0] + '.csv', dataset_folder + crop_dict[i][0] + '.csv')

# 讀取天氣資料
def getWeatherDf():
    df = pd.read_csv(dataset_folder + 'weather.csv', encoding='utf-8')
    # 移除不需要的欄位
    df = df.drop(mConfig.weather_drop_columns, axis=1)
    # print(df.head(3))
    # 使用index做merge，將weather表格依日期拉平
    df_date = df['date'].drop_duplicates().to_frame().set_index('date')

    for cityname, citycode in city_dict.items():
        df_city = df.loc[df['city'] == cityname].add_suffix('_' + citycode).set_index('date' + '_' + citycode)
        df_date = pd.merge(df_date, df_city, how='left', left_index = True, right_index = True)

    df_date = df_date[df_date.columns.drop(list(df_date.filter(regex='city')))]
    df_weather = df_date

    return df_weather

# 計算兩個日期間隔多少天
def daysBetweenDate(startdate: str, enddate: str) -> int:
    startdate = datetime.datetime.strptime(startdate, "%Y-%m-%d")
    enddate = datetime.datetime.strptime(enddate, "%Y-%m-%d")
    days = (enddate - startdate).days + 1
    return days

# 日期調整
def dateShift(startdate: str, shiftday: int) -> str:
    startdate = datetime.datetime.strptime(startdate, "%Y-%m-%d")
    targetdate = startdate + datetime.timedelta(days=shiftday)
    return datetime.datetime.strftime(targetdate, "%Y-%m-%d")

def getTyphoonDf():
    # 讀取颱風資料庫
    df_typhoon = pd.read_csv(dataset_folder + 'typhoon.csv', encoding='utf-8')

    # 將Warning的日期文字轉為4個欄位'startdate','starttime','enddate','endtime'
    df_typhoon[['startdate', 'starttime', 'enddate', 'endtime']] = df_typhoon['Warning'].str.split().tolist()
    # 將最前面塞入date欄位
    df_typhoon_new = pd.DataFrame(columns=df_typhoon.columns.insert(0, 'date'))

    # 將所有颱風按日期列出
    # 使用iterrows
    for index, row in df_typhoon.iterrows():
        days = daysBetweenDate(row['startdate'], row['enddate'])
        for day in range(0, days):
            date = dateShift(row['startdate'], day)
            datesr1 = pd.Series(date).append(df_typhoon.iloc[index]).rename({0: 'date'})
            df_typhoon_new = df_typhoon_new.append(datesr1, ignore_index=True)

    # 將相同日期的去除並暫時只留WarnMark欄位
    df_typhoon_wm = pd.DataFrame(df_typhoon_new, columns=['date'])
    df_typhoon_wm['WarnMark'] = 1
    df_typhoon_wm = df_typhoon_wm.drop_duplicates().reset_index().drop(columns=['index'])
    df_typhoon = df_typhoon_wm.set_index('date')

    return df_typhoon

def getCorpDf(_crop_id, _market_id):
    # 讀取農產品資料
    csv_name = crop_dict[_crop_id][0] + '.csv'
    df = pd.read_csv(dataset_folder + csv_name, encoding='utf-8')
    # 移除不需要的欄位
    df = df.drop(mConfig.market_drop_columns, axis=1)

    # 將休市價格填入前一日價格
    df = df.fillna(method="ffill")
    # 只拿出指定市場的資料
    df = df[df.Market == market_dict[_market_id][0]]

    df = df.dropna()
    df_crop = df.rename(columns={'Date': 'date'}).set_index('date')

    return df_crop

def getAllDf(_is_add_weather_data, _is_add_typhoon_data, _crop_id, _market_id):
    # 下載訓練資料集
    downloadDataset()

    # 取得訓練資料集 Dataframe
    df_weather = getWeatherDf()
    df_typhoon = getTyphoonDf()
    df_crop = getCorpDf(_crop_id, _market_id)

    df_all = df_crop

    # 是否要合併天氣資料
    if _is_add_weather_data:
        df_all = pd.merge(df_all, df_weather, how='inner', left_index=True, right_index=True)
    # 是否要合併颱風資料
    if _is_add_typhoon_data:
        df_all = pd.merge(df_all, df_typhoon, how='left', left_index=True, right_index=True).fillna(0)

    # 把平均價格移到最後1欄
    col_Avg_price = df_all.pop('Avg_price')
    df_all = pd.concat([df_all, col_Avg_price], axis = 1)

    # 將資料複製一份來作業, 將欄位index改為date
    df = df_all.copy()
    df = df.reset_index().rename(columns={'index': 'date'})

    return df