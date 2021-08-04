import numpy as np

from keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler

import mDataset
import mModel
import mOther

# # 選擇農產品，目前只有1 高麗菜, 15 香蕉
# _crop_id = 15
# # 選擇市場，目前只有1
# _market_id = 1
# # 是否要加入天氣資料
# _is_add_weather_data = False
# # 是否要加入颱風資料
# _is_add_typhoon_data = False
# # 訂定訓練資料的期間、測試資料的期間
# _train_start_date = '2000-01-01'  # '2000-06-01'
# _train_end_date = '2020-05-31'
# _test_start_date = '2020-06-01'
# _test_end_date = '2021-06-30'
# # 設定往前以及往後看的天數, 若many to many, past_day, future_day要設定一樣的值
# _past_day = 15
# _future_day = 15
# # 畫多少天的預測圖，要小於或等於上面future_day的數字, one to one 只有1張
# _plot_day = 15
# # 使用哪一個模型，目前有1, 2, 4
# _model_no = 1
# # 其它參數
# _batch_size = 128
# _epochs = 1000
# _validation_split = 0.1
# # 記錄現在時間
# datetime_now = mOther.getDatatimeString()
# # 是否要將結果存入
# _is_save_result = True
# date_today = mOther.getDateString()
# _save_result_dir = './result/%s/' % date_today
# _save_result_csv = 'result.csv'
# # Avg_price是否要shift
# _is_price_shift = None
# if not os.path.exists(_save_result_dir): os.makedirs(_save_result_dir)

