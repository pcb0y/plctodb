import pymysql

conn = pymysql.connect(
    host='192.168.15.26',
    port=3307,
    user='root',
    password='F3jD8gH2mB6',
    database='plc_process_db'
)
cursor = conn.cursor()

cursor.execute("SELECT id, username, role FROM users")
rows = cursor.fetchall()

print("用户列表：")
for row in rows:
    print(f"ID: {row[0]}, 用户名: {row[1]}, 角色: {row[2]}")

cursor.close()
conn.close()