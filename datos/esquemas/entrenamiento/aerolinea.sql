CREATE TABLE airports (
  airport_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique airport identifier',
  iata_code CHAR(3) NOT NULL COMMENT 'Three letter IATA code',
  airport_name VARCHAR(100) NOT NULL COMMENT 'Official airport name',
  city VARCHAR(60) NOT NULL COMMENT 'City served by the airport',
  country VARCHAR(60) NOT NULL COMMENT 'Country where the airport is located',
  PRIMARY KEY (airport_id)
) COMMENT='Airports served by the airline';

CREATE TABLE aircraft (
  aircraft_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique aircraft identifier',
  model VARCHAR(40) NOT NULL COMMENT 'Aircraft model',
  manufacturer VARCHAR(40) NOT NULL COMMENT 'Manufacturer name',
  capacity INT NOT NULL COMMENT 'Number of passenger seats',
  purchase_date DATE NOT NULL COMMENT 'Date the airline acquired the aircraft',
  PRIMARY KEY (aircraft_id)
) COMMENT='Fleet of aircraft';

CREATE TABLE routes (
  route_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique route identifier',
  origin_airport_id INT NOT NULL COMMENT 'Departure airport',
  destination_airport_id INT NOT NULL COMMENT 'Arrival airport',
  distance_km INT NOT NULL COMMENT 'Distance of the route in kilometers',
  PRIMARY KEY (route_id),
  FOREIGN KEY (origin_airport_id) REFERENCES airports (airport_id),
  FOREIGN KEY (destination_airport_id) REFERENCES airports (airport_id)
) COMMENT='Routes between two airports';

CREATE TABLE flights (
  flight_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique flight identifier',
  route_id INT NOT NULL COMMENT 'Route flown',
  aircraft_id INT NOT NULL COMMENT 'Aircraft used',
  departure_time DATETIME NOT NULL COMMENT 'Scheduled departure date and time',
  arrival_time DATETIME NOT NULL COMMENT 'Scheduled arrival date and time',
  status VARCHAR(15) NOT NULL COMMENT 'Status: scheduled, completed, delayed or cancelled',
  base_price DECIMAL(8,2) NOT NULL COMMENT 'Base fare in US dollars',
  PRIMARY KEY (flight_id),
  FOREIGN KEY (route_id) REFERENCES routes (route_id),
  FOREIGN KEY (aircraft_id) REFERENCES aircraft (aircraft_id)
) COMMENT='Individual flights';

CREATE TABLE passengers (
  passenger_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique passenger identifier',
  first_name VARCHAR(60) NOT NULL COMMENT 'Passenger first name',
  last_name VARCHAR(60) NOT NULL COMMENT 'Passenger last name',
  passport_number VARCHAR(15) NOT NULL COMMENT 'Passport number',
  nationality VARCHAR(40) NOT NULL COMMENT 'Nationality of the passenger',
  birth_date DATE NOT NULL COMMENT 'Date of birth',
  PRIMARY KEY (passenger_id)
) COMMENT='Registered passengers';

CREATE TABLE bookings (
  booking_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique booking identifier',
  passenger_id INT NOT NULL COMMENT 'Passenger who made the booking',
  booking_date DATE NOT NULL COMMENT 'Date the booking was made',
  total_amount DECIMAL(10,2) NOT NULL COMMENT 'Total paid in US dollars',
  channel VARCHAR(15) NOT NULL COMMENT 'Sales channel: website, app, agency or counter',
  PRIMARY KEY (booking_id),
  FOREIGN KEY (passenger_id) REFERENCES passengers (passenger_id)
) COMMENT='Bookings made by passengers';

CREATE TABLE tickets (
  ticket_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique ticket identifier',
  booking_id INT NOT NULL COMMENT 'Booking that includes the ticket',
  flight_id INT NOT NULL COMMENT 'Flight covered by the ticket',
  seat_number VARCHAR(4) NOT NULL COMMENT 'Assigned seat, for example 12A',
  fare_class VARCHAR(10) NOT NULL COMMENT 'Fare class: economy, business or first',
  price_paid DECIMAL(8,2) NOT NULL COMMENT 'Price paid for this ticket in US dollars',
  PRIMARY KEY (ticket_id),
  FOREIGN KEY (booking_id) REFERENCES bookings (booking_id),
  FOREIGN KEY (flight_id) REFERENCES flights (flight_id)
) COMMENT='Tickets issued per flight';

CREATE TABLE crew_members (
  crew_id INT NOT NULL AUTO_INCREMENT COMMENT 'Unique crew member identifier',
  first_name VARCHAR(60) NOT NULL COMMENT 'Crew member first name',
  last_name VARCHAR(60) NOT NULL COMMENT 'Crew member last name',
  role VARCHAR(20) NOT NULL COMMENT 'Role: pilot, copilot or attendant',
  hire_date DATE NOT NULL COMMENT 'Date the person was hired',
  PRIMARY KEY (crew_id)
) COMMENT='Pilots and cabin crew';

CREATE TABLE flight_crew (
  flight_id INT NOT NULL COMMENT 'Flight the crew member works',
  crew_id INT NOT NULL COMMENT 'Crew member assigned',
  PRIMARY KEY (flight_id, crew_id),
  FOREIGN KEY (flight_id) REFERENCES flights (flight_id),
  FOREIGN KEY (crew_id) REFERENCES crew_members (crew_id)
) COMMENT='Crew assigned to each flight';
