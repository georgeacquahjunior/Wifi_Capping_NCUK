CREATE DATABASE IF NOT EXISTS wifi_capping;
USE wifi_capping;

-- Users table for RADIUS authentication
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(255),
    data_limit_mb INT DEFAULT 1000,
    data_used_mb INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- RADIUS accounting sessions
CREATE TABLE IF NOT EXISTS radius_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(128) NOT NULL UNIQUE,
    username VARCHAR(64) NOT NULL,
    nas_ip_address VARCHAR(15) NOT NULL,
    nas_port INT,
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP NULL,
    bytes_in BIGINT DEFAULT 0,
    bytes_out BIGINT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_username (username),
    INDEX idx_session_id (session_id),
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

-- NAS (Network Access Server) devices
CREATE TABLE IF NOT EXISTS nas_devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nas_ip VARCHAR(15) NOT NULL UNIQUE,
    nas_name VARCHAR(64) NOT NULL,
    nas_secret VARCHAR(128) NOT NULL,
    nas_type VARCHAR(32) DEFAULT 'wireless',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin audit log
CREATE TABLE IF NOT EXISTS admin_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_user VARCHAR(64) NOT NULL,
    action VARCHAR(128) NOT NULL,
    target_user VARCHAR(64),
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (username, password, email, data_limit_mb) VALUES 
('testuser1', 'password123', 'test1@ncuk.ac.uk', 2000),
('testuser2', 'password456', 'test2@ncuk.ac.uk', 1500),
('admin', 'admin123', 'admin@ncuk.ac.uk', 10000);

INSERT INTO nas_devices (nas_ip, nas_name, nas_secret) VALUES
('192.168.1.1', 'Main WiFi Controller', 'nas_secret_key'),
('192.168.1.2', 'Library WiFi Controller', 'library_secret'),
('192.168.1.3', 'Dorm WiFi Controller', 'dorm_secret');