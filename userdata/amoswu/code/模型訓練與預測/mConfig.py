
dataset_folder = './mDataset/'
save_result_dir = './mResult/'

is_add_weather_data = False
is_add_typhoon_data = False

# 所有城市對照英文代碼
city_dict = {
    '基隆市':'KLU',
    '臺北市':'TPE',
    '新北市':'TPH',
    '桃園市':'TYC',
    '新竹市':'HSC',
    '新竹縣':'HSH',
    '苗栗縣':'MAL',
    '臺中市':'TXG',
    '彰化縣':'CWH',
    '南投縣':'NTO',
    '雲林縣':'YLH',
    '嘉義市':'CYI',
    '嘉義縣':'CHY',
    '臺南市':'TNN',
    '高雄市':'KHH',
    '屏東縣':'IUH',
    '宜蘭縣':'ILN',
    '花蓮縣':'HWA',
    '臺東縣':'TTT'
}

# 農作物
crop_dict = {
    1 : ['cabbage', '高麗菜 (LA1 甘藍 初秋)'],
    2 : ['carrot', '胡蘿蔔 (SB2 胡蘿蔔 清洗)'],
    3 : ['beeftomato', '牛番茄 (FJ3 番茄 牛蕃茄)'],
    4 : ['cucumber', '胡瓜 (FD1 花胡瓜)'],
    5 : ['loofah', '絲瓜 (FF1 絲瓜)'],
    6 : ['cabbage2', '包心白菜 (LC1 包心白 包白)'],
    7 : ['shallots', '青蔥 (SE6 青蔥 粉蔥)'],
    8 : ['bittergourd', '苦瓜 (FG1 苦瓜 白大米)'],
    9 : ['onion', '洋蔥 (SD1 洋蔥 本產)'],
    10 : ['waterspinach', '空心菜 (LF2 蕹菜 小葉)'],

    11 : ['guava', '番石榴 (P1 番石榴 珍珠芭)'],
    12 : ['pineapple', '鳳梨 (B2 鳳梨 金鑽鳳梨)'],
    13 : ['papaya', '木瓜 (I1 木瓜 網室紅肉)'],
    14 : ['watermelon', '西瓜 (T1 西瓜 大西瓜)'],
    15 : ['banana', '香蕉 (A1 香蕉)'],
    16 : ['apple', '蘋果 (X69 蘋果 富士進口)'],
    17 : ['pear', '梨子 (O4 梨 新興梨)'],
    18 : ['grape', '葡萄 (S1 葡萄 巨峰)'],
    19 : ['dragonfruit', '火龍果 (812 火龍果 紅肉)'],
    20 : ['mango', '芒果 (R1 芒果 愛文)'],

    21 : ['pakchoy', 'LD1 青江白菜 小梗 '],
    22 : ['cauliflower', 'FB11 花椰菜 青梗 留梗柄'],
    23 : ['lemon', 'F1 雜柑 檸檬 '],
    24 : ['tomato', '74 小番茄 玉女 ']
}

# 只要中文一樣就可以，不用分蔬菜還是水果的市場
market_dict = {
    1 : ['南投市', '蔬菜'],
    2 : ['屏東市', '蔬菜'],
    3 : ['永靖鄉', '蔬菜'],
    4 : ['西螺鎮', '蔬菜'],
    5 : ['高雄市', '蔬菜'],
    6 : ['鳳山區', '蔬菜'],
    7 : ['台中市', '蔬菜'],
    8 : ['台北一', '蔬菜'],
    9 : ['台北二', '蔬菜'],
    10 : ['台東市', '蔬菜'],
    11 : ['溪湖鎮', '蔬菜'],
    12 : ['花蓮市', '蔬菜'],
    13 : ['三重區', '蔬菜'],
    14 : ['桃　農', '蔬菜'],
    15 : ['宜蘭市', '蔬菜'],
    16 : ['豐原區', '蔬菜'],
    17 : ['板橋區', '蔬菜'],
    18 : ['三重區', '水果'],
    19 : ['嘉義市', '水果'],
    20 : ['高雄市', '水果'],
    21 : ['鳳山區', '水果'],
    22 : ['台中市', '水果'],
    23 : ['台北一', '水果'],
    24 : ['台北二', '水果'],
    25 : ['台東市', '水果'],
    26 : ['東勢區', '水果'],
    27 : ['桃　農', '水果'],
    28 : ['宜蘭市', '水果'],
    29 : ['豐原區', '水果'],
    30 : ['板橋區', '水果']
}

# 要移除的欄位列表
# weather columb全部列表: 'date', 'city', 'StnPres', 'SeaPres', 'StnPresMax', 'StnPresMaxTime', 'StnPresMin', 'StnPresMinTime', 'Temperature', 'TMax', 'TMaxTime', 'TMin', 'TMinTime', 'TdDewPoint', 'RH', 'RHMin', 'RHMinTime', 'WS', 'WD', 'WSGust', 'WDGust', 'WGustTime', 'Precp', 'PrecpHour', 'PrecpMax10', 'PrecpMax10Time', 'PrecpMax60', 'PrecpMax60Time', 'SunShine', 'SunShineRate', 'GloblRad', 'VisbMean', 'EvapA', 'UVIMax', 'UVIMaxTime', 'CloudAmount'
weather_drop_columns = [
                        'StnPresMaxTime',
                        'StnPresMinTime',
                        'TMaxTime',
                        'TMinTime',
                        'RHMinTime',
                        'WGustTime',
                        'PrecpMax10',
                        'PrecpMax10Time',
                        'PrecpMax60',
                        'PrecpMax60Time',
                        'UVIMax',
                        'UVIMaxTime'
]

# 要移除的欄位列表
# market columns 全部列表: 'Date', 'Market', 'Product', 'Up_price', 'Mid_price', 'Low_price', 'Avg_price', 'Volume', 'Month', 'Week_day', 'Year', 'Rest_day'
market_drop_columns = [
    'Up_price',
    'Mid_price',
    'Low_price',
    'Avg_price_diff',
    'Volume_diff'
]

