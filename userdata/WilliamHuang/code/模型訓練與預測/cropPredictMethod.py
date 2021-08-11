import os
from tensorflow.keras.models import Sequential, load_model
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import joblib
import numpy as np
import mDataset
import mOther
import mModel
import mMySQL
import mData, mConfig


# market_drop_columns_no = 1


# date_today = mOther.getDateString()
# save_result_dir = './mResult/%s/' % date_today
# path = './'
# price_na_del = False
# croplist = [11, 12, 13, 14, 16, 17, 18, 19, 20, 23, 24]
# daylist = [1, 2, 3, 7]
# market_id = 23
# crop_no = 19
# futureDay = 7
# pastDay = 10
# ohe = False
# ohe = True
# add_weather_data = False
# add_typhoon_data = True
# add_typhoon_data = False

# 先取一個大範圍的資料區間，避免ohe少了某幾個周月欄位
# data_get_start = '2019-01-01'
# today_date = mOther.getDateString2()
# end_date = today_date
# start_date = mDataset.dateShift(end_date, -30)




def price_na_method(price_na_del, df, market_id):
    if price_na_del:
        df = df
    else:
        # 將休市價格填入前一日價格
        df = df.fillna(method="ffill")
    # 只拿出指定市場的資料
    # df = df[df.Market == mConfig.market_dict[0]]
    return df

def load_model_scaler(path, h5_file_name, crop_no, futureDay):
    model = Sequential()
    model = load_model(path +'h5/' + h5_file_name)
    xx_scale, yy_scale =  mModel.scaler_load(path, futureDay, mConfig.crop_dict, crop_no)
    print(f'{crop_no}-{mConfig.crop_dict[crop_no][0]}_D{futureDay}_M23_')
    model.summary()
    return model, xx_scale, yy_scale 

# 市場日期進行onehotencoding
# 當ohe時，必然market_drop_columns_no =1 (即是刪除三個)
# 當不ohe時，可能為 1. 刪除三個 2. 刪除五個
def is_ohe(ohe, df_crop, market_drop_columns_no):
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

    elif market_drop_columns_no == 1:
        df_crop = df_crop.drop(['Month', 'Week_day'], axis=1).rename(columns={'Date': 'date'}).set_index('date')

    else: # 即是 market_drop_columns_no ==2
        df_crop = df_crop.rename(columns={'Date': 'date'}).set_index('date')

    return df_crop

# 是否合併天氣與颱風資料
def is_weather_typhoon(add_weather_data, add_typhoon_data, df_all, data_get_start, end_date, pastDay):
    if add_weather_data or add_typhoon_data:
        df_weather = mData.queryWeather(str(data_get_start), str(end_date))
        # 是否要合併天氣資料
        if add_weather_data:
            df_all = pd.merge(df_all, df_weather, how='inner', left_index = True, right_index = True)
        # 是否要合併颱風資料
        df_typhoon = df_weather['WarnMark']
        if add_typhoon_data:
            df_typhoon = df_typhoon.head(pastDay)
            df_all = pd.merge(df_all, df_typhoon, how='left', left_index = True, right_index = True).fillna(0)
    return df_all