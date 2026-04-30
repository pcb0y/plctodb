-- 挤出机工艺参数管理系统数据库结构
-- 创建数据库
CREATE DATABASE IF NOT EXISTS plc_process_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE plc_process_db;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'operator',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_username (username)
);

-- 模板表
CREATE TABLE IF NOT EXISTS templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 模板参数表
CREATE TABLE IF NOT EXISTS template_parameters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_id INT NOT NULL,
    parameter_name VARCHAR(100) NOT NULL,
    parameter_address VARCHAR(50) NOT NULL,
    parameter_value VARCHAR(100),
    parameter_unit VARCHAR(20),
    parameter_type VARCHAR(20) DEFAULT 'Int',
    is_readonly BOOLEAN DEFAULT FALSE,
    slot INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE,
    INDEX idx_template_parameters_template_id (template_id),
    INDEX idx_template_parameters_parameter_name (parameter_name)
);

-- 机台表
CREATE TABLE IF NOT EXISTS machines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    machine_code VARCHAR(50) NOT NULL UNIQUE,
    machine_name VARCHAR(100) NOT NULL,
    machine_type VARCHAR(50),
    ip_address VARCHAR(50),
    rack INT DEFAULT 0,
    slot INT DEFAULT 1,
    status VARCHAR(20) DEFAULT '',
    template_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE SET NULL,
    INDEX idx_machines_machine_code (machine_code)
);

-- 产品表
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_code VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(100) NOT NULL,
    product_spec VARCHAR(100),
    version INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_products_product_code (product_code)
);

-- 工艺记录表
CREATE TABLE IF NOT EXISTS process_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    machine_id INT NOT NULL,
    product_id INT NOT NULL,
    operator_id INT,
    record_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    version INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (operator_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_process_records_machine_id (machine_id),
    INDEX idx_process_records_product_id (product_id),
    INDEX idx_process_records_operator_id (operator_id),
    INDEX idx_process_records_record_time (record_time)
);

-- 工艺参数值表（工艺记录参数快照）
CREATE TABLE IF NOT EXISTS process_parameter_values (
    id INT AUTO_INCREMENT PRIMARY KEY,
    process_record_id INT NOT NULL,
    parameter_name VARCHAR(100) NOT NULL,
    parameter_address VARCHAR(50) NOT NULL,
    parameter_value VARCHAR(50) NOT NULL,
    parameter_unit VARCHAR(20),
    parameter_type VARCHAR(20) NOT NULL,
    is_readonly BOOLEAN DEFAULT FALSE,
    slot INT DEFAULT 1,
    FOREIGN KEY (process_record_id) REFERENCES process_records(id) ON DELETE CASCADE,
    INDEX idx_process_parameter_values_process_record_id (process_record_id),
    INDEX idx_process_parameter_values_parameter_name (parameter_name)
);

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    operation_type VARCHAR(50) NOT NULL,
    target_type VARCHAR(50),
    target_id INT,
    details TEXT,
    request_params TEXT,
    response_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_operation_logs_user_id (user_id),
    INDEX idx_operation_logs_operation_type (operation_type),
    INDEX idx_operation_logs_target_type (target_type),
    INDEX idx_operation_logs_created_at (created_at)
);

-- 报警参数表
CREATE TABLE IF NOT EXISTS alarm_parameters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    machine_id INT NOT NULL,
    alarm_address VARCHAR(50) NOT NULL,
    alarm_content VARCHAR(200) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(id) ON DELETE CASCADE,
    INDEX idx_alarm_parameters_machine_id (machine_id),
    INDEX idx_alarm_parameters_alarm_address (alarm_address),
    INDEX idx_alarm_parameters_is_active (is_active)
);

-- 插入默认管理员用户（密码：Windows,.1）
INSERT INTO users (username, hashed_password, role) VALUES 
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', 'admin');

-- 插入示例模板
INSERT INTO templates (name) VALUES
('默认模板'),
('诚逆源设备SJZ65-132'),
('ZJ19-163,ZJ20-79'),
('ZJ19-48'),
('ZJ21-29');

-- 插入ZJ21-29模板参数
INSERT INTO template_parameters (template_id, parameter_name, parameter_address, parameter_value, parameter_unit, parameter_type, is_readonly, slot) VALUES
((SELECT id FROM templates WHERE name = 'ZJ21-29'), '保温时长', 'DB1.DBD0', '60', '分钟', 'Int', FALSE, 1),
((SELECT id FROM templates WHERE name = 'ZJ21-29'), '温度设定', 'DB1.DBD4', '180.0', '℃', 'Real', FALSE, 1),
((SELECT id FROM templates WHERE name = 'ZJ21-29'), '压力设定', 'DB1.DBD8', '2.5', 'MPa', 'Real', FALSE, 1),
((SELECT id FROM templates WHERE name = 'ZJ21-29'), '转速设定', 'DB1.DBD12', '120', 'rpm', 'Int', FALSE, 1),
((SELECT id FROM templates WHERE name = 'ZJ21-29'), '当前温度', 'DB2.DBD0', '0.0', '℃', 'Real', TRUE, 1),
((SELECT id FROM templates WHERE name = 'ZJ21-29'), '当前压力', 'DB2.DBD4', '0.0', 'MPa', 'Real', TRUE, 1),
((SELECT id FROM templates WHERE name = 'ZJ21-29'), '当前转速', 'DB2.DBD8', '0', 'rpm', 'Int', TRUE, 1);