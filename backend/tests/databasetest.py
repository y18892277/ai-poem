import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='1106',
        database='poetry_battle'
    )
    print("数据库连接成功！")
    connection.close()
except Exception as e:
    print(f"数据库连接失败：{str(e)}")