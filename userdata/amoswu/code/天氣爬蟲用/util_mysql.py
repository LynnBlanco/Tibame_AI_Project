import pymysql

link = pymysql.connect(
	host = "34.71.74.214",
	user = "root",
	passwd = '1qaz2wsx#EDC',
	db = "team_project",
	charset = "utf8",
	port = 3306
)
# link = pymysql.connect(
# 	host="localhost",
# 	user="root",
# 	passwd="Abc12345",
# 	db="tibame",
# 	charset="utf8",
# 	port=3306
# )

cur = None

def dbConnect():
	global cur
	cur = link.cursor()

def dbDisconnect():
	link.close()

def dbCheckConnect():
	try:
		if link.open:
			pass
		else:
			dbConnect()
	except:
		pass

def exeSql(sql, param):
	try:
		cur.execute(sql, param)
		link.commit()
	except Exception as e:
		print(e, param)

def queryDB(sql,param=None):
	cur.execute(sql, param)
	link.commit()
	myTable = cur.fetchall()
	return myTable

