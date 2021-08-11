import numpy as np
import os
from tensorflow.keras.models import Sequential, load_model, clone_model
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timezone, timedelta

import mDataset
import mModel
import mOther

'''
本處版本僅限於試驗，實際訓練仍在colab上，故並未有迴圈式的訓練coding
'''

add_weather_data = False
add_typhoon_data = True
price_na_del = True
train_start_date = '2013-01-02'
train_end_date = '2020-05-31'
test_start_date = '2020-06-01'
test_end_date = '2021-06-18'
pastDay = 30
futureDay = 7
model_no = 3
repeat_train = True
LSTM_unit_1 = 10
LSTM_unit_2 = ''
batch_size = 30
epochs = 1
validation_split = 0.1
patience = 1
plotDay = 1
pic_days = 300
path = os.path.dirname(os.path.abspath(__file__)) + '/'
dev_notes = ''
date_today = mOther.getDateString()
# save_result_dir = './result/%s/' % date_today
market_id = 23
crop_no = 11
ohe = False
# save_google = True

# 建立訓練模型
def buildPredictModel(crop_no, crop_dict, market_id, add_weather_data, add_typhoon_data, price_na_del, ohe, 
                        train_start_date, train_end_date, test_start_date, test_end_date,
                        pastDay, futureDay, model_no, repeat_train, LSTM_unit_1, LSTM_unit_2,
                        batch_size, epochs, validation_split, patience,
                        plotDay, pic_days, path, dev_notes=''
                        ):
    # 取得現在時間(TP) 並設定為 +8 時區
    time_now = datetime.now(timezone(timedelta(hours=+8))).isoformat(timespec="seconds")[5:16].replace('-', '', 1).replace('T', '-')

    df = mDataset.getAllDf(add_weather_data, add_typhoon_data, crop_no, market_id, price_na_del)

        # 依訓練資料的期間、測試資料的期間來切分資料
    df_train, df_test = mModel.splitDataByDate(df, train_start_date, train_end_date, test_start_date, test_end_date)

    # train 正則化與建立
    df_train_scaled = df_train.values
    xx_scale = MinMaxScaler()
    x_train = mModel.buildX(xx_scale.fit_transform(df_train_scaled), pastDay, futureDay)
    yy_scale = MinMaxScaler()
    y_train_fitted_data = yy_scale.fit_transform(df_train_scaled[:, -1].reshape(-1, 1))
    y_train = mModel.buildY(y_train_fitted_data, pastDay, futureDay)

    # test 正則化與建立
    df_test_scaled = df_test.values
    x_test = mModel.buildX(xx_scale.fit_transform(df_test_scaled), pastDay, futureDay)
    y_test = mModel.buildY(yy_scale.fit_transform(df_test_scaled[:, -1].reshape(-1, 1)), pastDay, futureDay)
    
    # 模型訓練
    if model_no == 1:
        model = mModel.model_dict[model_no][0](x_train.shape, LSTM_unit_1, LSTM_unit_2)
        model_name = 'buildManyToOneModel01'
    elif model_no == 2:
        model = mModel.model_dict[model_no][0](x_train.shape, LSTM_unit_1, LSTM_unit_2)
        print('model2')
        model_name = 'buildManyToOneModel02'
    elif model_no == 3:
        model = mModel.model_dict[model_no][0](x_train.shape, LSTM_unit_1, LSTM_unit_2)
        model_name = 'buildManyToOneModel03'
        if repeat_train:
            model_repeat1 = clone_model(model)
            model_repeat2 = clone_model(model)
            model_repeat3 = clone_model(model)
            model_repeat4 = clone_model(model)
            model_repeat5 = clone_model(model)
        print('model3')
    else:
        print('選錯model了')

    callback = EarlyStopping(monitor="val_loss", patience=patience, verbose=2, mode="auto")


    if model_no == 3 and repeat_train == True:
        model_repeat1.compile(loss="mse", optimizer="adam", metrics=["mse"])
        train_history1 = model_repeat1.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_split=validation_split, callbacks=[callback])
        model_repeat2.compile(loss="mse", optimizer="adam", metrics=["mse"])
        train_history2 = model_repeat2.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_split=validation_split, callbacks=[callback])
        model_repeat3.compile(loss="mse", optimizer="adam", metrics=["mse"])
        train_history3 = model_repeat3.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_split=validation_split, callbacks=[callback])
        model_repeat4.compile(loss="mse", optimizer="adam", metrics=["mse"])
        train_history4 = model_repeat4.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_split=validation_split, callbacks=[callback])
        model_repeat5.compile(loss="mse", optimizer="adam", metrics=["mse"])
        train_history5 = model_repeat5.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_split=validation_split, callbacks=[callback])
    else:
        train_history1 =  model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_split=validation_split, callbacks=[callback])

    # 執行模型，預測價格
    # if model_no == 3 and repeat_train == True:
    #     y_pre1 = mModel.model_cal(model_repeat1, x_test, y_test)
    #     y_pre2 = mModel.model_cal(model_repeat2, x_test, y_test)
    #     y_pre3 = mModel.model_cal(model_repeat3, x_test, y_test)
    #     y_pre4 = mModel.model_cal(model_repeat4, x_test, y_test)
    #     y_pre5 = mModel.model_cal(model_repeat5, x_test, y_test)
    # else:
    #     y_pre = mModel.model_cal(model, x_test, y_test)
    if model_no == 3 and repeat_train == True:
        y_pre1 = mModel.model_cal(model_repeat1, x_test)
        y_pre2 = mModel.model_cal(model_repeat2, x_test)
        y_pre3 = mModel.model_cal(model_repeat3, x_test)
        y_pre4 = mModel.model_cal(model_repeat4, x_test)
        y_pre5 = mModel.model_cal(model_repeat5, x_test)
    else:
        y_pre = mModel.model_cal(model, x_test)

    # 計算分數
    if model_no == 3 and repeat_train == True:
        # 建立各模型-預測值轉換回實際價格，並計算各自分數
        pre_price1, test_price, diff_price1 = mModel.price_inverse(y_pre1, y_test, yy_scale)
        pre_price2, test_price, diff_price2 = mModel.price_inverse(y_pre2, y_test, yy_scale)
        pre_price3, test_price, diff_price3 = mModel.price_inverse(y_pre3, y_test, yy_scale)
        pre_price4, test_price, diff_price4 = mModel.price_inverse(y_pre4, y_test, yy_scale)
        pre_price5, test_price, diff_price5 = mModel.price_inverse(y_pre5, y_test, yy_scale)
        print('*'*10 + '1' +'*'*10)
        MSE_1, RMSE_1, MAE_1, R2_1 = mModel.score_cal(pre_price1, test_price)
        print('*'*10 + '2' +'*'*10)
        MSE_2, RMSE_2, MAE_2, R2_2 = mModel.score_cal(pre_price2, test_price)
        print('*'*10 + '3' +'*'*10)
        MSE_3, RMSE_3, MAE_3, R2_3 = mModel.score_cal(pre_price3, test_price)
        print('*'*10 + '4' +'*'*10)
        MSE_4, RMSE_4, MAE_4, R2_4 = mModel.score_cal(pre_price4, test_price)
        print('*'*10 + '5' +'*'*10)
        MSE_5, RMSE_5, MAE_5, R2_5 = mModel.score_cal(pre_price5, test_price)
        pre_price_list = [pre_price1, pre_price2, pre_price3, pre_price4, pre_price5 ]
        RMSE_min = min([RMSE_1, RMSE_2, RMSE_3, RMSE_4, RMSE_5])
        RMSE_dict = {
            RMSE_1:[mModel.score_cal(pre_price1, test_price), model_repeat1, 1], 
            RMSE_2:[mModel.score_cal(pre_price2, test_price), model_repeat2, 2], 
            RMSE_3:[mModel.score_cal(pre_price3, test_price), model_repeat3, 3], 
            RMSE_4:[mModel.score_cal(pre_price4, test_price), model_repeat4, 4],
            RMSE_5:[mModel.score_cal(pre_price5, test_price), model_repeat5, 5],
        }
        MSE, RMSE, MAE, R2 = RMSE_dict[RMSE_min][0]
        pre_price = pre_price_list[RMSE_dict[RMSE_min][2]-1]
    else:
        # 將預測值轉換回實際價格，並計算分數
        pre_price, test_price, diff_price = mModel.price_inverse(y_pre, y_test, yy_scale)
        MSE, RMSE, MAE, R2 = mModel.score_cal(pre_price, test_price)

    # 畫圖
    mOther.DrawingPlot(path, pre_price, test_price, pic_days, crop_dict, futureDay, crop_no, time_now, pastDay, RMSE)
  

    # 儲存scaler
    # mModel.scaler_save(path, time_now, xx_scale, yy_scale, pastDay, futureDay, crop_dict, crop_no, RMSE)
    mModel.scaler_save(path, xx_scale, yy_scale, futureDay, crop_dict, crop_no)
    
    # 儲存模型
    # mModel.model_save(path, time_now, model, crop_dict, crop_no, pastDay, futureDay, RMSE)
    mModel.model_save(path, model, crop_dict, crop_no, futureDay)

buildPredictModel(crop_no, mDataset.crop_dict, market_id, add_weather_data, add_typhoon_data, price_na_del, ohe,
                    train_start_date, train_end_date, test_start_date, test_end_date,
                    pastDay, futureDay, model_no, repeat_train, LSTM_unit_1, LSTM_unit_2,
                    batch_size, epochs, validation_split, patience,
                    plotDay, pic_days, path, dev_notes=''
                    )

# df = mDataset.getAllDf(add_weather_data, add_typhoon_data, crop_no, market_id, price_na_del)
# df, train_start_date, train_end_date, test_start_date, test_end_date
# df_train = df.iloc[df[(train_start_date <= df.date) & (df.date <= train_end_date)].index].set_index('date')
# df_test = df.iloc[df[(test_start_date <= df.date) & (df.date <= test_end_date)].index].set_index('date')

# print(train_start_date)
# print(np.array([df.date]))

# print(df)





