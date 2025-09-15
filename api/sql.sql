-- --------------------------------------------------------
-- Base de données : comptabilite
-- --------------------------------------------------------

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- Create database
CREATE DATABASE IF NOT EXISTS comptabilite;
USE comptabilite;

-- --------------------------------------------------------
-- Table : personnel
-- --------------------------------------------------------
CREATE TABLE personnel (
  id INT(11) NOT NULL AUTO_INCREMENT,
  matricule VARCHAR(50) NOT NULL UNIQUE,
  nom VARCHAR(50) NOT NULL,
  qualification VARCHAR(100) NOT NULL,
  affectation VARCHAR(50) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Table : section (centres de coût)
-- --------------------------------------------------------
CREATE TABLE section (
  id INT(11) NOT NULL AUTO_INCREMENT,
  code_section INT(11) NOT NULL UNIQUE,
  label VARCHAR(255) NOT NULL,
  unit VARCHAR(100) NOT NULL,
  type VARCHAR(50) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Table de liaison : personnel_section
-- --------------------------------------------------------
CREATE TABLE personnel_section (
  personnel_id INT(11) NOT NULL,
  section_id INT(11) NOT NULL,
  PRIMARY KEY (personnel_id, section_id),
  CONSTRAINT fk_personnel FOREIGN KEY (personnel_id) REFERENCES personnel (id) ON DELETE CASCADE,
  CONSTRAINT fk_section FOREIGN KEY (section_id) REFERENCES section (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Table : users (application users)
-- --------------------------------------------------------
CREATE TABLE users (
  id INT(11) NOT NULL AUTO_INCREMENT,
  firstname VARCHAR(50) NOT NULL,
  lastname VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL, -- hash (bcrypt/argon2)
  role VARCHAR(50) DEFAULT 'customer',
  status ENUM('active','inactive','suspended') DEFAULT 'active', 
  last_login DATETIME DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Table : roles (role-based access control)
-- --------------------------------------------------------
CREATE TABLE roles (
  id INT(11) NOT NULL AUTO_INCREMENT,
  role_name VARCHAR(50) NOT NULL UNIQUE, -- e.g. admin, accountant, auditor, manager
  description VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Table de liaison : user_roles (many-to-many)
-- --------------------------------------------------------
CREATE TABLE user_roles (
  user_id INT(11) NOT NULL,
  role_id INT(11) NOT NULL,
  PRIMARY KEY (user_id, role_id),
  CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
  CONSTRAINT fk_role FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Table de liaison : user_section (responsabilité analytique)
-- --------------------------------------------------------
CREATE TABLE user_section (
  user_id INT(11) NOT NULL,
  section_id INT(11) NOT NULL,
  PRIMARY KEY (user_id, section_id),
  CONSTRAINT fk_user_section FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
  CONSTRAINT fk_section_responsibility FOREIGN KEY (section_id) REFERENCES section (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Insert sample data
-- --------------------------------------------------------

-- Insert default roles
INSERT INTO roles (role_name, description) VALUES 
('admin', 'Administrator with full access'),
('manager', 'Manager with limited administrative access'),
('accountant', 'Accountant with financial data access'),
('customer', 'Basic user with limited access');

-- Insert sample admin user (password: admin123)
INSERT INTO users (firstname, lastname, email, password, role) VALUES 
('Admin', 'User', 'admin@example.com', '$2b$12$gdeyda9KA7Ov6TCRBU79r.cR9fG7W65zcs.d/ujTlfWcW0.ge9toC', 'admin');

-- Insert sample sections
INSERT INTO section (code_section, label, unit, type) VALUES 
(100, 'Direction Générale', 'DG', 'Administrative'),
(200, 'Comptabilité', 'COMPTA', 'Financial'),
(300, 'Ressources Humaines', 'RH', 'Administrative'),
(400, 'Production', 'PROD', 'Operational');

-- Insert sample personnel
INSERT INTO personnel (matricule, nom, qualification, affectation) VALUES 
('EMP001', 'Dupont Jean', 'Directeur', 'Direction'),
('EMP002', 'Martin Marie', 'Comptable', 'Comptabilité'),
('EMP003', 'Bernard Paul', 'RH Manager', 'Ressources Humaines'),
('EMP004', 'Durand Sophie', 'Opérateur', 'Production');

-- Link personnel to sections
INSERT INTO personnel_section (personnel_id, section_id) VALUES 
(1, 1), -- Jean Dupont -> Direction Générale
(2, 2), -- Marie Martin -> Comptabilité
(3, 3), -- Paul Bernard -> Ressources Humaines
(4, 4); -- Sophie Durand -> Production

COMMIT;
