import pymysql

conn = pymysql.connect(
    host='192.168.15.26',
    port=3307,
    user='root',
    password='F3jD8gH2mB6',
    database='plc_process_db'
)
cursor = conn.cursor()

cursor.execute("SELECT id, parameter_name, is_readonly FROM process_parameter_values ORDER BY id DESC LIMIT 20")
rows = cursor.fetchall()

print("工艺记录参数表的 is_readonly 值：")
print("-" * 60)
for row in rows:
    print(f"ID: {row[0]}, 名称: {row[1]}, is_readonly: {row[2]}")

cursor.close()
conn.close()