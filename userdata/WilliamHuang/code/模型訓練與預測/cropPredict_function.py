import pandas as pd
import numpy as np
import mModel
import mData, cropPredictMethod, mConfig

def crop_Predict(
                crop_no, market_id, pastDay, futureDay,
                ohe, price_na_del, market_drop_columns_no, add_weather_data, add_typhoon_data,
                data_get_start, end_date, path
                ):
        
    '''----------該作物統一資料區----------'''
    # 抓取資料庫該作物市場資料
    df_crop = mData.queryDailyPrice(2, data_get_start, end_date, crop_no, market_id)

    '''----------該作物 模型資料之取得----------'''
    h5_file_name = f'{crop_no}-{mConfig.crop_dict[crop_no][0]}_D{futureDay}_M23.h5'

    # 呼叫指定的模型與scaler
    model, xx_scale, yy_scale = cropPredictMethod.load_model_scaler(path, h5_file_name, crop_no, futureDay)
    '''----------market_drop_columns----------'''
    market_drop_columns = mConfig.market_drop_dict[market_drop_columns_no]
    # 移除不需要的欄位
    df = df_crop.drop(market_drop_columns, axis=1)
    '''----------price_na_del----------'''
    df = cropPredictMethod.price_na_method(price_na_del, df, market_id)

    # 只拿出指定市場的資料
    df = df[df.Market == mConfig.market_dict[market_id][0]]

    # 去除空值
    df = df.dropna()
    df_crop = df.reset_index().drop(['index'], axis=1)

    # 市場日期進行onehotencoding
    df_crop = cropPredictMethod.is_ohe(ohe, df_crop, market_drop_columns_no)

    df_crop = df_crop.tail(pastDay)

    df_all = df_crop
    df_all = cropPredictMethod.is_weather_typhoon(add_weather_data, add_typhoon_data, df_all, data_get_start, end_date, pastDay)

    # 把平均價格移到最後1欄
    col_Avg_price = df_all.pop('Avg_price')
    df_all = pd.concat([df_all, col_Avg_price], 1)

    # 將資料複製一份來作業, 將欄位index改為date
    df = df_all.copy()
    df = df.reset_index().rename(columns={'index': 'date'}).set_index('date').select_dtypes(exclude=['object'])

    x_test = xx_scale.transform(df.values).reshape(1, df.shape[0], df.shape[1])
    y_pre = mModel.model_cal(model, x_test)
    pre_price = yy_scale.inverse_transform(y_pre)
    pre_price = pre_price[0][0]
    print('pre_price: ', pre_price)
    print('-'*20)
    print(df)
    return pre_price, df['Avg_price'].tail(1)[0]


# 呼叫模型參數字典
model_input_param_dict = mConfig.model_input_param_dict


