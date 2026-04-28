import pymysql

conn = pymysql.connect(
    host='192.168.15.26',
    port=3307,
    user='root',
    password='F3jD8gH2mB6',
    database='plc_process_db'
)
cursor = conn.cursor()

cursor.execute("SELECT id, machine_name, template_id FROM machines LIMIT 10")
rows = cursor.fetchall()

print("机台信息：")
for row in rows:
    print(f"ID: {row[0]}, 名称: {row[1]}, 模板ID: {row[2]}")

cursor.close()
conn.close()