def buildPredictModel(_crop_id, _market_id, _is_add_weather_data, _is_add_typhoon_data,
                      _train_start_date, _train_end_date, _test_start_date, _test_end_date,
                      _past_day, _future_day, _plot_day,
                      _model_no, _batch_size, _epochs, _validation_split,
                      _is_save_result, _save_result_dir, _save_result_csv, _is_price_shift):
    # 記錄現在時間
    datetime_now = mOther.getDatatimeString()

    df = mDataset.getAllDf(_is_add_weather_data, _is_add_typhoon_data, _crop_id, _market_id)

    print('crop_name: %s, is_add_weather_data:%s, is_add_typhoon_data:%s, predict day:%s, crop_id:%s, market_id:%s' % (mDataset.crop_dict[_crop_id][1], _is_add_weather_data, _is_add_typhoon_data, _future_day, _crop_id, _market_id))
    # print(df.head(3))
    # print(df.tail(3))

    # 判斷是否要先將y_train, y_test的資料shift
    _is_price_shift = mModel.model_dict[_model_no][2]

    # 依訓練資料的期間、測試資料的期間來切分資料
    df_train, df_test = mModel.splitDataByDate(df, _train_start_date, _train_end_date, _test_start_date, _test_end_date)

    # 將非數字的欄位移除
    df_train = df_train.select_dtypes(exclude=['object'])
    df_test = df_test.select_dtypes(exclude=['object'])
    # print(df_train.dtypes)

    # 設定x_train, y_train的scaler
    x_sc = MinMaxScaler()
    y_sc = MinMaxScaler()

    # 將訓練資料做MinMaxScaler
    # 先將y_train fit MinMaxScaler，待未來使用
    x_sc.fit(df_train)
    y_train = df_train['Avg_price']
    y_sc.fit(y_train.to_frame())

    # 儲存scaler
    if _is_save_result: mModel.saveScaler(_save_result_dir, '', x_sc, _market_id, _crop_id, _future_day, 'x')
    if _is_save_result: mModel.saveScaler(_save_result_dir, '', y_sc, _market_id, _crop_id, _future_day, 'y')

    df_train_scaled = x_sc.transform(df_train)

    # 製作x_train, y_train
    x_train, y_train = mModel.buildTrain(df_train_scaled, _past_day, _future_day, _is_price_shift)
    # print('x_train shape:', x_train.shape)
    # print('y_train shape:', y_train.shape)

    # 將資料切分為訓練資料及驗證資料
    x_train, y_train, x_val, y_val = mModel.splitData(x_train, y_train, _validation_split)
    # print('x_train shape:', x_train.shape)
    # print('y_train shape:', y_train.shape)
    # print('x_val shape:', x_val.shape)
    # print('y_val shape:', y_val.shape)

    # 將資料由2D改為3D
    if _is_price_shift:
        y_train = y_train[:, np.newaxis, np.newaxis]
        y_val = y_val[:, np.newaxis, np.newaxis]
    else:
        y_train = y_train[:, :, np.newaxis]
        y_val = y_val[:, :, np.newaxis]
    # print('y_train shape:', y_train.shape)
    # print('y_val shape:', y_val.shape)

    # 模型建立
    try:
        model = mModel.model_dict[_model_no][0](x_train.shape)
        # print('model_no:', model_no)
    except Exception as e:
        print('model選錯了, except:', e)

    # 模型訓練
    callback = EarlyStopping(monitor="loss", patience=10, verbose=2, mode="auto")
    model.fit(x_train, y_train, epochs=1000, batch_size=128, validation_data=(x_val, y_val), verbose=2,
              callbacks=[callback])

    # 儲存模型
    if _is_save_result: mModel.saveH5(_save_result_dir, '', model, _future_day, _crop_id, _market_id)

    # 將x_test做MinMaxScaler
    df_test_scaled = x_sc.transform(df_test)
    # print(df_test_scaled.shape)

    # 將資料切為x_test, y_test
    x_test, y_test, y_real = mModel.buildTest(df_test_scaled, _past_day, _future_day, _is_price_shift)
    # print('x_test shape:', x_test.shape)
    # print('y_test shape:', y_test.shape)
    # print('y_real shape:', y_real.shape)

    # 執行價格預測
    x_test_pred = model.predict(x_test)
    # print('x_test_pred.shape:', x_test_pred.shape)

    x_test_pred_shape = x_test_pred.reshape(x_test_pred.shape[0], x_test_pred.shape[1])
    # print('x_test_pred_shape.shape', x_test_pred_shape.shape)
    y_real_shape = y_real.reshape(y_real.shape[0], 1)
    # print('y_real.shape', y_real.shape)
    # 將預測值轉換回實際價格
    x_test_pred_price = y_sc.inverse_transform(x_test_pred_shape)
    y_real_price = y_sc.inverse_transform(y_real_shape)

    # 建立可視的價格預測表
    # daycolumn_x = ['D' + str(x) for x in list(range(1, future_day+1))]
    # daycolumn_y = ['D0']
    # print('預測價格：\n', pd.DataFrame(x_test_pred_price[:,:future_day], columns=daycolumn_x))
    # print('實際價格：\n', pd.DataFrame(y_real_price[:future_day], columns=daycolumn_y))

    # print('x_test.shape:', x_test_pred.shape)
    # print('y_test.shape:', y_test.shape)
    score = model.evaluate(x_test, y_test, verbose=0)
    # print(score)

    # 畫圖
    pp = x_test_pred_price
    rp = y_real_price

    is_output_one = mModel.model_dict[_model_no][3]
    if is_output_one:
        if _is_save_result: mOther.drawResultOne(_save_result_dir, datetime_now, _future_day, _crop_id, _market_id, rp, pp)

    else:
        if _is_save_result: mOther.drawResult(_save_result_dir, datetime_now, _future_day, _crop_id, _market_id, rp, pp,
                                              _plot_day)

    # 儲存結果至csv
    is_output_one = mModel.model_dict[_model_no][3]
    if is_output_one:
        if _is_save_result: mOther.saveResultOne(_save_result_dir + _save_result_csv, datetime_now, _crop_id, _market_id, rp, pp,
                                                 _is_add_weather_data, _is_add_typhoon_data, _train_start_date, _model_no,
                                                 _past_day, _future_day, _batch_size, _epochs, _validation_split)
    else:
        if _is_save_result: mOther.saveResult(_save_result_dir + _save_result_csv, datetime_now, _crop_id, _market_id, rp, pp,
                                              _is_add_weather_data, _is_add_typhoon_data, _train_start_date, _model_no,
                                              _past_day, _future_day, _batch_size, _epochs, _validation_split)

    # 把本次的結果顯示出來
    print(mOther.showResult(_save_result_dir + _save_result_csv, datetime_now))


