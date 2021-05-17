import pymysql.cursors

mysql_cur = None
try:
    mysql_con = pymysql.connect(
        host='165.232.155.18',
        port=3306,
        user='admin',
        password='N4aC8G8JDTWSp2WRcgreRQCY',
        db='fras',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    '''
    mysql_con = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='Mrhungidol12345',
        db='fras',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )'''
    print('DB successfully connected')

except:
    print('DB connection failed')
