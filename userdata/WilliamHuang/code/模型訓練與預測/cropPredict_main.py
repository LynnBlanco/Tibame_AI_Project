import os
import mData, cropPredict_function, mConfig
import mOther, mMySQL

# 作物選擇
croplist = [11, 12, 13, 14, 16, 17, 18, 19, 20, 23, 24]
# 時間軸決定
daylist = [1, 2, 3, 7]

'''----------所有作物統一資料區----------'''
date_today = mOther.getDateString()
data_get_start = '2019-01-01'
today_date = mOther.getDateString2()
end_date = today_date
# start_date = mDataset.dateShift(end_date, -30)

path = os.path.dirname(os.path.abspath(__file__)) + '/'
# path = './'
# save_result_dir = './mResult/%s/' % date_today


# 模型預測執行
DB_category_insert = []
for crop_category in croplist:

    # 由於 梨子2017年以前，市場資料並無所有月份，將導致ohe月份缺少特定月份，相較訓練時的shape不一，故往前取自該年度
    if crop_category == 17:
        data_get_start = '2017-01-01'
    # 由於 芒果2007年以前，市場資料並無所有月份，將導致ohe月份缺少特定月份，相較訓練時的shape不一，故往前取自該年度
    elif crop_category == 20:    
        data_get_start = '2007-01-01'
    else:
        data_get_start = '2019-01-01'

    DB_days_insert = []
    
    for Pday in range(4):
        [crop_no, market_id, pastDay, futureDay, 
        ohe, price_na_del, market_drop_columns_no, add_weather_data, add_typhoon_data]  =  mConfig.model_input_param_dict[crop_category][Pday]

        
        if Pday == 0:
            nonpre_list =[today_date, 
                    crop_no, 
                    market_id, 
                    round(cropPredict_function.crop_Predict(crop_no, market_id, pastDay, futureDay,
                            ohe, price_na_del, market_drop_columns_no, add_weather_data, add_typhoon_data, 
                            data_get_start, end_date, path)[1], 2)]
            for i in nonpre_list:
                DB_days_insert.append(i)

                
        DB_days_insert.append(
            round(cropPredict_function.crop_Predict(crop_no, market_id, pastDay, futureDay,
                        ohe, price_na_del, market_drop_columns_no, add_weather_data, add_typhoon_data, 
                        data_get_start, end_date, path)[0], 2
                )
        )
    DB_days_insert.append(None)
    DB_days_insert.append('LSTM-Will')
    mData.insertPredictPrice (DB_days_insert[0], DB_days_insert[1], DB_days_insert[2], DB_days_insert[3], DB_days_insert[4], DB_days_insert[5], DB_days_insert[6], DB_days_insert[7], None, 'LSTM-Will')
    # insertPredictPrice(insert_date, crop_no, market_id, current_price, pred_1D_price, pred_2D_price, pred_3D_price, pred_7D_price, pred_15D_price, model_type):

    DB_category_insert.append(DB_days_insert)


print(DB_days_insert)
print(DB_category_insert)

mMySQL.link.close()


