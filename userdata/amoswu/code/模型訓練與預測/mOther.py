import mModel
import mDataset
import numpy as np
import csv
import pandas as pd
import datetime

from sklearn.metrics import mean_squared_error, r2_score

import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei'] #Show Chinese label
plt.rcParams['font.family'] ='sans-serif'
plt.rcParams['axes.unicode_minus'] = False   # 解决负号'-'显示为方块的问题

## code會在這兒停止
class StopExecution(Exception):
  def _render_traceback_(self):
    pass

# raise StopExecution

# 獲得目前時間字串
def getDatatimeString():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+8))).strftime("%Y-%m-%dT%H:%M:%S")

def getDateString():
    return datetime.datetime.now().strftime('%Y%m%d')

def getDateString2():
    return datetime.datetime.now().strftime('%Y-%m-%d')
# 記錄結果
result_column_lists = ['datetime', 'crop_id', 'crop_name', 'market_id', 'market_name', 'add_weather_data',
                       'add_typhoon_data', 'train_start_date', 'model_no', 'model_name', 'past_day', 'future_day',
                       'batch_size', 'epochs', 'validation_split', 'predDay', 'MSE', 'RMSE', 'R2']


def saveResult(_path, _now_time, _crop_id, _market_id, _real_value, _pred_value,
               _is_add_weather_data, _is_add_typhoon_data, _train_start_date, _model_no,
               _past_day, _future_day, _batch_size, _epochs, _validation_split):
  with open(_path, 'a', newline='', encoding='utf-8') as f:
    result_writer = csv.writer(f)
    if f.tell() == 0: result_writer.writerow(result_column_lists)
    for i in range(_future_day):
      # i + 1 = 未來1日的價格
      Dday = i + 1
      real_price = _real_value[Dday:]
      pred_price = _pred_value[:-Dday, i]

      MSE = mean_squared_error(real_price, pred_price)
      RMSE = np.sqrt(MSE)
      R2 = r2_score(real_price, pred_price)

      # result_lists = [datetime_now, crop_id, mDataset.crop_dict[crop_id][1], market_id, mDataset.market_dict[market_id], is_add_weather_data, is_add_typhoon_data, train_start_date, model_no, mModel.model_dict[model_no][1], past_day, future_day, batch_size, epochs, validation_split, Dday, MSE, RMSE, R2]

      result_lists = [_now_time, _crop_id, mDataset.crop_dict[_crop_id][1], _market_id,
                      mDataset.market_dict[_market_id][0],
                      _is_add_weather_data, _is_add_typhoon_data, _train_start_date, _model_no,
                      mModel.model_dict[_model_no][1], _past_day, _future_day, _batch_size, _epochs, _validation_split,
                      Dday,
                      MSE, RMSE, R2]
      result_writer.writerow(result_lists)


def saveResultOne(_path, _now_time, _crop_id, _market_id, _real_value, _pred_value,
                  _is_add_weather_data, _is_add_typhoon_data, _train_start_date, _model_no,
                  _past_day, _future_day, _batch_size, _epochs, _validation_split):
  with open(_path, 'a', newline='', encoding='utf-8') as f:
    result_writer = csv.writer(f)
    if f.tell() == 0: result_writer.writerow(result_column_lists)
    real_price = _real_value
    pred_price = _pred_value

    MSE = mean_squared_error(real_price, pred_price)
    RMSE = np.sqrt(MSE)
    R2 = r2_score(real_price, pred_price)

    result_lists = [_now_time, _crop_id, mDataset.crop_dict[_crop_id][1], _market_id, mDataset.market_dict[_market_id][0],
                    _is_add_weather_data, _is_add_typhoon_data, _train_start_date, _model_no,
                    mModel.model_dict[_model_no][1], _past_day, _future_day, _batch_size, _epochs, _validation_split,
                    _future_day,
                    MSE, RMSE, R2]
    result_writer.writerow(result_lists)

def showResult(_path, _now_time):
    pdresult = pd.read_csv(_path)
    result = pdresult[pdresult.datetime == _now_time]

    return result


# 畫圖
def drawResult(_path, _now_time, _future_day, _crop_id, _market_id, _true_value, _pred_value, _plot_day):
    for i in range(_plot_day):
        # i + 1 = 未來1日的價格
        Dday = i + 1
        real_price = _true_value
        pred_price = _pred_value[:, i:Dday]
        for j in range(Dday):
            pred_price = np.insert(pred_price, 0, None)
        fig, ax = plt.subplots()
        fig.set_size_inches(15, 5)

        ax.plot(real_price, label='real price')
        ax.plot(pred_price, label='pred price')

        ax.set(xlabel='day', ylabel='price',
               title='predict D' + str(Dday) + '_' + mDataset.crop_dict[_crop_id][1] + ' price')
        ax.legend()
        # ax.grid()

        plt.savefig(_path + _now_time + '_D' + str(Dday) + '_' + str(_crop_id) + '_' + str(_market_id) + '.png')

        # plt.show()


def drawResultOne(_path, _now_time, _future_day, _crop_id, _market_id, _true_value, _pred_value):
    real_price = _true_value
    pred_price = _pred_value

    fig, ax = plt.subplots()
    fig.set_size_inches(15, 5)

    ax.plot(real_price, label='real price')
    ax.plot(pred_price, label='pred price')

    ax.set(xlabel='day', ylabel='price',
           title='predict D' + str(_future_day) + '_' + mDataset.crop_dict[_crop_id][1] + ' price')
    ax.legend()
    # ax.grid()

    plt.savefig(_path + _now_time + '_D' + str(_future_day) + '_' + str(_crop_id) + '_' + str(_market_id) + '.png')

    # plt.show()