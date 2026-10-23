CREATE TABLE customers (
  customer_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique customer identifier',
  first_name VARCHAR(60) NOT NULL COMMENT 'Customer first name',
  last_name VARCHAR(60) NOT NULL COMMENT 'Customer last name',
  national_id VARCHAR(15) NOT NULL COMMENT 'National identity document number',
  email VARCHAR(100) COMMENT 'Contact email',
  phone_number VARCHAR(15) NOT NULL COMMENT 'Main phone number of the customer',
  city VARCHAR(60) COMMENT 'City of residence',
  registration_date DATE NOT NULL COMMENT 'Date the customer joined the company',
  PRIMARY KEY (customer_id)
) COMMENT='Customers of the telecom company';

CREATE TABLE plans (
  plan_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique plan identifier',
  plan_name VARCHAR(60) NOT NULL COMMENT 'Commercial name of the plan',
  monthly_fee DECIMAL(8,2) NOT NULL COMMENT 'Monthly fee in quetzales',
  data_gb INT NOT NULL COMMENT 'Included mobile data in gigabytes',
  minutes_included INT NOT NULL COMMENT 'Included voice minutes per month',
  PRIMARY KEY (plan_id)
) COMMENT='Mobile plans offered';

CREATE TABLE subscriptions (
  subscription_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique subscription identifier',
  customer_id INT NOT NULL COMMENT 'Customer who owns the line',
  plan_id INT NOT NULL COMMENT 'Plan contracted',
  start_date DATE NOT NULL COMMENT 'Date the line was activated',
  end_date DATE COMMENT 'Date the line was cancelled, null if still active',
  status VARCHAR(15) NOT NULL COMMENT 'Status: active, suspended or cancelled',
  PRIMARY KEY (subscription_id),
  FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
  FOREIGN KEY (plan_id) REFERENCES plans (plan_id)
) COMMENT='Lines contracted by customers';

CREATE TABLE invoices (
  invoice_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique invoice identifier',
  subscription_id INT NOT NULL COMMENT 'Line that is billed',
  issue_date DATE NOT NULL COMMENT 'Date the invoice was issued',
  due_date DATE NOT NULL COMMENT 'Payment deadline',
  amount DECIMAL(10,2) NOT NULL COMMENT 'Amount billed in quetzales',
  paid TINYINT(1) NOT NULL COMMENT '1 if the invoice was paid, 0 if still pending',
  PRIMARY KEY (invoice_id),
  FOREIGN KEY (subscription_id) REFERENCES subscriptions (subscription_id)
) COMMENT='Monthly invoices';

CREATE TABLE payments (
  payment_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique payment identifier',
  invoice_id INT NOT NULL COMMENT 'Invoice that was paid',
  payment_date DATE NOT NULL COMMENT 'Date of the payment',
  amount_paid DECIMAL(10,2) NOT NULL COMMENT 'Amount paid in quetzales',
  payment_method VARCHAR(20) NOT NULL COMMENT 'Method: cash, card, transfer or app',
  PRIMARY KEY (payment_id),
  FOREIGN KEY (invoice_id) REFERENCES invoices (invoice_id)
) COMMENT='Payments received for invoices';

CREATE TABLE recharges (
  recharge_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique recharge identifier',
  subscription_id INT NOT NULL COMMENT 'Prepaid line that was recharged',
  recharge_date DATETIME NOT NULL COMMENT 'Date and time of the recharge',
  amount DECIMAL(8,2) NOT NULL COMMENT 'Recharged amount in quetzales',
  channel VARCHAR(20) NOT NULL COMMENT 'Channel: store, app, bank or website',
  PRIMARY KEY (recharge_id),
  FOREIGN KEY (subscription_id) REFERENCES subscriptions (subscription_id)
) COMMENT='Balance recharges of prepaid lines';

CREATE TABLE calls (
  call_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique call identifier',
  subscription_id INT NOT NULL COMMENT 'Line that made the call',
  call_start DATETIME NOT NULL COMMENT 'Date and time the call started',
  duration_seconds INT NOT NULL COMMENT 'Duration of the call in seconds',
  destination_type VARCHAR(15) NOT NULL COMMENT 'Destination: local, national or international',
  PRIMARY KEY (call_id),
  FOREIGN KEY (subscription_id) REFERENCES subscriptions (subscription_id)
) COMMENT='Outgoing call records';

CREATE TABLE support_tickets (
  ticket_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique ticket identifier',
  customer_id INT NOT NULL COMMENT 'Customer who opened the ticket',
  opened_at DATETIME NOT NULL COMMENT 'Date and time the ticket was opened',
  closed_at DATETIME COMMENT 'Date and time it was closed, null if still open',
  category VARCHAR(30) NOT NULL COMMENT 'Category: billing, coverage, device or other',
  priority VARCHAR(10) NOT NULL COMMENT 'Priority: low, medium or high',
  PRIMARY KEY (ticket_id),
  FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
) COMMENT='Customer support tickets';
