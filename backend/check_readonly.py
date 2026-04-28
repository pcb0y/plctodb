import pymysql

conn = pymysql.connect(
    host='192.168.15.26',
    port=3307,
    user='root',
    password='F3jD8gH2mB6',
    database='plc_process_db'
)
cursor = conn.cursor()

template_id = 11

cursor.execute(f"SELECT id, parameter_name, is_readonly FROM template_parameters WHERE template_id = {template_id} LIMIT 20")
rows = cursor.fetchall()

print(f"模板 {template_id} 的参数 is_readonly 值：")
print("-" * 60)
for row in rows:
    print(f"ID: {row[0]}, 名称: {row[1]}, is_readonly: {row[2]}")

cursor.close()
conn.close()