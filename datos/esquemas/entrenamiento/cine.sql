CREATE TABLE movies (
  movie_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique movie identifier',
  title VARCHAR(120) NOT NULL COMMENT 'Movie title',
  genre VARCHAR(30) NOT NULL COMMENT 'Main genre',
  duration_min INT NOT NULL COMMENT 'Duration in minutes',
  release_date DATE NOT NULL COMMENT 'Premiere date',
  age_rating VARCHAR(5) NOT NULL COMMENT 'Age rating: G, PG, PG-13 or R',
  PRIMARY KEY (movie_id)
) COMMENT='Movies shown at the cinema chain';

CREATE TABLE theaters (
  theater_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique theater identifier',
  theater_name VARCHAR(80) NOT NULL COMMENT 'Name of the cinema complex',
  city VARCHAR(60) NOT NULL COMMENT 'City where it is located',
  opened_date DATE NOT NULL COMMENT 'Opening date',
  PRIMARY KEY (theater_id)
) COMMENT='Cinema complexes';

CREATE TABLE halls (
  hall_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique hall identifier',
  theater_id INT NOT NULL COMMENT 'Complex where the hall is',
  hall_name VARCHAR(30) NOT NULL COMMENT 'Hall name or number',
  seats INT NOT NULL COMMENT 'Number of seats',
  is_3d TINYINT(1) NOT NULL COMMENT '1 if the hall supports 3D projection, 0 otherwise',
  PRIMARY KEY (hall_id),
  FOREIGN KEY (theater_id) REFERENCES theaters (theater_id)
) COMMENT='Projection halls';

CREATE TABLE screenings (
  screening_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique screening identifier',
  movie_id INT NOT NULL COMMENT 'Movie shown',
  hall_id INT NOT NULL COMMENT 'Hall where it is shown',
  start_time DATETIME NOT NULL COMMENT 'Date and time the screening starts',
  ticket_price DECIMAL(6,2) NOT NULL COMMENT 'Ticket price in quetzales',
  PRIMARY KEY (screening_id),
  FOREIGN KEY (movie_id) REFERENCES movies (movie_id),
  FOREIGN KEY (hall_id) REFERENCES halls (hall_id)
) COMMENT='Scheduled screenings';

CREATE TABLE customers (
  customer_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique customer identifier',
  full_name VARCHAR(100) NOT NULL COMMENT 'Full name',
  email VARCHAR(100) COMMENT 'Contact email',
  birth_date DATE NOT NULL COMMENT 'Date of birth',
  joined_date DATE NOT NULL COMMENT 'Date the customer joined the loyalty club',
  PRIMARY KEY (customer_id)
) COMMENT='Loyalty club members';

CREATE TABLE tickets (
  ticket_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique ticket identifier',
  screening_id INT NOT NULL COMMENT 'Screening the ticket is for',
  customer_id INT COMMENT 'Member who bought it, null for walk-in buyers',
  seat_label VARCHAR(5) NOT NULL COMMENT 'Seat, for example F12',
  purchase_time DATETIME NOT NULL COMMENT 'Date and time of the purchase',
  price_paid DECIMAL(6,2) NOT NULL COMMENT 'Price paid in quetzales',
  PRIMARY KEY (ticket_id),
  FOREIGN KEY (screening_id) REFERENCES screenings (screening_id),
  FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
) COMMENT='Tickets sold';

CREATE TABLE concessions (
  item_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique concession item identifier',
  item_name VARCHAR(60) NOT NULL COMMENT 'Item name, such as popcorn or soda',
  price DECIMAL(6,2) NOT NULL COMMENT 'Price in quetzales',
  PRIMARY KEY (item_id)
) COMMENT='Snack bar items';

CREATE TABLE concession_sales (
  sale_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique snack sale identifier',
  ticket_id INT NOT NULL COMMENT 'Ticket the snack was bought with',
  item_id INT NOT NULL COMMENT 'Item bought',
  quantity INT NOT NULL COMMENT 'Units bought',
  PRIMARY KEY (sale_id),
  FOREIGN KEY (ticket_id) REFERENCES tickets (ticket_id),
  FOREIGN KEY (item_id) REFERENCES concessions (item_id)
) COMMENT='Snack bar sales';
