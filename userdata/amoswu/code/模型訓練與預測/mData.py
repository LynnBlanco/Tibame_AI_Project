import pandas as pd
import mMySQL
import mConfig
import mData


# 查天氣：
# def queryWeather (起始日期, 結束日期)
def queryWeather(start_date, end_date):
	mMySQL.dbConnect()
	cursor = mMySQL.cur

	args = [start_date, end_date]
	cursor.callproc('p_tbl_weather_r', args)
	column_names = tuple([i[0] for i in cursor.description])
	# print(column_names)
	l = []
	for data in cursor.fetchall():
	    l.append(data)

	table = pd.DataFrame(l, columns=column_names)

	# mMySQL.dbDisconnect()

	return table
# 範例：print(queryWeather('2021-01-19','2021-06-29'))


# 查批發價：
# def queryDailyPrice (查詢類別, 查詢起始日期, 查詢結束日期, 農產品id, 市場id)
# 查詢類別：
# 1 查該市場全部蔬菜或水果
# 2 查指定的水果
def queryDailyPrice(query_type, start_date, end_date, crop_id, market_id):
	mMySQL.dbConnect()
	cursor = mMySQL.cur

	args = [query_type, start_date, end_date, crop_id, market_id]
	cursor.callproc('p_daily_crop_price_r', args)
	column_names = tuple([i[0] for i in cursor.description])
	# print(column_names)
	l = []
	for data in cursor.fetchall():
		l.append(data)

	table = pd.DataFrame(l, columns=column_names)

	# mMySQL.dbDisconnect()

	return table
# print(queryDailyPrice(1,'2021-07-29','2021-08-01',8,8))


# 插入預測價格：
# def insertPredictPrice (插入日期, 農產品id, 市場id,當日價格,預測1日價格,預測2日價格,預測3日價格,預測7日價格,預測15日價格, 模組中文名稱(可以自訂))
def insertPredictPrice(insert_date, crop_id, market_id, current_price, pred_1D_price, pred_2D_price, pred_3D_price, pred_7D_price, pred_15D_price, model_type):
	mMySQL.dbConnect()
	cursor = mMySQL.cur

	args = [insert_date, crop_id, market_id, current_price, pred_1D_price, pred_2D_price, pred_3D_price, pred_7D_price, pred_15D_price, model_type, 0]
	cursor.callproc('p_predict_crop_price_c', args)

	# mMySQL.dbDisconnect()
# 範例：insertPredictPrice('2021-07-31',2,8,10,100,200,300,700,1500,'self-attention')

def getCorpDfFromDB(_quepy_type, _start_date, _end_date, _crop_id, _market_id):
	# 讀取農產品資料
	df_crop = mData.queryDailyPrice(_quepy_type, _start_date, _end_date, _crop_id, _market_id)

	# 要移除的欄位
	market_drop_columns = mConfig.market_drop_columns

	# 移除不需要的欄位
	df = df_crop.drop(market_drop_columns, axis=1)

	# 將休市價格填入前一日價格
	df = df.fillna(method="ffill")

	df = df.dropna()

	df_crop = df.rename(columns={'Date': 'date'}).set_index('date')

	return df_crop

def getAllDfFromDB(_is_add_weather_data, _is_add_typhoon_data, _start_date, _end_date, _crop_id, _market_id):

	# 取得訓練資料集 Dataframe
	df_weather = None # 還沒寫
	df_typhoon = None # 還萬寫
	query_type = 2
	df_crop = getCorpDfFromDB(query_type, _start_date, _end_date, _crop_id, _market_id)

	df_all = df_crop

	# 是否要合併天氣資料
	if _is_add_weather_data:
		pass
	# 是否要合併颱風資料
	if _is_add_typhoon_data:
		pass

	# 把平均價格移到最後1欄
	col_Avg_price = df_all.pop('Avg_price')
	df_all = pd.concat([df_all, col_Avg_price], axis=1)

	# 將資料複製一份來作業, 將欄位index改為date
	df = df_all.copy()
	df = df.reset_index().rename(columns={'index': 'date'})
	# 將非數字欄位移除
	df = df.select_dtypes(exclude=['object'])

	return df

# 農產品id：
# '1','高麗菜','LA1 甘藍 初秋 '
# '2','胡蘿蔔','SB2 胡蘿蔔 清洗 '
# '3','牛番茄','FJ3 番茄 牛蕃茄 '
# '4','胡瓜','FD1 花胡瓜  '
# '5','絲瓜','FF1 絲瓜  '
# '6','包心白菜','LC1 包心白 包白 '
# '7','青蔥','SE6 青蔥 粉蔥 '
# '8','苦瓜','FG1 苦瓜 白大米 '
# '9','洋蔥','SD1 洋蔥 本產 '
# '10','空心菜','LF2 蕹菜 小葉 '
# '11','番石榴','P1 番石榴 珍珠芭 '
# '12','鳳梨','B2 鳳梨 金鑽鳳梨 '
# '13','木瓜','I1 木瓜 網室紅肉 '
# '14','西瓜','T1 西瓜 大西瓜 '
# '15','香蕉','A1 香蕉  '
# '16','蘋果','X69 蘋果 富士進口 '
# '17','梨子','O4 梨 新興梨 '
# '18','葡萄','S1 葡萄 巨峰 '
# '19','火龍果','812 火龍果 紅肉 '
# '20','芒果','R1 芒果 愛文 '
# '21','青江菜','LD1 青江白菜 小梗 '
# '22','花椰菜','FB11 花椰菜 青梗 留梗柄'
# '23','檸檬','F1 雜柑 檸檬 '
# '24','小番茄','74 小番茄 玉女 '

# 市場id：
# '1','南投市','蔬菜'
# '2','屏東市','蔬菜'
# '3','永靖鄉','蔬菜'
# '4','西螺鎮','蔬菜'
# '5','高雄市','蔬菜'
# '6','鳳山區','蔬菜'
# '7','台中市','蔬菜'
# '8','台北一','蔬菜'
# '9','台北二','蔬菜'
# '10','台東市','蔬菜'
# '11','溪湖鎮','蔬菜'
# '12','花蓮市','蔬菜'
# '13','三重區','蔬菜'
# '14','桃　農','蔬菜'
# '15','宜蘭市','蔬菜'
# '16','豐原區','蔬菜'
# '17','板橋區','蔬菜'
# '18','三重區','水果'
# '19','嘉義市','水果'
# '20','高雄市','水果'
# '21','鳳山區','水果'
# '22','台中市','水果'
# '23','台北一','水果'
# '24','台北二','水果'
# '25','台東市','水果'
# '26','東勢區','水果'
# '27','桃　農','水果'
# '28','宜蘭市','水果'
# '29','豐原區','水果'
# '30','板橋區','水果'


