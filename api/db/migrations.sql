-- Drop existing database (⚠️ careful, this deletes all data)
-- DROP DATABASE IF EXISTS comptabilite;

-- Create database if it doesn’t exist
CREATE DATABASE IF NOT EXISTS comptabilite;
USE comptabilite;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firstname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'customer'
);

-- Example index for faster email lookups (used in login/signup)
CREATE INDEX idx_users_email ON users(email);

-- Optionally insert an admin user (password = 'admin123', bcrypt hash needs to be generated in Python)
-- INSERT INTO users (firstname, lastname, email, password, role)
-- VALUES ('Admin', 'User', 'admin@example.com', '<bcrypt_hash_here>', 'admin');
--mysql -u root -p < db/migrations.sql
--OR
--SOURCE /path/to/your_project/db/migrations.sql;