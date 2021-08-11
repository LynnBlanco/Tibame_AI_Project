import numpy as np
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten, LSTM, GRU, TimeDistributed, RepeatVector, Lambda, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.models import Sequential, load_model, clone_model
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib

# 將資料整理為x
def buildX(train, pastDay=30, futureDay=3):
    x = []
    for i in range(train.shape[0] - futureDay - pastDay):
        x.append(train[i : i+pastDay])
    return np.array(x)

# 將資料整理為y
def buildY(test, pastDay=30, futureDay=3):
    y = []
    for i in range(test.shape[0] - futureDay - pastDay):
        y.append(test[i+pastDay+futureDay : i+pastDay+futureDay+1, -1])
    return np.array(y)


# 依訓練資料的期間、測試資料的期間來切分資料
def splitDataByDate(df, train_start_date, train_end_date, test_start_date, test_end_date):
    df_train = df.iloc[df[(train_start_date <= df.date) & (df.date <= train_end_date)].index].set_index('date')
    df_test = df.iloc[df[(test_start_date <= df.date) & (df.date <= test_end_date)].index].set_index('date')

    # 將非數字的欄位移除
    df_train = df_train.select_dtypes(exclude=['object'])
    df_test = df_test.select_dtypes(exclude=['object'])

    return df_train, df_test

# 模型1 (純雙層LSTM)
def buildManyToOneModel01(shape, LSTM_unit_1, LSTM_unit_2):
    model = Sequential()
    # model.add(GRU(units=256,
    #     return_sequences=False,
    #     input_shape=(shape[1], shape[2])))
    model.add(LSTM(units=LSTM_unit_1,
        return_sequences=True,
        input_shape=(shape[1], shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(units=LSTM_unit_2, return_sequences=False,))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='mse', optimizer='adam')
    model.summary()
    return model

# 模型2 (LSTM 搭配Biderectional)
def buildManyToOneModel02(shape, LSTM_unit_1, LSTM_unit_2):
    model = Sequential()
    # model.add(Bidirectional(LSTM(units=LSTM_unit_1,
    #     return_sequences=True,
    #     input_shape=(shape[1], shape[2])
    #     )))
    model.add(LSTM(units=LSTM_unit_1,
        return_sequences=True,
        input_shape=(shape[1], shape[2])
        ))
    model.add(Dropout(0.2))
    # model.add(LSTM(units=LSTM_unit_2, 
    #             return_sequences=False, 
    #             input_shape=(shape[1], shape[2]),
    #             go_backwards=True
    #             ))
    model.add(Bidirectional(LSTM(units=LSTM_unit_2, 
                return_sequences=False, 
                input_shape=(shape[1], shape[2]),
                go_backwards=True
                )))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='mse', optimizer='adam')
    model.build((None, shape[1], shape[2]))
    model.summary()
    return model

# 模型3
def buildManyToOneModel03(shape, LSTM_unit_1, LSTM_unit_2):
    model = Sequential()
    model.add(LSTM(LSTM_unit_1, return_sequences=False, input_shape=(shape[1], shape[2])))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='mse', optimizer='adam', metrics=['mse'])
    model.summary()
    return model

# 模型字典: function name, 說明, 是否shift day, 是否只輸出1天(本次預設皆shift)
model_dict = {
    1 : [buildManyToOneModel01, 'LSTM many to one', True, True],
    2 : [buildManyToOneModel02, 'LSTM & Biderectional many to one', True, True],
    3 : [buildManyToOneModel03, 'One LSTM to one', True, True],
    # 4 : [buildManyToOneModel4, 'LSTM many to one', True, True],
    5 : ['', ''],
}

# scaler 存檔
# def scaler_save(path, time_now, xx_scale, yy_scale, pastDay, futureDay, crop_dict, crop_no, RMSE):
def scaler_save(path, xx_scale, yy_scale, futureDay, crop_dict, crop_no):
    joblib.dump(xx_scale, path + 'scaler/' + f'{crop_no}-{crop_dict[crop_no][0]}_D{futureDay}_M23_' + 'X_scaler.model')
    # joblib.dump(xx_scale, path + 'scaler/' + f'{crop_dict[crop_no][0]}_{time_now}_P{pastDay}F{futureDay}_RMSE={int(round(RMSE, 0))}' + 'X_scaler.model')
    joblib.dump(yy_scale, path + 'scaler/' + f'{crop_no}-{crop_dict[crop_no][0]}_D{futureDay}_M23_' + 'Y_scaler.model')
    # joblib.dump(yy_scale, path + 'scaler/' + f'{crop_dict[crop_no][0]}_{time_now}_P{pastDay}F{futureDay}_RMSE={int(round(RMSE, 0))}' + 'Y_scaler.model')

# scaler模型獲取
def scaler_load(path, futureDay, crop_dict, crop_no):
# def scaler_load(path, scaler_time, xx_scale, yy_scale, pastDay, futureDay, crop_dict, crop_no, RMSE):
    xx_scale = joblib.load(path + 'scaler/' + f'{crop_no}-{crop_dict[crop_no][0]}_D{futureDay}_M23_' + 'X_scaler.model')
    # xx_scale = joblib.load(path + 'scaler/' + f'{crop_dict[crop_no][0]}_{scaler_time}_P{pastDay}F{futureDay}_RMSE={int(round(RMSE, 0))}' + 'X_scaler.model')
    yy_scale = joblib.load(path + 'scaler/' + f'{crop_no}-{crop_dict[crop_no][0]}_D{futureDay}_M23_' + 'Y_scaler.model')
    # yy_scale = joblib.load(path + 'scaler/' + f'{crop_dict[crop_no][0]}_{scaler_time}_P{pastDay}F{futureDay}_RMSE={int(round(RMSE, 0))}' + 'Y_scaler.model')
    return xx_scale, yy_scale

# def model_save(path, time_now, model, crop_dict, crop_no, pastDay, futureDay, RMSE):
def model_save(path, model, crop_dict, crop_no, futureDay):
    # model.save(path + 'h5/' + f'{crop_dict[crop_no][0]}_{time_now}_P{pastDay}F{futureDay}_RMSE={int(round(RMSE, 0))}.h5')
    model.save(path + 'h5/' + f'{crop_no}-{crop_dict[crop_no][0]}_D{futureDay}_M23.h5')
    print('MODEL-SAVED')

# 預測結果與實際結果的 數值迴轉
def price_inverse(y_pre, y_test, yy_scale):
    pre_price = yy_scale.inverse_transform(y_pre)
    test_price = yy_scale.inverse_transform(y_test)
    diff_price = pre_price - test_price

    return pre_price, test_price, diff_price

# 價格預測
def model_cal(model, x_test):
    # score = model.evaluate(x_test, y_test)
    # print('Score: {}'.format(score))
    y_pre = model.predict(x_test)
    # print('y_pre.shape:', y_pre.shape, 'y_test.shape:', y_test.shape)
    return y_pre

# 計分
def score_cal(pre_price, test_price):
    MSE = mean_squared_error(test_price.reshape(-1, 1), pre_price.reshape(-1, 1))
    RMSE = np.sqrt(MSE)
    MAE = mean_absolute_error(test_price.reshape(-1, 1), pre_price.reshape(-1, 1))
    R2 = r2_score(test_price.reshape(-1, 1), pre_price.reshape(-1, 1))
    print(f"MSE value : {MSE}", f"\nRMSE value : {RMSE}", f"\nMAE value : {MAE}", f"\nR2 score value : {R2}")
    return MSE, RMSE, MAE, R2