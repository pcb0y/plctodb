-- 挤出机工艺参数管理系统数据库结构
-- 创建数据库
CREATE DATABASE IF NOT EXISTS plc_process_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE plc_process_db;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'operator') DEFAULT 'operator',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 模板表
CREATE TABLE IF NOT EXISTS templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 模板参数表
CREATE TABLE IF NOT EXISTS template_parameters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_id INT NOT NULL,
    parameter_name VARCHAR(100) NOT NULL,
    parameter_address VARCHAR(50) NOT NULL,
    data_type VARCHAR(20) DEFAULT 'Int',
    unit VARCHAR(20),
    is_readonly BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE
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
    FOREIGN KEY (template_id) REFERENCES templates(id)
);

-- 产品表
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_code VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(100) NOT NULL,
    product_spec VARCHAR(100),
    version INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 工艺参数表（机台-产品关联参数）
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
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 工艺记录表
CREATE TABLE IF NOT EXISTS process_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    machine_id INT NOT NULL,
    product_id INT NOT NULL,
    record_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operator VARCHAR(50),
    notes TEXT,
    version INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 工艺记录参数快照表
CREATE TABLE IF NOT EXISTS record_parameters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_id INT NOT NULL,
    parameter_name VARCHAR(100) NOT NULL,
    parameter_address VARCHAR(50) NOT NULL,
    parameter_value VARCHAR(100),
    parameter_unit VARCHAR(20),
    data_type VARCHAR(20) DEFAULT 'Int',
    is_readonly BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (record_id) REFERENCES process_records(id) ON DELETE CASCADE
);

-- 插入默认管理员用户（密码：Windows,.1）
INSERT INTO users (username, password_hash, role) VALUES 
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', 'admin');

-- 插入示例模板
INSERT INTO templates (template_name, description) VALUES
('默认模板', '系统默认工艺参数模板'),
('诚逆源设备SJZ65-132', '诚逆源挤出机设备模板'),
('ZJ19-163,ZJ20-79', 'ZJ系列挤出机模板'),
('ZJ19-48', 'ZJ19系列挤出机模板'),
('ZJ21-29', 'ZJ21系列挤出机模板');
