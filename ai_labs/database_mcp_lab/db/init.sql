CREATE DATABASE IF NOT EXISTS demo_db;
USE demo_db;

DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(50)
);

INSERT INTO users (name, email, role) VALUES
('Alice Johnson', 'alice@example.com', 'admin'),
('Bob Smith', 'bob@example.com', 'user'),
('Charlie Brown', 'charlie@example.com', 'user'),
('Diana Prince', 'diana@example.com', 'manager'),
('Ethan Hunt', 'ethan@example.com', 'user'),
('Fiona Gallagher', 'fiona@example.com', 'user');

-- Products table
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10,2),
    stock INT
);

INSERT INTO products (name, price, stock) VALUES
('Laptop', 1200.00, 10),
('Smartphone', 799.99, 25),
('Headphones', 149.99, 50),
('Keyboard', 89.99, 30),
('Mouse', 49.99, 45),
('Monitor', 299.99, 20);

-- Orders table
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    quantity INT,
    order_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO orders (user_id, product_id, quantity, order_date) VALUES
(1, 1, 1, '2025-09-01'),
(2, 2, 2, '2025-09-02'),
(3, 3, 1, '2025-09-05'),
(4, 4, 3, '2025-09-10'),
(5, 2, 1, '2025-09-11'),
(6, 5, 2, '2025-09-12');
