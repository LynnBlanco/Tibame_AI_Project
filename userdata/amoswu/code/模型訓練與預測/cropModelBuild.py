# 價格預測版本v5

import os
import mOther
import mModelBuild

# 選擇農產品，目前只有1 高麗菜, 15 香蕉
crop_id = 2
# 選擇市場，目前只有台北一 8或23都可以
market_id = 8
# 是否要加入天氣資料
is_add_weather_data = False
# 是否要加入颱風資料
is_add_typhoon_data = False
# 訂定訓練資料的期間、測試資料的期間
train_start_date = '2000-01-01' # '2000-06-01'
train_end_date = '2020-05-31'
test_start_date = '2020-06-01'
test_end_date = '2021-06-30'
# 設定往前以及往後看的天數, 若many to many, past_day, future_day要設定一樣的值
past_day = 15
future_day = 1
# 畫多少天的預測圖，要小於或等於上面future_day的數字, one to one 只有1張
plot_day = 1
# 使用哪一個模型，目前有1, 2, 4
model_no = 4
# 其它參數
batch_size = 128
epochs = 1000
validation_split = 0.1

# 是否要將結果存入
is_save_result = True
date_today = mOther.getDateString()
save_result_dir = './mResult/'
# save_result_dir = './mResult/%s/' % date_today
save_result_csv = 'result.csv'
# Avg_price是否要shift
is_price_shift = None

if not os.path.exists(save_result_dir):os.makedirs(save_result_dir)

# 產生預測模型，以及儲存結果
croplist = [1, 2, 4, 5, 6, 7, 15]
daylist = [1, 2, 3, 7, 15]
marketlist = [8]

for m_id in marketlist:
    for c_id in croplist:
        for f_day in daylist:
            mModelBuild.buildPredictModel(c_id, m_id, is_add_weather_data, is_add_typhoon_data,
                                          train_start_date, train_end_date, test_start_date, test_end_date,
                                          past_day, f_day, plot_day,
                                          model_no, batch_size, epochs, validation_split,
                                          is_save_result, save_result_dir, save_result_csv, is_price_shift)