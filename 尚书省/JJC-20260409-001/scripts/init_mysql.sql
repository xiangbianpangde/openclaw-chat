-- 数据库初始化脚本
-- 泰迪杯 B 题：上市公司财报智能问数助手

USE caiwu_assistant;

-- ==================== 基础表 ====================

-- 公司信息表
CREATE TABLE companies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_code VARCHAR(20) UNIQUE NOT NULL,
    company_name VARCHAR(100) NOT NULL,
    industry VARCHAR(50),
    listed_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_code (company_code),
    INDEX idx_name (company_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- PDF 文件表
CREATE TABLE pdf_files (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    company_code VARCHAR(20) NOT NULL,
    report_year INT NOT NULL,
    report_type VARCHAR(20),  -- 年报/季报/半年报
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    file_hash VARCHAR(64),
    upload_status ENUM('pending', 'uploaded', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_company_year (company_code, report_year),
    INDEX idx_status (upload_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- PDF 解析结果表（范围分区）
CREATE TABLE pdf_parse_results (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    company_code VARCHAR(20) NOT NULL,
    company_name VARCHAR(100),
    pdf_hash VARCHAR(64),
    page_num INT,
    content_type ENUM('text', 'table', 'image'),
    parse_result JSON,
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_company (company_code),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
)
PARTITION BY RANGE COLUMNS (company_code, created_at) (
    PARTITION p_a_2024 VALUES LESS THAN ('B', '2025-01-01'),
    PARTITION p_b_2024 VALUES LESS THAN ('C', '2025-01-01'),
    PARTITION p_c_2024 VALUES LESS THAN ('D', '2025-01-01'),
    PARTITION p_d_2024 VALUES LESS THAN ('E', '2025-01-01'),
    PARTITION p_e_2024 VALUES LESS THAN ('F', '2025-01-01'),
    PARTITION p_f_2024 VALUES LESS THAN ('G', '2025-01-01'),
    PARTITION p_g_2024 VALUES LESS THAN ('H', '2025-01-01'),
    PARTITION p_h_2024 VALUES LESS THAN ('I', '2025-01-01'),
    PARTITION p_i_2024 VALUES LESS THAN ('J', '2025-01-01'),
    PARTITION p_j_2024 VALUES LESS THAN ('K', '2025-01-01'),
    PARTITION p_k_2024 VALUES LESS THAN ('L', '2025-01-01'),
    PARTITION p_l_2024 VALUES LESS THAN ('M', '2025-01-01'),
    PARTITION p_m_2024 VALUES LESS THAN ('N', '2025-01-01'),
    PARTITION p_n_2024 VALUES LESS THAN ('O', '2025-01-01'),
    PARTITION p_o_2024 VALUES LESS THAN ('P', '2025-01-01'),
    PARTITION p_p_2024 VALUES LESS THAN ('Q', '2025-01-01'),
    PARTITION p_q_2024 VALUES LESS THAN ('R', '2025-01-01'),
    PARTITION p_r_2024 VALUES LESS THAN ('S', '2025-01-01'),
    PARTITION p_s_2024 VALUES LESS THAN ('T', '2025-01-01'),
    PARTITION p_t_2024 VALUES LESS THAN ('U', '2025-01-01'),
    PARTITION p_u_2024 VALUES LESS THAN ('V', '2025-01-01'),
    PARTITION p_v_2024 VALUES LESS THAN ('W', '2025-01-01'),
    PARTITION p_w_2024 VALUES LESS THAN ('X', '2025-01-01'),
    PARTITION p_x_2024 VALUES LESS THAN ('Y', '2025-01-01'),
    PARTITION p_y_2024 VALUES LESS THAN ('Z', '2025-01-01'),
    PARTITION p_z_2024 VALUES LESS THAN (MAXVALUE, '2025-01-01'),
    PARTITION p_future VALUES LESS THAN (MAXVALUE, MAXVALUE)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 财务数据表（年份分区）
CREATE TABLE financial_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    company_code VARCHAR(20) NOT NULL,
    report_year INT NOT NULL,
    report_type VARCHAR(20),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(20, 4),
    unit VARCHAR(20),
    source_page INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_company_year (company_code, report_year),
    INDEX idx_metric (metric_name)
)
PARTITION BY RANGE (report_year) (
    PARTITION p2020 VALUES LESS THAN (2021),
    PARTITION p2021 VALUES LESS THAN (2022),
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION pmax VALUES LESS THAN MAXVALUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==================== 安全相关表 ====================

-- 用户表
CREATE TABLE users (
    id VARCHAR(64) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 角色表
CREATE TABLE roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 权限表
CREATE TABLE permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    permission_name VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(50),
    action VARCHAR(20),
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 角色权限关联表
CREATE TABLE role_permissions (
    role_id INT,
    permission_id INT,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 用户角色关联表
CREATE TABLE user_roles (
    user_id VARCHAR(64),
    role_id INT,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==================== 审计日志表 ====================

-- 操作日志表
CREATE TABLE audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(64),
    action VARCHAR(50),
    resource VARCHAR(100),
    method VARCHAR(10),
    request_body JSON,
    response_status INT,
    response_time_ms INT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_action (action),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 查询日志表
CREATE TABLE query_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(64),
    query_sql TEXT,
    natural_language_query TEXT,
    result_count INT,
    execution_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==================== 任务调度表 ====================

-- 解析任务表
CREATE TABLE parse_tasks (
    task_id VARCHAR(64) PRIMARY KEY,
    total_files INT,
    completed_files INT,
    failed_files INT,
    status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    checkpoint JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 人工审核队列
CREATE TABLE manual_review_queue (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    file_path VARCHAR(500) NOT NULL,
    reason VARCHAR(200),
    status ENUM('pending', 'processing', 'completed', 'skipped') DEFAULT 'pending',
    reviewer_id VARCHAR(64),
    review_result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==================== 初始化数据 ====================

-- 插入预定义角色
INSERT INTO roles (role_name, description) VALUES
('admin', '系统管理员，拥有所有权限'),
('analyst', '数据分析师，可查询和分析数据'),
('viewer', '只读用户，仅查看数据'),
('uploader', '数据上传员，可上传 PDF 文件');

-- 插入预定义权限
INSERT INTO permissions (permission_name, resource, action, description) VALUES
('pdf:upload', 'pdf', 'create', '上传 PDF 文件'),
('pdf:download', 'pdf', 'read', '下载 PDF 文件'),
('pdf:delete', 'pdf', 'delete', '删除 PDF 文件'),
('data:query', 'data', 'read', '查询财务数据'),
('data:export', 'data', 'export', '导出数据'),
('admin:user_manage', 'user', 'manage', '用户管理'),
('admin:system_config', 'system', 'config', '系统配置'),
('admin:audit_view', 'audit', 'read', '查看审计日志');

-- 分配角色权限（admin 拥有所有权限）
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p WHERE r.role_name = 'admin';

-- 分配 analyst 权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p 
WHERE r.role_name = 'analyst' AND p.permission_name IN ('pdf:download', 'data:query', 'data:export');

-- 分配 viewer 权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p 
WHERE r.role_name = 'viewer' AND p.permission_name IN ('data:query');

-- 分配 uploader 权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p 
WHERE r.role_name = 'uploader' AND p.permission_name IN ('pdf:upload', 'pdf:download');

-- ==================== 视图和存储过程 ====================

-- 创建公司财务数据视图
CREATE VIEW v_company_financial_summary AS
SELECT 
    c.company_code,
    c.company_name,
    fd.report_year,
    MAX(CASE WHEN fd.metric_name = '营业收入' THEN fd.metric_value END) AS revenue,
    MAX(CASE WHEN fd.metric_name = '净利润' THEN fd.metric_value END) AS net_profit,
    MAX(CASE WHEN fd.metric_name = '总资产' THEN fd.metric_value END) AS total_assets,
    MAX(CASE WHEN fd.metric_name = '净资产' THEN fd.metric_value END) AS net_assets
FROM companies c
JOIN financial_data fd ON c.company_code = fd.company_code
GROUP BY c.company_code, c.company_name, fd.report_year;

-- 创建解析任务统计视图
CREATE VIEW v_parse_task_stats AS
SELECT 
    status,
    COUNT(*) AS task_count,
    SUM(total_files) AS total_files,
    SUM(completed_files) AS completed_files,
    SUM(failed_files) AS failed_files,
    AVG(CASE WHEN completed_files > 0 THEN completed_files * 100.0 / total_files END) AS avg_success_rate
FROM parse_tasks
GROUP BY status;

DELIMITER $$

-- 创建更新检查点的存储过程
CREATE PROCEDURE update_parse_checkpoint(
    IN p_task_id VARCHAR(64),
    IN p_file_path VARCHAR(500),
    IN p_status VARCHAR(20)
)
BEGIN
    DECLARE v_checkpoint JSON;
    
    -- 获取当前检查点
    SELECT checkpoint INTO v_checkpoint FROM parse_tasks WHERE task_id = p_task_id;
    
    IF v_checkpoint IS NULL THEN
        SET v_checkpoint = JSON_OBJECT('completed', JSON_ARRAY(), 'failed', JSON_ARRAY());
    END IF;
    
    -- 更新检查点
    IF p_status = 'completed' THEN
        SET v_checkpoint = JSON_SET(
            v_checkpoint,
            '$.completed',
            JSON_ARRAY_APPEND(JSON_EXTRACT(v_checkpoint, '$.completed'), '$', p_file_path)
        );
        UPDATE parse_tasks 
        SET checkpoint = v_checkpoint, 
            completed_files = completed_files + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE task_id = p_task_id;
    ELSEIF p_status = 'failed' THEN
        SET v_checkpoint = JSON_SET(
            v_checkpoint,
            '$.failed',
            JSON_ARRAY_APPEND(JSON_EXTRACT(v_checkpoint, '$.failed'), '$', p_file_path)
        );
        UPDATE parse_tasks 
        SET checkpoint = v_checkpoint, 
            failed_files = failed_files + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE task_id = p_task_id;
    END IF;
END$$

DELIMITER ;

-- ==================== 性能优化配置 ====================

-- 启用慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
SET GLOBAL log_queries_not_using_indexes = 'ON';

-- 创建复合索引（覆盖索引）
CREATE INDEX idx_query_optimization ON financial_data (company_code, report_year, metric_name);

-- ==================== 数据加密配置 ====================

-- 启用 TDE（需要 MySQL Enterprise 或 Percona）
-- INSTALL PLUGIN keyring_file SONAME 'keyring_file.so';
-- SET GLOBAL keyring_file_data = '/var/lib/mysql-keyring/keyring';

-- 对敏感表启用加密
ALTER TABLE financial_data ENCRYPTION='Y';
ALTER TABLE pdf_parse_results ENCRYPTION='Y';
