import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor(dictionary=True)
            print("数据库连接成功")
            return True
        except Error as e:
            print(f"数据库连接失败: {e}")
            return False
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("数据库连接已关闭")
    
    def execute(self, query, params=None, fetch=False, fetchone=False):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if fetchone:
                return self.cursor.fetchone()
            elif fetch:
                return self.cursor.fetchall()
            else:
                self.connection.commit()
                return self.cursor.lastrowid if self.cursor.lastrowid else True
        except Error as e:
            print(f"数据库操作失败: {e}")
            self.connection.rollback()
            return False
    
    def create_tables(self):
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'operator',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS machines (
                id INT AUTO_INCREMENT PRIMARY KEY,
                machine_code VARCHAR(50) UNIQUE NOT NULL,
                machine_name VARCHAR(100) NOT NULL,
                machine_type VARCHAR(50),
                ip_address VARCHAR(50),
                rack INT DEFAULT 0,
                slot INT DEFAULT 1,
                status VARCHAR(20) DEFAULT 'offline',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_code VARCHAR(50) UNIQUE NOT NULL,
                product_name VARCHAR(100) NOT NULL,
                product_spec VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS process_parameters (
                id INT AUTO_INCREMENT PRIMARY KEY,
                machine_id INT NOT NULL,
                product_id INT NOT NULL,
                parameter_name VARCHAR(100) NOT NULL,
                parameter_address VARCHAR(50) NOT NULL,
                parameter_value VARCHAR(100),
                parameter_unit VARCHAR(20),
                parameter_type VARCHAR(20) DEFAULT 'Int',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (machine_id) REFERENCES machines(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                UNIQUE KEY unique_machine_product_param (machine_id, product_id, parameter_name)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS process_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                machine_id INT NOT NULL,
                product_id INT NOT NULL,
                operator_id INT,
                record_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                parameters_snapshot TEXT,
                notes TEXT,
                FOREIGN KEY (machine_id) REFERENCES machines(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                FOREIGN KEY (operator_id) REFERENCES users(id) ON DELETE SET NULL
            )
            """
        ]
        
        for table_sql in tables:
            self.execute(table_sql)
        
        print("数据表创建完成")
