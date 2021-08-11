import numpy as np
import csv
import pandas as pd
from datetime import datetime, timezone, timedelta
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt


# code會在這兒停止
class StopExecution(Exception):
  def _render_traceback_(self):
    pass

# 獲得目前時間字串
def getDatatimeString():
    return datetime.now(timezone(timedelta(hours=+8))).strftime("%Y-%m-%dT%H:%M:%S")

def getDateString():
    return datetime.now().strftime('%Y%m%d')

def getDateString2():
    return datetime.now().strftime('%Y-%m-%d')


# 記錄結果
result_column_lists = ['time_now', 'crop_name', 'market_name', 'add_weather_data', 'add_typhoon_data', 'train_start_date', 
              'x_train.shape', 'x_test.shape', 
              'model_no', 'model_name', 'pastday', 'futureDay', 'batch_size', 'epochs', 'validation_split', 'patience', 
              'predDay', 'MSE', 'RMSE', 'MAE', 'R2', 'weather_drop_columns', 'city_drop_list', 'market_drop_columns', 'dev_notes', 'LSTM_unit_1', 'LSTM_unit_2', 'repeat_train']

def saveResultOne(path, time_now, crop_dict, crop_no, market_dict, model_dict, market_no, add_weather_data, add_typhoon_data, train_start_date, 
                    x_train, x_test, 
                    model_no, pastDay, futureDay, batch_size, epochs, validation_split, patience,
                    preDay, MSE, RMSE, MAE, R2, weather_drop_columns, city_drop_list, market_drop_columns, dev_notes, LSTM_unit_1, LSTM_unit_2, repeat_train):
    with open(path, 'a', newline='', encoding='utf-8') as f:
        result_writer = csv.writer(f)
        if f.tell()==0: result_writer.writerow(result_column_lists)

        result_lists = [time_now, crop_dict[crop_no][1], market_dict[market_no], add_weather_data, add_typhoon_data, train_start_date, 
                    x_train.shape, x_test.shape, 
                    model_no, model_dict[model_no][1], pastDay, futureDay, batch_size, epochs, validation_split, patience,
                    preDay, MSE, RMSE, MAE, R2, weather_drop_columns, city_drop_list, market_drop_columns, dev_notes, LSTM_unit_1, LSTM_unit_2, f'repeat={repeat_train}']
        result_writer.writerow(result_lists)      

def showResult(path, time_now):
    pdresult = pd.read_csv(path)
    result = pdresult[pdresult.datetime == time_now]

    return result

# 畫圖
def DrawingPlot(path, pre_price, test_price, pic_days, crop_dict, futureDay, crop_no, time_now, pastDay, RMSE):
    plt.figure(figsize=(15,5))
    plt.plot(test_price[-pic_days:], label='Real Price')
    plt.plot(pre_price[-pic_days:], label='Predict Price')
    plt.xlabel('day')   
    plt.ylabel('price')
    plt.title(crop_dict[crop_no][0] + ' predict D' + str(futureDay) + ' price')
    plt.legend()
    plt.savefig(path + 'img/' + f'{crop_dict[crop_no][0]}_{time_now}_P{pastDay}F{futureDay}_RMSE={int(round(RMSE, 0))}  .png')
    # print('pic_saved')
    # plt.show()

