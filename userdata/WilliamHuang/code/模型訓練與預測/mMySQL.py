import pymysql

link = pymysql.connect(
	host = "請輸入host",
	user = "請輸入名稱",
	passwd = '請輸入密碼',
	db = "請輸入db",
	charset = "utf8",
	port = int("請輸入port")
)

cur = None

def dbConnect():
	global cur
	# link.ping(reconnect=True)
	cur = link.cursor()
	# link.commit()


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


def is_connected(self):
	"""Check if the server is alive"""
	try:
		self.conn.ping(reconnect=True)
		print("db is connecting")
	except:
		# traceback.print_exc()
		self.conn = self.to_connect()
		print("db reconnect")