import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten, LSTM, TimeDistributed, RepeatVector, Lambda
from keras.callbacks import EarlyStopping, ModelCheckpoint
import joblib

# 建立訓練資料，將資料整理為x_train, y_train
def buildTrain(train, past_day, future_day, is_price_shift):
  x_train, y_train = [], []
  # i+past_day = 本日
  if is_price_shift:
    for i in range(train.shape[0]-future_day-past_day):
      x_train.append(train[i:i+past_day])
      y_train.append(train[i+past_day+future_day-1, -1])
    return np.array(x_train), np.array(y_train)
  else:
    for i in range(train.shape[0]-future_day-past_day):
      x_train.append(train[i:i+past_day])
      y_train.append(train[i+past_day:i+past_day+future_day, -1])
    return np.array(x_train), np.array(y_train)

# 建立測試資料，將資料整理為x_test, y_test, y_real
def buildTest(test, past_day, future_day, is_price_shift):
  x_test, y_test, y_real = [], [], []
  # i+past_day = 本日
  if is_price_shift:
    for i in range(test.shape[0]-future_day-past_day):
      x_test.append(test[i:i+past_day])
      y_test.append(test[i+past_day+future_day-1, -1])
      y_real.append(test[i+past_day+future_day-1][-1])
    return np.array(x_test), np.array(y_test), np.array(y_real)
  else:
    for i in range(test.shape[0]-future_day-past_day):
      x_test.append(test[i:i+past_day])
      y_test.append(test[i+past_day:i+past_day+future_day, -1])
      y_real.append(test[i+past_day][-1])
    return np.array(x_test), np.array(y_test), np.array(y_real)

# 將資料切分為訓練資料及驗證資料
def splitData(X,Y,rate):
  X_train = X[:int(X.shape[0]*(1-rate))]
  Y_train = Y[:int(Y.shape[0]*(1-rate))]
  X_val = X[int(X.shape[0]*(1-rate)):]
  Y_val = Y[int(Y.shape[0]*(1-rate)):]

  return X_train, Y_train, X_val, Y_val

# 將資料依期間切分為訓練資料及測試資料
def splitDataByDate(_df,_train_start_date, _train_end_date, _test_start_date, _test_end_date):
  df_train = _df.iloc[_df[(_train_start_date <= _df.date) & (_df.date <= _train_end_date)].index].set_index('date')
  df_test = _df.iloc[_df[(_test_start_date <= _df.date) & (_df.date <= _test_end_date)].index].set_index('date')

  return df_train, df_test

# 模型建立
def buildManyToManyModel(shape):
  model = Sequential()
  model.add(LSTM(10, input_length=shape[1], input_dim=shape[2], return_sequences=True))
  model.add(TimeDistributed(Dense(1)))
  # https://stackoverflow.com/questions/43034960/many-to-one-and-many-to-many-lstm-examples-in-keras
  # model.add(Lambda(lambda x: x[:, -7:, :])) #Select last N from output
  model.compile(loss="mse", optimizer="adam")
  model.summary()
  return model

# 模型2
def buildManyToManyModel2(shape):
  model = Sequential()
  model.add(LSTM(50, return_sequences=True, input_shape=(shape[1], shape[2])))
  model.add(Dropout(0.2))
  model.add(LSTM(50, return_sequences=True))
  model.add(Dropout(0.2))
  model.add(LSTM(50, return_sequences=True))
  model.add(Dropout(0.2))
  model.add(TimeDistributed(Dense(1)))
  model.compile(loss="mse", optimizer="adam")
  model.summary()
  return model

# 模型3
def buildManyToManyModel3(shape, past_day):
  model = Sequential()
  model.add(LSTM(10, input_length=shape[1], input_dim=shape[2], return_sequences=True))
  # model.add(TimeDistributed(Dense(1)))
  # https://stackoverflow.com/questions/43034960/many-to-one-and-many-to-many-lstm-examples-in-keras
  model.add(Lambda(lambda x: x[:, past_day*-1:, :])) #Select last N from output
  model.compile(loss="mse", optimizer="adam")
  model.summary()
  return model

# 模型4
def buildManyToOneModel4(shape):
  model = Sequential()
  model.add(LSTM(10, input_length=shape[1], input_dim=shape[2]))
  # output shape: (1, 1)
  model.add(Dense(1))
  model.compile(loss="mse", optimizer="adam")
  model.summary()
  return model

# 模型字典: function name, 說明, 是否shift day, 是否只輸出1天
model_dict = {
    1 : [buildManyToManyModel, 'LSTM many to many', False, False],
    2 : [buildManyToManyModel2, 'LSTM many to many', False, False],
    3 : [buildManyToManyModel3, 'LSTM many to many', False, False],
    4 : [buildManyToOneModel4, 'LSTM many to one', True, True],
    5 : ['', ''],
}
# 儲存scaler
def saveScaler(_path, _now_time, _scaler, _market_id, _crop_id, _pre_day, _name):
  joblib.dump(_scaler, _path + _now_time + '_M' + str(_market_id) + '_C' + str(_crop_id) + '_D' + str(_pre_day) + '_' + _name + '.save')

# 儲存scaler
def loadScaler(_path, _market_id, _crop_id, _pre_day, _name):
  return joblib.load(_path + '_M' + str(_market_id) + '_C' + str(_crop_id) + '_D' + str(_pre_day) + '_' + _name + '.save')

def saveH5(_path, _now_time, _model, _pre_day, _crop_id, _market_id):
  _model.save(_path + _now_time + '_D' + str(_pre_day) + '_C' + str(_crop_id) + '_M' + str(_market_id) + '.h5')

# 建立預測輸入資料
def buildPredictEntryOne(_np):
    list_entry = []
    for i in range(_np.shape[0]):
        list_entry.append(_np[i])

    np_entry = np.array(list_entry)
    np_entry = np_entry.reshape(1, np_entry.shape[0], np_entry.shape[1])
    return np_entry