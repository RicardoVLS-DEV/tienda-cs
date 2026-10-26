-- Si usas hosting compartido, omite las dos primeras líneas y selecciona tu base en phpMyAdmin
CREATE DATABASE IF NOT EXISTS store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE store;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    category VARCHAR(60),
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

INSERT INTO products (name, description, price, stock, category) VALUES
('Highland coffee 500 g', 'Medium roast, notes of chocolate and walnut.', 189.00, 24, 'Pantry'),
('Ceramic mug', 'Handmade, 350 ml.', 120.00, 40, 'Home'),
('Hardcover notebook', '160 pages, ivory paper.', 95.50, 60, 'Stationery');
