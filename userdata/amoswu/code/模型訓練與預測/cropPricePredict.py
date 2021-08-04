import mDataset
import mOther
import mPredictPrice
import mData
import mConfig

date_today = mOther.getDateString()
save_result_dir = mConfig.save_result_dir
# save_result_dir = './mResult/%s/' % date_today

croplist = [1, 2, 4, 5, 6, 7, 15]
daylist = [1, 2, 3, 7, 15]

marketlist = [8]

predict_date = ''    # 輸入''就是今天的日期

insert_date = mOther.getDateString2() # '2021-08-03'

past_day = 15

insertDB = True

for m_id in marketlist:
    for c_id in croplist:
        current_price, predict_price_dict = mPredictPrice.cropPricePredictOne(predict_date, past_day, daylist, c_id, m_id)
        print(current_price, predict_price_dict)
        pred_1D_price = predict_price_dict.get(1, None)
        pred_2D_price = predict_price_dict.get(2, None)
        pred_3D_price = predict_price_dict.get(3, None)
        pred_7D_price = predict_price_dict.get(7, None)
        pred_15D_price = predict_price_dict.get(15, None)
        model_type = 'LSTM-Amos'
        if insertDB:
            mData.insertPredictPrice(insert_date, c_id, m_id, current_price, pred_1D_price, pred_2D_price,pred_3D_price, pred_7D_price, pred_15D_price, model_type)