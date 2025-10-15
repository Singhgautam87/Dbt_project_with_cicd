-- Initialize sample data for dbt project
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50),
    name VARCHAR(255),
    email VARCHAR(255),
    region VARCHAR(100),
    signup_date DATE
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(50),
    customer_id VARCHAR(50),
    amount DECIMAL(10,2),
    transaction_date DATE,
    status VARCHAR(50)
);

-- Insert sample data
INSERT INTO customers (customer_id, name, email, region, signup_date) VALUES
('1001', 'John Doe', 'john.doe@email.com', 'North', '2023-01-15'),
('1002', 'Jane Smith', 'jane.smith@email.com', 'South', '2023-02-20'),
('1003', 'Bob Johnson', 'bob.johnson@email.com', 'East', '2023-03-10'),
('1004', 'Alice Brown', 'alice.brown@email.com', 'West', '2023-04-05'),
('1005', 'Charlie Wilson', 'charlie.wilson@email.com', 'North', '2023-05-12');

INSERT INTO transactions (transaction_id, customer_id, amount, transaction_date, status) VALUES
('TXN001', '1001', 150.00, '2023-06-01', 'SUCCESS'),
('TXN002', '1002', 75.50, '2023-06-02', 'SUCCESS'),
('TXN003', '1001', 200.00, '2023-06-03', 'FAILED'),
('TXN004', '1003', 300.25, '2023-06-04', 'SUCCESS'),
('TXN005', '1002', 125.75, '2023-06-05', 'PENDING'),
('TXN006', '1004', 80.00, '2023-06-06', 'SUCCESS'),
('TXN007', '1005', 450.00, '2023-06-07', 'REFUND'),
('TXN008', '1001', 90.00, '2023-06-08', 'SUCCESS');

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_customers_id ON customers(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_id ON transactions(transaction_id);
CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
