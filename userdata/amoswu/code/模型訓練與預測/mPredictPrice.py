from keras.models import Sequential, load_model
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
import keras.backend as K

import mConfig
import mDataset
import mOther
import mModel
import mData

date_today = mOther.getDateString()
save_result_dir = './mResult/'
# save_result_dir = './mResult/%s/' % date_today

def predictFromH5(_df, _list_predict_day, _crop_id, _market_id):
    # 取得h5的檔案
    pre_dict = {}

    for p_day in _list_predict_day:
        h5_file_name = '_D' + str(p_day) + '_C' + str(_crop_id) + '_M' + str(_market_id) + '.h5'

        model = load_model(save_result_dir + h5_file_name)
        # model.summary()

        # 設定x_train, y_train的scaler
        x_sc = mModel.loadScaler(save_result_dir, _market_id, _crop_id, p_day, 'x')
        y_sc = mModel.loadScaler(save_result_dir, _market_id, _crop_id, p_day, 'y')

        # x_sc.fit(_df)
        df_scaled = x_sc.transform(_df)

        np_entry = mModel.buildPredictEntryOne(df_scaled)

        pred_value = model.predict(np_entry)
        K.clear_session()

        pred_value_shape = pred_value.reshape(pred_value.shape[0], pred_value.shape[1])

        # 將預測值轉換回實際價格
        pred_value_price = y_sc.inverse_transform(pred_value_shape)

        pred_price = pred_value_price[0][0]

        pre_dict[p_day] = pred_price

    return pre_dict

def cropPricePredictOne(_predict_date, _past_day, _list_predict_day, _crop_id, _market_id):

    today_date = mOther.getDateString2()
    if _predict_date != '':
        today_date = _predict_date

    end_date = today_date
    start_date = mDataset.dateShift(end_date, -30)

    print('crop_name:%s, start_date:%s, end_date:%s, past_day:%s, crop_id:%s, market_id:%s ' % (mDataset.crop_dict[_crop_id][1], start_date, end_date, _past_day, _crop_id, _market_id))

    is_add_weather_data = mConfig.is_add_weather_data
    is_add_typhoon_data = mConfig.is_add_typhoon_data
    df_crop = mData.getAllDfFromDB(is_add_weather_data, is_add_typhoon_data, start_date, end_date, _crop_id, _market_id)

    df = df_crop.tail(_past_day)

    pred_dict = predictFromH5(df, _list_predict_day, _crop_id, _market_id)

    current_price = np.array(df['Avg_price'].tail(1))[0]

    return current_price, pred_dict
