CREATE TABLE users (
  user_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique user identifier',
  full_name VARCHAR(100) NOT NULL COMMENT 'Full name of the user',
  email VARCHAR(100) NOT NULL COMMENT 'Login email',
  country VARCHAR(40) NOT NULL COMMENT 'Country of the user',
  signup_date DATE NOT NULL COMMENT 'Date the account was created',
  PRIMARY KEY (user_id)
) COMMENT='Registered shoppers';

CREATE TABLE categories (
  category_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique category identifier',
  category_name VARCHAR(60) NOT NULL COMMENT 'Name of the product category',
  PRIMARY KEY (category_id)
) COMMENT='Product categories';

CREATE TABLE products (
  product_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique product identifier',
  product_name VARCHAR(120) NOT NULL COMMENT 'Product name',
  category_id INT NOT NULL COMMENT 'Category of the product',
  price DECIMAL(10,2) NOT NULL COMMENT 'Current price in US dollars',
  stock INT NOT NULL COMMENT 'Units available in stock',
  created_at DATE NOT NULL COMMENT 'Date the product was added to the catalog',
  PRIMARY KEY (product_id),
  FOREIGN KEY (category_id) REFERENCES categories (category_id)
) COMMENT='Product catalog';

CREATE TABLE orders (
  order_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique order identifier',
  user_id INT NOT NULL COMMENT 'User who placed the order',
  order_date DATETIME NOT NULL COMMENT 'Date and time the order was placed',
  status VARCHAR(15) NOT NULL COMMENT 'Status: pending, shipped, delivered or cancelled',
  shipping_country VARCHAR(40) NOT NULL COMMENT 'Destination country',
  total_amount DECIMAL(12,2) NOT NULL COMMENT 'Order total in US dollars',
  PRIMARY KEY (order_id),
  FOREIGN KEY (user_id) REFERENCES users (user_id)
) COMMENT='Customer orders';

CREATE TABLE order_items (
  item_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique order line identifier',
  order_id INT NOT NULL COMMENT 'Order that contains the line',
  product_id INT NOT NULL COMMENT 'Product purchased',
  quantity INT NOT NULL COMMENT 'Units purchased',
  unit_price DECIMAL(10,2) NOT NULL COMMENT 'Price per unit at the time of purchase',
  PRIMARY KEY (item_id),
  FOREIGN KEY (order_id) REFERENCES orders (order_id),
  FOREIGN KEY (product_id) REFERENCES products (product_id)
) COMMENT='Lines of each order';

CREATE TABLE payments (
  payment_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique payment identifier',
  order_id INT NOT NULL COMMENT 'Order that was paid',
  method VARCHAR(20) NOT NULL COMMENT 'Method: card, paypal or transfer',
  paid_at DATETIME NOT NULL COMMENT 'Date and time of the payment',
  amount DECIMAL(12,2) NOT NULL COMMENT 'Amount paid in US dollars',
  PRIMARY KEY (payment_id),
  FOREIGN KEY (order_id) REFERENCES orders (order_id)
) COMMENT='Payments received';

CREATE TABLE shipments (
  shipment_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique shipment identifier',
  order_id INT NOT NULL COMMENT 'Order that is shipped',
  carrier VARCHAR(30) NOT NULL COMMENT 'Shipping company',
  shipped_date DATE NOT NULL COMMENT 'Date the package left the warehouse',
  delivered_date DATE COMMENT 'Date it was delivered, null if still in transit',
  PRIMARY KEY (shipment_id),
  FOREIGN KEY (order_id) REFERENCES orders (order_id)
) COMMENT='Shipments of orders';

CREATE TABLE order_returns (
  return_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique return identifier',
  item_id INT NOT NULL COMMENT 'Order line that was returned',
  return_date DATE NOT NULL COMMENT 'Date the return was requested',
  reason VARCHAR(60) NOT NULL COMMENT 'Reason for the return',
  refund_amount DECIMAL(10,2) NOT NULL COMMENT 'Amount refunded in US dollars',
  PRIMARY KEY (return_id),
  FOREIGN KEY (item_id) REFERENCES order_items (item_id)
) COMMENT='Returned items';

CREATE TABLE reviews (
  review_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique review identifier',
  product_id INT NOT NULL COMMENT 'Product reviewed',
  user_id INT NOT NULL COMMENT 'User who wrote the review',
  rating INT NOT NULL COMMENT 'Rating from 1 to 5 stars',
  review_date DATE NOT NULL COMMENT 'Date of the review',
  comment_text VARCHAR(200) COMMENT 'Written comment',
  PRIMARY KEY (review_id),
  FOREIGN KEY (product_id) REFERENCES products (product_id),
  FOREIGN KEY (user_id) REFERENCES users (user_id)
) COMMENT='Product reviews';
